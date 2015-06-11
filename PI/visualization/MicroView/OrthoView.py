# =========================================================================
#
# Copyright (c) 2000-2008 GE Healthcare
# Copyright (c) 2011-2015 Parallax Innovations Inc.
#
# Use, modification and redistribution of the software, in source or
# binary forms, are permitted provided that the following terms and
# conditions are met:
#
# 1) Redistribution of the source code, in verbatim or modified
#   form, must retain the above copyright notice, this license,
#   the following disclaimer, and any notices that refer to this
#   license and/or the following disclaimer.
#
# 2) Redistribution in binary form must include the above copyright
#    notice, a copy of this license and the following disclaimer
#   in the documentation or with other materials provided with the
#   distribution.
#
# 3) Modified copies of the source code must be clearly marked as such,
#   and must not be misrepresented as verbatim copies of the source code.
#
# EXCEPT WHEN OTHERWISE STATED IN WRITING BY THE COPYRIGHT HOLDERS AND/OR
# OTHER PARTIES, THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE
# SOFTWARE "AS IS" WITHOUT EXPRESSED OR IMPLIED WARRANTY INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE.  IN NO EVENT UNLESS AGREED TO IN WRITING WILL
# ANY COPYRIGHT HOLDER OR OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
# THE SOFTWARE UNDER THE TERMS OF THIS LICENSE BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, LOSS OF DATA OR DATA BECOMING INACCURATE OR LOSS OF PROFIT OR
# BUSINESS INTERRUPTION) ARISING IN ANY WAY OUT OF THE USE OR INABILITY TO
# USE THE SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
#
# =========================================================================

#
# This file represents a derivative work by Parallax Innovations Inc.
#

"""
OrthoView creates a vtk Visualization pipeline with 4 RenderPanes (one 3D pane and
3 orthogonal 2D panes) and a few actors (OrthoPlanes, Annotations, etc).
"""

from zope import interface, component, event

import vtk
import vtk.util.colors as vtkcolors
from vtk.util.numpy_support import vtk_to_numpy
import logging
import wx
from vtkEVS import EVSOrthoPlanesFactory, AnnotateFactory, \
    EVSOutlineFactory, \
    EVSAnatomicalLabelsFactory, EVSRenderPane2D

from PI.visualization.common import MicroViewObjectShelve, MicroViewSettings
from PI.visualization.common.CoordinateSystem import CoordinateSystem
from PI.visualization.common.events import MicroViewSettingsModifiedEvent
from PI.visualization.MicroView.interfaces import IMicroViewOutput, IOrthoView, IImage
from PI.visualization.MicroView.events import ViewportModifiedEvent, WindowLevelTextChangeEvent, \
    ScalesVisibilityChangeEvent, ColourBarVisibilityChangeEvent, ViewportModified2Event, XSliceValueChangeEvent, \
    YSliceValueChangeEvent, ZSliceValueChangeEvent, \
    ActionEvent, BackgroundColourChangeEvent, SetWindowLevelCommand, \
    WindowLevelPresetEvent, TrackedSliceIndexChangeEvent, SynchronizeEvent

import numpy as np

import LineSegmentSelectionFactory
import MicroViewRenderPane
import WindowLevelDialogGUIC
import BackgroundColourSelectorDialogC
import cProfile


red1 = (1.0, 0.0, 0.0)
green1 = (0.0, 1.0, 0.0)
blue1 = (0.0, 0.0, 1.0)
blue2 = (0.1843, 0.2392, 0.4314)


class OrthoView(object):

    interface.implements(IOrthoView)

    def __init__(self, paneframe, index=0):

        self._index = index
        self.ignore_events = False
        self.wl_dlg = None
        self.__lut_index = 0
        self.profile = cProfile.Profile()
        self.profiler_state = 0
        self.__last_xslice_number = None
        self.__last_yslice_number = None
        self.__last_zslice_number = None

        self._synced_observers = {}

        # listen to certain zope events
        component.provideHandler(self.OnConfigModified)
        component.provideHandler(self.onViewportModifiedEvent)
        component.provideHandler(self.onViewportModified2Event)
        component.provideHandler(self.onScalesVisibilityChangeEvent)
        component.provideHandler(self.onColourBarVisibilityChangeEvent)
        component.provideHandler(self.onBackgroundColourChangeEvent)
        component.provideHandler(self.onSetWindowLevelCommandEvent)
        component.provideHandler(self.onSynchronizeEvent)

        self.z_axis_dimension_name = 'Distance'

        # These next variables should be removed - we're putting them here to allow
        # Optina's plugin to work (it has irregularly spaced z-slices)
        self._x_values = None
        self._y_values = None
        self._z_values = None

        self._current_slice_annotation = 2

        # Actors
        self.__orthoPlanes = EVSOrthoPlanesFactory.EVSOrthoPlanesFactory()
        self.GetOrthoPlanes().SetOutlineOpacity(1.0)

        # Listen for modification events on the sliceplane objects
        self.GetOrthoPlanes().GetAxialPlane().AddObserver(
            'ModifiedEvent', self.onAxialPlaneModified)

        self.GetOrthoPlanes().GetSagittalPlane().AddObserver(
            'ModifiedEvent', self.onSagittalPlaneModified)

        self.GetOrthoPlanes().GetCoronalPlane().AddObserver(
            'ModifiedEvent', self.onCoronalPlaneModified)

        self.volumeOutline = EVSOutlineFactory.EVSOutlineFactory()
        self.volumeOutline.SetColor(vtkcolors.goldenrod_dark)
        self.volumeOutline.SetOpacity(1.0)

        self.axesLabels = EVSAnatomicalLabelsFactory.EVSAnatomicalLabelsFactory(
        )
        self.axesLabels.SetPositiveColor((0, 1, 0))
        self.axesLabels.SetNegativeColor((1, 0, 0))

        self.bLineAdded = False

        self.lineSegment = LineSegmentSelectionFactory.LineSegmentSelectionFactory(
        )
        self.lineSegment.AddObserver(
            'ModifiedEvent', self.OnLineSegmentModified)

        self.lineSegmentAnnotate = AnnotateFactory.AnnotateFactory()
        self.lineSegmentAnnotate.SetPosition('NW')

        self.sliceNumberAnnotate = AnnotateFactory.AnnotateFactory()
        self.sliceNumberAnnotate.SetPosition('SE')
        self.sliceNumberAnnotate.SetText('Z-Slice:')

        #
        # Render panes
        #
        self.renderPanes = []

        # 3D render pane
        pane3D = MicroViewRenderPane.MicroViewRenderPane(
            paneframe, index=self._index, name='pane3D')
        state = self.getBackgroundColour()

        pane3D.GetRenderer().SetGradientBackground(state.GetGradientState())
        bg = state.GetTopColour()
        pane3D.GetRenderer().SetBackground2(
            bg[0] / 255., bg[1] / 255., bg[2] / 255.)
        if state.GetGradientState():
            bg = state.GetBottomColour()
        pane3D.GetRenderer().SetBackground(
            bg[0] / 255., bg[1] / 255., bg[2] / 255.)

        pane3D.SetBorderWidth(2)
        pane3D.SetBorderColor(blue2)
        pane3D.ConnectOrthoPlanes(self.__orthoPlanes)
        pane3D.ConnectActorFactory(self.volumeOutline)
        pane3D.ConnectActorFactory(self.axesLabels)

        self.GetOrthoPlanes().GetIntersections().SetEndVisibility(
            0, pane3D.GetRenderer())
        self.GetOrthoPlanes().GetIntersections().SetLineVisibility(
            1, pane3D.GetRenderer())
        self.renderPanes.append(pane3D)

        # Add a orientation actor
        self.orientationActor = vtk.vtkAxesActor()
        self.orientationWidget = vtk.vtkOrientationMarkerWidget()
        self.orientationWidget.KeyPressActivationOff()
        self.orientationWidget.SetOutlineColor(1, 1, 0)
        self.orientationWidget.SetOrientationMarker(self.orientationActor)

        self.orientationWidget.SetDefaultRenderer(
            self.renderPanes[0].GetRenderer())
        self.orientationWidget.SetInteractor(self.renderPanes[
                                             0].GetRenderer().GetRenderWindow().GetInteractor())

        self.bIs3DView = True

        bshouldDisplayWidget = self.bIs3DView and MicroViewSettings.MicroViewSettings.getObject(
        ).bShowImageOrientation
        self.enableOrientationWidget(bshouldDisplayWidget)

        # Colour-bar actor
        self.colourbarActor = None
        self.colourbar_visibility = False
        self.scales_visibility = False

        # 2D panes
        # cuiColor.NormalizedOn()
        for plane, color, idx in (
            (self.GetOrthoPlanes().GetAxialPlane(), blue1, 1),
            (self.GetOrthoPlanes().GetCoronalPlane(), green1, 2),
                (self.GetOrthoPlanes().GetSagittalPlane(), red1, 3)):
            pane = EVSRenderPane2D.EVSRenderPane2D(
                paneframe, index=self._index, name='pane2d_%d' % idx)
            pane.SetBorderColor(color)
            pane.ConnectPlane(plane)
            pane.ConnectActorFactory(self.GetOrthoPlanes().GetIntersections())
            pane.SetOrthoPlanes(self.__orthoPlanes)
            pane.SetTrackedSlicePlaneIndex(3 - idx)
            self.renderPanes.append(pane)

            # Add a legend scale actor
            pane.scaleActor = vtk.vtkLegendScaleActor()
            pane.scaleActor.SetLegendVisibility(0)

            # Make scales green
            #pane.scaleActor.GetTopAxis().GetProperty().SetColor(0, 1, 0)
            pane.scaleActor.GetRightAxis().GetProperty().SetColor(0, 1, 0)
            # pane.scaleActor.SetTopBorderOffset(40)
            pane.scaleActor.SetRightBorderOffset(40)
            pane.scaleActor.AllAxesOff()
            pane.GetRenderer().AddActor(pane.scaleActor)

        # Create the default lookup table for this image viewer
        self._minmax = False

        # Keypress bindings for options
        paneframe.BindEvent("<KeyPress-z>", lambda evt: self.ToggleOption(
            evt, 'bUseSpacing'))
        paneframe.BindEvent("<KeyPress-f>", lambda evt: self.ToggleOption(
            evt, 'bShowPlaneBorders'))
        paneframe.BindEvent(
            "<KeyPress-e>", lambda evt: self.ToggleOption(evt, 'bShowAxes'))

        pane3D.BindEvent("<KeyPress-i>", lambda evt: self.ToggleOption(
            evt, 'bShowSagittalPlane'))
        pane3D.BindEvent("<KeyPress-j>", lambda evt: self.ToggleOption(
            evt, 'bShowCoronalPlane'))
        pane3D.BindEvent("<KeyPress-k>", lambda evt: self.ToggleOption(
            evt, 'bShowAxialPlane'))
        pane3D.BindEvent("<KeyPress-l>", lambda evt: self.onKeyPressL())
        pane3D.BindEvent("<KeyPress-o>", lambda evt: self.ToggleOption(
            evt, 'bShowAnatomicalLabels'))

        # hook up some events and observers
        for pane in self.renderPanes:
            ##             pane.AddObserver('UserEvent', self.OnRenderPane2DUserEvent)
            ##             pane.BindEvent("<Control-ButtonPress-1>", lambda e: None)
            ##             pane.BindEvent("<Control-B1-Motion>", lambda e: None)
            ##             pane.BindEvent("<Control-ButtonRelease-1>", self.SetOrthoCenter)
            pane.BindEvent(
                "<KeyPress-1>", lambda evt: self.SetLineSegmentMark(evt, 0))
            pane.BindEvent(
                "<KeyPress-2>", lambda evt: self.SetLineSegmentMark(evt, 1))
            pane.BindEvent("<KeyPress-r>", self.ResetView)
            pane.BindEvent("<KeyPress-space>", self.onActionKeyPress)
            pane.BindEvent("<KeyPress-P>", self.onProfileEvent)

        for pane in self.renderPanes[1:]:
            pane.BindEvent("<KeyPress-t>", self.SavePlaneAsImage)

    def tearDown(self):

        # remove zope events
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.OnConfigModified)
        gsm.unregisterHandler(self.onViewportModifiedEvent)
        gsm.unregisterHandler(self.onViewportModified2Event)
        gsm.unregisterHandler(self.onScalesVisibilityChangeEvent)
        gsm.unregisterHandler(self.onColourBarVisibilityChangeEvent)
        gsm.unregisterHandler(self.onBackgroundColourChangeEvent)
        gsm.unregisterHandler(self.onSetWindowLevelCommandEvent)
        gsm.unregisterHandler(self.onSynchronizeEvent)

        self.renderPanes[0].DisconnectActorFactory(self.volumeOutline)
        self.renderPanes[0].DisconnectActorFactory(self.axesLabels)
        self.renderPanes[0].DisconnectActorFactory(self.lineSegment)
        self.renderPanes[0].DisconnectActorFactory(self.lineSegmentAnnotate)
        self.renderPanes[0].DisconnectActorFactory(self.sliceNumberAnnotate)
        self.renderPanes[0].GetRenderer().RemoveActor(self.colourbarActor)

        for i in range(3):
            self.renderPanes[i + 1].DisconnectActorFactory(self.lineSegment)
            self.renderPanes[i + 1].DisconnectActorFactory(
                self.GetOrthoPlanes().GetIntersections())
            try:
                self.renderPanes[i + 1].DisconnectActorFactory(
                    self.lineSegmentAnnotate)
            except:
                pass
            try:
                self.renderPanes[i + 1].DisconnectActorFactory(
                    self.sliceNumberAnnotate)
            except:
                pass

        for pane in self.renderPanes:
            pane.tearDown()
            pane.RemoveAllEventHandlers()

        self.GetOrthoPlanes().GetAxialPlane().RemoveAllEventHandlers()
        self.GetOrthoPlanes().GetAxialPlane().RemoveAllObservers()
        self.GetOrthoPlanes().tearDown()

        self.lineSegment.tearDown()

        self.GetLookupTable().RemoveAllObservers()

        self.volumeOutline.RemoveAllEventHandlers()
        self.sliceNumberAnnotate.RemoveAllEventHandlers()
        self.lineSegmentAnnotate.RemoveAllEventHandlers()
        self.axesLabels.RemoveAllEventHandlers()

        del(self.renderPanes)
        del(self.__orthoPlanes)
        del(self.lineSegment)
        del(self.volumeOutline)
        del(self.sliceNumberAnnotate)
        del(self.lineSegmentAnnotate)
        del(self.orientationActor)
        del(self.orientationWidget)
        del(self.axesLabels)
        del(self.colourbarActor)

    def enableOrientationWidget(self, bIsVisible=True):

        if not bIsVisible:
            self.disableOrientationWidget()
        else:

            vp = self.GetRenderPanes()[0].GetViewport()
            w = vp[3] - vp[1]

            self.orientationWidget.SetViewport(
                vp[0], vp[1], vp[0] + w * 0.2, vp[1] + w * 0.2)
            self.orientationWidget.EnabledOn()
            self.orientationWidget.InteractiveOff()

    def disableOrientationWidget(self):
        self.orientationWidget.EnabledOff()
        # self.orientationWidget.InteractiveOff()

    def GetImageIndex(self):
        return self._index

    def onLookupTableModified(self, obj, evt):

        _min, _max = obj.GetTableRange()
        w = _max - _min
        l = (_max + _min) / 2.0

        if self._minmax:
            text = "Min/Max: %0.2f/%0.2f" % (_min, _max)
        else:
            text = "Window/Level: %0.2f/%0.2f" % (w, l)

        # determine W/L text, and forward this to GUI
        event.notify(WindowLevelTextChangeEvent(text))

    def onSagittalPlaneModified(self, obj, evt):

        if self._current_slice_annotation != 0:
            return

        # X axis
        x_slice_number = int(round(
            self.GetOrthoPlanes().GetSagittalPlane().GetSliceIndex()))
        x_slice_position = self.GetOrthoPlanes(
        ).GetSagittalPlane().GetSlicePosition()
        value = '%d' % x_slice_number

        # Called when the axial slice is modified
        self.sliceNumberAnnotate.SetText('X-Slice: %s' % value)

        # post an event indicating that current x-slice has changed
        event.notify(XSliceValueChangeEvent(x_slice_number, x_slice_position))

    def onCoronalPlaneModified(self, obj, evt):

        if self._current_slice_annotation != 1:
            return

        y_slice_number = int(round(
            self.GetOrthoPlanes().GetCoronalPlane().GetSliceIndex()))
        y_slice_position = self.GetOrthoPlanes(
        ).GetCoronalPlane().GetSlicePosition()
        value = '%d' % y_slice_number

        # Called when the axial slice is modified
        self.sliceNumberAnnotate.SetText('Y-Slice: %s' % value)

        # post an event indicating that current y-slice has changed
        event.notify(YSliceValueChangeEvent(y_slice_number, y_slice_position))

    def onAxialPlaneModified(self, obj, evt):

        if self._current_slice_annotation != 2:
            return

        name = self.z_axis_dimension_name
        z_slice_number = int(round(
            self.GetOrthoPlanes().GetAxialPlane().GetSliceIndex()))
        z_slice_position = self.GetOrthoPlanes(
        ).GetAxialPlane().GetSlicePosition()

        if name == 'Distance':
            # this is a standard z-slice
            label = 'Z-Slice'
            try:
                value = '%d' % z_slice_number
            except:
                # we sometimes get called before the input has been set
                value = ''
        elif name == 'Wavelength':
            label = 'Wavelength (nm)'
            # kludge - account for wavelength data being not regularly spaced
            # for Optina data
            try:
                value = '%0.3f' % self._z_values[z_slice_number]
            except:
                value = 'error'
        elif name == 'Time':
            label = 'Time (ms)'
            value = '%0.2f' % z_slice_position
        else:
            label = name
            value = '%0.2f' % z_slice_position

        # Called when the axial slice is modified
        self.sliceNumberAnnotate.SetText('%s: %s' % (label, value))

        # post an event indicating that current z-slice has changed
        if z_slice_number != self.__last_zslice_number:
            self.__last_zslice_number = z_slice_number
            event.notify(
                ZSliceValueChangeEvent(z_slice_number, z_slice_position))

    def GetObjectState(self):
        """Serialize - returns a serializable representation of this class"""
        class OrthoViewData(object):
            pass
        obj = OrthoViewData()

        # grab orthoview settings
        obj.orthoPlanes = self.GetOrthoPlanes().GetObjectState()

        return obj

    def GetOrthoPlanes(self):

        return self.__orthoPlanes

    def SetLookupTable(self, table):

        old_table = self.GetLookupTable()
        if old_table:
            old_table.RemoveAllObservers()
        self.GetOrthoPlanes().SetLookupTable(table)
        if self.colourbarActor:
            self.colourbarActor.SetLookupTable(table)
        table.AddObserver('ModifiedEvent', self.onLookupTableModified)

    def GetLookupTable(self):

        return self.GetOrthoPlanes().GetLookupTable()

    def SetLUTIndex(self, lut_index):
        """keep track of current image lookup table by an index number"""
        self.__lut_index = lut_index
        if self.wl_dlg:
            self.wl_dlg.getHistogramControl().SetLutIndex(lut_index)

    def _initializeConfig(self):
        """Initialize user options for OrthoView."""

        ApplicationSettings = MicroViewSettings.MicroViewSettings.getObject()

        # always reset these values
        ApplicationSettings.bShowAxialPlane = True
        ApplicationSettings.bShowCoronalPlane = True
        ApplicationSettings.bShowSagittalPlane = True

        # notify everyone
        event.notify(MicroViewSettingsModifiedEvent(ApplicationSettings))

    @component.adapter(ScalesVisibilityChangeEvent)
    def onScalesVisibilityChangeEvent(self, evt):
        self.scales_visibility = bool(evt.GetVisibility())
        for pane in self.renderPanes[1:]:
            pane.scaleActor.SetRightAxisVisibility(int(evt.GetVisibility()))

    def GetScalebarVisibility(self):
        return self.scales_visibility

    @component.adapter(ColourBarVisibilityChangeEvent)
    def onColourBarVisibilityChangeEvent(self, evt):

        pane = self.renderPanes[0]
        if evt.GetVisibility():
            # create actor if needed
            if self.colourbarActor is None:
                self.colourbarActor = vtk.vtkScalarBarActor()
                self.colourbarActor.SetOrientationToVertical()
                self.colourbarActor.SetNumberOfLabels(5)
                self.colourbarActor.SetLookupTable(self.GetLookupTable())
                self.colourbarActor.SetWidth(0.1)
            # add actor
            pane.GetRenderer().AddActor(self.colourbarActor)
            self.colourbar_visibility = True
        else:
            # remove actor
            pane.GetRenderer().RemoveActor(self.colourbarActor)
            self.colourbar_visibility = False

        pane.Modified()
        pane.Render()

    def GetColourbarVisibility(self):
        return self.colourbar_visibility

    @component.adapter(MicroViewSettingsModifiedEvent)
    def OnConfigModified(self, evt):

        try:
            self.axesLabels.SetVisibility(
                int(evt.GetConfig().bShowAnatomicalLabels))
        except AttributeError, evt:
            logging.error(
                "Please re-install zope.interface from the forked repository")

        self.GetOrthoPlanes().SetTextureInterpolate(
            int(evt.GetConfig().bInterpolateTextures))
        self.GetOrthoPlanes().TogglePlanesOutline(
            int(evt.GetConfig().bShowPlaneBorders))
        self.GetOrthoPlanes().GetIntersections().SetLineVisibility(
            int(evt.GetConfig().bShowAxes))
        self.volumeOutline.SetVisibility(
            int(evt.GetConfig().bShowVolumeOutline))

        self.GetOrthoPlanes().ToggleSagittalPlane(self.renderPanes[
            0].GetRenderer(), int(evt.GetConfig().bShowSagittalPlane))
        self.GetOrthoPlanes().ToggleCoronalPlane(self.renderPanes[
            0].GetRenderer(), int(evt.GetConfig().bShowCoronalPlane))
        self.GetOrthoPlanes().ToggleAxialPlane(self.renderPanes[
            0].GetRenderer(), int(evt.GetConfig().bShowAxialPlane))
        self.SetMeasurementUnit(evt.GetConfig().GetUnitLabel())

        # The orientation widget should only be active over top of a 3D pane
        bshouldDisplayWidget = self.bIs3DView and evt.GetConfig(
        ).bShowImageOrientation
        self.enableOrientationWidget(bshouldDisplayWidget)

        self._minmax = evt.GetConfig().bUseMinMaxForWindowLevel
        self.renderPanes[0].Render()

    def ToggleOption(self, e, option):

        ApplicationSettings = MicroViewSettings.MicroViewSettings.getObject()
        val = ApplicationSettings.__dict__[option]
        ApplicationSettings.__dict__[option] = not val

        # notify everyone
        event.notify(MicroViewSettingsModifiedEvent(ApplicationSettings))

    def getBackgroundColour(self):

        root = MicroViewObjectShelve.MicroViewObjectShelve.getObject(
        ).getRoot()

        if 'options.pane3D.background' not in root or not isinstance(root['options.pane3D.background'], BackgroundColourSelectorDialogC.ColourState):
            root[
                'options.pane3D.background'] = BackgroundColourSelectorDialogC.ColourState()
            root.sync()

        return root['options.pane3D.background']

    def setBackgroundColour(self, colour):

        root = MicroViewObjectShelve.MicroViewObjectShelve.getObject(
        ).getRoot()
        root['options.pane3D.background'] = colour
        root.sync()

    def onKeyPressL(self, force=False):
        """
        New-style handler for pressing l key -- this used to simply toggle background colour, now it's a little more
        complicated
        """

        # grab shelf configuration object, see if there's any colour info in
        # there
        state = self.getBackgroundColour()

        newstyle_keybinding = state.GetKeybindingState()
        if force:
            newstyle_keybinding = force

        if not newstyle_keybinding:

            # toggle between black and grey - old style behaviour
            retval = wx.ID_OK
            gradient_on = False
            new_state = state.copy()
            top = new_state.GetTopColour()

            if top != (0, 0, 0) and top != (90, 90, 90):
                top = (0, 0, 0)

            if top == (0, 0, 0):
                top = (90, 90, 90)
            else:
                top = (0, 0, 0)
            bottom = top

            new_state.top_colour = top
            new_state.bottom_colour = bottom
            new_state.bGradientOn = gradient_on

        else:

            dlg = BackgroundColourSelectorDialogC.BackgroundColourSelectorDialogC(
                None, state=state)
            retval = dlg.ShowModal()

            if retval == wx.ID_OK:
                new_state = dlg.GetState()

            dlg.Destroy()

        if retval == wx.ID_OK:

            gradient_on = new_state.GetGradientState()

            if not gradient_on:
                new_state.SetBottomColour(new_state.GetTopColour())

            # remember state
            state.set(new_state)
            self.setBackgroundColour(state)

            event.notify(BackgroundColourChangeEvent())

    @component.adapter(BackgroundColourChangeEvent)
    def onBackgroundColourChangeEvent(self, evt):

        state = self.getBackgroundColour()

        top = state.GetTopColour()
        bottom = state.GetBottomColour()
        gradient_on = state.GetGradientState()

        # set background colours
        if gradient_on:
            self.renderPanes[0].GetRenderer().GradientBackgroundOn()
        else:
            self.renderPanes[0].GetRenderer().GradientBackgroundOff()
        self.renderPanes[0].GetRenderer().SetBackground2(
            top[0] / 255., top[1] / 255., top[2] / 255.)
        self.renderPanes[0].GetRenderer().SetBackground(
            bottom[0] / 255., bottom[1] / 255., bottom[2] / 255.)

        # flag renderer as modified, otherwise colour change doesn't take
        # effect immediately
        self.renderPanes[0].Modified()

        self.Render()

    @component.adapter(SetWindowLevelCommand)
    def onSetWindowLevelCommandEvent(self, evt):
        _min, _max = evt.getTableRange()
        table = self.GetLookupTable()
        table.SetTableRange(_min, _max)
        table.Modified()
        self.Render()

    def SetInputData(self, image, mviewIn):

        #        # due to a problem with Atamai's SlicePlaneFactory, we need
        #        # to ensure there's no inputs before loading in another one
        #
        #        n = self.GetOrthoPlanes().GetNumberOfInputs()
        #        while n > 0:
        #            self.GetOrthoPlanes().RemoveInput(n-1)
        #            n = self.GetOrthoPlanes().GetNumberOfInputs()

        # set coordinate type
        coord_system = image.GetCoordinateSystem()
        for pane in self.renderPanes:
            pane.SetCoordinateSystem(coord_system)

        # make sure header info is correct, otherwise extent calculation may be
        # wrong
        extent = image.GetExtent()

        rank = 0
        for i in range(len(extent) / 2):
            if extent[2 * i] != extent[2 * i + 1]:
                rank += 1

        self.rank = rank

        if self.rank == 2:
            self.GetOrthoPlanes().SetSliceInterpolate(0)
            self.renderPanes[0].BindPanToButton(1)
        else:
            self.GetOrthoPlanes().SetSliceInterpolate(1)
            self.renderPanes[0].BindRotateToButton(1)

        self.GetOrthoPlanes().SetInputData(image.GetRealImage())
        self.volumeOutline.SetInputData(image.GetRealImage())
        self.axesLabels.SetInputData(image.GetRealImage())

        # reset labels
        dimensions = image.GetDimensionInformation()
        self.z_axis_dimension_name = dimensions[-1].GetTypeName()

        # kludge
        # TODO: remove me
        if self.z_axis_dimension_name == 'Wavelength':
            self._x_values = image.GetXSlicePositions()
            self._y_values = image.GetYSlicePositions()
            self._z_values = image.GetZSlicePositions()

        labels = []

        # If patient position is specified, use this info
        dicom_header = image.GetDICOMHeader()
        o = ''
        if 'PatientPosition' in dicom_header:
            o = dicom_header.PatientPosition

        if o != '':

            if coord_system == CoordinateSystem.vtk_coords:
                # account for DICOM vs VTK discrepency
                mapping = {'HFP': 'FFS', 'FFP': 'HFS', 'HFS': 'FFP', 'FFS': 'HFP'}
                o = mapping.get(o, '')

            if o == 'HFP':
                labels = ["L", "R", "P", "A", "I", "S"]
            elif o == 'FFP':
                labels = ["R", "L", "P", "A", "S", "I"]
            elif o == 'HFS':
                labels = ["R", "L", "A", "P", "I", "S"]
            elif o == 'FFS':
                labels = ["L", "R", "A", "P", "S", "I"]
            else:
                # default
                labels = ["x", "x", "y", "y", "z", "z"]
        else:
            # fall back to relying on default dimension names
            for d in dimensions:
                labels.append(d.GetName()[0])
                labels.append(d.GetName()[0])

        self.axesLabels.SetLabels(labels)

        self.lineSegment.SetInput(image.GetRealImage())

        # VTK-6 - find a better way...
        image.Update()

        self.imageScalarRange = image.GetScalarRange()
        # self.autoscale(image)

        self.GetOrthoPlanes().SetLookupTable(self.GetLookupTable())

        # reset image transform
        self.GetOrthoPlanes().SetImageTransform(None)

        # reinitialize config
        self._initializeConfig()

        # reset view
        self.ResetView()

    def autoscale(self, input):

        # if image has a valid window & level setting - use it
        dicom_header = input.GetDICOMHeader()

        if 'WindowWidth' in dicom_header:

            _min, _max = input.GetScalarRange()
            try:
                # take only the first component of window center and window
                # width
                if dicom_header[0x0028, 0x1050].VM > 1:
                    center = dicom_header.WindowCenter[-1]
                else:
                    center = dicom_header.WindowCenter

                if dicom_header[0x0028, 0x1051].VM > 1:
                    width = dicom_header.WindowWidth[-1]
                else:
                    width = dicom_header.WindowWidth

                w = abs(float(width * dicom_header.RescaleSlope))
                l = float(
                    center * dicom_header.RescaleSlope - dicom_header.RescaleIntercept)

                _min = l - (w / 2.0)
                _max = l + (w / 2.0)
            except Exception, e:
                logging.exception("OrthoView")

            table = self.GetLookupTable()
            if table:
                self.GetLookupTable().SetTableRange(_min, _max)
        else:
            # no hard-coded window/level is set - choose a sensible one
            # this code should never be reached, since MVImage() now
            # automatically sets this
            event.notify(WindowLevelPresetEvent('Auto-adjust (99%)'))

    def SetImageTransform(self, transform):

        self.GetOrthoPlanes().SetImageTransform(transform)

        if transform is not None:
            transform = transform.GetInverse()

        for obj in (self.lineSegment,):
            obj.SetTransform(transform)
        for pane in self.renderPanes:
            pane.Render()

    def GetImageTransform(self):
        return self.GetOrthoPlanes().GetImageTransform()

    def GetRenderPanes(self):
        return self.renderPanes

    def onActionKeyPress(self, evt):
        """
        Generate an Action Event - the expected behaviour is that the plugin manager
        will capture this, and forward action key events on to the active plugin
        """
        event.notify(ActionEvent(evt))

    def onProfileEvent(self, evt):
        """Toggles profiling"""
        self.profiler_state = (self.profiler_state + 1) % 2
        if self.profiler_state == 1:
            logging.info("cProfiler enabled.")
            self.profile.enable()
        else:
            import time
            import os
            self.profile.disable()
            filename = os.path.abspath('profile-{0}'.format(time.time()))
            logging.info(
                "cProfiler disabled.  Dumping to {0}".format(filename))
            self.profile.dump_stats(filename)

    def ResetView(self, evt=None):
        for pane in self.renderPanes:
            pane.ResetView()
        ## JDG - self.GetOrthoPlanes().OrthoPlanesReset()

    def Render(self):
        for pane in self.renderPanes:
            pane.Render()

    def SetLineSegmentMark(self, evt, i=0):
        p = evt.pane.GetCursorPosition(evt)
        if p:
            self.lineSegment.SetPoint(i, p[0], p[1], p[2])

        # does the line tool need to be added to scenes?
        if not self.bLineAdded:
            for pane in self.renderPanes:
                pane.ConnectActorFactory(self.lineSegment)
            self.bLineAdded = True

    def EnableMotionMonitoring(self):
        for pane in self.renderPanes:
            pane.EnableMotionMonitoring()

    def DisableMotionMonitoring(self):
        for pane in self.renderPanes:
            pane.DisableMotionMonitoring()

    def OnLineSegmentModified(self, obj, evt):
        """callback method for ModifiedEvent of LineSegmentSelection"""

        # refresh the annotate
        text = self.lineSegment.GetAnnotateText()
        self.lineSegmentAnnotate.SetText(text)

    def SetMeasurementUnit(self, unit):
        self.measurementUnit = unit
        self.lineSegment.SetMeasurementUnits(unit)

    def SetOrthoCenter(self, evt):
        x, y, z = evt.pane.GetCursorPosition(evt)
        self.GetOrthoPlanes().SetOrthoCenter(x, y, z)

    def SavePlaneAsImage(self, evt):
        plane = evt.pane.GetPlane()

        # get a global object that can manage saving image to disk
        obj = component.getUtility(IMicroViewOutput)
        obj.SavePlaneAsImage(plane)

    @component.adapter(ViewportModifiedEvent)
    def onViewportModifiedEvent(self, evt):
        """Respond to change in viewport layout - part 1 - occurs at beginning of e.g. double-click event"""

        # Ignore events that come from other viewports
        if evt.GetPanes()[0] not in self.renderPanes:
            return

        # Disconnect some factories
        for pane in self.renderPanes:
            if self.lineSegmentAnnotate in pane.GetActorFactories():
                pane.DisconnectActorFactory(self.lineSegmentAnnotate)
            if self.sliceNumberAnnotate in pane.GetActorFactories():
                pane.DisconnectActorFactory(self.sliceNumberAnnotate)

        # Connect some factories
        pane = evt.GetPanes()[0]
        pane.ConnectActorFactory(self.lineSegmentAnnotate)
        pane.ConnectActorFactory(self.sliceNumberAnnotate)

    @component.adapter(ViewportModified2Event)
    def onViewportModified2Event(self, evt):
        """Respond to change in viewport layout - part 2- occurs at end of e.g. double-click event"""

        # Ignore events that come from other viewports
        if evt._pane[0] not in self.renderPanes:
            return

        self._current_slice_annotation = c = evt._pane[
            0].GetTrackedSliceIndex()

        # update annotation text
        if c == 0:
            self.onSagittalPlaneModified(None, None)
        elif c == 1:
            self.onCoronalPlaneModified(None, None)
        else:
            self.onAxialPlaneModified(None, None)

        # The orientation widget should only be active over top of a 3D pane
        self.bIs3DView = not isinstance(
            evt._pane[0], EVSRenderPane2D.EVSRenderPane2D)

        bshouldDisplayWidget = self.bIs3DView and MicroViewSettings.MicroViewSettings.getObject(
        ).bShowImageOrientation
        self.enableOrientationWidget(bshouldDisplayWidget)

        # fire off an event here
        event.notify(TrackedSliceIndexChangeEvent(self.GetTrackedSliceIndex()))

    def GetTrackedSliceIndex(self):
        return self._current_slice_annotation

    def WindowLevelPopup(self):

        ApplicationSettings = MicroViewSettings.MicroViewSettings.getObject()

        try:
            mode = ApplicationSettings.bUseMinMaxForWindowLevel
        except:
            mode = ApplicationSettings.bUseMinMaxForWindowLevel = False

        mode_label = {True: 'Min/Max', False: 'Window/Level'}[mode]

        _min, _max = self.GetLookupTable().GetTableRange()
        self.wl_dlg = WindowLevelDialogGUIC.WindowLevelDialogGUIC(
            None, scalar_range=self.imageScalarRange,
            current_range=(_min, _max),
            mode = mode_label)

        # get some info about the dialog
        w, h = self.wl_dlg.getHistogramPanel().GetSize()

        # set up histogram image
        image = component.getUtility(
            IImage, name='Image-{0}'.format(self.GetImageIndex()))
        histogram = image.GetHistogramStatistics()

        histogram.AutomaticBinningOn()
        histogram.GenerateHistogramImageOn()
        histogram.SetHistogramImageSize(w, h)
        histogram.SetHistogramImageScaleToLog()

        # get access to vtk image as a numpy array
        histogram.GetOutput().Update()
        array_name = histogram.GetOutput().GetPointData().GetArrayName(0)
        arr = vtk_to_numpy(
            histogram.GetOutput().GetPointData().GetArray(array_name))
        arr.shape = histogram.GetOutput().GetDimensions()[::-1]
        histogram_image = 255 - arr

        histogram.GenerateHistogramImageOff()

        # flip top to bottom
        histogram_image = histogram_image[:, ::-1, :]

        spacing = histogram.GetBinSpacing()
        origin = histogram.GetBinOrigin()
        num = histogram.GetHistogram().GetSize()
        x = np.linspace(origin, origin + (num - 1) * spacing, num)

        # convert to numpy array
        arr = histogram.GetHistogram()
        y = vtk_to_numpy(arr)

        # update histogram control with this histogram information
        hc = self.wl_dlg.getHistogramControl()
        hc.SetAbsoluteRange((x[0], x[-1]))
        hc.SetCurrentRange([_min, _max])
        hc.SetHistogram(histogram=y, image=histogram_image)

        return_value = self.wl_dlg.ShowModal()

        # update config file
        if return_value == wx.ID_OK:
            ApplicationSettings.bUseMinMaxForWindowLevel = (
                self.wl_dlg.getMode() == 1)
            # notify everyone of w/l preference changes
            event.notify(MicroViewSettingsModifiedEvent(ApplicationSettings))
            _min, _max = self.wl_dlg.getTableRange()

        self.wl_dlg.Destroy()

        # send a command to adjust w/l - this gets done unconditionally to
        # handle dialog cancels as well as okays
        event.notify(SetWindowLevelCommand(_min, _max))

    @component.adapter(SynchronizeEvent)
    def onSynchronizeEvent(self, evt):

        my_idx = self.GetImageIndex()

        _old = evt.GetOldSyncList()
        _new = evt.GetNewSyncList()

        # abort if this message isn't for me
        if not(my_idx in _old or my_idx in _new):
            return

        # remove old observers
        for idx in self._synced_observers.keys():
            for observer, obj in self._synced_observers[idx]:
                obj.RemoveObserver(observer)
            del(self._synced_observers[idx])

        # abort if this message isn't for me (again)
        if not(my_idx in _new):
            return

        # add new observers
        for num in _new:

            # don't listen to our own events here
            if num != my_idx:

                self._synced_observers[num] = []

                orthoView = component.getUtility(
                    IOrthoView, name='OrthoView-%d' % num)
                orthoPlanes = orthoView.GetOrthoPlanes()

                # listen to changes to cameras
                panes = orthoView.GetRenderPanes()
                for i in range(len(panes)):
                    camera = panes[i].GetRenderer().GetActiveCamera()
                    observer = camera.AddObserver('ModifiedEvent', lambda obj, evt, idx=i:
                                                  self.onSyncedCameraModifiedEvent(obj, evt, idx))
                    self._synced_observers[num].append((observer, camera))

                # listen to changes to orthoPlanes
                observer = orthoPlanes.AddObserver('ModifiedEvent',
                                                   lambda obj, evt,
                                                   orthoView=orthoView: self.onSynchedOrthoPlanesModifiedEvent(obj, evt, orthoView))
                self._synced_observers[num].append((observer, orthoPlanes))

    def onSynchedOrthoPlanesModifiedEvent(self, obj, evt, orthoView):
        """an OrthoPlanes object has changed in some way"""

        modified = False

        if self.ignore_events:
            return

        other_planes = orthoView.GetOrthoPlanes()
        my_planes = self.GetOrthoPlanes()

        x1, y1, z1 = other_planes.GetOrthoCenter()
        x2, y2, z2 = my_planes.GetOrthoCenter()

        self.ignore_events = True

        if not (x1, y1, z1) == (x2, y2, z2):
            my_planes.SetOrthoCenter(x1, y1, z1)
            modified = True

        t1 = my_planes.GetTransform()
        m1 = t1.GetMatrix()
        m2 = other_planes.GetTransform().GetMatrix()
        if m1.GetMTime() != m2.GetMTime():
            t1.SetMatrix(m2)

        if modified:
            my_planes.Modified()

        self.ignore_events = False

    def onSyncedCameraModifiedEvent(self, obj, evt, idx):
        """a camera that we listen to has changed"""

        if self.ignore_events:
            return

        self.ignore_events = True
        my_camera = self.GetRenderPanes()[idx].GetRenderer().GetActiveCamera()
        my_camera.DeepCopy(obj)
        self.ignore_events = False
