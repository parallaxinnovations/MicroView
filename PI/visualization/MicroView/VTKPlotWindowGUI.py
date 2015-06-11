# -*- coding: utf-8 -*-

###########################################################################
# Python code generated with wxFormBuilder (version Apr 10 2012)
# http://www.wxformbuilder.org/
##
# PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
# Class VTKPlotWindowGUI
###########################################################################


class VTKPlotWindowGUI (wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(
            787, 612), style=wx.TAB_TRAVERSAL)

        bSizer64 = wx.BoxSizer(wx.VERTICAL)

        self.m_panelMatplotPanel = wx.Panel(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer64.Add(self.m_panelMatplotPanel, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(bSizer64)
        self.Layout()

    def __del__(self):
        pass
