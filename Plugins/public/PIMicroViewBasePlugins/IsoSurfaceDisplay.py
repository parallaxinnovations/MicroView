# =========================================================================
#
# Copyright (c) 2000-2002 Enhanced Vision Systems
# Copyright (c) 2002-2008 GE Healthcare
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
IsoSurfaceDisplay - Generate iso-contour surfaces.

IsoSurfaceDisplay is a MicroView plugin which allows the user to perform simple
image segmentation.  The plugin is flexible enough to allow the desired iso-value
to be set interactively, as well as the contour color.  Additional capabilities
include:

    o The ability to resample the image prior to segmentation, to cut down
      processing time.

    o The ability to pre-process the image with a Gaussian smooth kernel.

    o The ability to crop the image, prior to segmentation, using the 7 and 8
      keys.

    o The ability to save the segmented surface in a number of file formats.
"""

import os
import math
import logging
import vtk
import wx
from zope import component, event, interface

import vtkAtamai.SurfaceObjectFactory
from vtkEVS import EVSFileDialog

from PI.visualization.vtkMultiIO import vtkLoadWriters
from PI.visualization.common.events import ProgressEvent
from PI.visualization.MicroView import MicroViewPlugIn

from PI.visualization.MicroView.interfaces import IPlugin, IROIProvider, ICurrentImage, ICurrentViewportManager, \
    IOrthoView, ICurrentOrthoView
from PI.visualization.MicroView.events import ROIEnabledEvent, CurrentImageChangeEvent, NoImagesLoadedEvent, \
    ROIModelModifiedEvent, CurrentImageClosingEvent

import IsosurfaceGUIC


class IsoSurfaceDisplayState(object):

    def __init__(self):
        self.threshold = None
        self.surface_quality_factor = 25.0
        self.decimation_factor = 0.0
        self.surface_colour = (255, 255, 255, 255)
        self.bEnableImageSmoothing = False
        self.bClipSurfaceWithCurrentROI = False
        self._factory = None
        self._area = None
        self._volume = None
        self._poly_count = None
        self._region_count = None
        self._disconnected = True

    def GetFactory(self):
        return self._factory

    def SetFactory(self, fact):
        self._factory = fact


class IsoSurfaceDisplay(MicroViewPlugIn.MicroViewPlugIn):

    interface.implements(IROIProvider, IPlugin)

    __classname__ = "Display Isosurface..."
    __label__ = "Isosurface"
    __shortname__ = "IsoSurfaceDisplay"
    __description__ = "Isosurface tool"
    __iconname__ = "isosurface"
    __menuentry__ = "Visualize|Isosurface"
    __managergroup__ = None
    __tabname__ = "Isosurface"

    def __init__(self, parent):

        MicroViewPlugIn.MicroViewPlugIn.__init__(self, parent)

        self._helpLink = 'isosurface-isosurface-tool'

        # Create a geometry writer
        (self._writer, self._ft) = vtkLoadWriters.LoadGeometryWriters()

        # create a gui container for this plugin
        MicroViewPlugIn.MicroViewPlugIn.CreatePluginDialogFrame(self, parent)

        self._color = (1.0, 1.0, 1.0)
        self._filename = None

        self._app_states = {}
        self._current_image_index = None

        self._transform = None

        # create remaining gui
        self.CreateGUI()

        # listen to certain zope events
        component.provideHandler(self.onModelModifiedEvent)
        component.provideHandler(self.onROIEnabledEvent)
        component.provideHandler(self.OnImageChangeEvent)
        component.provideHandler(self.OnNoImagesLoadedEvent)
        component.provideHandler(self.OnCurrentImageClosingEvent)

        # Invoke an event to react to currently loaded image
        self.InvokeImageLoadedEvent()

    def saveCurrentGUIState(self):

        state = self._app_states[self._current_image_index]

        state.surface_quality_factor = self.gui.m_sliderSurfaceQuality.GetValue(
        )
        state.decimation_factor = self.gui.m_sliderDecimationFactor.GetValue()
        state.threshold = self.gui.m_textCtrlImageThreshold.GetValue()
        state.bClipSurfaceWithCurrentROI = self.gui.m_checkBoxClipping.GetValue(
        )
        state.bClipSurfaceWithCurrentROI = self.gui.m_checkBoxImageSmoothing.GetValue(
        )
        state.surface_colour = self.gui.m_colourPicker.GetColour()

    def updateGUIState(self):

        state = self._app_states[self._current_image_index]

        if state.threshold is None:
            table = component.getUtility(ICurrentOrthoView).GetLookupTable()
            if table:
                _min, _max = table.GetTableRange()
                val = (_min + _max) / 2.0
                state.threshold = '%0.3f' % val

        self.gui.m_sliderSurfaceQuality.SetValue(
            state.surface_quality_factor or 25.0)
        self.gui.m_sliderDecimationFactor.SetValue(
            state.decimation_factor or 0.0)
        self.gui.m_textCtrlImageThreshold.SetValue(state.threshold or '')
        self.gui.m_checkBoxClipping.SetValue(state.bClipSurfaceWithCurrentROI)
        self.gui.m_checkBoxImageSmoothing.SetValue(
            state.bClipSurfaceWithCurrentROI)
        self.gui.m_colourPicker.SetColour(
            state.surface_colour or (255, 255, 255, 255))

    @component.adapter(CurrentImageChangeEvent)
    def OnImageChangeEvent(self, evt):

        self.gui.Enable(True)

        # save current gui state
        if self._current_image_index is not None:
            self.saveCurrentGUIState()

        self._current_image_index = evt.GetCurrentImageIndex()

        if self._current_image_index not in self._app_states:
            self._app_states[
                self._current_image_index] = IsoSurfaceDisplayState()

        # load current gui state
        self.updateGUIState()

        state = self._app_states[self._current_image_index]

        self.UpdateStatisticsText()

    @component.adapter(NoImagesLoadedEvent)
    def OnNoImagesLoadedEvent(self, evt):
        self.gui.Enable(False)

    @component.adapter(CurrentImageClosingEvent)
    def OnCurrentImageClosingEvent(self, evt):
        self.HideGeometry()

    def SetTransform(self, t):
        self._transform = t

    def Render(self):
        "Render - Renders the current isosurface"
        with wx.BusyCursor():
            component.getUtility(ICurrentViewportManager).Render()

    def SetResizeFactor(self, evt):
        """Set image rescale factor"""
        val = evt.GetInt()
        logging.debug("image resize: %s" % str(val))
        self.gui.m_buttonUpdate.Enable(True)
        self.gui.m_buttonSaveSurface.Enable(False)
        self.gui.m_sliderSurfaceQuality.SetValue(val)

    def SetDecimationFactor(self, evt):
        """Set image decimation factor"""
        val = evt.GetInt()
        self.gui.m_buttonUpdate.Enable(True)
        self.gui.m_buttonSaveSurface.Enable(False)
        self.gui.m_sliderDecimationFactor.SetValue(val)

    def SaveGeometry(self, filename=None):
        """Save the geometry to a file"""
        if filename is None:
            self._filename = EVSFileDialog.asksaveasfilename(
                message='Save Surface', filetypes=self._ft,
                defaultfile='surface.vtp', defaultextension='*.vtp')
        else:
            self._filename = filename
        if self._filename:
            try:
                self._writer.SetFileName(self._filename)
            except AttributeError, msg:
                logging.exception("IsoSurfaceDisplay")
                dlg = wx.MessageDialog(
                    self._Dialog, str(msg), 'Error', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
            self._writer.SetInputConnection(
                self._app_states[self._current_image_index].GetFactory().GetInputConnection())

            try:
                with wx.BusyCursor():
                    event.notify(ProgressEvent("Saving surface...", 0.0))
                    self._writer.Write()
                    event.notify(ProgressEvent("Saving surface...", 1.0))
                    logging.info(
                        "Surface saved to '{0}'".format(self._filename))
            except IOError, (errno, strerror):
                logging.exception("IsoSurfaceDisplay")
                dlg = wx.MessageDialog(self._Dialog, "[Errno %d]: %s" % (
                    errno, strerror), 'Error', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

    def onThresholdChanged(self, evt):

        evt.Skip()
        enabled = True
        try:
            _ = float(self.gui.m_textCtrlImageThreshold.GetValue())
        except:
            enabled = False
        self.gui.m_buttonUpdate.Enable(enabled)

    def onClipSurfaceChanged(self, evt):
        """onClipSurfaceChanged - Toggles the use of the current ROI"""
        self.gui.m_buttonUpdate.Enable(True)
        self.gui.m_buttonSaveSurface.Enable(False)

    def onEnableSmoothingChanged(self, evt):
        """
        onEnableSmoothingChanged - Toggle the use of image smoothing
        """

        self.gui.m_buttonUpdate.Enable(True)
        self.gui.m_buttonClear.Enable(False)
        self.gui.m_buttonSaveSurface.Enable(False)

    def GetSurfaceColor(self, evt):
        """
        GetSurfaceColor - Ask user to select a surface colour.  Pops up
        a colour chooser to allow user to select an RGB value.
        """
        self._color = (
            evt.Colour.red / 255., evt.Colour.green / 255., evt.Colour.blue / 255.)
        self.SetSurfaceColor()
        self.Render()

    def SetSurfaceColor(self):
        """SetSurfaceColor - Sets the current polygon surface color to
        whatever is defined in self._color"""
        r, g, b = self._color
        if self._app_states[self._current_image_index].GetFactory():
            self._app_states[
                self._current_image_index].GetFactory().GetProperty().SetColor(r, g, b)

    def UpdateGeometry(self, evt):
        """Shows and updates the isosurface geometry"""

        # remove any old surface - frees a lot of memory!
        if not self._app_states[self._current_image_index]._disconnected:
            self.HideGeometry()
        self._BuildPipeline()
        self.Render()

        # update GUI
        self.gui.m_buttonUpdate.Enable(False)
        self.gui.m_buttonClear.Enable(True)
        self.gui.m_buttonSaveSurface.Enable(True)

    def GetArea(self):
        """GetArea - returns the surface area of the current polygon"""
        return self._app_states[self._current_image_index]._area

    def GetVolume(self):
        """GetVolume - returns the volume of the current polygon"""
        return self._app_states[self._current_image_index]._volume

    def UpdateStatisticsText(self):
        if self._app_states[self._current_image_index]._area:
            self.gui.m_staticTextArea.SetLabel(u'%0.3f mm\u00B2' % (
                self._app_states[self._current_image_index]._area))
        else:
            self.gui.m_staticTextArea.SetLabel('')
        if self._app_states[self._current_image_index]._volume:
            self.gui.m_staticTextVolume.SetLabel(u'%0.3f mm\u00B3' % (
                self._app_states[self._current_image_index]._volume))
        else:
            self.gui.m_staticTextVolume.SetLabel('')
        if self._app_states[self._current_image_index]._poly_count:
            self.gui.m_staticTextPolygonCount.SetLabel('%d' % (
                self._app_states[self._current_image_index]._poly_count))
        else:
            self.gui.m_staticTextPolygonCount.SetLabel('')
        if self._app_states[self._current_image_index]._region_count:
            self.gui.m_staticTextRegionCount.SetLabel('%d' % (
                self._app_states[self._current_image_index]._region_count))
        else:
            self.gui.m_staticTextRegionCount.SetLabel('')

    def UpdateMathValues(self):

        connection = self._app_states[
            self._current_image_index].GetFactory().GetInputConnection()
        object = connection.GetProducer().GetOutput()

        # determine number of connected components
        _f = vtk.vtkPolyDataConnectivityFilter()
        _f.SetInputConnection(connection)
        _f.Update()
        nregions = _f.GetNumberOfExtractedRegions()

        self._app_states[
            self._current_image_index]._poly_count = object.GetNumberOfPolys()
        self._app_states[self._current_image_index]._volume, self._app_states[
            self._current_image_index]._area = 0.0, 0.0
        self._app_states[self._current_image_index]._region_count = nregions

        if self._app_states[self._current_image_index]._poly_count > 0:
            math0 = vtk.vtkMassProperties()
            math0.SetInputConnection(connection)
            math0.Update()
            self._app_states[self._current_image_index]._volume, self._app_states[
                self._current_image_index]._area = math0.GetVolume(), math0.GetSurfaceArea()

        self.UpdateStatisticsText()

        # log some results
        logger = logging.getLogger('results')
        logger.info("Isosurface plugin (%s):" % (component.getUtility(
            ICurrentViewportManager).GetPageState().GetTitle()))
        logger.info(u"\tArea: %0.3f mm\u00B2" %
                    self._app_states[self._current_image_index]._area)
        logger.info(u'\tVolume: %0.3f mm\u00B3' % (
            self._app_states[self._current_image_index]._volume))
        logger.info('\tPolygon Count: %d' % (
            self._app_states[self._current_image_index]._poly_count))
        logger.info('\tRegion Count: %d' % (
            self._app_states[self._current_image_index]._region_count))
        logger.info('')

    def HideGeometry(self, evt=None):
        """
        HideGeometry - Hides the isosurface geometry.
        If evt=1, delete the surface.
        """

        self.gui.m_buttonClear.Enable(False)
        self.gui.m_buttonSaveSurface.Enable(False)
        self.gui.m_buttonUpdate.Enable(True)

        self._app_states[self._current_image_index]._disconnected = True

        try:
            self.GetMicroView().pane3D.DisconnectActorFactory(
                self._app_states[self._current_image_index].GetFactory())
        except ValueError:
            logging.exception("IsoSurfaceDisplay")

        self.GetMicroView().pane3D.Modified()
        self.Render()
        self._app_states[self._current_image_index].SetFactory(None)

        self.gui.m_staticTextArea.SetLabel('')
        self.gui.m_staticTextVolume.SetLabel('')
        self.gui.m_staticTextPolygonCount.SetLabel('')
        self.gui.m_staticTextRegionCount.SetLabel('')

    def _BuildPipeline(self):
        """_BuildPipeline - Builds the visualization pipeline"""

        image = component.getUtility(ICurrentImage)

        # update image (VTK-6 compatible)
        image.Update()

        # image reslice object
        reslice = vtk.vtkImageReslice()
        reslice.SetInterpolationModeToCubic()
        reslice.ReleaseDataFlagOn()
        reslice.SetInputConnection(image.GetOutputPort())
        if self._transform:
            reslice.SetTransform(self._transform)

        # get extents, spacings, etc
        in_extent = image.GetExtent()
        in_spacing = image.GetSpacing()
        in_origin = image.GetOrigin()

        # get stencil data
        stencil_data = image.GetStencilData()

        # Set image resample factor
        f = self.gui.m_sliderSurfaceQuality.GetValue() / 100.0
        if f == 0.0:
            f = 0.001

        # Set surface decimation factor
        decf = self.gui.m_sliderDecimationFactor.GetValue() / 100.0

        # Enable/Disable stencil usage
        if self.gui.m_checkBoxClipping.GetValue() is True and stencil_data:
            if vtk.vtkVersion().GetVTKMajorVersion() > 5:
                reslice.SetStencilData(stencil_data)
            else:
                reslice.SetStencil(stencil_data)
            reslice.SetBackgroundLevel(image.GetScalarRange()[0])
            ext = stencil_data.GetExtent()
        else:
            ext = in_extent
            if vtk.vtkVersion().GetVTKMajorVersion() > 5:
                reslice.SetStencilData(None)
            else:
                reslice.SetStencil(None)

        # expand extent slightly - account for downsampling later too
        fudge = int(math.ceil(1.0 / f))
        ext = [ext[0] - fudge, ext[1] + fudge, ext[
            2] - fudge, ext[3] + fudge, ext[4] - fudge, ext[5] + fudge]

        reslice.SetOutputExtent(ext)

        # set default origin/spacing -- these two lines work...
        reslice.SetOutputSpacing(in_spacing)
        reslice.SetOutputOrigin(in_origin)

        # do we need to downsample the image?
        if (f < 1.0):
            resample = vtk.vtkImageResample()
            resample.SetInputConnection(reslice.GetOutputPort())
            resample.ReleaseDataFlagOn()
            for i in range(3):
                resample.SetAxisMagnificationFactor(i, f)
            obj = resample
        else:
            obj = reslice

        # do we need to smooth the image?
        if (self.gui.m_checkBoxImageSmoothing.GetValue() == True):
            smooth = vtk.vtkImageGaussianSmooth()
            smooth.SetStandardDeviation(1.0)
            smooth.ReleaseDataFlagOn()
            smooth.SetInputConnection(obj.GetOutputPort())
            obj = smooth

        clip = vtk.vtkImageClip()
        clip.SetInputConnection(obj.GetOutputPort())

        # setup contour filter
        cf = vtk.vtkMarchingCubes()
        cf.SetNumberOfContours(1)
        val = float(self.gui.m_textCtrlImageThreshold.GetValue())
        cf.SetValue(0, val)
        cf.SetComputeScalars(0)
        cf.SetComputeNormals(0)
        cf.SetInputConnection(clip.GetOutputPort())

        # decimate surface
        decimate = vtk.vtkDecimatePro()
        decimate.SetInputConnection(cf.GetOutputPort())
        decimate.PreserveTopologyOn()
        decimate.SetTargetReduction(decf)

        # To cut down on memory consumption, we use the clip object
        # to process the image a chunk at a time.  By default we
        # use 20 chunks -- but if the chunks are too small, we'll adjust this
        # number

        clip.UpdateInformation()
        ext = clip.GetInput().GetExtent()

        # main processing loop
        with wx.BusyCursor():
            event.notify(ProgressEvent("Generating surface...", 0.0))
            clip.SetOutputWholeExtent(ext[0], ext[
                                      1], ext[2], ext[3], ext[4], ext[5])
            decimate.Update()
            event.notify(ProgressEvent("Generating surface...", 1.0))

        # Create the rendered Geometry
        if not self._app_states[self._current_image_index].GetFactory():
            self._app_states[
                self._current_image_index].SetFactory(vtkAtamai.SurfaceObjectFactory.SurfaceObjectFactory())
            self._app_states[self._current_image_index].GetFactory().SetInputConnection(
                decimate.GetOutputPort())
            self._app_states[self._current_image_index].GetFactory().SetBackfaceProperty(
                self._app_states[self._current_image_index].GetFactory().GetProperty())
            self._app_states[
                self._current_image_index].GetFactory().NormalGenerationOn()
        self.SetSurfaceColor()

        self.GetMicroView().pane3D.ConnectActorFactory(
            self._app_states[self._current_image_index].GetFactory())
        self._app_states[self._current_image_index]._disconnected = False

        # Update math values
        self.UpdateMathValues()

    def CreateGUI(self):

        # create a sizer for root widget
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self._Dialog.SetSizer(self.sizer)
        self.gui = IsosurfaceGUIC.IsosurfaceGUIC(self._Dialog)

        # Bind events
        self.gui.m_textCtrlImageThreshold.Bind(
            wx.EVT_TEXT, self.onThresholdChanged)
        self.gui.m_checkBoxClipping.Bind(
            wx.EVT_CHECKBOX, self.onClipSurfaceChanged)
        self.gui.m_checkBoxImageSmoothing.Bind(
            wx.EVT_CHECKBOX, self.onEnableSmoothingChanged)
        self.gui.m_sliderSurfaceQuality.Bind(
            wx.EVT_SCROLL_CHANGED, self.SetResizeFactor)
        self.gui.m_sliderDecimationFactor.Bind(
            wx.EVT_SCROLL_CHANGED, self.SetDecimationFactor)
        self.gui.m_colourPicker.Bind(
            wx.EVT_COLOURPICKER_CHANGED, self.GetSurfaceColor)
        self.gui.m_buttonClear.Bind(
            wx.EVT_BUTTON, lambda evt, s=self: s.HideGeometry(0))
        self.gui.m_buttonSaveSurface.Bind(
            wx.EVT_BUTTON, lambda evt, s=self: s.SaveGeometry())
        self.gui.m_buttonUpdate.Bind(wx.EVT_BUTTON, self.UpdateGeometry)

    def OnPluginClose(self):

        for num in self._app_states:

            factory = self._app_states[num].GetFactory()
            if factory:
                orthoView = component.getUtility(
                    IOrthoView, 'OrthoView-%d' % (num + 1))
                orthoView.renderPanes[0].DisconnectActorFactory(factory)
            self._app_states[num].SetFactory(None)

        # unregister our zope handlers
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.onModelModifiedEvent)
        gsm.unregisterHandler(self.onROIEnabledEvent)
        gsm.unregisterHandler(self.OnImageChangeEvent)
        gsm.unregisterHandler(self.OnNoImagesLoadedEvent)
        gsm.unregisterHandler(self.OnCurrentImageClosingEvent)

    @component.adapter(ROIModelModifiedEvent)
    def onModelModifiedEvent(self, evt):

        # A current ROI object has changed - enable 'Update' button
        self.gui.m_buttonUpdate.Enable()

    @component.adapter(ROIEnabledEvent)
    def onROIEnabledEvent(self, evt):
        if (self.gui.m_checkBoxClipping.GetValue() == True):
            self.gui.m_buttonSaveSurface.Enable(False)
            self.gui.m_buttonUpdate.Enable(True)

##########################################################################


def createPlugin(panel):
    return IsoSurfaceDisplay(panel)
