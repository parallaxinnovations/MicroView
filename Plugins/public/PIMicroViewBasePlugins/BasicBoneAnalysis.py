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
BasicBoneAnalysis - Computes bone mineral density and stereology.

BasicBoneAnalysis is a MicroView plugin which allows the user to compute the BMD,
mean, standard deviation, volume, voxels, and bone volume fraction given
a region of interest.
"""

import StringIO
import datetime
import tempfile
import os
import logging
import vtk
import wx
from zope import component, event, interface

from PI.visualization.common.events import ProgressEvent
from PI.visualization.vtkMultiIO.events import HeaderValueModifiedEvent, HeaderModifiedEvent
from PI.visualization.MicroView import MicroViewPlugIn
from PI.visualization.MicroView import _MicroView
from PI.visualization.MicroView.interfaces import IPlugin, IMicroViewMainFrame, IResultWindow, \
    ICurrentOrthoView, ICurrentImage, ICurrentMicroViewInput, IStandardROIProvider, IROIProvider
from PI.visualization.MicroView.events import CurrentImageChangeEvent, ROIEnabledEvent, NoImagesLoadedEvent

import BasicBoneAnalysisGUIC
import BasicBoneAnalysisAdvancedOptionsDialog


class BasicBoneAppState(object):

    def __init__(self):
        self.threshold = ''
        self.bBMDChecked = False
        self.bStereologyChecked = False
        self.BoneADU = '0'
        self.WaterADU = '0'
        self.LowerExclusion = '-65534'
        self.UpperExclusion = '65535'
        self.bVerboseOutput = False
        self.bEnablePurify = False


class BasicBoneAnalysis(MicroViewPlugIn.MicroViewPlugIn):

    interface.implements(IPlugin)

    __classname__ = "Basic Bone Analysis..."
    __label__ = "Basic Bone"
    __shortname__ = "BasicBoneAnalysis"
    __description__ = "Basic Bone Analysis Tool"
    __iconname__ = "bone_analysis"
    __menuentry__ = "Analyze|Bone Analysis|"
    __managergroup__ = "Applications"
    __tabname__ = "Bone"

    def __init__(self, parent):

        MicroViewPlugIn.MicroViewPlugIn.__init__(self, parent)

        self._parent = parent

        self._helpLink = 'basic-bone-basic-bone-analysis-application'

        self._ROIObject = None
        # self._ROIImage = None
        self._StenciledImage = None
        self._Threshold = None

        self._OutputUpdated = 0
        self._BMDUpdated = 0
        self._StereologyUpdated = 0

        self._ResultsDict = {}

        self._activeObject = None
        self._progressText = None

        self._app_states = {}
        self._current_image_index = None

        # create a gui container for this plugin
        MicroViewPlugIn.MicroViewPlugIn.CreatePluginDialogFrame(self, parent)

        self._tempdir = tempfile.gettempdir()
        self._icon_set = 0

        # Create GUI
        self._roi_plugins = {}
        self.CreateGUI()

        # Set some initial values
        curr_dir = self.GetCurrentDirectory()
        self.gui.m_filePicker.SetPath(os.path.join(
            curr_dir, "AnalysisResults.txt"))

        # Bind events to main dialog
        self.gui.m_buttonActivateROI.Bind(wx.EVT_BUTTON, self.onActivateROI)
        self.gui.m_buttonClearROI.Bind(wx.EVT_BUTTON, self.onClearROI)
        self.gui.m_buttonAutoThreshold.Bind(
            wx.EVT_BUTTON, self.onAutoThreshold)
        self.gui.m_buttonAdvancedOptions.Bind(
            wx.EVT_BUTTON, self.onAdvancedOptions)
        self.gui.m_buttonRun.Bind(wx.EVT_BUTTON, self.onRun)
        self.gui.m_buttonShowResults.Bind(wx.EVT_BUTTON, self.onShowResults)
        self.gui.m_checkBoxBMD.Bind(wx.EVT_CHECKBOX, self.onBMDChecked)
        self.gui.m_checkBoxStereology.Bind(
            wx.EVT_CHECKBOX, self.onStereologyChecked)
        self.gui.m_textCtrlThreshold.Bind(
            wx.EVT_TEXT, self.onThresholdValueChanged)

        # listen to certain zope events
        component.provideHandler(self.OnImageChangeEvent)
        component.provideHandler(self.OnNoImagesLoadedEvent)
        component.provideHandler(self.onHeaderValueModifiedEvent)
        component.provideHandler(self.onHeaderModifiedEvent)
        component.provideHandler(self.onROIEnabledEvent)

        # fake our first change input event
        mv = component.getUtility(IMicroViewMainFrame)
        current_image = mv.GetCurrentImageIndex()
        number_images_displayed = mv.GetNumberOfImagesCurrentlyLoaded()
        title = mv.GetCurrentImageTitle()
        self.OnImageChangeEvent(CurrentImageChangeEvent(
            current_image, number_images_displayed, title))

        # examine header too
        self.ExamineImageHeader()

    def saveCurrentGUIState(self):

        state = self._app_states[self._current_image_index]

        val = self.gui.m_textCtrlThreshold.GetValue()
        try:
            float(val)
            state.threshold = val
        except:
            logging.error("Invalid threshold: {0}".format(val))
            return

        state.bBMDChecked = self.gui.m_checkBoxBMD.GetValue()
        state.bStereologyChecked = self.gui.m_checkBoxStereology.GetValue()

        val = self.advanced_options_dlg.m_textCtrlBoneADU.GetValue()
        try:
            int(val)
            state.BoneADU = val
        except:
            logging.error("Invalid BoneADU: {0}".format(val))

        val = self.advanced_options_dlg.m_textCtrlWaterADU.GetValue()
        try:
            float(val)
            state.WaterADU = val
        except:
            logging.error("Invalid WaterADU: {0}".format(val))

        val = self.advanced_options_dlg.m_textCtrlLowerExclusion.GetValue()
        try:
            int(val)
            state.LowerExclusion = val
        except:
            logging.error("Invalid LowerExclusion: {0}".format(val))

        val = self.advanced_options_dlg.m_textCtrlUpperExclusion.GetValue()
        try:
            int(val)
            state.UpperExclusion = val
        except:
            logging.error("Invalid UpperExclusion: {0}".format(val))

        state.bVerboseOutput = self.advanced_options_dlg.m_checkBoxEnableVerbose.GetValue()
        state.bEnablePurify = self.advanced_options_dlg.m_checkBoxEnablePurify.GetValue()

    def updateGUIState(self):

        state = self._app_states[self._current_image_index]

        self.gui.m_textCtrlThreshold.SetValue(state.threshold)
        self.gui.m_checkBoxBMD.SetValue(state.bBMDChecked)
        self.gui.m_checkBoxStereology.SetValue(state.bStereologyChecked)

        self.advanced_options_dlg.m_textCtrlBoneADU.SetValue(state.BoneADU)
        self.advanced_options_dlg.m_textCtrlWaterADU.SetValue(state.WaterADU)
        self.advanced_options_dlg.m_textCtrlLowerExclusion.SetValue(
            state.LowerExclusion)
        self.advanced_options_dlg.m_textCtrlUpperExclusion.SetValue(
            state.UpperExclusion)
        self.advanced_options_dlg.m_checkBoxEnableVerbose.SetValue(
            state.bVerboseOutput)
        self.advanced_options_dlg.m_checkBoxEnablePurify.SetValue(
            state.bEnablePurify)

    def onActivateROI(self, evt):
        """Activate a ROI plugin"""
        n = self.gui.m_choiceROIPlugin.GetSelection()
        label = self.gui.m_choiceROIPlugin.GetString(n)
        plugin_class = self._roi_plugins[label]
        self.GetPluginManager().ActivatePlugin(
            plugin_class, bShouldSelect=False)

    def onClearROI(self, evt):
        """Clear all ROI."""
        self.GetMicroView().ClearROI()
        self.GetMicroView().pane3D.Render()

    def onAutoThreshold(self, evt):

        with wx.BusyCursor():
            self._Threshold = self.GetMicroView().GetROIStats().GetThreshold()

        if self._Threshold is None:

            dlg = wx.MessageDialog(
                self._Dialog, 'Volume of Interest is not defined.  Please select a VOI before continuing.',
                'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

            return -1

        state = self._app_states[self._current_image_index]
        state.threshold = "%0.4f" % self._Threshold
        self.gui.m_textCtrlThreshold.SetValue(state.threshold)

        # This next bit of code shouldn't be here, because it exposes the
        # implementation of MicroView's window/level code too much
        table = component.getUtility(ICurrentOrthoView).GetLookupTable()
        r = table.GetRange()
        level = (r[1] + r[0]) / 2.0
        delta = self._Threshold - level
        r = (r[0] + delta, r[1] + delta)
        table.SetRange(r[0], r[1])

        self.updateRunButtonState()

        return self._Threshold

    def onAdvancedOptions(self, evt):

        # setup values
        self.updateGUIState()

        # display advanced options dialog
        ret = self.advanced_options_dlg.ShowModal()
        self.advanced_options_dlg.Hide()

        # update based on dialog manipulation
        if ret == wx.ID_OK:
            self.saveCurrentGUIState()

    def onRun(self, evt):
        """Main method to run everything"""

        state = self._app_states[self._current_image_index]

        # verify that an ROI exists for current image
        image = component.getUtility(ICurrentImage)
        stencil_data = image.GetStencilData()

        if stencil_data is None:
            message = 'Volume of Interest undefined.\n' + \
                      'Please select an VOI before continuing.'

            dlg = wx.MessageDialog(
                self._Dialog, message, 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return -1

        logging.info("BasicBoneAnalysis run on active ROI")

        # the Stencil
        self.__stencil_data = self.GetMicroView().GetROIStencilData()

        # VTK-6 change needed here
        if vtk.vtkVersion().GetVTKMajorVersion() > 5:
            pass
        else:
            logging.debug("TODO: retire this code")
            self.__stencil_data.Update()

        # if an image transform has been set, bail out
        t = component.getUtility(ICurrentOrthoView).GetImageTransform()
        if t is not None:
            dlg = wx.MessageDialog(
                self._Dialog, "The Bone Analysis Tool does not support transformed images!", 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return -1

        # check if threshold is set
        if self._Threshold is None:
            dlg = wx.MessageDialog(
                self._Dialog, "Threshold undefined.  Please set threshold before continuing.", 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return -1

        self.gui.m_buttonRun.Enable(False)

        with wx.BusyCursor():
            # free memory
            self.FreeMemory()

            self._ResultsDict = {}

            #======================
            # check for output file
            #======================
            if self.gui.m_checkBoxAppend.GetValue():
                mode = 'a'
            else:
                mode = 'w'

            # reset output strings
            self._TextFileIO = open(self.gui.m_filePicker.GetPath(), mode)
            # self._PluginSerializer.CreateNewFile(self.gui.m_filePicker.GetPath(),
            # mode)
            self._BMDOutStr = None
            self._StereologyOutStr = None

            # if (1):  # a hook for batched job
            if self.gui.m_checkBoxBMD.IsChecked():
                self._BMDUpdated = 0
                self._BMDUpdated = (self.DoBMD() == 0)
            if self.gui.m_checkBoxStereology.IsChecked():
                self._StereologyUpdated = 0
                self._StereologyUpdated = (self.DoStereology() == 0)

            outstr = StringIO.StringIO()

            outstr.write("\n#############################################\n")
            outstr.write("# File: %s\n" % self.GetMicroView().GetFileName())
            outstr.write("# Time: %s\n" % datetime.datetime.now().isoformat())
            outstr.write("# VOI Extent: %s\n" %
                         str(self.__stencil_data.GetExtent()))
            outstr.write("# Voxel Size (mm): %.6f x %.6f x %.6f\n" % component.getUtility(
                ICurrentImage).GetSpacing())
            outstr.write("# Verbose Mode: %s\n" %
                         {True: 'On', False: 'Off'}[state.bVerboseOutput])
            outstr.write("# Enable Purify: %s\n" %
                         {True: 'On', False: 'Off'}[state.bEnablePurify])
            outstr.write('#############################################\n')

            self._HeaderOutStr = outstr.getvalue()
            outstr.close()

            self.SaveResults()
            self.ShowResults()

            self._TextFileIO.close()
            self.gui.m_buttonRun.Enable(True)

    def onShowResults(self, evt):
        self.ShowResults()

    def onBMDChecked(self, evt):
        state = self._app_states[self._current_image_index]
        state.bBMDChecked = evt.IsChecked()

    def onStereologyChecked(self, evt):
        state = self._app_states[self._current_image_index]
        state.bStereologyChecked = evt.IsChecked()

    def onThresholdValueChanged(self, evt):
        self.updateRunButtonState()

    def SetButtonValue(self, function, state):
        if not hasattr(self, function + 'Checked'):
            return -1
        getattr(self, function + 'Checked').set(state)
        return 0

    def CreateGUI(self):

        # create a sizer for root widget
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self._Dialog.SetSizer(self.sizer)
        self.gui = BasicBoneAnalysisGUIC.BasicBoneAnalysisGUIC(self._Dialog)

        # create advanced dialog
        self.advanced_options_dlg = BasicBoneAnalysisAdvancedOptionsDialog.BasicBoneAnalysisAdvancedOptionsDialog(
            wx.GetApp().GetTopWindow())

        # what is the name of the `Standard` ROI tool?
        standard_roi_name = 'StandardROI'  # this is the default plugin name

        # the next bit allows a bit of system customization in the future
        for (name, plugin_class) in component.getUtilitiesFor(IStandardROIProvider):
            standard_roi_name = plugin_class.GetShortName()
            break  # take first from the list - we only expect one

        # determine what plugins are capable of providing ROIs -- remember their names
        self._roi_plugins = {}
        for (name, plugin_class) in component.getUtilitiesFor(IROIProvider):
            label = plugin_class.GetLabel()
            name = plugin_class.GetShortName()
            self._roi_plugins[label] = name

        # sort plugin labels
        labels = self._roi_plugins.keys()
        labels.sort()

        self.gui.m_choiceROIPlugin.Clear()
        sel = 0
        for n, name in enumerate(labels):
            self.gui.m_choiceROIPlugin.Append(name)
            if self._roi_plugins[name] == standard_roi_name:
                sel = n
        self.gui.m_choiceROIPlugin.SetSelection(n)

    @component.adapter(NoImagesLoadedEvent)
    def OnNoImagesLoadedEvent(self, evt):
        self.gui.Enable(False)

    @component.adapter(CurrentImageChangeEvent)
    def OnImageChangeEvent(self, evt):

        self.gui.Enable(True)

        self._OutputUpdated = 0
        self._BMDUpdated = 0
        self._StereologyUpdated = 0

        self._ROIObject = None
        self._Threshold = None

        try:
            input = component.getUtility(ICurrentImage)
            self._Dialog.Enable(True)
        except:
            # no image loaded - disable ourselves
            self._Dialog.Enable(False)
            return

        self._Origin = input.GetOrigin()
        self._Spacing = input.GetSpacing()
        self._Extent = input.GetExtent()
        self._dims = input.GetDimensions()

        (xDim, yDim, zDim) = self._dims

        spacing = self._Spacing
        extent = self._Extent
        self._maxDimMM = max([(extent[1] - extent[0]) * spacing[0],
                              (extent[3] - extent[2]) * spacing[1],
                              (extent[5] - extent[4]) * spacing[2]])
        self._maxDimMM = min([(extent[1] - extent[0]) * spacing[0],
                              (extent[3] - extent[2]) * spacing[1],
                              (extent[5] - extent[4]) * spacing[2]])

        # save current gui state
        if self._current_image_index is not None:
            self.saveCurrentGUIState()

        self._current_image_index = evt.GetCurrentImageIndex()

        if self._current_image_index not in self._app_states:
            self._app_states[self._current_image_index] = BasicBoneAppState()

        # load current gui state
        self.updateGUIState()

    def ExamineImageHeader(self):

        try:
            image = component.getUtility(ICurrentImage)
        except:
            return

        header = image.GetHeader()
        state = self._app_states[self._current_image_index]

        state.BoneADU = header.get('boneHU', '0')
        state.WaterADU = header.get('waterADU', '0.0')
        state.LowerExclusion = header.get('exclusionADU', '-65534')
        state.UpperExclusion = header.get('UpperExclusionADU', '65535')

    @component.adapter(HeaderValueModifiedEvent)
    def onHeaderValueModifiedEvent(self, e=None):

        if e._key in ('boneHU', 'waterADU', 'exclusionADU', 'UpperExclusionADU'):
            self.ExamineImageHeader()

    @component.adapter(HeaderModifiedEvent)
    def onHeaderModifiedEvent(self, evt):
        self.ExamineImageHeader()

    def GetROIImage(self, clipDataOn=0):
        """Return ROI Image port from ROIStencil"""
        component.getUtility(ICurrentImage).Update()
        minV, maxV = component.getUtility(ICurrentImage).GetScalarRange()
        reslice = vtk.vtkImageReslice()
        reslice.SetInputConnection(
            component.getUtility(ICurrentImage).GetOutputPort())
        reslice.SetInterpolationModeToCubic()

        # 2014-12-22 this is important
        self.__stencil_data.Update()

        # VTK-6
        if vtk.vtkVersion().GetVTKMajorVersion() > 5:
            reslice.SetStencilData(self.__stencil_data)
        else:
            reslice.SetStencil(self.__stencil_data)

        reslice.SetOutputExtent(self.__stencil_data.GetWholeExtent())
        reslice.SetOutputOrigin(self._Origin)
        reslice.SetOutputSpacing(self._Spacing)
        reslice.SetBackgroundLevel(minV)
        reslice.Update()

        return reslice

    def FreeMemory(self):
        """Free memory"""
        pass

    def DoBMD(self):
        return self.BMDAnalysis()

    def DoStereology(self):
        return self.StereologyAnalysis()

    # functions rid off BMDAnalysis
    def BMDAnalysis(self):
        with wx.BusyCursor():
            state = self._app_states[self._current_image_index]
            imageStats2 = _MicroView.vtkImageStatistics()
            imageStats2.SetInputConnection(component.getUtility(
                ICurrentImage).GetOutputPort())

            # VTK-6
            if vtk.vtkVersion().GetVTKMajorVersion() > 5:
                imageStats2.SetStencilData(self.__stencil_data)
            else:
                imageStats2.SetStencil(self.__stencil_data)

            imageStats2.SetWaterValue(float(state.WaterADU))
            imageStats2.SetBoneValue(int(state.BoneADU))
            imageStats2.SetLowerExclusionValue(int(state.LowerExclusion))
            imageStats2.SetUpperExclusionValue(int(state.UpperExclusion))
            imageStats2.SetBVFThreshold(float(state.threshold))
            imageStats2.SetProgressText('BMD Analysis...')
            imageStats2.AddObserver(
                'ProgressEvent', self.HandleVTKProgressEvent)
            imageStats2.Update()

            # Mean and Standard Deviation
            self.Mean = imageStats2.GetMean()[0]
            self.StdDev = imageStats2.GetStandardDeviation()[0]

            #  self.MeanResultLabel.configure(text="%0.2f" % self.Mean)
            #  self.StdDevResultLabel.configure(text="%0.2f" % self.StdDev)

            # BMD
            self.BMD = imageStats2.GetBMD()
            self.BMC = imageStats2.GetBoneMass()
            self.Volume = imageStats2.GetVolume() * 1000.0  # we use mm^3 here
            self.Voxels = imageStats2.GetVoxelCount()
            self.ThresholdedBMD = imageStats2.GetThresholdedBMD()
            self.ThresholdedBMC = imageStats2.GetThresholdedBoneMass()

            # BVF
            self.BVF = 0.0
            try:
                self.BVF = imageStats2.GetBoneVoxelCount() / float(
                    imageStats2.GetVoxelCount())
            except:
                pass

            del imageStats2

            out = StringIO.StringIO()
            out.write("\n==============\n")
            out.write("= BMD Analysis\n")
            out.write("==============\n")
            out.write("  Mean: %10.4f\n" % (self.Mean,))
            out.write("  Standard Deviation: %10.4f\n" % (self.StdDev,))
            out.write("  Total Volume: %10.4f (mm^3)\n" % (self.Volume,))
            out.write("  Bone Volume: %10.4f (mm^3)\n" % (
                self.Volume * self.BVF,))
            out.write("  Voxel: %d\n" % self.Voxels)
            if int(state.BoneADU) == 0:
                out.write(
                    "  Bone mineral content (mg): Error, No BoneHU for image.\n")
                out.write("  BMD (mg/cc): Error, No BoneHU for image.\n")
                out.write(
                    "  Tissue mineral density (mg/cc): Error, No BoneHU for image.\n")
            else:
                out.write("  Bone mineral content (mg): %10.4f\n" % (
                    self.BMC))
                out.write("  BMD (mg/cc): %10.4f\n" % (self.BMD))
                out.write("  Tissue mineral content (mg): %10.4f\n" % (
                    self.ThresholdedBMC))
                out.write("  Tissue mineral density (mg/cc): %10.4f\n" % (
                    self.ThresholdedBMD))
            out.write("  BVF: %10.4f\n" % self.BVF)
            out.write('\n')

            self._BMDOutStr = out.getvalue()
            out.close()

            self._ResultsDict['BMDMean'] = self.Mean
            self._ResultsDict['BMDStdDev'] = self.StdDev
            self._ResultsDict['BMDVolume'] = self.Volume
            self._ResultsDict['BMDBoneVolume'] = self.Volume * self.BVF
            self._ResultsDict['BMDVoxels'] = self.Voxels
            self._ResultsDict['BMDBVF'] = self.BVF
            if int(state.BoneADU) > 0:
                self._ResultsDict['BMDBMC'] = self.BMC
                self._ResultsDict['BMDBMD'] = self.BMD
                self._ResultsDict['BMDTMC'] = self.ThresholdedBMC
                self._ResultsDict['BMDTMD'] = self.ThresholdedBMD

            event.notify(ProgressEvent("BMD Analysis... Done.", 1.0))

        # return status
        return 0

    def StereologyAnalysis(self):
        """Perform stereology analysis on a sub-region of an image"""

        # user have to define an ROI - enforce fore now...
        # should allow to use whole image as default

        event.notify(ProgressEvent("Stereology...", 0.0))
        state = self._app_states[self._current_image_index]
        origin = self._Origin
        spacing = self._Spacing

        # --- generate a mask from stencil ----
        self.__stencil_data.Update()
        stencil_image = vtk.vtkImageStencilToImage()
        stencil_image.SetInput(self.__stencil_data)
        stencil_image.SetInsideValue(255)
        stencil_image.SetOutsideValue(0)
        stencil_image.SetOutputScalarTypeToUnsignedChar()
        stencil_image.Update()

        # --- image purify -----
        event.notify(ProgressEvent("Stereology: Purify...", 0.2))

        roi_image_reslice = self.GetROIImage()

        # optionally create a purification filter
        if state.bEnablePurify:
            purify = _MicroView.vtkImagePurify()
            purify.SetInputConnection(roi_image_reslice.GetOutputPort())
            purify.SetThreshold(self._Threshold)
            purify.UpdateInformation()

        # --- Create an object to calculate stereology parameters
        stereology = _MicroView.vtkImageStereology()
        if state.bEnablePurify:
            stereology.SetInputConnection(purify.GetOutputPort())
            stereology.SetThreshold(1)
        else:
            stereology.SetInputConnection(roi_image_reslice.GetOutputPort())
            stereology.SetThreshold(self._Threshold)

        stereology.SetImageMask(stencil_image.GetOutput())

        event.notify(ProgressEvent("Stereology...", 0.4))

        stereology.Update()

        event.notify(ProgressEvent("Stereology...", 0.8))

        outfile = StringIO.StringIO()
        outfile.write('\n==============\n')
        outfile.write('= Stereology\n')
        outfile.write('==============\n')
        outfile.write(
            '  Total # of points used:  {0}\n'.format(stereology.GetnumVoxels()))
        voxel_volume = self._Spacing[0] * self._Spacing[1] * self._Spacing[2]
        outfile.write("  Total volume of examined region (mm^3): %10.4f\n" % (
            stereology.GetnumVoxels() * voxel_volume,))

        if state.bVerboseOutput:
            outfile.write('\n')
            outfile.write('  The total number of voxels occupied by bone:   %d\n' %
                          int(stereology.GetPp() * stereology.GetnumVoxels()))
            outfile.write(
                '  The number of intersections (entering and leaving) for each direction:\n')
            outfile.write('        %d    %d :    %d    %d  :    %d    %d\n' % (
                stereology.GetIntX(),
                stereology.GetIntXO(),
                stereology.GetIntY(),
                stereology.GetIntYO(),
                stereology.GetIntZ(),
                stereology.GetIntZO()))
            outfile.write('\n')

        outfile.write('  The Euler # found using 27 surrounding voxels:  {0}\n'.format(
            stereology.GetEuler3D()))
        outfile.write("            -Euler # / Volume analyzed (1/mm^3):  %0.5f\n" % (
            -1.0 * stereology.GetEuler3D() / voxel_volume / stereology.GetnumVoxels()))

        outfile.write('\n')
        outfile.write(
            '  Morphologic variables calculated from total planar intersection counts:\n')
        outfile.write(
            '         BV/TV      BS/BV        Tb.Th       Tb.N        Tb.Sp\n')

        format = '%0.6f   %0.6f     %0.6f    %0.6f    %0.6f'
        if state.bVerboseOutput:
            outfile.write('   (x)  ' + format % (
                stereology.GetBVTV(),
                stereology.GetxBSBV(),
                stereology.GetxTbTh(),
                stereology.GetxTbN(),
                stereology.GetxTbSp()) + '\n')
            outfile.write('   (y)  ' + format % (
                stereology.GetBVTV(),
                stereology.GetyBSBV(),
                stereology.GetyTbTh(),
                stereology.GetyTbN(),
                stereology.GetyTbSp()) + '\n')
            outfile.write('   (z)  ' + format % (
                stereology.GetBVTV(),
                stereology.GetzBSBV(),
                stereology.GetzTbTh(),
                stereology.GetzTbN(),
                stereology.GetzTbSp()) + '\n')
            outfile.write('  (avg) ' + format % (
                stereology.GetBVTV(),
                stereology.GetBSBV(),
                stereology.GetTbTh(),
                stereology.GetTbN(),
                stereology.GetTbSp()) + '\n')

        outfile.write('\n')

        self._ResultsDict['StereologyTotalPoints'] = stereology.GetnumVoxels()
        self._ResultsDict[
            'StereologyTotalVolume'] = stereology.GetnumVoxels() * voxel_volume
        self._ResultsDict['StereologyBoneVoxels'] = int(
            stereology.GetPp() * stereology.GetnumVoxels())
        self._ResultsDict['StereologyEulerNumber'] = stereology.GetEuler3D()
        self._ResultsDict['StereologyEulerVolume'] = -1.0 * \
            stereology.GetEuler3D() / voxel_volume / stereology.GetnumVoxels()
        self._ResultsDict['StereologyAvgBVTV'] = stereology.GetBVTV()
        self._ResultsDict['StereologyAvgBSBV'] = stereology.GetBSBV()
        self._ResultsDict['StereologyAvgTbTh'] = stereology.GetTbTh()
        self._ResultsDict['StereologyAvgTbN'] = stereology.GetTbN()
        self._ResultsDict['StereologyAvgTbSp'] = stereology.GetTbSp()

        self._StereologyOutStr = outfile.getvalue()
        outfile.close()

        event.notify(ProgressEvent("Stereology: Done.", 1.0))

        # normal status
        return 0

    def SaveResults(self):
        logger = logging.getLogger('results')

        self._TextFileIO.write(self._HeaderOutStr + '\n')
        logger.info(self._HeaderOutStr)

        # ROI parameter
        if self._BMDOutStr:
            self._TextFileIO.write(self._BMDOutStr + '\n')
            logger.info(self._BMDOutStr)
        if self._StereologyOutStr:
            self._TextFileIO.write(self._StereologyOutStr + '\n')
            logger.info(self._StereologyOutStr)

    def ShowResults(self):

        object = component.getUtility(IMicroViewMainFrame)
        object.ShowResultsWindow()

    def GetResults(self, *args):
        if not args[0] in self._ResultsDict:
            logging.error(
                'Advanced Analysis - results dictionary has no key %s' % (args[0]))
            return
        return self._ResultsDict[args[0]]

    def OnPluginClose(self):
        """Remove active graphic once plugin is closed"""
        # unregister our zope handlers
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.OnImageChangeEvent)
        gsm.unregisterHandler(self.OnNoImagesLoadedEvent)
        gsm.unregisterHandler(self.onHeaderValueModifiedEvent)
        gsm.unregisterHandler(self.onHeaderModifiedEvent)
        gsm.unregisterHandler(self.onROIEnabledEvent)

    def OnOptionDialogChange(self, optionvar, value):
        if hasattr(self, optionvar):
            getattr(self, optionvar).set(value)

    @component.adapter(ROIEnabledEvent)
    def onROIEnabledEvent(self, evt):

        # Check state of run button
        self.updateRunButtonState()

    def updateRunButtonState(self):

        try:
            threshold = float(self.gui.m_textCtrlThreshold.GetValue())
            bThresholdValid = True
        except:
            bThresholdValid = False

        image = component.getUtility(ICurrentImage)
        stencil_data = image.GetStencilData()

        if (stencil_data is not None) and bThresholdValid:
            self.gui.m_buttonRun.Enable(True)
        else:
            self.gui.m_buttonRun.Enable(False)

##########################################################################


def createPlugin(panel):
    return BasicBoneAnalysis(panel)
