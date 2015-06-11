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
# Class OpenCloseMorphologyDialog
###########################################################################


class OpenCloseMorphologyDialog (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Open/Close Image",
                           pos=wx.DefaultPosition, size=wx.Size(372, 282), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer161 = wx.BoxSizer(wx.VERTICAL)

        bSizer162 = wx.BoxSizer(wx.HORIZONTAL)

        sbSizer60 = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, u"Kernel Size"), wx.VERTICAL)

        fgSizer46 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer46.SetFlexibleDirection(wx.BOTH)
        fgSizer46.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText198 = wx.StaticText(
            self, wx.ID_ANY, u"X:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText198.Wrap(-1)
        fgSizer46.Add(
            self.m_staticText198, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_spinCtrlX = wx.SpinCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 10, 3)
        self.m_spinCtrlX.SetMinSize(wx.Size(70, -1))

        fgSizer46.Add(self.m_spinCtrlX, 0, wx.ALL, 5)

        self.m_staticText199 = wx.StaticText(
            self, wx.ID_ANY, u"Y:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText199.Wrap(-1)
        fgSizer46.Add(
            self.m_staticText199, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_spinCtrlY = wx.SpinCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 10, 3)
        self.m_spinCtrlY.SetMinSize(wx.Size(70, -1))

        fgSizer46.Add(self.m_spinCtrlY, 0, wx.ALL, 5)

        self.m_staticText200 = wx.StaticText(
            self, wx.ID_ANY, u"Z:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText200.Wrap(-1)
        fgSizer46.Add(
            self.m_staticText200, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_spinCtrlZ = wx.SpinCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 10, 3)
        self.m_spinCtrlZ.SetMinSize(wx.Size(70, -1))

        fgSizer46.Add(self.m_spinCtrlZ, 0, wx.ALL, 5)

        sbSizer60.Add(fgSizer46, 0, 0, 5)

        bSizer162.Add(sbSizer60, 0, wx.ALL, 5)

        sbSizer61 = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, u"Threshold"), wx.VERTICAL)

        fgSizer47 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer47.SetFlexibleDirection(wx.BOTH)
        fgSizer47.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText197 = wx.StaticText(
            self, wx.ID_ANY, u"Open Value:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText197.Wrap(-1)
        fgSizer47.Add(
            self.m_staticText197, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_textCtrlOpenValue = wx.TextCtrl(
            self, wx.ID_ANY, u"0.0", wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer47.Add(self.m_textCtrlOpenValue, 0, wx.ALL, 5)

        self.m_staticText201 = wx.StaticText(
            self, wx.ID_ANY, u"Close Value:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText201.Wrap(-1)
        fgSizer47.Add(
            self.m_staticText201, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_textCtrlCloseValue = wx.TextCtrl(
            self, wx.ID_ANY, u"255.0", wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer47.Add(self.m_textCtrlCloseValue, 0, wx.ALL, 5)

        sbSizer61.Add(fgSizer47, 0, 0, 5)

        bSizer162.Add(sbSizer61, 0, wx.ALL | wx.EXPAND, 5)

        bSizer161.Add(bSizer162, 0, wx.ALL | wx.EXPAND, 5)

        bSizer161.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self.m_staticline8 = wx.StaticLine(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizer161.Add(self.m_staticline8, 0, wx.EXPAND | wx.ALL, 5)

        m_sdbSizer12 = wx.StdDialogButtonSizer()
        self.m_sdbSizer12OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer12.AddButton(self.m_sdbSizer12OK)
        self.m_sdbSizer12Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer12.AddButton(self.m_sdbSizer12Cancel)
        m_sdbSizer12.Realize()

        bSizer161.Add(m_sdbSizer12, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 5)

        self.SetSizer(bSizer161)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass
