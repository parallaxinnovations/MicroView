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
# Class AnisotropicSmoothingDialog
###########################################################################


class AnisotropicSmoothingDialog (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Anisotropic Smoothing",
                           pos=wx.DefaultPosition, size=wx.Size(525, 316), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer133 = wx.BoxSizer(wx.VERTICAL)

        bSizer135 = wx.BoxSizer(wx.HORIZONTAL)

        bSizer134 = wx.BoxSizer(wx.VERTICAL)

        fgSizer34 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer34.SetFlexibleDirection(wx.BOTH)
        fgSizer34.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText146 = wx.StaticText(
            self, wx.ID_ANY, u"Number of Iterations:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText146.Wrap(-1)
        fgSizer34.Add(
            self.m_staticText146, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_spinCtrlNumIterations = wx.SpinCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 10, 4)
        fgSizer34.Add(self.m_spinCtrlNumIterations, 0, wx.ALL, 5)

        self.m_staticText147 = wx.StaticText(
            self, wx.ID_ANY, u"Diffusion Threshold:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText147.Wrap(-1)
        fgSizer34.Add(
            self.m_staticText147, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_textCtrlDiffusionThreshold = wx.TextCtrl(
            self, wx.ID_ANY, u"5.0", wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer34.Add(self.m_textCtrlDiffusionThreshold, 0, wx.ALL, 5)

        self.m_staticText148 = wx.StaticText(
            self, wx.ID_ANY, u"Diffusion Factor:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText148.Wrap(-1)
        fgSizer34.Add(
            self.m_staticText148, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_textCtrlDiffusionFactor = wx.TextCtrl(
            self, wx.ID_ANY, u"1.0", wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer34.Add(self.m_textCtrlDiffusionFactor, 0, wx.ALL, 5)

        bSizer134.Add(fgSizer34, 1, wx.EXPAND, 5)

        sbSizer48 = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, u"Neighbourhood"), wx.VERTICAL)

        fgSizer36 = wx.FlexGridSizer(0, 3, 0, 0)
        fgSizer36.SetFlexibleDirection(wx.BOTH)
        fgSizer36.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_checkBoxUseFaces = wx.CheckBox(
            self, wx.ID_ANY, u"Faces", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_checkBoxUseFaces.SetValue(True)
        fgSizer36.Add(self.m_checkBoxUseFaces, 0, wx.ALL, 5)

        self.m_checkBoxUseEdges = wx.CheckBox(
            self, wx.ID_ANY, u"Edges", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_checkBoxUseEdges.SetValue(True)
        fgSizer36.Add(self.m_checkBoxUseEdges, 0, wx.ALL, 5)

        self.m_checkBoxUseCorners = wx.CheckBox(
            self, wx.ID_ANY, u"Corners", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_checkBoxUseCorners.SetValue(True)
        fgSizer36.Add(self.m_checkBoxUseCorners, 0, wx.ALL, 5)

        sbSizer48.Add(fgSizer36, 1, wx.EXPAND, 5)

        bSizer134.Add(sbSizer48, 0, wx.EXPAND, 5)

        m_radioBox9Choices = [u"Gradient Value", u"Pixel Value"]
        self.m_radioBox9 = wx.RadioBox(
            self, wx.ID_ANY, u"Magnitude", wx.DefaultPosition, wx.DefaultSize, m_radioBox9Choices, 2, wx.RA_SPECIFY_COLS)
        self.m_radioBox9.SetSelection(0)
        bSizer134.Add(self.m_radioBox9, 0, wx.ALL | wx.EXPAND, 0)

        bSizer135.Add(bSizer134, 0, wx.EXPAND, 5)

        sbSizer50 = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, u"Preview"), wx.VERTICAL)

        self.m_bitmapPreview = wx.StaticBitmap(
            self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0)
        sbSizer50.Add(self.m_bitmapPreview, 1, wx.ALL | wx.EXPAND, 5)

        self.m_buttonUpdate = wx.Button(
            self, wx.ID_ANY, u"Update", wx.DefaultPosition, wx.DefaultSize, 0)
        sbSizer50.Add(
            self.m_buttonUpdate, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        bSizer135.Add(sbSizer50, 1, wx.EXPAND | wx.LEFT, 5)

        bSizer133.Add(bSizer135, 1, wx.EXPAND, 5)

        self.m_staticline7 = wx.StaticLine(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        bSizer133.Add(self.m_staticline7, 0, wx.EXPAND | wx.ALL, 5)

        m_sdbSizer9 = wx.StdDialogButtonSizer()
        self.m_sdbSizer9OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer9.AddButton(self.m_sdbSizer9OK)
        self.m_sdbSizer9Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer9.AddButton(self.m_sdbSizer9Cancel)
        m_sdbSizer9.Realize()

        bSizer133.Add(m_sdbSizer9, 0, wx.BOTTOM | wx.EXPAND, 5)

        self.SetSizer(bSizer133)
        self.Layout()

        self.Centre(wx.BOTH)

    def __del__(self):
        pass
