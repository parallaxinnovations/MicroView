# =========================================================================
#
# Copyright (c) 2011-2015 Parallax Innovations Inc
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

"""
BasePlotWindow is the base class for plotting graphs (lines and histograms).

It is inherited and modified by various data plotters.
"""

import collections
import logging
import math
import sys
import os
import numpy as np
import wx
import vtk

from zope import component, event

import datetime

import matplotlib
import matplotlib.font_manager  # For Ubuntu 14.04
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigCanvas
import pylab

import vtkEVS.EVSFileDialog as EVSFileDialog

# imported to get PACKAGE_VERSION info
from PI.visualization.MicroView import *
from PI.visualization.MicroView.events import PlotWindowCursorPosition, \
    BinSizeModifiedEvent, CurrentImageChangeEvent, \
    HistogramClosedEvent, OrthoPlanesRemoveInputEvent, \
    HistogramIsActiveROIEvent, AutoThresholdCommandEvent, HistogramSelectionModifiedEvent

from PI.visualization.MicroView.interfaces import IMicroViewMainFrame

from PI.visualization.common import MicroViewSettings
from PI.visualization.MicroView._MicroView import *
import StockItems
import VTKPlotWindowGUI
import PlotInfoGUIC


def bind(actor, evt, action, **kw):
    actor.Bind(evt, action, **kw)


class MicroViewNavigationToolbar(NavigationToolbar2WxAgg, wx.ToolBar):

    def __init__(self, canvas):
        NavigationToolbar2WxAgg.__init__(self, canvas)

        self.bCursorCanBeDisplayed = True
        self.bCursorDisplayEnabled = True

        # turn on zoom immediately
        self.ToggleTool(self._NTB2_ZOOM, True)
        self.zoom()

        # enable display of nearest data point
        self.ToggleTool(self.VIEW_NEARESTDATA, True)

        # disable autothreshold
        self.EnableTool(self.AUTO_THRESHOLD, False)

        # turn off highlighting
        self.SetHighlightEnabled(False)
        self.SetHighlightVisible(False)

    def GetHighlightEnabled(self):
        return self.GetToolEnabled(self.SHOW_HIGHLIGHT)

    def SetHighlightEnabled(self, enabled):
        self.EnableTool(self.SHOW_HIGHLIGHT, bool(enabled))

    def GetHighlightVisible(self):
        return self.GetToolState(self.SHOW_HIGHLIGHT)

    def SetHighlightVisible(self, v):
        self.ToggleTool(self.SHOW_HIGHLIGHT, bool(v))

    def _init_toolbar(self):

        self._parent = self.canvas.GetParent()

        self.wx_ids = {}

        _NTB2_HOME = wx.NewId()
        self._NTB2_BACK = wx.NewId()
        self._NTB2_FORWARD = wx.NewId()
        self._NTB2_PAN = wx.NewId()
        self._NTB2_ZOOM = wx.NewId()
        _NTB2_SUBPLOT = wx.NewId()

        self.wx_ids['Back'] = self._NTB2_BACK
        self.wx_ids['Forward'] = self._NTB2_FORWARD
        self.wx_ids['Pan'] = self._NTB2_PAN
        self.wx_ids['Zoom'] = self._NTB2_ZOOM

        # Add MicroView-specific tools
        stockicons = StockItems.StockIconFactory()

        self.SAVE_DATA = wx.NewId()
        self.SAVE_SNAPSHOT = wx.NewId()
        self.VIEW_SYMBOLS = wx.NewId()
        self.VIEW_NEARESTDATA = wx.NewId()
        self.AUTO_THRESHOLD = wx.NewId()
        self.SHOW_HIGHLIGHT = wx.NewId()
        self.COPY_HIGHLIGHT = wx.NewId()
        self.SELECT_ROI = wx.NewId()

        dummy_bitmap = wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS)
        icon_size = dummy_bitmap.GetWidth()
        self.SetToolBitmapSize(wx.Size(icon_size, icon_size))
        self.AddSimpleTool(self.SAVE_DATA, stockicons.getToolbarBitmap(
            wx.ART_FILE_SAVE_AS), 'Save data', 'Save data to file')
        self.AddSimpleTool(self.SAVE_SNAPSHOT, stockicons.getToolbarBitmap(
            'glyphicons_011_camera'), 'Save snapshot', 'Save snapshot')
        self.AddCheckTool(self.VIEW_SYMBOLS, stockicons.getToolbarBitmap(
            'office-chart-line-stacked-with-symbols'), shortHelp='Show symbols', longHelp='Show symbols')
        self.AddCheckTool(self.VIEW_NEARESTDATA, stockicons.getToolbarBitmap(
            'office-chart-line-stacked-with-nearest-data'), shortHelp='View nearest datapoint',
            longHelp='View nearest datapoint')
        self.AddSimpleTool(
            self.AUTO_THRESHOLD, stockicons.getToolbarBitmap(
                'autothreshold-wizard-24'),
            'Automatically select threshold from histogram', 'Automatically select threshold from histogram')
        self.AddCheckTool(self.SHOW_HIGHLIGHT, stockicons.getToolbarBitmap(
            'highlight'), shortHelp='Show Highlight', longHelp='Show Highlight')
        self.AddSimpleTool(self.COPY_HIGHLIGHT, stockicons.getToolbarBitmap(
            'copy'), 'Copy Highlight', 'Copy Highlight')

        # The following tools are copied from the original matplotlib code

        self.AddSimpleTool(_NTB2_HOME, stockicons.getToolbarBitmap('glyphicons_020_home'),
                           'Home', 'Reset original view')
        self.AddSimpleTool(self._NTB2_BACK, stockicons.getToolbarBitmap('glyphicons_170_step_backward'),
                           'Back', 'Back navigation view')
        self.AddSimpleTool(self._NTB2_FORWARD, stockicons.getToolbarBitmap('glyphicons_178_step_forward'),
                           'Forward', 'Forward navigation view')
        # todo: get new bitmap
        self.AddCheckTool(self._NTB2_PAN, stockicons.getToolbarBitmap('glyphicons_186_move'),
                          shortHelp='Pan',
                          longHelp='Pan with left, zoom with right')
        self.AddCheckTool(self._NTB2_ZOOM, stockicons.getToolbarBitmap('glyphicons_093_crop'),
                          shortHelp='Zoom', longHelp='Zoom to rectangle')
        self.AddCheckTool(self.SELECT_ROI, stockicons.getToolbarBitmap(
            'select_histogram_region'),
            longHelp='Select Histogram Region',
            shortHelp='Select Region')

        bind(self, wx.EVT_TOOL, self.home, id=_NTB2_HOME)
        bind(self, wx.EVT_TOOL, self.forward, id=self._NTB2_FORWARD)
        bind(self, wx.EVT_TOOL, self.back, id=self._NTB2_BACK)
        bind(self, wx.EVT_TOOL, self.zoom, id=self._NTB2_ZOOM)
        bind(self, wx.EVT_TOOL, self.pan, id=self._NTB2_PAN)

        self.Realize()

    def zoom(self, *args):
        self.ToggleTool(self.SELECT_ROI, False)
        NavigationToolbar2WxAgg.zoom(self, *args)

    def pan(self, *args):
        self.ToggleTool(self.SELECT_ROI, False)
        NavigationToolbar2WxAgg.pan(self, *args)

    def press_zoom(self, evt):
        """the press mouse button in zoom to rect mode callback"""

        if evt.button == 1:
            NavigationToolbar2WxAgg.press_zoom(self, evt)
        elif evt.button == 3:
            self.back(evt)

    def press(self, evt):
        self.bCursorCanBeDisplayed = (evt.button != 1)
        NavigationToolbar2WxAgg.press(self, evt)

    def release(self, evt):
        self.bCursorCanBeDisplayed = True
        NavigationToolbar2WxAgg.release(self, evt)

    def ShouldIShowCursor(self):
        return (self.bCursorCanBeDisplayed and self.bCursorDisplayEnabled)

    def ToggleShowCursor(self):
        self.bCursorDisplayEnabled = not self.bCursorDisplayEnabled


class BasePlotWindow(VTKPlotWindowGUI.VTKPlotWindowGUI):

    def CreateLowerPanel(self):
        return PlotInfoGUIC.PlotInfoGUIC(self)

    def EnableToolbar(self):
        self.toolbar.EnableTool(self.toolbar.AUTO_THRESHOLD, False)
        self.toolbar.EnableTool(self.toolbar.VIEW_SYMBOLS, True)
        self.toolbar.EnableTool(self.toolbar.COPY_HIGHLIGHT, False)
        self.toolbar.EnableTool(self.toolbar.SHOW_HIGHLIGHT, False)

    def __del__(self):
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.OnImageChangeEvent)

    def __init__(self, parent, *args, **kw):

        VTKPlotWindowGUI.VTKPlotWindowGUI.__init__(self, parent)

        # ------------------------------------------------------------------------------------
        # Set up some zope event handlers
        # ------------------------------------------------------------------------------------
        component.provideHandler(self.OnImageChangeEvent)

        self._voxel_volume_set = False
        self._voxel_volume = 1.0
        if ('bar' in kw):
            self._usebar = True
        else:
            self._usebar = False

        self._scale = 1.0
        self._unit = kw.get('units', 'pixels')

        self._dragging = 0                       # is this needed?
        self._x0 = None
        self._y0 = None
        self._x1 = None
        self._y1 = None
        self._select_x0 = None
        self._select_x1 = None
        self._select_i0 = None
        self._select_i1 = None
        self.xdata = []
        self.ydata = []
        self._line = [None, None]
        self._liney = None
        self._title = "This is the title"
        self.filename = ''
        self._xlabel = ""
        self._ylabel = ""
        self._usesymbols = False
        # indicates whether nearest data point should be highlighted or not
        self._use_highlight_data = True
        self._isROI = False
        self._linelength = None
        self._inputname = ""
        self._highlight_visible = False
        self.__shortname__ = 'VTKPlot'
        self._otsu_threshold = None
        self._otsu_marker = None

        self._unit_scalings = {'pixels': 1.0, 'mm': 1.0, 'wavelength': 1.0}
        self.plot_data = None
        self.legend = None

        if ('scale' in kw):
            self._scale = float(kw['scale'])
        if ('title' in kw):
            self._title = kw['title']
        if ('xlabel' in kw):
            self._xlabel = kw['xlabel']
        if ('ylabel' in kw):
            self._ylabel = kw['ylabel']

        # get icon factory
        self._stockicons = StockItems.StockIconFactory()

        # create info panel - it'll depend on whether this is a line plot or
        # histogram window
        self.lower_panel = self.CreateLowerPanel()
        self.GetSizer().Add(self.lower_panel, 0, wx.EXPAND, 5)

        # create a matplotlib panel
        self.dpi = 100
        self.fig = Figure((3.0, 3.0), dpi=self.dpi)
#        self.fig.subplots_adjust(left=0.07, right=0.97, bottom=0.08, top=0.95)
        self.fig.subplots_adjust(left=0.0, right=1, bottom=0.0, top=1)

        self.axes = self.fig.add_subplot(111)

        # default labels
        self.axes.set_title(self._title, size=10)
        self.axes.set_ylabel(self._ylabel, size=8)

        self.line_tool = None    # A red, horizontal line tool
        self.end_markers = None  # Markers that go at the end of each line
        self.data_markers = None  # Marks that indicate nearest data point

        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        sizer = wx.BoxSizer(wx.VERTICAL)

        # create canvas for plot widget
        self.canvas = FigCanvas(self.m_panelMatplotPanel, -1, self.fig)

        self.m_panelMatplotPanel.SetSizer(sizer)
        self.m_panelMatplotPanel.Fit()

        # activate interactive navigation
        self.toolbar = MicroViewNavigationToolbar(self.canvas)
        self.toolbar.Realize()

        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.canvas.GetSizeTuple()
        self.toolbar.SetSize(wx.Size(fw, th))

        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        self.toolbar.update()

        # adjust toolbar
        self.EnableToolbar()

        # wire up events
        self.canvas.mpl_connect('motion_notify_event', self.MouseMoveEvent)
        self.canvas.mpl_connect('key_press_event', self.KeyPressEvent)
        self.canvas.mpl_connect('figure_leave_event', self.LeaveCanvasEvent)

        # wire up events here
        self.toolbar.Bind(
            wx.EVT_TOOL, self.SaveData, id=self.toolbar.SAVE_DATA)
        self.toolbar.Bind(
            wx.EVT_TOOL, self.SaveSnapShot, id=self.toolbar.SAVE_SNAPSHOT)
        self.toolbar.Bind(
            wx.EVT_TOOL, self.symbolsOnOff, id=self.toolbar.VIEW_SYMBOLS)
       # self.toolbar.Bind(wx.EVT_TOOL, self.Reset, id=self.toolbar.RESET_VIEW)
        self.toolbar.Bind(
            wx.EVT_TOOL, self.AutoThreshold, id=self.toolbar.AUTO_THRESHOLD)
        self.toolbar.Bind(
            wx.EVT_TOOL, self.onCopyHighlightToolbarButton, id=self.toolbar.COPY_HIGHLIGHT)
        self.toolbar.Bind(
            wx.EVT_TOOL, self.onShowHighlightToolbarToogle, id=self.toolbar.SHOW_HIGHLIGHT)
        self.toolbar.Bind(
            wx.EVT_TOOL, self.NearestDataSymbolsOnOff, id=self.toolbar.VIEW_NEARESTDATA)
        self.toolbar.Bind(
            wx.EVT_TOOL, self.select_roi, id=self.toolbar.SELECT_ROI)

        # listen to size events
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self._plotData = None

        # This table is used to make the input invisible
        self._wlTableInvisible = vtk.vtkWindowLevelLookupTable()
        self._wlTableInvisible.SetSaturationRange(0, 0)
        self._wlTableInvisible.SetHueRange(0, 0)
        self._wlTableInvisible.SetValueRange(0, 1)
        self._wlTableInvisible.SetNumberOfColors(2)
        self._wlTableInvisible.SetTableValue(0, 0.0, 0.0, 0.0, 0.0)
        self._wlTableInvisible.SetTableValue(1, 0.0, 0.0, 0.0, 0.0)
        self._wlTableInvisible.Build()

        # Invoke an event to react to currently loaded image
        mv = component.getUtility(IMicroViewMainFrame)
        current_image = mv.GetCurrentImageIndex()
        number_images_displayed = mv.GetNumberOfImagesCurrentlyLoaded()
        title = mv.GetCurrentImageTitle()
        self.OnImageChangeEvent(CurrentImageChangeEvent(
            current_image, number_images_displayed, title))

    def OnPaint(self, evt):

        s = self.GetClientSize()

        try:
            self.fig.tight_layout(pad=0.25)
        except ValueError:
            # turn off legend
            if self.legend:
                self.legend.set_visible(False)
            return

        if (s[0] < 350) or (s[1] < 350):
            # turn off legend
            if self.legend:
                self.legend.set_visible(False)
        else:
            if self.legend:
                self.legend.set_visible(True)

        self.canvas.draw()

    def ClearPlot(self):

        self.xdata = np.array([])
        self.ydata = np.array([])

        if self.plot_data:
            for p in self.plot_data:
                p.remove()
        if self.end_markers:
            self.end_markers.remove()
        if self.data_markers:
            self.data_markers.remove()

        self.HideOtsuThreshold()
        self.plot_data = self.end_markers = self.data_markers = None

        # redraw canvas
        self.canvas.draw()

    def SetFileName(self, filename):
        self.filename = filename

    def update_axes_bounds(self):

        xmax = round(self.xdata.max(), 0) + 1
        xmin = 0

        ymin = round(self.ydata.min(), 0) - 1
        ymax = round(self.ydata.max(), 0) + 1

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)

    def update_colour_names(self):

        numC = 1
        if len(self.ydata.shape) > 1:
            numC = self.ydata.shape[-1]
            self.colours = ['red', 'green', 'blue', 'black']
        else:
            self.ydata.shape = (self.ydata.shape[0], 1)
            self.colours = ['black']

    def update_channel_names(self):

        numC = 1
        if len(self.ydata.shape) > 1:
            numC = self.ydata.shape[-1]
            self.channel_names = ['red', 'green', 'blue', 'opacity']
        else:
            self.ydata.shape = (self.ydata.shape[0], 1)
            self.channel_names = ['chan. 1']

    def draw_plot(self):
        """ Redraws the plot"""

        # set axis range
        self.update_axes_bounds()
        self.update_colour_names()
        self.update_channel_names()

        self.axes.grid(True, color='gray')
        pylab.setp(self.axes.get_xticklabels(), visible=True)

        numC = 1
        if len(self.ydata.shape) > 1:
            numC = self.ydata.shape[-1]
        else:
            self.ydata.shape = (self.ydata.shape[0], 1)

        self.file_label = '# Pos. (%s)\t' % self._unit + \
            (numC - 1) * '%s\t' + '%s' + '\n#'
        self.file_label = self.file_label % tuple(self.channel_names[:numC])

        args = []
        marker_x = []
        marker_y = []
        marker_c = []

        for i in range(numC):
            args.append(self.xdata)
            args.append(self.ydata[:, i])
            args.append(self.colours[i])
            marker_x.append(self.xdata[0])
            marker_y.append(self.ydata[0, i])
            marker_c.append('b')
            marker_x.append(self.xdata[-1])
            marker_y.append(self.ydata[-1, i])
            marker_c.append('g')

            if self.plot_data:
                if len(self.plot_data) != numC:
                    for p in self.plot_data:
                        p.remove()
                    self.plot_data = None

            if self.plot_data is None:
                self.plot_data = self.axes.plot(*args, linewidth=1)
                self.legend = self.axes.legend(
                    tuple(self.channel_names[0:numC]))
                pylab.setp(self.legend.get_texts(), fontsize='x-small')
            else:
                for i in range(numC):
                    self.plot_data[i].set_xdata(args[i * 3 + 0])
                    self.plot_data[i].set_ydata(args[i * 3 + 1])

        # draw end markers
        if self.end_markers:
            self.end_markers.remove()
        self.end_markers = self.axes.scatter(
            marker_x, marker_y, c=tuple(marker_c), linewidths=0, zorder=3)

    @component.adapter(CurrentImageChangeEvent)
    def OnImageChangeEvent(self, evt):

        # I only care about the input image number - I need to make a context switch here to account
        # for multiple ROIs
        self._current_index = evt.GetCurrentImageIndex()

    def showThresholdMarker(self, threshold):

        dlg = wx.MessageDialog(self, 'threshold:' + ' %0.1f' % (
            threshold), 'Auto-Threshold', wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        if self._usebar is True:
            self._otsu_threshold = threshold
            # draw Otsu threshold
            if self._otsu_marker:
                self._otsu_marker.remove()
            self._otsu_marker = self.axes.scatter([self._otsu_threshold], [-1000], c='r',
                                                  marker='^', linewidths=0, zorder=3)

    def GetMouseMoveLabelFormat(self):
        return 'x=%11.5f, y=%s'

    def MouseMoveEvent(self, evt):

        refresh_required = False

        # erase current data markers
        if self.data_markers:
            self.data_markers.remove()
            self.data_markers = None
            refresh_required = True

        # determine nearest data values and update wx gui
        if evt.xdata and len(self.xdata) > 0:
            index = abs(self.xdata - evt.xdata).argmin()
            val = self.ydata[index, :]
            marker_x = [self.xdata[index]] * len(val)
            marker_y = val
            marker_c = ['red'] * len(val)
            if len(val) == 1:
                val = val[0]
            else:
                val = tuple(val)

            # update line/histogram
            if evt.button == 2 or (evt.button == 1 and self.toolbar._active == 'SELECT_ROI'):
                self.setLinePoint(1, evt)

            fmt = self.GetMouseMoveLabelFormat()

            self.lower_panel.m_staticTextNearestDataValue.SetLabel(
                fmt % (self.xdata[index], str(val)))

            # optionally draw highlighted data
            if self._use_highlight_data and self.toolbar.ShouldIShowCursor():
                # draw data markers
                self.data_markers = self.axes.scatter(
                    marker_x, marker_y, c=marker_c, linewidths=0, zorder=4)
                refresh_required = True

        else:
            self.lower_panel.m_staticTextNearestDataValue.SetLabel('')

        if refresh_required:
            self.canvas.draw()

        # update wx user interface
        self.reportPosition([evt.xdata, evt.ydata])
        self.reportLineLength()

    def SetSelectionRange(self, x0, x1):
        self._select_x0 = x0
        self._select_x1 = x1
        self.NotifyHistoHighlightChange()

    def GetSelectionRange(self):
        return self._select_x0, self._select_x1

    def KeyPressEvent(self, evt):

        k = evt.key

        if k == '1':
            self.setFirstLinePoint(evt)
        elif k == '2':
            self.setSecondLinePoint(evt)
        elif k == 'r':
            self.Reset()
        elif k == 'y':
            self.removeMeasurementLine()

    def LeaveCanvasEvent(self, evt):
        # remove marker
        if self.data_markers:
            self.data_markers.remove()
            self.data_markers = None
        self.canvas.draw()

    def SetBinSize(self, evt=None, binsize=None):
        if binsize is None:
            binsize = float(self.binVar.get())
        else:
            self.binVar.set(str(binsize))
        # generate an event
        event.notify(BinSizeModifiedEvent(binsize))

    def Delete(self):
        self.Hide()

    def Hide(self, evt=None):

        self.removeMeasurementLine()
        if self._usebar is True:
            if self._isROI is False:
                self.HideHighlight()
            self.HideOtsuThreshold()

    def HideHighlight(self, image_index=None):

        if self._isROI is True:
            self._isROI = False
            event.notify(HistogramClosedEvent())

        if self._usebar is True and self.GetHighlightVisible() is True:
            self.SetHighlightVisible(False)

        self.NotifyHistoHighlightChange()
        self.OrthoPlanesRemoveInput('histogram')

    def HideOtsuThreshold(self):
        if self._otsu_marker:
            self._otsu_marker.remove()
            self._otsu_marker = None

    def OrthoPlanesRemoveInput(self, name):
        event.notify(OrthoPlanesRemoveInputEvent(name))

    def Reset(self, e=None):

        self.removeMeasurementLine()

        # this might need to be reworked
        self.lower_panel.m_staticTextLineLength.SetLabel('')

    def GetCurrentDirectory(self):

        # determine working directory
        curr_dir = cwd = os.getcwd()
        config = MicroViewSettings.MicroViewSettings.getObject()

        # over-ride with system-wide directory
        try:
            curr_dir = config.GlobalCurrentDirectory or curr_dir
        except:
            config.GlobalCurrentDirectory = curr_dir

        try:
            curr_dir = config.CurrentSnapshotDirectory or curr_dir
        except:
            config.CurrentSnapshotDirectory = curr_dir

        return curr_dir

    def SaveCurrentDirectory(self, curr_dir):
        config = MicroViewSettings.MicroViewSettings.getObject()
        config.CurrentSnapshotDirectory = curr_dir

    def GetwlTableInvisible(self):
        return self._wlTableInvisible

    def CreateHighlightLookupTable(self):

        # Create colour table for histogram overlay
        table = vtk.vtkWindowLevelLookupTable()
        table.SetSaturationRange(0, 0)
        table.SetHueRange(0, 0)
        table.SetValueRange(0, 1)
        table.SetLevel(0.5)
        table.SetWindow(1.0)
        table.SetNumberOfColors(2)
        table.SetTableValue(0, 0.0, 0.0, 0.0, 0.0)
        table.SetTableValue(1, 1.0, 0.0, 0.0, 1.0)
        table.Build()
        return table

    def GetInputName(self):
        return self._inputname

    def SetInputName(self, name):
        self._inputname = name

    def NotifyHistoHighlightChange(self):
        event.notify(HistogramSelectionModifiedEvent(
            self._select_x0, self._select_x1, self.GetHighlightVisible()))

    def SelectionToROI(self):
        """Assert ourselves as the owner of the ROI object for this image"""

        # This next line is increasingly not accurate - need something better
        self._isROI = True

        # send out a notification to allow any ROI visuals to modify themselves
        event.notify(HistogramIsActiveROIEvent())

    def GetROIType(self, index):
        return 'custom'

    def AutoThreshold(self, evt):
        """Force an autothreshold calculation

        This routine posts an AutoThresholdCommandEvent command in order to request a new calculation of an
        optimal Otsu threshold.
        """
        event.notify(AutoThresholdCommandEvent())

    def SetInput(self, inp):

        if self.plot_data:
            for p in self.plot_data:
                p.remove()
            self.plot_data = None

        if self.data_markers:
            self.data_markers.remove()
            self.data_markers = None

        self._plotData = inp

        # bit of a bad name -- this next line actually resets all inputs, then
        # adds self._plotData
        self.SetHighlightVisible(False)

    def SaveSnapShot(self, evt):
        # Fetch the required filename and file type.
        filetypes, exts, filter_index = self.canvas._get_imagesave_wildcards()
        default_file = "image." + self.canvas.get_default_filetype()
        dlg = wx.FileDialog(self, "Save snapshot to file", "", default_file,
                            filetypes,
                            wx.SAVE | wx.OVERWRITE_PROMPT)
        dlg.SetFilterIndex(filter_index)
        if dlg.ShowModal() == wx.ID_OK:
            dirname = dlg.GetDirectory()
            filename = dlg.GetFilename()
            format = exts[dlg.GetFilterIndex()]
            basename, ext = os.path.splitext(filename)
            if ext.startswith('.'):
                ext = ext[1:]
            if ext in ('svg', 'pdf', 'ps', 'eps', 'png') and format != ext:
                # looks like they forgot to set the image type drop
                # down, going with the extension.
                dlg = wx.MessageDialog(self, 'extension %s did not match the selected image type %s; going with %s' %
                                             (ext, format, ext), 'Warning', wx.OK | wx.ICON_WARNING)
                dlg.ShowModal()
                dlg.Destroy()
                format = ext
            try:
                self.canvas.print_figure(
                    os.path.join(dirname, filename), format=format)
            except Exception, e:
                logging.error(e.message)

    def SaveData(self, e=None, filename=""):
        """Save line/histogram data to a text file"""
        ft = collections.OrderedDict([])
        ft["text files"] = ["*.txt"]

        curr_dir = self.GetCurrentDirectory()

        if filename == "":
            filename = EVSFileDialog.asksaveasfilename(
                message='Save Line Data', filetypes=ft, defaultdir=curr_dir, defaultextension='.txt')

        if not filename:
            return

        self.SaveCurrentDirectory(os.path.dirname(filename))

        _file = open(filename, 'wt')

        # write out a header
        _file.write('#\n')
        _file.write('# Creation Date: %s\n' %
                    datetime.datetime.now().isoformat())

        if self.filename:
            filename = self.filename.encode(
                sys.getfilesystemencoding() or 'UTF-8')
        else:
            filename = '(unknown)'

        _file.write('# Image filename: %s\n' % filename)
        _file.write('# MicroView Software Version: %s\n' % PACKAGE_VERSION)
        _file.write('# MicroView Software SHA1: %s\n' % PACKAGE_SHA1)
        _file.write('#\n')

        n = len(self.xdata)
        numC = self.ydata.shape[-1]
        _format = '%f\t' + (numC - 1) * '%f\t' + '%f\n'

        _file.write(self.file_label + '\n')

        for xval, yval in zip(self.xdata, self.ydata):
            # take care -- yval could be from a multichannel image
            l = [xval]
            l.extend(yval)
            _file.write(_format % tuple(l))

        _file.close()

    def PlotData(self):

            # Check that we haven`t gotten here early - EVT_SHOW events can trigger
            # early attempts to plot data before we are ready
        if self._plotData is None:
            return

        # default plotter assumes data is in a 2D numpy array
        self.xdata = self._plotData[:, 0]
        self.ydata = self._plotData[:, 1]
        self.draw_plot()
        self.canvas.draw()

    def symbolsOnOff(self, e=None):
        self._usesymbols = not self._usesymbols

        if self._usesymbols:
            pylab.setp(self.plot_data, marker='o')
        else:
            pylab.setp(self.plot_data, marker='')

        self.canvas.draw()

    def removeMeasurementLine(self, redraw=True):
        """removes a visible measurement rule from the screen"""

        self._line[0] = self._line[1] = None
        self._linelength = None

        if self.line_tool:
            self.line_tool.remove()
            if redraw:
                self.canvas.draw()
            self.line_tool = None

    def setLinePoint(self, index, evt):

        if evt.xdata is None:
            return

        # if this is a histogram, we use nearest data values
        if self._usebar is True:
            idx = abs(self.xdata - evt.xdata).argmin()
            evt.xdata = self.xdata[idx]
            if index == 0:
                self._select_i0 = idx
                self._select_x0 = evt.xdata
            else:
                self._select_i1 = idx
                self._select_x1 = evt.xdata

        (self._line[index], self._liney) = evt.xdata, evt.ydata

        # draw line or histogram highlight
        if self._usebar is True:
            i0 = min(self._select_i0, self._select_i1)
            i1 = max(self._select_i0, self._select_i1)
            if i0 is not None and i1 is not None:
                if self.line_tool is None:
                    self.line_tool, = self.axes.plot(self.xdata[
                                                     i0:i1], self.ydata[i0:i1], linestyle='-', color='red')
                else:
                    self.line_tool.set_data(
                        self.xdata[i0:i1], self.ydata[i0:i1])
        else:

            if index == 0:
                x0 = self._line[0]
                x1 = self._line[1] or x0
            else:
                x1 = self._line[1]
                x0 = self._line[0] or x1

            if self.line_tool is None:
                self.line_tool, = self.axes.plot([x0, x1], [
                                                 self._liney, self._liney], linestyle='-', color='red', marker='|')
            else:
                self.line_tool.set_data([x0, x1], [self._liney, self._liney])

        self.canvas.draw()

        if self._line[0] and self._line[1]:
            if self._usebar is True:
                self.UpdateVolumeFractionText()
            else:
                self._linelength = abs(self._line[0] - self._line[1])
                self.reportLineLength()

    def setFirstLinePoint(self, evt=None):
        self.setLinePoint(0, evt)

    def setSecondLinePoint(self, evt=None):
        self.setLinePoint(1, evt)

    def SetUnitScalings(self, val):
        self._unit_scalings = val

    def getUnitLabel(self):
        """Returns the units label"""
        return self._unit

    def setUnitLabel(self, val):
        """Sets the units label on the measurement tool"""

        self._unit = val

        self._xlabel = self._unit
        self.axes.set_xlabel(self._unit, size=8)
        self.reportLineLength()

    def reportPosition(self, pos):

        # fire off position event
        event.notify(PlotWindowCursorPosition(pos[0], pos[1]))

    def reportLineLength(self):

        label2 = ''

        if self._linelength is not None:
            label2 = "%0.3f %s" % (self._linelength, self._unit)
        self.lower_panel.m_staticTextLineLength.SetLabel(label2)

    def UpdateVolumeFractionText(self):
        pass

    def onShowHighlightToolbarToogle(self, evt):
        self.SetHighlightVisible(bool(evt.GetInt()))

    def onCopyHighlightToolbarButton(self, evt):

        # user has clicked copy highlight button - the intention is to set the highlighted
        # image as the current ROI

        self.SelectionToROI()

    def SetHighlightVisible(self, v):
        self.toolbar.SetHighlightVisible(v)
        self.toolbar.EnableTool(self.toolbar.COPY_HIGHLIGHT, v)
        self.NotifyHistoHighlightChange()

    def GetHighlightVisible(self):
        return self.toolbar.GetHighlightVisible()

    def SetHighlightEnabled(self, v):
        return self.toolbar.SetHighlightEnabled(v)

    def GetHighlightEnabled(self):
        return self.toolbar.GetHighlightEnabled()

    def NearestDataSymbolsOnOff(self, evt):
        self.toolbar.ToggleShowCursor()

    def select_roi(self, *args):
        """Activate select roi mode"""

        self.toolbar.ToggleTool(self.toolbar.wx_ids['Zoom'], False)
        self.toolbar.ToggleTool(self.toolbar.wx_ids['Pan'], False)

        if self.toolbar._active == 'SELECT_ROI':
            self.toolbar._active = None
        else:
            self.toolbar._active = 'SELECT_ROI'

        if self.toolbar._idPress is not None:
            self.toolbar._idPress = self.toolbar.canvas.mpl_disconnect(
                self.toolbar._idPress)
            self.toolbar.mode = ''

        if self.toolbar._idRelease is not None:
            self.toolbar._idRelease = self.toolbar.canvas.mpl_disconnect(
                self.toolbar._idRelease)
            self.toolbar.mode = ''

        self.toolbar._idPress = self.toolbar.canvas.mpl_connect('button_press_event',
                                                                self.press_select_roi)
        self.toolbar._idRelease = self.toolbar.canvas.mpl_connect('button_release_event',
                                                                  self.release_select_roi)

    def press_select_roi(self, evt):
        if evt.button == 2 or (evt.button == 1 and self.isROISelectionActive()):
            self.setFirstLinePoint(evt)
            self.setSecondLinePoint(evt)

    def release_select_roi(self, evt):
        pass

    def isROISelectionActive(self):
        """Returns true if ROI selection mode is enabled"""
        return self.toolbar._active == 'SELECT_ROI'
