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
# Class RescaleImageGUI
###########################################################################


class RescaleImageGUI (wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(
            255, 285), style=wx.TAB_TRAVERSAL)

        bSizer86 = wx.BoxSizer(wx.VERTICAL)

        bSizer87 = wx.BoxSizer(wx.VERTICAL)

        sbSizer39 = wx.StaticBoxSizer(wx.StaticBox(
            self, wx.ID_ANY, u"Rescaling Pairs"), wx.VERTICAL)

        fgSizer25 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer25.SetFlexibleDirection(wx.BOTH)
        fgSizer25.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText97 = wx.StaticText(
            self, wx.ID_ANY, u"Original Value 1", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText97.Wrap(-1)
        fgSizer25.Add(self.m_staticText97, 0,
                      wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_textCtrlOldValue1 = wx.TextCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer25.Add(self.m_textCtrlOldValue1, 0, wx.ALL, 5)

        self.m_staticText98 = wx.StaticText(
            self, wx.ID_ANY, u"Original Value 2", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText98.Wrap(-1)
        fgSizer25.Add(self.m_staticText98, 0,
                      wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_textCtrlOldValue2 = wx.TextCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer25.Add(self.m_textCtrlOldValue2, 0, wx.ALL, 5)

        self.m_staticText99 = wx.StaticText(
            self, wx.ID_ANY, u"New Value 1", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText99.Wrap(-1)
        fgSizer25.Add(self.m_staticText99, 0,
                      wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_textCtrlNewValue1 = wx.TextCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer25.Add(self.m_textCtrlNewValue1, 0, wx.ALL, 5)

        self.m_staticText100 = wx.StaticText(
            self, wx.ID_ANY, u"New Value 2", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText100.Wrap(-1)
        fgSizer25.Add(self.m_staticText100, 0,
                      wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_textCtrlNewValue2 = wx.TextCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer25.Add(self.m_textCtrlNewValue2, 0, wx.ALL, 5)

        sbSizer39.Add(fgSizer25, 1, wx.EXPAND, 5)

        bSizer87.Add(sbSizer39, 0, wx.EXPAND, 5)

        sbSizer40 = wx.StaticBoxSizer(wx.StaticBox(
            self, wx.ID_ANY, u"Output Setting"), wx.VERTICAL)

        fgSizer26 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer26.SetFlexibleDirection(wx.BOTH)
        fgSizer26.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText101 = wx.StaticText(
            self, wx.ID_ANY, u"Output Scalar Type", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText101.Wrap(-1)
        fgSizer26.Add(self.m_staticText101, 0,
                      wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        m_choiceScalarTypeChoices = [
            u"Char", u"Unsigned Char", u"Short", u"Unsigned Short", u"Int", u"Float", u"Double"]
        self.m_choiceScalarType = wx.Choice(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choiceScalarTypeChoices, 0)
        self.m_choiceScalarType.SetSelection(0)
        fgSizer26.Add(self.m_choiceScalarType, 0, wx.ALL, 5)

        self.m_checkBoxClampOverflow = wx.CheckBox(
            self, wx.ID_ANY, u"Clamp Overflow", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_checkBoxClampOverflow.SetValue(True)
        fgSizer26.Add(self.m_checkBoxClampOverflow, 0, wx.ALL, 5)

        sbSizer40.Add(fgSizer26, 1, wx.EXPAND, 5)

        bSizer87.Add(sbSizer40, 1, wx.EXPAND, 5)

        self.m_buttonRescale = wx.Button(
            self, wx.ID_ANY, u"Rescale Image", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_buttonRescale.Enable(False)

        bSizer87.Add(self.m_buttonRescale, 0, wx.ALL, 5)

        bSizer86.Add(bSizer87, 0, 0, 5)

        self.SetSizer(bSizer86)
        self.Layout()

        # Connect Events
        self.m_textCtrlOldValue1.Bind(wx.EVT_TEXT, self.onTextValidate)
        self.m_textCtrlOldValue2.Bind(wx.EVT_TEXT, self.onTextValidate)
        self.m_textCtrlNewValue1.Bind(wx.EVT_TEXT, self.onTextValidate)
        self.m_textCtrlNewValue2.Bind(wx.EVT_TEXT, self.onTextValidate)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def onTextValidate(self, event):
        event.Skip()
