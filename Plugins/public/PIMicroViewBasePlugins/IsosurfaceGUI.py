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
# Class IsosurfaceGUI
###########################################################################


class IsosurfaceGUI (wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(
            428, 572), style=wx.TAB_TRAVERSAL)

        bSizer87 = wx.BoxSizer(wx.VERTICAL)

        bSizer88 = wx.BoxSizer(wx.VERTICAL)

        sbSizerIsosurfaceParameters = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, u"Isosurface Parameters"), wx.VERTICAL)

        bSizer99 = wx.BoxSizer(wx.VERTICAL)

        fgSizer21 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer21.SetFlexibleDirection(wx.BOTH)
        fgSizer21.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText108 = wx.StaticText(
            self, wx.ID_ANY, u"Image Threshold:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText108.Wrap(-1)
        fgSizer21.Add(
            self.m_staticText108, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_textCtrlImageThreshold = wx.TextCtrl(
            self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_textCtrlImageThreshold.SetMaxLength(0)
        self.m_textCtrlImageThreshold.SetToolTipString(
            u"Defines the grayscale value to use for generating an isosurface.")

        fgSizer21.Add(self.m_textCtrlImageThreshold, 0, wx.ALL, 5)

        self.m_staticText109 = wx.StaticText(
            self, wx.ID_ANY, u"Surface Quality Factor (%):", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText109.Wrap(-1)
        fgSizer21.Add(
            self.m_staticText109, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_sliderSurfaceQuality = wx.Slider(
            self, wx.ID_ANY, 25, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_BOTTOM | wx.SL_LABELS)
        self.m_sliderSurfaceQuality.SetToolTipString(
            u"Defines an image resample value, between zero and one. Each dimension of the input image is resampled by this factor prior to determining the isosurface.  Set this to a small value to generate a coarse surface quickly, then increase to generate a higher quality surface.")

        fgSizer21.Add(self.m_sliderSurfaceQuality, 0, wx.ALL | wx.EXPAND, 5)

        self.m_staticText110 = wx.StaticText(
            self, wx.ID_ANY, u"Decimation Factor (%):", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText110.Wrap(-1)
        fgSizer21.Add(
            self.m_staticText110, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_sliderDecimationFactor = wx.Slider(
            self, wx.ID_ANY, 0, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.m_sliderDecimationFactor.SetToolTipString(
            u"Defines percentage of isosurface elements to remove in final processing step.")

        fgSizer21.Add(self.m_sliderDecimationFactor, 0, wx.ALL | wx.EXPAND, 5)

        self.m_staticText111 = wx.StaticText(
            self, wx.ID_ANY, u"Surface Color:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText111.Wrap(-1)
        fgSizer21.Add(
            self.m_staticText111, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_colourPicker = wx.ColourPickerCtrl(self, wx.ID_ANY, wx.Colour(
            255, 255, 255), wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE)
        fgSizer21.Add(self.m_colourPicker, 0, wx.ALL, 5)

        bSizer99.Add(fgSizer21, 1, wx.EXPAND, 5)

        self.m_checkBoxImageSmoothing = wx.CheckBox(
            self, wx.ID_ANY, u"Enable Image Smoothing", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer99.Add(self.m_checkBoxImageSmoothing, 0, wx.ALL, 5)

        self.m_checkBoxClipping = wx.CheckBox(
            self, wx.ID_ANY, u"Clip Surface with current ROI", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer99.Add(self.m_checkBoxClipping, 0, wx.ALL, 5)

        sbSizerIsosurfaceParameters.Add(bSizer99, 1, wx.EXPAND, 5)

        bSizer88.Add(sbSizerIsosurfaceParameters, 0, wx.EXPAND, 5)

        sbSizerSurfaceInformation = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, u"Surface Information"), wx.VERTICAL)

        fgSizer20 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer20.SetFlexibleDirection(wx.BOTH)
        fgSizer20.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText102 = wx.StaticText(
            self, wx.ID_ANY, u"Area:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText102.Wrap(-1)
        fgSizer20.Add(self.m_staticText102, 0, wx.ALL, 5)

        self.m_staticTextArea = wx.StaticText(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextArea.Wrap(-1)
        fgSizer20.Add(self.m_staticTextArea, 0, wx.ALL, 5)

        self.m_staticText104 = wx.StaticText(
            self, wx.ID_ANY, u"Volume:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText104.Wrap(-1)
        fgSizer20.Add(self.m_staticText104, 0, wx.ALL, 5)

        self.m_staticTextVolume = wx.StaticText(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextVolume.Wrap(-1)
        fgSizer20.Add(self.m_staticTextVolume, 0, wx.ALL, 5)

        self.m_staticText106 = wx.StaticText(
            self, wx.ID_ANY, u"Polygon Count:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText106.Wrap(-1)
        fgSizer20.Add(self.m_staticText106, 0, wx.ALL, 5)

        self.m_staticTextPolygonCount = wx.StaticText(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextPolygonCount.Wrap(-1)
        fgSizer20.Add(self.m_staticTextPolygonCount, 0, wx.ALL, 5)

        self.m_staticText226 = wx.StaticText(
            self, wx.ID_ANY, u"Region Count:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText226.Wrap(-1)
        fgSizer20.Add(self.m_staticText226, 0, wx.ALL, 5)

        self.m_staticTextRegionCount = wx.StaticText(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextRegionCount.Wrap(-1)
        fgSizer20.Add(self.m_staticTextRegionCount, 0, wx.ALL, 5)

        sbSizerSurfaceInformation.Add(fgSizer20, 1, wx.EXPAND, 5)

        bSizer88.Add(sbSizerSurfaceInformation, 0, wx.EXPAND, 5)

        sbSizerCommands = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, u"Commands"), wx.VERTICAL)

        fgSizer19 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer19.SetFlexibleDirection(wx.BOTH)
        fgSizer19.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_buttonClear = wx.Button(
            self, wx.ID_ANY, u"Clear", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_buttonClear.Enable(False)

        fgSizer19.Add(self.m_buttonClear, 0, wx.ALL, 5)

        self.m_buttonSaveSurface = wx.Button(
            self, wx.ID_ANY, u"Save Surface", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_buttonSaveSurface.Enable(False)

        fgSizer19.Add(self.m_buttonSaveSurface, 0, wx.ALL, 5)

        self.m_buttonUpdate = wx.Button(
            self, wx.ID_ANY, u"Update", wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer19.Add(self.m_buttonUpdate, 0, wx.ALL, 5)

        sbSizerCommands.Add(fgSizer19, 1, wx.EXPAND, 5)

        bSizer88.Add(sbSizerCommands, 0, wx.EXPAND, 5)

        bSizer87.Add(bSizer88, 0, 0, 5)

        self.SetSizer(bSizer87)
        self.Layout()

    def __del__(self):
        pass
