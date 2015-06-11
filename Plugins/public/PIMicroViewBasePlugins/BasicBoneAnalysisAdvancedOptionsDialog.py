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
# Class BasicBoneAnalysisAdvancedOptionsDialog
###########################################################################


class BasicBoneAnalysisAdvancedOptionsDialog (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"MicroView Analysis Options",
                           pos=wx.DefaultPosition, size=wx.Size(309, 274), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer92 = wx.BoxSizer(wx.VERTICAL)

        self.m_notebookOptions = wx.Notebook(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_panel23 = wx.Panel(
            self.m_notebookOptions, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        fgSizer31 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer31.SetFlexibleDirection(wx.BOTH)
        fgSizer31.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText149 = wx.StaticText(
            self.m_panel23, wx.ID_ANY, u"Bone ADU:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText149.Wrap(-1)
        fgSizer31.Add(
            self.m_staticText149, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_textCtrlBoneADU = wx.TextCtrl(
            self.m_panel23, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_textCtrlBoneADU.SetMaxLength(0)
        fgSizer31.Add(self.m_textCtrlBoneADU, 0, wx.ALL, 5)

        self.m_staticText150 = wx.StaticText(
            self.m_panel23, wx.ID_ANY, u"Water ADU:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText150.Wrap(-1)
        fgSizer31.Add(
            self.m_staticText150, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_textCtrlWaterADU = wx.TextCtrl(
            self.m_panel23, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_textCtrlWaterADU.SetMaxLength(0)
        fgSizer31.Add(self.m_textCtrlWaterADU, 0, wx.ALL, 5)

        self.m_staticText151 = wx.StaticText(
            self.m_panel23, wx.ID_ANY, u"Lower Exclusion ADU:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText151.Wrap(-1)
        fgSizer31.Add(
            self.m_staticText151, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_textCtrlLowerExclusion = wx.TextCtrl(
            self.m_panel23, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_textCtrlLowerExclusion.SetMaxLength(0)
        fgSizer31.Add(self.m_textCtrlLowerExclusion, 0, wx.ALL, 5)

        self.m_staticText152 = wx.StaticText(
            self.m_panel23, wx.ID_ANY, u"Upper Exclusion ADU:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText152.Wrap(-1)
        fgSizer31.Add(
            self.m_staticText152, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_textCtrlUpperExclusion = wx.TextCtrl(
            self.m_panel23, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_textCtrlUpperExclusion.SetMaxLength(0)
        fgSizer31.Add(self.m_textCtrlUpperExclusion, 0, wx.ALL, 5)

        self.m_panel23.SetSizer(fgSizer31)
        self.m_panel23.Layout()
        fgSizer31.Fit(self.m_panel23)
        self.m_notebookOptions.AddPage(self.m_panel23, u"BMD", True)
        self.m_panel24 = wx.Panel(
            self.m_notebookOptions, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        bSizer93 = wx.BoxSizer(wx.VERTICAL)

        self.m_checkBoxEnableVerbose = wx.CheckBox(
            self.m_panel24, wx.ID_ANY, u"Enable verbose output", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer93.Add(self.m_checkBoxEnableVerbose, 0, wx.ALL, 5)

        self.m_checkBoxEnablePurify = wx.CheckBox(
            self.m_panel24, wx.ID_ANY, u"Enable purify algorithm", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer93.Add(self.m_checkBoxEnablePurify, 0, wx.ALL, 5)

        self.m_panel24.SetSizer(bSizer93)
        self.m_panel24.Layout()
        bSizer93.Fit(self.m_panel24)
        self.m_notebookOptions.AddPage(self.m_panel24, u"Stereology", False)

        bSizer92.Add(self.m_notebookOptions, 1, wx.EXPAND | wx.ALL, 5)

        m_sdbSizer4 = wx.StdDialogButtonSizer()
        self.m_sdbSizer4OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer4.AddButton(self.m_sdbSizer4OK)
        self.m_sdbSizer4Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer4.AddButton(self.m_sdbSizer4Cancel)
        m_sdbSizer4.Realize()

        bSizer92.Add(m_sdbSizer4, 0, wx.BOTTOM | wx.EXPAND, 5)

        self.SetSizer(bSizer92)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass
