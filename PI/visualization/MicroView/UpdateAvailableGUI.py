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
# Class UpdateAvailableGUI
###########################################################################


class UpdateAvailableGUI (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(
            self, parent, id=wx.ID_ANY, title=u"MicroView Update Available",
            pos=wx.DefaultPosition, size=wx.Size(375, 179), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer105 = wx.BoxSizer(wx.VERTICAL)

        bSizer106 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_bitmap2 = wx.StaticBitmap(self, wx.ID_ANY, wx.ArtProvider.GetBitmap(
            wx.ART_INFORMATION,), wx.DefaultPosition, wx.Size(-1, -1), 0)
        bSizer106.Add(self.m_bitmap2, 0, wx.ALL, 5)

        self.m_staticTextVersionMessage = wx.StaticText(
            self, wx.ID_ANY, u"A new version of MicroView is available for download!\nVersion %s can be downloaded by using the following link:", wx.DefaultPosition, wx.Size(-1, 50), 0)
        self.m_staticTextVersionMessage.Wrap(300)
        bSizer106.Add(
            self.m_staticTextVersionMessage, 0, wx.ALL | wx.EXPAND, 5)

        bSizer105.Add(bSizer106, 0, wx.EXPAND, 5)

        self.m_hyperlink1 = wx.HyperlinkCtrl(
            self, wx.ID_ANY, u"http://www.parallax-innovations.com/microview",
            u"http://www.parallax-innovations.com/microview", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE)
        bSizer105.Add(self.m_hyperlink1, 0, wx.ALL | wx.BOTTOM | wx.TOP, 10)

        bSizer105.AddSpacer((0, 0), 0, wx.EXPAND, 5)

        self.m_checkBoxShowDialog = wx.CheckBox(
            self, wx.ID_ANY, u"Show this dialog at start-up", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_checkBoxShowDialog.SetValue(True)
        bSizer105.Add(self.m_checkBoxShowDialog, 0, wx.ALL, 5)

        self.m_buttonOk = wx.Button(
            self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer105.Add(
            self.m_buttonOk, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        self.SetSizer(bSizer105)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.m_buttonOk.Bind(wx.EVT_BUTTON, self.onButtonClick)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def onButtonClick(self, event):
        event.Skip()
