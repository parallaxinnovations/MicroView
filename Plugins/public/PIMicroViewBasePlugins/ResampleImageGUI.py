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
# Class ResampleImageGUI
###########################################################################


class ResampleImageGUI (wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(
            476, 132), style=wx.TAB_TRAVERSAL)

        fgSizer10 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer10.SetFlexibleDirection(wx.BOTH)
        fgSizer10.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText50 = wx.StaticText(
            self, wx.ID_ANY, u"Resample Factor:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText50.Wrap(-1)
        fgSizer10.Add(
            self.m_staticText50, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 5)

        self.m_textCtrlResampleFactor = wx.TextCtrl(
            self, wx.ID_ANY, u"2.0", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_textCtrlResampleFactor.SetMaxLength(0)
        fgSizer10.Add(self.m_textCtrlResampleFactor, 0, wx.ALL, 5)

        self.m_staticText51 = wx.StaticText(
            self, wx.ID_ANY, u"Original voxel size:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText51.Wrap(-1)
        fgSizer10.Add(self.m_staticText51, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.m_staticTextOriginalSize = wx.StaticText(
            self, wx.ID_ANY, u"100.000 x 100.000 x 100.000", wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_staticTextOriginalSize.Wrap(-1)
        self.m_staticTextOriginalSize.SetMinSize(wx.Size(240, -1))

        fgSizer10.Add(self.m_staticTextOriginalSize, 0, wx.ALL, 5)

        self.m_staticText53 = wx.StaticText(
            self, wx.ID_ANY, u"Resampled voxel size:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText53.Wrap(-1)
        fgSizer10.Add(self.m_staticText53, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        self.m_staticTextResampledSize = wx.StaticText(
            self, wx.ID_ANY, u"200.000 x 200.000 x 200.000", wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_staticTextResampledSize.Wrap(-1)
        self.m_staticTextResampledSize.SetMinSize(wx.Size(240, -1))

        fgSizer10.Add(self.m_staticTextResampledSize, 0, wx.ALL, 5)

        self.m_buttonResample = wx.Button(
            self, wx.ID_ANY, u"Resample...", wx.DefaultPosition, wx.DefaultSize, 0)
        fgSizer10.Add(self.m_buttonResample, 0, wx.ALL, 5)

        self.SetSizer(fgSizer10)
        self.Layout()

        # Connect Events
        self.m_buttonResample.Bind(wx.EVT_BUTTON, self.onResampleButton)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def onResampleButton(self, event):
        event.Skip()
