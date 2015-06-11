# =========================================================================
#
# Copyright (c) 2011-2015 Parallax Innovations Inc
#
# =========================================================================

import wx
import time
from zope import component
from PI.visualization.MicroView.events import ZSliceValueChangeEvent
from PI.visualization.MicroView.interfaces import ICurrentImage
import BasePlotWindow
from twisted.internet import reactor


class SpectrumPlotWindow(BasePlotWindow.BasePlotWindow):

    def __init__(self, parent, id=-1, title="Untitled Dialog", *args, **kw):

        self.wavelength_line_tool = None
        self.z_indicator_value = None
        self._zindex = 0
        self._delayed_cb = None
        self._last_delayed_redraw = 0

        BasePlotWindow.BasePlotWindow.__init__(self, parent, *args, **kw)

        # ------------------------------------------------------------------------------------
        # Set up some zope event handlers
        # ---------------------------------------------------------------------
        component.provideHandler(self.onZSliceValueChanged)

        # listen to when this widget is shown or hidden
        wx.EVT_SHOW(self, self.onShowEvent)

    def __del__(self):
        # unregister our zope handlers
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.onZSliceValueChanged)

    def SetInput(self, *args, **kw):

        if 'zindex' in kw:

            zindex = kw['zindex']
            del(kw['zindex'])
            self.SetZIndexValue(zindex)

        BasePlotWindow.BasePlotWindow.SetInput(self, *args, **kw)

    def SaveData(self, evt=None, filename=""):
        """Save spectrum data to a text file"""

        numC = self.ydata.shape[-1]
        self.file_label = '# Wavelength (%s)\t' % self._unit + (
            numC - 1) * '%s\t' + '%s' + '\n#'
        self.file_label = self.file_label % tuple(self.channel_names[:numC])

        BasePlotWindow.BasePlotWindow.SaveData(self, evt, filename)

    def NotifyHistoHighlightChange(self):

        # Override here to ensure we don't post histogram-like events
        pass

    def SetZIndexValue(self, zindex):

        self._zindex = zindex
        self.z_indicator_value = zindex

    def onShowEvent(self, evt):

        if self.IsShown():
            self.UpdateSliceIndicator(self._zindex)

    @component.adapter(ZSliceValueChangeEvent)
    def onZSliceValueChanged(self, evt):

        try:
            component.getUtility(ICurrentImage)
        except:
            # no image loaded so exit early
            return

        # get current z-slice index
        self.SetZIndexValue(int(round(evt.GetSliceValue())))

        # we'd like to give regular plot updates without bring the system
        # to it's knees - we'll guarantee the user a redraw at least every
        # half second
        dt = time.time() - self._last_delayed_redraw

        # schedule an update in 0.25 second
        if self._delayed_cb:
            self._delayed_cb.cancel()

        if dt > 1.0:
            # perform redraw immediately
            self.doScheduledRedraw()
        else:
            # schedule for later
            self._delayed_cb = reactor.callLater(0.25, self.doScheduledRedraw)

    def doScheduledRedraw(self):

        self._delayed_cb = None
        self._last_delayed_redraw = time.time()

        # update position of z-slice indicator
        if self.IsShown():
            self.UpdateSliceIndicator(self._zindex)

    def UpdateSliceIndicator(self, zindex):
        # draw an indicator on plot window to indicate which slice we are
        # looking at
        self.z_indicator_value = zindex
        self.PlotData()

    def update_axes_bounds(self):

        xmax = round(self.xdata.max(), 0) + 1
        xmin = round(self.xdata.min(), 0) - 1
        ymin = round(self.ydata.min(), 0) - 1
        ymax = round(self.ydata.max(), 0) + 1

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)

    def update_channel_names(self):
        self.channel_names = ['point', 'line', 'area']

    def draw_plot(self):

        # draw standard items to window
        BasePlotWindow.BasePlotWindow.draw_plot(self)

        if self.z_indicator_value is None:
            return

        # now add in a red line at the correct z-slice value
        ymin, ymax = self.axes.get_ybound()
        delta_y = abs(ymax - ymin)

        x = self.xdata[self.z_indicator_value]
        y = self.ydata[self.z_indicator_value]

        if self.wavelength_line_tool is None:
            self.wavelength_line_tool, =  self.axes.plot([x, x], [y - (
                delta_y / 20.0), y + (delta_y / 20.0)], linestyle='-', color='red')
        else:
            #  update
            self.wavelength_line_tool.set_xdata([x, x])
            self.wavelength_line_tool.set_ydata(
                [y - (delta_y / 20.0), y + (delta_y / 20.0)])
