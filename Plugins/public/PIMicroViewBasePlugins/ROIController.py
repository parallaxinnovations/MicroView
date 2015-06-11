import logging
import time
import datetime
import wx
import wx.lib.masked
from zope import component, event

from PI.visualization.MicroView.interfaces import ICurrentImage, IOrthoView, ICurrentOrthoPlanes, \
    IMicroViewMainFrame, IImage
from PI.visualization.MicroView.events import ROIKeyEvent, ROIEnabledEvent, ROIDisabledEvent, \
    ROIModifiedEvent, ROIModelModifiedEvent, ROIModelLinkingChangeEvent, ROIModelOrientationChangeEvent, \
    ROIModelTypeChangeEvent, ROIModelControlPointChangeEvent, NotebookPageChangingEvent, \
    CurrentImageClosingEvent

import ROIModel
import vtkROIView
import vtk


class StandardROIToolState(object):

    """Container for standard ROI tool state"""

    def __init__(self, image):
        self.tool_type_index = 0
        self.tool_orientation_index = 2
        self.tool_units_index = 0
        self.observer = None
        self.__orthoplanes_observer = None
        self.roi_extent = [0, 1, 0, 1, 0, 1]
        self.arb_orientation_option = False
        self.model = ROIModel.ROIModel()
        self.view = vtkROIView.vtkROIView()
        self.SetInput(image)

    def SetInput(self, image):
        self.model.SetInput(image)
        self.view.SetInput(image)

    def GetModel(self):
        return self.model

    def GetView(self):
        return self.view

    def SetOrthoPlanesObserver(self, obs):
        self.__orthoplanes_observer = obs

    def GetOrthoPlanesObserver(self):
        return self.__orthoplanes_observer


class ROIController(object):

    """Contains GUI interaction code for the Standard ROI plugin.

    In a standard MVC model, this class is 'C'ontroller.
    """

    def __init__(self, plugin, gui):

        self._plugin = plugin
        self.gui = gui

        self._app_states = {}
        self._current_image_index = None
        self.bIgnoreGUIEvents = False
        self.bArbitraryOrientation = False

        # These next four variables are used to eat duplicate GUI events
        self._oldSizes = None
        self._oldCenters = None
        self._oldSizeEntries = None
        self._oldCenterEntries = None

        # wire up GUI Widget view logic

        gui = self.GetGUIView()

        gui.m_toggleBtnSizeLinking.Bind(
            wx.EVT_TOGGLEBUTTON, self.ToggleHeightWidthLinking)
        gui.m_choiceTool.Bind(wx.EVT_CHOICE, self.onToolChange)
        gui.m_choiceOrientation.Bind(
            wx.EVT_CHOICE, self.onToolOrientationChange)
        gui.m_choiceUnits.Bind(wx.EVT_CHOICE, self.onUnitChange)
        gui.m_selectWholeImageButton.Bind(
            wx.EVT_BUTTON, self.onSelectWholeImage)
        gui.m_centerROIButton.Bind(wx.EVT_BUTTON, self.onCenterROI)
        gui.m_buttonShow.Bind(wx.EVT_BUTTON, self.onButtonROIShow)
        gui.m_checkBoxAllowArbOrientation.Bind(
            wx.EVT_CHECKBOX, self.onArbOrientationCheckbox)

        # time limited features
        gui.m_checkBoxAllowArbOrientation.Disable()

        # Bind handlers for text entry changes

        # 1 - focus events
        gui.m_textCtrlROISizeX.Bind(
            wx.EVT_KILL_FOCUS, lambda evt: self.onSizeEntry(0, evt))
        gui.m_textCtrlROISizeY.Bind(
            wx.EVT_KILL_FOCUS, lambda evt: self.onSizeEntry(1, evt))
        gui.m_textCtrlROISizeZ.Bind(
            wx.EVT_KILL_FOCUS, lambda evt: self.onSizeEntry(2, evt))
        gui.m_textCtrlROICenterX.Bind(
            wx.EVT_KILL_FOCUS, lambda evt: self.onCenterEntry(0, evt))
        gui.m_textCtrlROICenterY.Bind(
            wx.EVT_KILL_FOCUS, lambda evt: self.onCenterEntry(1, evt))
        gui.m_textCtrlROICenterZ.Bind(
            wx.EVT_KILL_FOCUS, lambda evt: self.onCenterEntry(2, evt))

        # 2 - key events
        gui.m_textCtrlROISizeX.Bind(
            wx.EVT_CHAR, lambda evt: self.onSizeChar(0, evt))
        gui.m_textCtrlROISizeY.Bind(
            wx.EVT_CHAR, lambda evt: self.onSizeChar(1, evt))
        gui.m_textCtrlROISizeZ.Bind(
            wx.EVT_CHAR, lambda evt: self.onSizeChar(2, evt))
        gui.m_textCtrlROICenterX.Bind(
            wx.EVT_CHAR, lambda evt: self.onCenterChar(0, evt))
        gui.m_textCtrlROICenterY.Bind(
            wx.EVT_CHAR, lambda evt: self.onCenterChar(1, evt))
        gui.m_textCtrlROICenterZ.Bind(
            wx.EVT_CHAR, lambda evt: self.onCenterChar(2, evt))

        # 3 - enter key events
        gui.m_textCtrlROISizeX.Bind(
            wx.EVT_TEXT_ENTER, lambda evt: self.onSizeEntry(0, evt))
        gui.m_textCtrlROISizeY.Bind(
            wx.EVT_TEXT_ENTER, lambda evt: self.onSizeEntry(1, evt))
        gui.m_textCtrlROISizeZ.Bind(
            wx.EVT_TEXT_ENTER, lambda evt: self.onSizeEntry(2, evt))
        gui.m_textCtrlROICenterX.Bind(
            wx.EVT_TEXT_ENTER, lambda evt: self.onCenterEntry(0, evt))
        gui.m_textCtrlROICenterY.Bind(
            wx.EVT_TEXT_ENTER, lambda evt: self.onCenterEntry(1, evt))
        gui.m_textCtrlROICenterZ.Bind(
            wx.EVT_TEXT_ENTER, lambda evt: self.onCenterEntry(2, evt))

        # 4 - Bind handlers for slider modifications
        gui.m_sliderSizeX.Bind(
            wx.EVT_SLIDER, lambda evt: self.onSetSize(0, evt))
        gui.m_sliderSizeY.Bind(
            wx.EVT_SLIDER, lambda evt: self.onSetSize(1, evt))
        gui.m_sliderSizeZ.Bind(
            wx.EVT_SLIDER, lambda evt: self.onSetSize(2, evt))
        gui.m_sliderCenterX.Bind(
            wx.EVT_SLIDER, lambda evt: self.onSetCenter(0, evt))
        gui.m_sliderCenterY.Bind(
            wx.EVT_SLIDER, lambda evt: self.onSetCenter(1, evt))
        gui.m_sliderCenterZ.Bind(
            wx.EVT_SLIDER, lambda evt: self.onSetCenter(2, evt))

        # 5 - register zope event handlers
        component.provideHandler(self.onROIKeyEvent)
        component.provideHandler(self.onModelModifiedEvent)
        component.provideHandler(self.onModelLinkingChangeEvent)
        component.provideHandler(self.onROITypeChangeEvent)
        component.provideHandler(self.onROIOrientationChangeEvent)
        component.provideHandler(self.onROIControlPointsChanged)
        component.provideHandler(self.OnNotebookPageChangingEvent)
        component.provideHandler(self.onCurrentImageClosingEvent)

    def GetCurrentState(self):
        idx = self.GetCurrentImageIndex()
        return self._app_states.get(idx, None)

    def GetCurrentImageIndex(self):
        return self._current_image_index


    def OnPluginClose(self):

        # stop listening
        self.removeObservers()

        # unregister our zope handlers
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.onROIKeyEvent)
        gsm.unregisterHandler(self.onModelModifiedEvent)
        gsm.unregisterHandler(self.onModelLinkingChangeEvent)
        gsm.unregisterHandler(self.onROITypeChangeEvent)
        gsm.unregisterHandler(self.onROIOrientationChangeEvent)
        gsm.unregisterHandler(self.onROIControlPointsChanged)
        gsm.unregisterHandler(self.OnNotebookPageChangingEvent)
        gsm.unregisterHandler(self.onDemoAuthorized)
        gsm.unregisterHandler(self.onCurrentImageClosingEvent)

    def GetGUIView(self):
        """Returns the view"""
        return self.gui

    def GetVTKView(self, image_index=None):
        if image_index is None:
            image_index = self._current_image_index
        return self._app_states[image_index].GetView()

    def GetModel(self, image_index=None):
        if image_index is None:
            image_index = self._current_image_index
        if image_index is not None:
            return self._app_states[image_index].GetModel()
        else:
            return None

    def getPlugin(self):
        return self._plugin

    def SetROIType(self, roi_type):
        return self.GetModel().setModelROIType(roi_type)

    def GetROIType(self, image_index=None):
        return self.GetModel(image_index).getModelROIType()

    def GetROIBounds(self, image_index=None):
        return self.GetModel(image_index).getModelROIBounds()

    def GetROIExtent(self, image_index=None):
        return self.GetModel(image_index).getModelROIExtent()

    def GetROIStencil(self, image_index=None):
        return self.GetModel(image_index).getModelROIStencil()

    def GetModelROICenterInPixels(self, image_index=None):
        return self.GetModel(image_index).getModelROICenterInPixels()

    def GetModelROICenterInMillimeters(self, image_index=None):
        return self.GetModel(image_index).getModelROICenterInMillimeters()

    def GetModelROISizeInPixels(self, image_index=None):
        return self.GetModel(image_index).getModelROISizeInPixels()

    def GetModelROISizeInMillimeters(self, image_index=None):
        return self.GetModel(image_index).getModelROISizeInMillimeters()

    def SetModelROICenterInPixels(self, center, image_index=None):
        return self.GetModel(image_index).setModelROICenterInPixels(center)

    def SetModelROICenterInMillimeters(self, center, image_index=None):
        return self.GetModel(image_index).setModelROICenterInMillimeters(center)

################### VTK Related code ##########################

    def configureScales(self):
        """Configure the scale bars for new input or unit change."""

        image = component.getUtility(ICurrentImage)

        origin = image.GetOrigin()
        spacing = image.GetSpacing()
        dims = image.GetDimensions()

        gui = self.GetGUIView()

        size_limits = [
            1, dims[0],
            1, dims[1],
            1, dims[2]
        ]

        center_limits = [
            0, dims[0] - 1,
            0, dims[1] - 1,
            0, dims[2] - 1
        ]

        increments = [1, 1, 1]

        if gui.m_choiceUnits.GetSelection() == 0:  # display is showing mm
            for i in range(3):
                size_limits[i * 2] *= spacing[i]
                size_limits[i * 2 + 1] *= spacing[i]
                increments[i] *= spacing[i]
                center_limits[i * 2] += origin[i]
                center_limits[i * 2 + 1] = origin[i] + dims[i] * spacing[i]

        gui.m_sliderSizeX.SetRange(
            min(size_limits[0], size_limits[1]), max(size_limits[0], size_limits[1]))
        gui.m_sliderSizeY.SetRange(
            min(size_limits[2], size_limits[3]), max(size_limits[2], size_limits[3]))
        gui.m_sliderSizeZ.SetRange(
            min(size_limits[4], size_limits[5]), max(size_limits[4], size_limits[5]))

        gui. m_sliderCenterX.SetRange(
            min(center_limits[0], center_limits[1]), max(center_limits[0], center_limits[1]))
        gui. m_sliderCenterY.SetRange(
            min(center_limits[2], center_limits[3]), max(center_limits[2], center_limits[3]))
        gui. m_sliderCenterZ.SetRange(
            min(center_limits[4], center_limits[5]), max(center_limits[4], center_limits[5]))

    def OnImageChangeEvent(self, evt):
        """This method mimics our standard zope-event handler, but isn't actually called directly by zope

        The reason for this difference is because the Standard ROI tool uses an MVC encapsulation model, whereas
        most other plugins are monolithic.  The standard ROI plugin class receives the OnImageChangeEvent event,
        then passes it to the controller, which then handles everything.
        """

        # enable GUI
        gui = self.GetGUIView()
        gui.Enable(evt.GetNumberOfImagesCurrentlyLoaded() > 0)

        # save current gui state
        if self._current_image_index is not None:
            self.saveCurrentGUIState()

        self._current_image_index = evt.GetCurrentImageIndex()

        # create an ROI state object for this image if one doesn't already
        # exist
        self.initialize_state_object()

        # load current gui state
        self.updateGUIState()

        # update rotation behaviour
        self.updateROIRotationBehaviour()

        # If this is the first ROI, set it to automatically be displayed
        if len(self._app_states) == 1:
            self.DisplayROI()
        else:
            # add plane observer, but only if visual is displayed
            self.add_plane_observer()

    def initialize_state_object(self):
        if self._current_image_index not in self._app_states:
            gui = self.GetGUIView()
            image = component.getUtility(ICurrentImage)
            self._app_states[
                self._current_image_index] = state = StandardROIToolState(image)
            # initialize model and view with current GUI settings
            model = state.GetModel()
            state.tool_type_index = gui.m_choiceTool.GetSelection()
            state.tool_orientation_index = gui.m_choiceOrientation.GetSelection()
            state.tool_units_index = gui.m_choiceUnits.GetSelection()
            self.configureScales()
            model.setModelROIType(
                model.getModelROITypes()[state.tool_type_index])
            model.setModelROIOrientation(
                gui.m_choiceOrientation.GetStringSelection())

            # If model ROI Extent doesn't exist, create a default one
            if self.GetModel().getModelROIExtent() is None:
                self.GetModel().setModelDefaultROI()

            if len(self._app_states) > 1:
                state.view.DisableROI()

    def onPlanesModified(self, obj, evt):
        self.updateROIRotationBehaviour()

    def onPlanesEndAction(self, obj, evt):

        # copy view's transform into model -- we do this at tail end of interaction to avoid
        # regenerating stencils during interactive periods (it's fairly CPU
        # intensive)

        if self.bArbitraryOrientation:
            orthoPlanes = component.getUtility(ICurrentOrthoPlanes)
            t = vtk.vtkTransform()
            t.DeepCopy(orthoPlanes.GetTransform())
            self.GetModel().setTransform(t)

    def updateROIRotationBehaviour(self):
        pass

    def saveCurrentGUIState(self):
        """push app state into an object"""

        state = self.GetCurrentState()
        gui = self.GetGUIView()

        # Disconnect monitoring of the VTK ROI
        if state.observer:
            state.GetView().GetCube().RemoveObserver(state.observer)
            state.observer = None

        state.tool_type_index = gui.m_choiceTool.GetSelection()
        state.tool_orientation_index = gui.m_choiceOrientation.GetSelection()
        state.tool_units_index = gui.m_choiceUnits.GetSelection()
        state.arb_orientation_option = gui.m_checkBoxAllowArbOrientation.GetValue()

    def updateGUIState(self):
        """restore app state from an object"""

        state = self.GetCurrentState()
        image = component.getUtility(ICurrentImage)

        # Let the model and view know about the input image
        state.SetInput(image)

        # wire up VTK view logic
        if state.observer is None:
            state.observer = state.GetView().GetCube().AddObserver(
                'EndAction', self.onStandardROIModifiedEvent)
        else:
            logging.warning("stale observer detected!!")

        gui = self.GetGUIView()
        gui.m_choiceTool.SetSelection(state.tool_type_index)
        gui.m_choiceOrientation.SetSelection(state.tool_orientation_index)
        gui.m_choiceUnits.SetSelection(state.tool_units_index)
        gui.m_checkBoxAllowArbOrientation.SetValue(
            state.arb_orientation_option)

        if state.view.GetROIVisibility():
            label = 'Hide ROI'
        else:
            label = 'Show ROI'
        gui.m_buttonShow.SetLabel(label)
        gui.Layout()

        self.bArbitraryOrientation = state.arb_orientation_option

        # Let the GUI view know about the image
        self.configureScales()

        # now set values for scrollbars, based on model value
        self.onModelModifiedEvent(None)

    @component.adapter(CurrentImageClosingEvent)
    def onCurrentImageClosingEvent(self, evt):
        self.resetGUI()

    @component.adapter(NotebookPageChangingEvent)
    def OnNotebookPageChangingEvent(self, evt):
        self.resetGUI()

    def resetGUI(self):
        # stop listening to existing orthoplane
        self.removeObservers()

    def removeObservers(self):
        """Stop listening to events from a render window"""
        state_obj = self.GetCurrentState()

        # stop listening to plane events
        self.remove_plane_observer()

        # stop listening to our own model
        if state_obj:
            observer = state_obj.observer
            if observer:
                state_obj.GetView().GetCube().RemoveObserver(observer)
                state_obj.observer = None

    @component.adapter(ROIKeyEvent)
    def onROIKeyEvent(self, evt):

        e = evt.GetEvent()
        key = e.char

        # Figure out how to handle control+key events -- looks like we might
        # need to use Alt key instead
        if key == '3':
            self.onSetROICenter(e)
        elif key == '7':
            index = 0
            if e.alt_key or e.ctrl_key:
                self.SetOrthoCenterAsPoint(index, e)
            else:
                self.SetPoint(index, e)
        elif key == '8':
            index = 1
            if e.alt_key or e.ctrl_key:
                self.SetOrthoCenterAsPoint(index, e)
            else:
                self.SetPoint(index, e)

    def EnableROI(self):
        """Show ROI and set proper initial values."""

        self.DisplayROI()

        # Enable the ROI - create one if it doesn't already exist
        model = self.GetModel()
        if model:
            if model.getModelROIExtent() is None:
                model.setModelDefaultROI()

            roi_type = model.getModelROIType()

            self.GetVTKView().ShowROI(roi_type)

            gui = self.GetGUIView()
            gui.m_buttonShow.SetLabel("Hide ROI")

            # update image with stencil from the current model
            self.updateStencilData()

            # whenever this ROI is visible,
            # this class is the active ROI tool
            event.notify(
                ROIEnabledEvent(self._plugin.GetShortName(), self.GetCurrentImageIndex()))

    def DisableAllROIs(self):
        """Disable all ROIs for all loaded images"""
        for image_index in self._app_states:
            self.DisableROI(image_index)

    def DisableROI(self, image_index=None):
        """Disable ROI for specified image: hide actors, clear setting."""

        logging.info("DisableROI() called")

        if image_index is None:
            image_index = self.GetCurrentImageIndex()

        image = component.getUtility(
            IImage, name='Image-%d' % (image_index + 1))

        model = self.GetModel(image_index)
        if model is None:
            return

        view = self.GetVTKView(image_index)
        if view is None:
            return

        gui = self.GetGUIView()
        gui.m_buttonShow.SetLabel("Show ROI")

        model.clearROIControlPoints()
        view.DisableROI()

        # check to see whether we're the current stencil
        if image.GetStencilDataOwner() == "StandardROITool":
            image.SetStencilData(None)

        # stop listening to plane events
        self.remove_plane_observer()

        event.notify(
            ROIDisabledEvent(self._plugin.GetShortName(), image_index))

    def add_plane_observer(self):

        # only add observer if our view is connected to VTK viewport
        view = self.GetVTKView()
        if view.IsConnected() and view.GetROIVisibility():

            # listen to changes to this pane's orthoplanes
            state_obj = self.GetCurrentState()
            observer = state_obj.GetOrthoPlanesObserver()

            if observer is None:
                orthoPlanes = component.getUtility(ICurrentOrthoPlanes)
                state_obj.SetOrthoPlanesObserver(
                    orthoPlanes.AddObserver('ModifiedEvent', self.onPlanesModified))
                state_obj.SetOrthoPlanesObserver(
                    orthoPlanes.AddObserver('EndAction', self.onPlanesEndAction))

    def remove_plane_observer(self):
        state_obj = self.GetCurrentState()
        if state_obj:
            if state_obj.GetOrthoPlanesObserver():
                orthoPlanes = component.getUtility(ICurrentOrthoPlanes)
                orthoPlanes.RemoveObserver(state_obj.GetOrthoPlanesObserver())
                state_obj.SetOrthoPlanesObserver(None)

    def onStandardROIModifiedEvent(self, obj, evt):
        """
        onStandardROIModifiedEvent -    Callback method on EndAction of the ROICubeFactory:
                                        update the widgets to reflect the change of ROI, which
                                        is introduced by actor manipulation.
        """
        bounds = tuple(self.GetVTKView().GetCube().GetROIBounds())
        self.GetModel().setModelROIBounds(bounds)
        self.send_modified_notification(evt)

    def updateStencilData(self):
        """feed model stencil into current image"""
        image = component.getUtility(ICurrentImage)
        stencil_data = self.GetModel().getModelROIStencil()
        image.SetStencilData(stencil_data, owner=self._plugin.GetShortName())

################### Model Event Handlers ##########################
    @component.adapter(ROIModelModifiedEvent)
    def onModelModifiedEvent(self, evt):

        gui = self.GetGUIView()
        model = self.GetModel()
        unit = gui.m_choiceUnits.GetSelection()
        image = component.getUtility(ICurrentImage)
        numC = numC = image.GetNumberOfScalarComponents()
        dataSize = image.GetScalarSize()

        sm = model.getModelROISizeInMillimeters()
        cm = model.getModelROICenterInMillimeters()
        cp = model.getModelROICenterInPixels()
        sp = model.getModelROISizeInPixels()

        # update the GUI View
        if unit == 0:  # mm
            _size, _center, width = sm, cm, 4
            _format1 = '%%0.%df' % width
            _format2 = '%%0.%df' % width
        else:
            _size, _center, width = sp, cp, 1
            _format1 = '%d'
            _format2 = '%%0.%df' % width

        # disable gui updates
        self.bIgnoreGUIEvents = True

        gui.m_textCtrlROISizeX.SetValue(_format1 % abs(_size[0]))
        gui.m_textCtrlROISizeY.SetValue(_format1 % abs(_size[1]))
        gui.m_textCtrlROISizeZ.SetValue(_format1 % abs(_size[2]))
        gui.m_sliderSizeX.SetValue(abs(_size[0]))
        gui.m_sliderSizeY.SetValue(abs(_size[1]))
        gui.m_sliderSizeZ.SetValue(abs(_size[2]))

        gui.m_textCtrlROICenterX.SetValue(_format2 % _center[0])
        gui.m_textCtrlROICenterY.SetValue(_format2 % _center[1])
        gui.m_textCtrlROICenterZ.SetValue(_format2 % _center[2])
        gui.m_sliderCenterX.SetValue(_center[0])
        gui.m_sliderCenterY.SetValue(_center[1])
        gui.m_sliderCenterZ.SetValue(_center[2])

        # enable gui updates
        self.bIgnoreGUIEvents = False

        # update the extent label
        e = model.getModelROIExtent()
        text = "%d, %d, %d, %d, %d, %d" % e
        gui.m_extentLabel.SetLabel(text)

        # update the output file/memory size label
        sz = (e[1] - e[0] + 1) * (e[3] - e[2] + 1) * \
            (e[5] - e[4] + 1) * numC * dataSize

        sz_gb = sz / 1024 / 1024 / 1024.
        if sz < 1e6:
            sz_label = '%d bytes' % sz
        else:
            if sz_gb > 1.0:
                sz_label = '%0.4g GiB' % (sz / 1024 / 1024 / 1024.)
            else:
                sz_label = '%0.4g MiB' % (sz / 1024 / 1024.)

        gui.m_staticTextFileSizeLabel.SetLabel(sz_label)

        # update the VTK View
        self.GetVTKView().setViewROIBounds(model.getModelROIBounds())

        self.send_modified_notification(evt)

    def send_modified_notification(self, evt):

        # update image with stencil from the current model
        if evt:
            self.updateStencilData()

        # notify everyone external that ROI has changed
        if evt:
            event.notify(
                ROIModifiedEvent(self._plugin.GetShortName(), self.GetCurrentImageIndex()))

    @component.adapter(ROIModelLinkingChangeEvent)
    def onModelLinkingChangeEvent(self, evt):
        self.GetGUIView().m_toggleBtnSizeLinking.SetValue(
            self.GetModel().getModelROILinking())

    @component.adapter(ROIModelTypeChangeEvent)
    def onROITypeChangeEvent(self, evt):

        self.GetVTKView().ShowROI(self.GetModel().getModelROIType())
        self.send_modified_notification(evt)
        self.GetVTKView().GetCube().Render()
        self.GetVTKView().GetSphere().Render()
        self.GetVTKView().GetCylinder().Render()

    @component.adapter(ROIModelOrientationChangeEvent)
    def onROIOrientationChangeEvent(self, evt):

        orientation = self.GetModel().getModelROIOrientation()

        if orientation == 'X':
            self.GetVTKView().GetCylinder().SetOrientationToX()
        elif orientation == 'Y':
            self.GetVTKView().GetCylinder().SetOrientationToY()
        elif orientation == 'Z':
            self.GetVTKView().GetCylinder().SetOrientationToZ()
        else:
            logging.error('onROIOrientationChangeEvent: wrong orientation!!')

        self.GetVTKView().GetCylinder()._Update()
        self.GetVTKView().GetCylinder().Render()

        self.send_modified_notification(evt)

    @component.adapter(ROIModelControlPointChangeEvent)
    def onROIControlPointsChanged(self, evt):
        """
        Handle event from the Model indicating that ROI control points
        have changed.
        """

        # if both control points are set, make sure ROI is enabled
        points = self.GetModel().getModelROIControlPoints()
        p1, p2 = points

        self.GetVTKView().setViewROIControlPoints(points)

        self.DisplayROI()

        if (p1 is not None) and (p2 is not None):
            self.EnableROI()
            self.send_modified_notification(evt)

    def DisplayROI(self):

        # check to see if the view has been realized
        if not self.GetVTKView().IsConnected():
            panes = component.getUtility(IOrthoView, name='OrthoView-%d' % (
                self._current_image_index + 1)).GetRenderPanes()
            for pane in panes:
                self.GetVTKView().Connect3DActorFactories(pane)

        # this code makes sure toggling visibility adds/removes plane observer
        self.add_plane_observer()

    def RenderAll(self):
        for pane in self.GetRenderPanes():
            pane.Render()

    def GetRenderPanes(self):
        panes = component.getUtility(IOrthoView, name='OrthoView-%d' % (
            self._current_image_index + 1)).GetRenderPanes()
        return panes


################### View Event Handlers ##########################

    def ToggleHeightWidthLinking(self, evt):

        # update Model
        self.GetModel().setModelROILinking(evt.GetSelection() == 1)

    def onSetCenter(self, index, evt):
        """Call back for ROI centre scalebar manipulation"""

        if self.bIgnoreGUIEvents:
            return

        gui = self.GetGUIView()

        center = (
            gui.m_sliderCenterX.GetValue(),
            gui.m_sliderCenterY.GetValue(),
            gui.m_sliderCenterZ.GetValue(),
        )

        gui.m_staticTextErrorMessage2.SetLabel("")

        if gui.m_choiceUnits.GetSelection() == 0:
            self.GetModel().setModelROICenterInMillimeters(center)
        else:
            self.GetModel().setModelROICenterInPixels(center)

    def onSetSize(self, index, evt):
        """Call back function for the size scale bars."""

        if self.bIgnoreGUIEvents:
            return

        gui = self.GetGUIView()

        # compute the ROI size, as determined by scale values
        sizes = (
            gui.m_sliderSizeX.GetValue(),
            gui.m_sliderSizeY.GetValue(),
            gui.m_sliderSizeZ.GetValue(),
        )

        gui.m_staticTextErrorMessage1.SetLabel("")

        if gui.m_choiceUnits.GetSelection() == 0:
            self.GetModel().setModelROISizeInMillimeters(sizes)
        else:
            self.GetModel().setModelROISizeInPixels(sizes)

    def onToolChange(self, evt):
        """Switch between cube, cylinder and sphere."""
        m = self.GetModel()
        m.setModelROIType(m.getModelROITypes()[evt.GetSelection()])

    def onToolOrientationChange(self, evt):
        """Switch orientation of cylinder."""

        m = self.GetModel()
        self.GetModel().setModelROIOrientation({
                                               0: 'X', 1: 'Y', 2: 'Z'}[evt.GetSelection()])

    def onUnitChange(self, evt):
        """
        OnUnitChange -  Reconfigure the scale bars and change the
                        entry fields values to reflect the proper unit.
        """
        self.configureScales()
        self.onModelModifiedEvent(None)

    def onSelectWholeImage(self, evt):
        """Callback function of Select Whole Image button."""

        # disable dimension linking (otherwise we fail for non-square images)
        self.GetModel().setModelROILinkingOff()

        # tell the model to expand it's extent
        self.GetModel().setModelROIExtent(self.GetModel().getImageExtent())

    def onCenterROI(self, evt):

        position = self.getPlugin().GetMicroView().GetOrthoCenter()
        m = component.getUtility(
            ICurrentOrthoPlanes).GetTransform().GetMatrix()
        position = m.MultiplyPoint((position[0], position[1], position[2], 1))
        self.GetModel().setModelROICenterInMillimeters(position)
        self.GetModel().checkExtentPreserveCenter()

    def onButtonROIShow(self, evt):

        # make sure actors are added

        is_visible = self.GetVTKView().GetROIVisibility()
        if is_visible:
            self.DisableROI()
        else:
            self.EnableROI()

        self.RenderAll()

    def onArbOrientationCheckbox(self, evt):

        pass

    def onSizeChar(self, index, evt):
        """Callback for each character pressed in size controls"""

        evt.Skip()
        sizes = self.validateSizeControls()

    def onCenterChar(self, index, evt):
        """Callback for each character pressed in center controls"""

        evt.Skip()
        centers = self.validateCenterControls()

    def onSizeEntry(self, index, evt):
        """Callback function for entry fields for ROI Sizes."""

        # this is important - onSizeEntry is also called when focus is lost
        evt.Skip()

        if self.bIgnoreGUIEvents:
            return

        sizes = self.validateSizeControls()

        if sizes:
            # compute the ROI size, as determined by entrybox values
            if sizes != self._oldSizeEntries:
                self._oldSizeEntries = sizes
                gui = self.GetGUIView()
                if gui.m_choiceUnits.GetSelection() == 0:
                    self.GetModel().setModelROISizeInMillimeters(sizes)
                else:
                    self.GetModel().setModelROISizeInPixels(sizes)
                self.GetModel().checkExtentPreserveSize()

    def onCenterEntry(self, index, evt):
        """Callback function of entry fields for ROI Center."""

        # this is important - onCenterEntry is also called when focus is lost
        evt.Skip()

        if self.bIgnoreGUIEvents:
            return

        center = self.validateCenterControls()

        if center:
            if center != self._oldCenterEntries:
                self._oldCenterEntries = center
                gui = self.GetGUIView()
                if gui.m_choiceUnits.GetSelection() == 0:
                    self.GetModel().setModelROICenterInMillimeters(center)
                else:
                    self.GetModel().setModelROICenterInPixels(center)
                self.GetModel().checkExtentPreserveCenter()

    def validateSizeControls(self):

        gui = self.GetGUIView()
        error_message = ""
        bValid = True
        sizes = None

        # are entries all valid floats?
        try:
            sizes = (
                float(gui.m_textCtrlROISizeX.GetValue()),
                float(gui.m_textCtrlROISizeY.GetValue()),
                float(gui.m_textCtrlROISizeZ.GetValue()))
        except:
            bValid = False
            error_message = "Invalid Entry: bad ROI size value"

        # are entries within bounds?
        if bValid:

            image = component.getUtility(ICurrentImage)
            spacing = image.GetSpacing()
            dims = image.GetDimensions()

            # convert text values to pixels
            bMeasurePixels = gui.m_choiceUnits.GetSelection() == 1
            if bMeasurePixels:
                sizes_in_pixels = sizes
            else:
                sizes_in_pixels = (
                    sizes[0] * spacing[0], sizes[1] * spacing[1], sizes[2] * spacing[2])

            for i in range(3):
                if sizes_in_pixels[i] < 1:
                    bValid = False
                    error_message = "Invalid Entry: dimension must be >= 1"
                    break
                if sizes_in_pixels[i] > dims[i]:
                    bValid = False
                    error_message = "Invalid Entry: ROI dimension to large"
                    break

        gui.m_staticTextErrorMessage1.SetLabel(error_message)

        return sizes

    def validateCenterControls(self):

        gui = self.GetGUIView()

        bValid = True
        centers = None

        # are entries all valid floats?
        try:
            centers = (
                float(gui.m_textCtrlROICenterX.GetValue()),
                float(gui.m_textCtrlROICenterY.GetValue()),
                float(gui.m_textCtrlROICenterZ.GetValue()))
        except:
            bValid = False

        # are entries within bounds?
        if bValid:

            image = component.getUtility(ICurrentImage)
            spacing = image.GetSpacing()
            dims = image.GetDimensions()
            origins = image.GetOrigin()

            # convert text values to pixels
            bMeasurePixels = gui.m_choiceUnits.GetSelection() == 0
            if bMeasurePixels:
                centers_in_pixels = centers
            else:
                centers_in_pixels = (
                    (centers[0] - origins[0]) / spacing[0],
                    (centers[1] - origins[1]) / spacing[1],
                    (centers[2] - origins[2]) / spacing[2],
                )

            for i in range(3):
                if centers_in_pixels[i] < 0.5:
                    bValid = False
                    break
                if centers_in_pixels[i] >= dims[i]:
                    bValid = False
                    break

        if bValid:
            gui.m_staticTextErrorMessage2.SetLabel("")
        else:
            gui.m_staticTextErrorMessage2.SetLabel("Invalid Entry")

        return centers

    def _GetCursorPosition(self, evt):
        evt.pane.DoPickActor(evt)
        infoList = evt.pane._PickInformationList
        if not infoList:
            return None

        # we are only interest in SlicePlaneFactory
        for info in infoList:
            if info.factory.IsA('OrthoPlanesFactory') or \
                    info.factory.IsA('SlicePlaneFactory'):
                return info.position

        return None

    def SetPoint(self, index, evt):
        """Callback of key-press-7 and key-press-8 events.
        This is an alternative method to set the ROI: set two
        diagonal corners of a cube.
        """

        position = self._GetCursorPosition(evt)
        if position is None:
            return

        # update Model
        self.GetModel().setModelROIControlPoint(index, position)

    def SetPoints(self, point1, point2):
        self.GetModel().setModelROIControlPoint(0, point1)
        self.GetModel().setModelROIControlPoint(1, point2)

    def SetOrthoCenterAsPoint(self, index, evt):
        """Callback function of control-keypress-7"""
        if evt.pane.GetOrthoPlanes().IsA('OrthoPlanesFactory'):
            position = evt.pane.GetOrthoPlanes().GetOrthoCenter()

        # update Model
        self.GetModel().setModelROIControlPoint(index, position)

    def onSetROICenter(self, evt):
        """Set ROI Center to the present mouse location."""

        position = self._GetCursorPosition(evt)
        if position is None:
            return

        self.GetModel().setModelROICenterInMillimeters(position)
        self.GetModel().checkExtentPreserveCenter()
