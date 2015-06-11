# -*- coding: utf-8 -*-

###########################################################################
# Python code generated with wxFormBuilder (version Nov  6 2013)
# http://www.wxformbuilder.org/
##
# PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
# Class ChooseFilterRadiusDialog
###########################################################################


class ChooseFilterRadiusDialog (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Filter radius", pos=wx.DefaultPosition, size=wx.Size(
            289, 182), style=wx.CAPTION | wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer105 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticTextVersionMessage = wx.StaticText(
            self, wx.ID_ANY, u"Enter {0} filter radius:", wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_staticTextVersionMessage.Wrap(-1)
        bSizer105.Add(
            self.m_staticTextVersionMessage, 0, wx.ALL | wx.EXPAND | wx.LEFT | wx.TOP, 10)

        self.m_textCtrlRadius = wx.TextCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer105.Add(
            self.m_textCtrlRadius, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)

        bSizer105.AddSpacer((0, 0), 0, wx.EXPAND, 5)

        self.m_checkBox3DFilter = wx.CheckBox(
            self, wx.ID_ANY, u"Apply as a 3D filter", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_checkBox3DFilter.SetValue(True)
        bSizer105.Add(
            self.m_checkBox3DFilter, 0, wx.ALL | wx.BOTTOM | wx.TOP, 5)

        bSizer105.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self.m_staticline12 = wx.StaticLine(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizer105.Add(self.m_staticline12, 0, wx.EXPAND | wx.ALL, 5)

        m_sdbSizer17 = wx.StdDialogButtonSizer()
        self.m_sdbSizer17OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer17.AddButton(self.m_sdbSizer17OK)
        self.m_sdbSizer17Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer17.AddButton(self.m_sdbSizer17Cancel)
        m_sdbSizer17.Realize()

        bSizer105.Add(m_sdbSizer17, 1, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(bSizer105)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass
