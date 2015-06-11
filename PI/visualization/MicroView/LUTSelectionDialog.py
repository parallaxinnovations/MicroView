# -*- coding: utf-8 -*-

###########################################################################
# Python code generated with wxFormBuilder (version Oct  8 2012)
# http://www.wxformbuilder.org/
##
# PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
# Class LUTSelectionDialog
###########################################################################


class LUTSelectionDialog (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(
            self, parent, id=wx.ID_ANY, title=u"Select Palette",
            pos=wx.DefaultPosition, size=wx.Size(332, 205), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer126 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText137 = wx.StaticText(
            self, wx.ID_ANY, u"Select Palette from the menu below:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText137.Wrap(-1)
        bSizer126.Add(self.m_staticText137, 0,
                      wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_panelPalette = wx.Panel(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer126.Add(self.m_panelPalette, 1, wx.EXPAND | wx.ALL, 5)

        m_sdbSizer8 = wx.StdDialogButtonSizer()
        self.m_sdbSizer8OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer8.AddButton(self.m_sdbSizer8OK)
        self.m_sdbSizer8Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer8.AddButton(self.m_sdbSizer8Cancel)
        m_sdbSizer8.Realize()

        bSizer126.Add(m_sdbSizer8, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(bSizer126)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass
