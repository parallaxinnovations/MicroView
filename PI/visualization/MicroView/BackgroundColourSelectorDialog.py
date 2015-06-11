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
# Class BackgroundColourSelectorDialog
###########################################################################


class BackgroundColourSelectorDialog (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(
            self, parent, id=wx.ID_ANY, title=u"Background Colour",
            pos=wx.DefaultPosition, size=wx.Size(352, 225), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer96 = wx.BoxSizer(wx.VERTICAL)

        fgSizer27 = wx.FlexGridSizer(0, 3, 0, 0)
        fgSizer27.SetFlexibleDirection(wx.BOTH)
        fgSizer27.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText114 = wx.StaticText(
            self, wx.ID_ANY, u"Top Gradient Colour:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText114.Wrap(-1)
        fgSizer27.Add(self.m_staticText114, 0,
                      wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_colourPickerTop = wx.ColourPickerCtrl(self, wx.ID_ANY, wx.Colour(
            0, 58, 117), wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE)
        fgSizer27.Add(self.m_colourPickerTop, 0, wx.ALL, 5)

        self.m_checkBoxApplyGradient = wx.CheckBox(
            self, wx.ID_ANY, u"Apply Gradient", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_checkBoxApplyGradient.SetValue(True)
        fgSizer27.Add(self.m_checkBoxApplyGradient,
                      0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_staticText115 = wx.StaticText(
            self, wx.ID_ANY, u"Bottom Gradient Colour:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText115.Wrap(-1)
        fgSizer27.Add(self.m_staticText115, 0,
                      wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_colourPickerBottom = wx.ColourPickerCtrl(self, wx.ID_ANY, wx.Colour(
            255, 255, 255), wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE)
        fgSizer27.Add(self.m_colourPickerBottom, 0, wx.ALL, 5)

        bSizer96.Add(fgSizer27, 0, wx.EXPAND | wx.LEFT, 5)

        m_radioBoxKeyBindingChoices = [
            u"L-key displays this dialog", u"L-key toggles between grey and black"]
        self.m_radioBoxKeyBinding = wx.RadioBox(
            self, wx.ID_ANY, u"Keybinding Behaviour", wx.DefaultPosition, wx.DefaultSize, m_radioBoxKeyBindingChoices, 1, wx.RA_SPECIFY_COLS)
        self.m_radioBoxKeyBinding.SetSelection(0)
        bSizer96.Add(self.m_radioBoxKeyBinding, 0, wx.ALL | wx.EXPAND, 5)

        bSizer96.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        m_sdbSizer6 = wx.StdDialogButtonSizer()
        self.m_sdbSizer6OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer6.AddButton(self.m_sdbSizer6OK)
        self.m_sdbSizer6Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer6.AddButton(self.m_sdbSizer6Cancel)
        m_sdbSizer6.Realize()

        bSizer96.Add(
            m_sdbSizer6, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.EXPAND, 5)

        self.SetSizer(bSizer96)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.m_colourPickerTop.Bind(
            wx.EVT_COLOURPICKER_CHANGED, self.onTopColourChanged)
        self.m_checkBoxApplyGradient.Bind(
            wx.EVT_CHECKBOX, self.onApplyGradient)
        self.m_colourPickerBottom.Bind(
            wx.EVT_COLOURPICKER_CHANGED, self.onBottomColourChanged)
        self.m_radioBoxKeyBinding.Bind(
            wx.EVT_RADIOBOX, self.onKeyBindingChanged)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def onTopColourChanged(self, evt):
        evt.Skip()

    def onApplyGradient(self, evt):
        evt.Skip()

    def onBottomColourChanged(self, evt):
        evt.Skip()

    def onKeyBindingChanged(self, evt):
        evt.Skip()
