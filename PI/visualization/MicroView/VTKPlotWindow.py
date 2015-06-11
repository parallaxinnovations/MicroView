# =========================================================================
#
# Copyright (c) 2000-2008 GE Healthcare
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

#
# This file represents a derivative work by Parallax Innovations Inc.
#

"""
VTKPlotWindow is a class for plotting graphs (lines and histograms).
"""

import logging
import numpy
import wx
import pylab

from zope import event

import vtk
from vtk.util import numpy_support

from PI.visualization.MicroView.events import BinSizeModifiedEvent, \
    HistogramClosedEvent, AutoThresholdCommandEvent

from PI.visualization.MicroView._MicroView import *
import PlotInfoGUIC
import HistogramInfoGUIC
import BasePlotWindow


class VTKPlotWindow(BasePlotWindow.BasePlotWindow):

    def __init__(self, parent, *args, **kw):

        self._transform = vtk.vtkTransform()

        BasePlotWindow.BasePlotWindow.__init__(self, parent, *args, **kw)

        # wire up additional event handling
        self.canvas.mpl_connect(
            'button_press_event', self.MouseButtonPressEvent)
        self.canvas.mpl_connect(
            'button_release_event', self.MouseButtonReleaseEvent)

        if self._usebar:

            self.lower_panel.m_spinCtrlLower.Bind(
                wx.EVT_SPINCTRLDOUBLE, self.setFloatControlPoint)
            self.lower_panel.m_spinCtrlUpper.Bind(
                wx.EVT_SPINCTRLDOUBLE, self.setFloatControlPoint)

        self.lower_panel.SetAutoLayout(True)

    def CreateLowerPanel(self):

        if self._usebar is False:
            return PlotInfoGUIC.PlotInfoGUIC(self)
        else:
            return HistogramInfoGUIC.HistogramInfoGUIC(self)

    def EnableToolbar(self):
        if self._usebar is False:
            self.toolbar.EnableTool(self.toolbar.AUTO_THRESHOLD, False)
            self.toolbar.EnableTool(self.toolbar.VIEW_SYMBOLS, True)
            self.toolbar.EnableTool(self.toolbar.COPY_HIGHLIGHT, False)
            self.toolbar.EnableTool(self.toolbar.SHOW_HIGHLIGHT, False)
        else:
            self.toolbar.EnableTool(self.toolbar.AUTO_THRESHOLD, True)
            self.toolbar.EnableTool(self.toolbar.VIEW_SYMBOLS, False)
            self.toolbar.EnableTool(self.toolbar.COPY_HIGHLIGHT, False)
            self.toolbar.EnableTool(self.toolbar.SHOW_HIGHLIGHT, False)

    def GetMouseMoveLabelFormat(self):

        if self._usebar:
            return 'x=%0.2f, y=%s'
        else:
            return BasePlotWindow.BasePlotWindow.GetMouseMoveLabelFormat(self)

    def MouseButtonPressEvent(self, evt):

        # middle mouse button?
        if evt.button == 1 and (evt.button == 1 and self.isROISelectionActive()):
            self.toolbar.EnableTool(self.toolbar.SHOW_HIGHLIGHT, False)
        elif evt.button == 2:
            self.MiddleButtonPressEvent(evt)

    def MouseButtonReleaseEvent(self, evt):

        # middle mouse button?  region-select enabled?
        if evt.button == 2 or (evt.button == 1 and self.isROISelectionActive()):
            self.MiddleButtonReleaseEvent(evt)

    def MiddleButtonPressEvent(self, evt):

        self.toolbar.EnableTool(self.toolbar.SHOW_HIGHLIGHT, False)

        # Reset line data
        self._line[0] = self._line[1] = None
        # Set first point
        self.setLinePoint(0, evt)

    def MiddleButtonReleaseEvent(self, evt):

        if self._select_x0 > self._select_x1:
            t = self._select_x0
            self._select_x0 = self._select_x1
            self._select_x1 = t
        if self._select_x0 != self._select_x1:
            self.SetSelectionRange(self._select_x0, self._select_x1)
            self.toolbar.EnableTool(self.toolbar.SHOW_HIGHLIGHT, True)

    def UpdateVolumeFractionText(self):

        if self._usebar is True:

            n = self.xdata[1] - self.xdata[0]
            i0, i1 = min(self._select_i0, self._select_i1), max(
                self._select_i0, self._select_i1)

            partial_volume = self.ydata[i0:i1].sum()
            volume_fraction = partial_volume / float(self.ydata.sum())

            if self._voxel_volume_set is True:
                self.lower_panel.m_staticTextSelectedVolumeLabel.SetLabel(
                    u'Selected Volume:')
                self.lower_panel.m_staticTextSelectedVolume.SetLabel(
                    u'%0.3f mm\u00B3' % (partial_volume * self._voxel_volume))
            else:
                self.lower_panel.m_staticTextSelectedVolumeLabel.SetLabel(
                    'Number Voxels')
                self.lower_panel.m_staticTextSelectedVolume.SetLabel(
                    '%d' % (partial_volume))
            self.lower_panel.m_staticTextVolumeFraction.SetLabel(
                '%0.4f' % (volume_fraction))

            vals = (self.xdata[i0], self.xdata[i1])
            if i0 == i1:
                vals = 0.0, 0.0
                if self.GetHighlightVisible() is False:
                    self.SetHighlightVisible(False)

            # set Selection fields
            self.lower_panel.m_spinCtrlLower.SetValue(vals[0])
            self.lower_panel.m_spinCtrlUpper.SetValue(vals[1])

    def Reset(self, e=None):

        self.removeMeasurementLine()

        if self._usebar:
            self.toolbar.SetHighlightVisible(False)
            self.HideHighlight()
            self.HideOtsuThreshold()

    def GetROIType(self, index):
        return 'custom'

    # TODO: are next two methods required for VTK-6?
    def GetROIStencil(self, image_index=None):
        print 'TODO: manage image index'
        event.notify(GetROIStencilEvent())
        return self._ROIStencil

    def SetROIStencilData(self, s):
        self._ROIStencil = s

    def AutoThreshold(self, evt):
        """Force an autothreshold calculation

        This routine posts an AutoThresholdCommandEvent command in order to request a new calculation of an
        optimal Otsu threshold.
        """
        event.notify(AutoThresholdCommandEvent())

    def SetInputConnection(self, algorithm):

        import pdb
        pdb.set_trace()

    def SetInputData(self, inp):

        if self.plot_data:
            for p in self.plot_data:
                p.remove()
            self.plot_data = None

        self._plotData = inp

        if self._usebar is True:
            pass
        else:
            # we're plotting line data - may need to transform the x axis
            p = vtk.vtkTransformPolyDataFilter()
            p.SetTransform(self._transform)
            p.SetInput(inp)
            self._plotData = p.GetOutput()

        if self._usebar:
            self.lower_panel.m_spinCtrlLower.SetValue(0)
            self.lower_panel.m_spinCtrlUpper.SetValue(0)

    def SetHistogramData(self, x, y):
        self.xdata = numpy.array(x)
        self.ydata = numpy.array(y)

    def SaveData(self, evt=None, filename=""):
        """Save line/histogram data to a text file"""

        if not self._usebar:
            numC = self.ydata.shape[-1]
            self.file_label = '# Pos. (%s)\t' % self._unit + (
                numC - 1) * '%s\t' + '%s' + '\n#'
            self.file_label = self.file_label % tuple(
                self.channel_names[:numC])
        else:
            self.file_label = '# Bin\tCount\n#'

        BasePlotWindow.BasePlotWindow.SaveData(self, evt, filename)

    def SetVoxelDimensions(self, xv, yv, zv):
        # voxel dimensions, in mm
        self._voxel_volume = (xv * yv * zv)
        self._voxel_volume_set = True
        self.lower_panel.m_staticTextSelectedVolume.SetLabel('')

    def PlotData(self):

        # remove any measurement line that might exist
        self.removeMeasurementLine(False)

        if self._usebar is False:
            # handle 'pixel' vs 'mm' options:
            self._transform.Identity()
            self._transform.Scale(self._unit_scalings[self._unit], self._unit_scalings[
                                  self._unit], self._unit_scalings[self._unit])
            self._plotData.Update()
            points = numpy_support.vtk_to_numpy(
                self._plotData.GetPoints().GetData())
            points = (points - points[0]).transpose()
            self.xdata = sum(points * points) ** 0.5
            self.ydata = numpy_support.vtk_to_numpy(
                self._plotData.GetPointData().GetScalars()).astype('float32')
        else:
            inc = abs(self.xdata[1] - self.xdata[0])
            self.lower_panel.m_spinCtrlLower.SetIncrement(inc)
            self.lower_panel.m_spinCtrlUpper.SetIncrement(inc)
            self.lower_panel.m_spinCtrlLower.SetMin(self.xdata[0])
            self.lower_panel.m_spinCtrlLower.SetMax(self.xdata[-1])
            self.lower_panel.m_spinCtrlUpper.SetMin(self.xdata[0])
            self.lower_panel.m_spinCtrlUpper.SetMax(self.xdata[-1])

        self.draw_plot()
        self.canvas.draw()

    def draw_plot(self):
        """ Redraws the plot"""

        self.axes.grid(True, color='gray')
        pylab.setp(self.axes.get_xticklabels(), visible=True)

        dims = 1
        if len(self.ydata.shape) > 1:
            dims = self.ydata.shape[-1]
            self.colours = ['red', 'green', 'blue', 'black']
            self.channel_names = ['red', 'green', 'blue', 'opacity']
        else:
            self.ydata.shape = (self.ydata.shape[0], 1)
            self.colours = ['black']
            self.channel_names = ['chan. 1']

        args = []
        marker_x = []
        marker_y = []
        marker_c = []

        if self._usebar is False:
            for i in range(dims):
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
                if len(self.plot_data) != dims:
                    for p in self.plot_data:
                        p.remove()
                    self.plot_data = None

            if self.plot_data is None:
                self.plot_data = self.axes.plot(*args, linewidth=1)
                self.legend = self.axes.legend(tuple(self.channel_names))
                pylab.setp(self.legend.get_texts(), fontsize='x-small')
            else:
                for i in range(dims):
                    self.plot_data[i].set_xdata(args[i * 3 + 0])
                    self.plot_data[i].set_ydata(args[i * 3 + 1])

            # draw end markers
            if self.end_markers:
                self.end_markers.remove()
            self.end_markers = self.axes.scatter(
                marker_x, marker_y, c=tuple(marker_c), linewidths=0, zorder=3)

        else:
            if self.plot_data:
                for p in self.plot_data:
                    p.remove()
            w = abs(self.xdata[1] - self.xdata[0]) / float(dims)
            for i in range(dims):
                self.plot_data = self.axes.plot(
                    self.xdata + i * w, self.ydata[:, i], color=self.colours[i], rasterized=True)
            self.legend = self.axes.legend(tuple(self.channel_names))
            pylab.setp(self.legend.get_texts(), fontsize='x-small')

        xmax = round(self.xdata.max(), 0) + 1
        xmin = 0

        ymin = round(self.ydata.min(), 0) - 1
        ymax = round(self.ydata.max(), 0) + 1

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)

    def setFloatControlPoint(self, evt):

        # read value from spin control
        floatspin = evt.GetEventObject()
        value = floatspin.GetValue()
        name = floatspin.GetName()

        lower_value = self.lower_panel.m_spinCtrlLower.GetValue()
        upper_value = self.lower_panel.m_spinCtrlUpper.GetValue()

        if name == 'lower':
            lower_value = min(value, upper_value)
        else:
            upper_value = max(value, lower_value)

        # find nearest real data value (x axis)
        index = abs(self.xdata - lower_value).argmin()
        evt.xdata = self.xdata[index]
        evt.ydata = self._liney
        self.setFirstLinePoint(evt)

        index = abs(self.xdata - upper_value).argmin()
        evt.xdata = self.xdata[index]
        evt.ydata = self._liney
        self.setSecondLinePoint(evt)

    def setUnitLabel(self, val):
        """Sets the units label on the measurement tool"""

        BasePlotWindow.BasePlotWindow.setUnitLabel(self, val)

        self._transform.Scale(self._unit_scalings[self._unit],
                              self._unit_scalings[self._unit],
                              self._unit_scalings[self._unit])
        if self._usebar:
            self._xlabel = ''
            self.axes.set_xlabel('Grayscale Value', size=8)

    def reportLineLength(self):

        if self._usebar is True:
            return
        else:
            BasePlotWindow.BasePlotWindow.reportLineLength(self)
