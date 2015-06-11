# -*- coding: utf-8 -*-

###########################################################################
# Python code generated with wxFormBuilder (version Nov  6 2013)
# http://www.wxformbuilder.org/
##
# PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.html2 as webview

###########################################################################
# Class UpstreamMessageDialogGUI
###########################################################################


class UpstreamMessageDialogGUI (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString,
                           pos=wx.DefaultPosition, size=wx.Size(619, 482), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer196 = wx.BoxSizer(wx.VERTICAL)

        self.m_wxHtmlWindow = webview.WebView.New(self)
        bSizer196.Add(self.m_wxHtmlWindow, 1, wx.ALL | wx.EXPAND, 5)

        self.m_staticline13 = wx.StaticLine(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizer196.Add(self.m_staticline13, 0, wx.EXPAND | wx.ALL, 5)

        m_sdbSizer19 = wx.StdDialogButtonSizer()
        self.m_sdbSizer19OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer19.AddButton(self.m_sdbSizer19OK)
        m_sdbSizer19.Realize()

        bSizer196.Add(m_sdbSizer19, 0, wx.BOTTOM | wx.EXPAND, 5)

        self.SetSizer(bSizer196)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass


if __name__ == '__main__':
    import sys

    app = wx.App()
    dlg = UpstreamMessageDialogGUI(None)
    dlg.m_wxHtmlWindow.LoadURL("http://google.com")

    if sys.platform == 'darwin':
        dlg.Show()
        app.MainLoop()
    else:
        dlg.ShowModal()
