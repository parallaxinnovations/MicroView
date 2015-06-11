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
# Class AdaptiveOtsuThresholdDialog
###########################################################################


class AdaptiveOtsuThresholdDialog (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Adaptive Otsu Threshold",
                           pos=wx.DefaultPosition, size=wx.Size(263, 186), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer164 = wx.BoxSizer(wx.VERTICAL)

        bSizer165 = wx.BoxSizer(wx.VERTICAL)

        sbSizer62 = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, u"Parameters"), wx.VERTICAL)

        fgSizer48 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer48.SetFlexibleDirection(wx.BOTH)
        fgSizer48.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText203 = wx.StaticText(
            self, wx.ID_ANY, u"Lower Cutoff:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText203.Wrap(-1)
        fgSizer48.Add(
            self.m_staticText203, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.m_textCtrlLowerCutoff = wx.TextCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer48.Add(self.m_textCtrlLowerCutoff, 0, wx.ALL, 5)

        self.m_staticText223 = wx.StaticText(
            self, wx.ID_ANY, u"Chunk size:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText223.Wrap(-1)
        fgSizer48.Add(
            self.m_staticText223, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.m_spinCtrlChunkSize = wx.SpinCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 1024, 64)
        fgSizer48.Add(self.m_spinCtrlChunkSize, 0, wx.ALL, 5)

        sbSizer62.Add(fgSizer48, 0, wx.EXPAND, 5)

        bSizer165.Add(sbSizer62, 0, wx.ALL | wx.EXPAND, 5)

        bSizer164.Add(bSizer165, 1, wx.EXPAND, 5)

        m_sdbSizer13 = wx.StdDialogButtonSizer()
        self.m_sdbSizer13OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer13.AddButton(self.m_sdbSizer13OK)
        self.m_sdbSizer13Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer13.AddButton(self.m_sdbSizer13Cancel)
        m_sdbSizer13.Realize()

        bSizer164.Add(m_sdbSizer13, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 5)

        self.SetSizer(bSizer164)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass
