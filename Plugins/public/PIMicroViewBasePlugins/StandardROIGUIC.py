import wx
import wx.lib.buttons
import wx.lib.masked

from zope import component

import StandardROIGUI
# don't change this
from PI.visualization.MicroView.interfaces import IStockIconProvider
from PI.visualization.common import FloatSlider

import logging


class StandardROIGUIC(StandardROIGUI.StandardROIGUI):

    def __init__(self, parent):

        self.logger = logging.getLogger(__name__)

        StandardROIGUI.StandardROIGUI.__init__(self, parent)

        # erase warning message early
        self.m_staticTextErrorMessage1.SetLabel("")
        self.m_staticTextErrorMessage2.SetLabel("")

        # get stock icon factory from object registry
        stockicons = component.getUtility(IStockIconProvider)
        pkg = self.__module__.split('.')[0] + '.Icons'
        self._open_icon = stockicons.getBitmap('stock_link_open', package=pkg)
        self._closed_icon = stockicons.getBitmap(
            'stock_link_closed', package=pkg)

        # make masked number controls
        children = self.GetChildren()

        # iterate over all children looking for things - wxFB has limitations
        # that we need to overcome
        flex_sizers = []
        x_labels = []
        y_labels = []
        z_labels = []
        sliders = []
        for index in range(len(children)):
            name = children[index].GetName()
            if name == 'staticText':
                label = children[index].GetLabel()
                if label == 'X:':
                    sizer = children[index].GetContainingSizer()
                    flex_sizers.append(sizer)
                    x_labels.append(index)
                elif label == 'Y:':
                    y_labels.append(index)
                elif label == 'Z:':
                    z_labels.append(index)
            elif name == 'slider':
                sliders.append(index)

        # replace 6 sliders with custom FloatSliders
        sx = FloatSlider.FloatSlider(self, -1, 50, 0, 100, 1)
        sx.SetMinSize(wx.Size(100, -1))
        sy = FloatSlider.FloatSlider(self, -1, 50, 0, 100, 1)
        sy.SetMinSize(wx.Size(100, -1))
        sz = FloatSlider.FloatSlider(self, -1, 50, 0, 100, 1)
        sz.SetMinSize(wx.Size(100, -1))

        flex_sizers[0].Replace(self.m_sliderSizeX, sx)
        flex_sizers[0].Replace(self.m_sliderSizeY, sy)
        flex_sizers[0].Replace(self.m_sliderSizeZ, sz)

        self.m_sliderSizeX.Destroy()
        self.m_sliderSizeY.Destroy()
        self.m_sliderSizeZ.Destroy()

        self.m_sliderSizeX = sx
        self.m_sliderSizeY = sy
        self.m_sliderSizeZ = sz

        cx = FloatSlider.FloatSlider(self, -1, 50, 0, 100, 0.5)
        cx.SetMinSize(wx.Size(100, -1))
        cy = FloatSlider.FloatSlider(self, -1, 50, 0, 100, 0.5)
        cy.SetMinSize(wx.Size(100, -1))
        cz = FloatSlider.FloatSlider(self, -1, 50, 0, 100, 0.5)
        cz.SetMinSize(wx.Size(100, -1))

        flex_sizers[1].Replace(self.m_sliderCenterX, cx)
        flex_sizers[1].Replace(self.m_sliderCenterY, cy)
        flex_sizers[1].Replace(self.m_sliderCenterZ, cz)

        self.m_sliderCenterX.Destroy()
        self.m_sliderCenterY.Destroy()
        self.m_sliderCenterZ.Destroy()

        self.m_sliderCenterX = cx
        self.m_sliderCenterY = cy
        self.m_sliderCenterZ = cz

        flex_sizers[0].Layout()

    def DisablePlugin(self, reason_string=''):

        # we don't really do anything with this
        self.logger.warning(reason_string)
