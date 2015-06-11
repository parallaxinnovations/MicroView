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
# Class WindowLevelDialogGUI
###########################################################################


class WindowLevelDialogGUI (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Window and Level Settings",
                           pos=wx.DefaultPosition, size=wx.Size(366, 363), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer69 = wx.BoxSizer(wx.VERTICAL)

        m_radioBoxInteractionModeChoices = [u"Window/Level", u"Min/Max"]
        self.m_radioBoxInteractionMode = wx.RadioBox(
            self, wx.ID_ANY, u"Interaction mode", wx.DefaultPosition, wx.DefaultSize, m_radioBoxInteractionModeChoices, 2, wx.RA_SPECIFY_COLS)
        self.m_radioBoxInteractionMode.SetSelection(0)
        bSizer69.Add(self.m_radioBoxInteractionMode, 0, wx.ALL | wx.EXPAND, 5)

        sbSizer64 = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, u"Histogram"), wx.VERTICAL)

        self.m_panelHistogram = wx.Panel(
            self, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, -1), wx.TAB_TRAVERSAL)
        self.m_panelHistogram.SetMinSize(wx.Size(-1, 128))

        sbSizer64.Add(self.m_panelHistogram, 1, wx.EXPAND | wx.ALL, 5)

        bSizer69.Add(sbSizer64, 1, wx.ALL | wx.EXPAND, 5)

        sbSizer33 = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, u"Thresholds"), wx.HORIZONTAL)

        self.m_panelThresholds = wx.Panel(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        sbSizer33.Add(self.m_panelThresholds, 1, wx.EXPAND | wx.ALL, 5)

        bSizer69.Add(sbSizer33, 0, wx.ALL | wx.EXPAND, 5)

        self.m_staticline10 = wx.StaticLine(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizer69.Add(self.m_staticline10, 0, wx.EXPAND | wx.ALL, 5)

        m_sdbSizer2 = wx.StdDialogButtonSizer()
        self.m_sdbSizer2OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer2.AddButton(self.m_sdbSizer2OK)
        self.m_sdbSizer2Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer2.AddButton(self.m_sdbSizer2Cancel)
        m_sdbSizer2.Realize()

        bSizer69.Add(m_sdbSizer2, 0, wx.BOTTOM | wx.EXPAND, 5)

        self.SetSizer(bSizer69)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.m_radioBoxInteractionMode.Bind(
            wx.EVT_RADIOBOX, self.onIteractionModeChange)
        self.m_sdbSizer2Cancel.Bind(wx.EVT_BUTTON, self.onCancelButton)
        self.m_sdbSizer2OK.Bind(wx.EVT_BUTTON, self.onOkButton)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def onIteractionModeChange(self, event):
        event.Skip()

    def onCancelButton(self, event):
        event.Skip()

    def onOkButton(self, event):
        event.Skip()
