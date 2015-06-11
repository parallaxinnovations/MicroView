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
# Class HistogramInfoGUI
###########################################################################


class HistogramInfoGUI (wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(
            719, -1), style=wx.TAB_TRAVERSAL)

        bSizer66 = wx.BoxSizer(wx.HORIZONTAL)

        bSizer185 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText58 = wx.StaticText(
            self, wx.ID_ANY, u"Nearest Data Value:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText58.Wrap(-1)
        bSizer185.Add(self.m_staticText58, 0, wx.ALL, 5)

        self.m_staticTextNearestDataValue = wx.StaticText(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(150, -1), 0)
        self.m_staticTextNearestDataValue.Wrap(-1)
        bSizer185.Add(self.m_staticTextNearestDataValue, 0, wx.ALL, 5)

        bSizer66.Add(bSizer185, 0, 0, 0)

        bSizer186 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticTextSelectedVolumeLabel = wx.StaticText(
            self, wx.ID_ANY, u"Selected Volume:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextSelectedVolumeLabel.Wrap(-1)
        bSizer186.Add(self.m_staticTextSelectedVolumeLabel, 0, wx.ALL, 5)

        self.m_staticTextSelectedVolume = wx.StaticText(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(100, -1), 0)
        self.m_staticTextSelectedVolume.Wrap(-1)
        bSizer186.Add(self.m_staticTextSelectedVolume, 0, wx.ALL, 5)

        bSizer66.Add(bSizer186, 0, 0, 0)

        bSizer187 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText62 = wx.StaticText(
            self, wx.ID_ANY, u"Volume Fraction:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText62.Wrap(-1)
        bSizer187.Add(self.m_staticText62, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.m_staticTextVolumeFraction = wx.StaticText(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(150, -1), 0)
        self.m_staticTextVolumeFraction.Wrap(-1)
        bSizer187.Add(self.m_staticTextVolumeFraction, 0, wx.ALL, 5)

        bSizer66.Add(bSizer187, 0, 0, 0)

        self.SetSizer(bSizer66)
        self.Layout()

    def __del__(self):
        pass
