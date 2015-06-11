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
# Class ApplicationPreferencesDialog
###########################################################################


class ApplicationPreferencesDialog (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Preferences",
                           pos=wx.DefaultPosition, size=wx.Size(621, 498), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer107 = wx.BoxSizer(wx.VERTICAL)

        bSizer105 = wx.BoxSizer(wx.HORIZONTAL)

        bSizer106 = wx.BoxSizer(wx.VERTICAL)

        self.m_treeCtrl1 = wx.TreeCtrl(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE)
        self.m_treeCtrl1.SetMinSize(wx.Size(175, -1))

        bSizer106.Add(self.m_treeCtrl1, 1, wx.ALL | wx.EXPAND, 5)

        self.m_searchCtrl2 = wx.SearchCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER)
        self.m_searchCtrl2.ShowSearchButton(True)
        self.m_searchCtrl2.ShowCancelButton(True)
        bSizer106.Add(self.m_searchCtrl2, 0, wx.ALL | wx.EXPAND, 5)

        bSizer105.Add(bSizer106, 0, wx.EXPAND, 5)

        self.m_panelMainPanel = wx.Panel(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.m_panelMainPanel.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))

        bSizer105.Add(self.m_panelMainPanel, 1, wx.EXPAND | wx.ALL, 5)

        bSizer107.Add(bSizer105, 1, wx.EXPAND, 5)

        self.m_staticline5 = wx.StaticLine(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizer107.Add(self.m_staticline5, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        m_sdbSizer7 = wx.StdDialogButtonSizer()
        self.m_sdbSizer7OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer7.AddButton(self.m_sdbSizer7OK)
        self.m_sdbSizer7Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer7.AddButton(self.m_sdbSizer7Cancel)
        m_sdbSizer7.Realize()

        bSizer107.Add(m_sdbSizer7, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(bSizer107)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass
