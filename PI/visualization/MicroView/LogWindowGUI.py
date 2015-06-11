# -*- coding: utf-8 -*-

###########################################################################
# Python code generated with wxFormBuilder (version Apr 10 2012)
# http://www.wxformbuilder.org/
##
# PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

LOG_SAVE = 1000
LOG_CLEAR = 1001

###########################################################################
# Class LogWindowGUI
###########################################################################


class LogWindowGUI (wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(
            699, 504), style=wx.TAB_TRAVERSAL)

        bSizer80 = wx.BoxSizer(wx.VERTICAL)

        self.m_toolBar2 = wx.ToolBar(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL)
        self.m_toolBar2.AddLabelTool(LOG_SAVE, u"tool", wx.ArtProvider.GetBitmap(
            wx.ART_FILE_SAVE_AS,), wx.NullBitmap, wx.ITEM_NORMAL, u"Save As...", u"Save statistics to a file", None)

        self.m_toolBar2.AddLabelTool(LOG_CLEAR, u"tool", wx.ArtProvider.GetBitmap(
            wx.ART_CUT,), wx.NullBitmap, wx.ITEM_NORMAL, u"Clear results", u"Clear results", None)

        self.m_toolBar2.Realize()

        bSizer80.Add(self.m_toolBar2, 0, wx.EXPAND, 5)

        self.m_textCtrlLog = wx.TextCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition,
            wx.DefaultSize, wx.HSCROLL | wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_RICH2)
        bSizer80.Add(self.m_textCtrlLog, 1, wx.ALL | wx.EXPAND, 0)

        self.SetSizer(bSizer80)
        self.Layout()

        # Connect Events
        self.Bind(wx.EVT_TOOL, self.onToolClicked, id=LOG_SAVE)
        self.Bind(wx.EVT_TOOL, self.onToolClicked, id=LOG_CLEAR)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def onToolClicked(self, event):
        event.Skip()
