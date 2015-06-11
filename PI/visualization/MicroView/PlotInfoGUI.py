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
# Class PlotInfoGUI
###########################################################################


class PlotInfoGUI (wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(
            617, -1), style=wx.TAB_TRAVERSAL)

        bSizer66 = wx.BoxSizer(wx.HORIZONTAL)
        #bSizer66 = wx.WrapSizer()

        bSizer183 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText60 = wx.StaticText(
            self, wx.ID_ANY, u"Line Length:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText60.Wrap(-1)
        bSizer183.Add(
            self.m_staticText60, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT | wx.LEFT, 5)

        self.m_staticTextLineLength = wx.StaticText(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(100, -1), 0)
        self.m_staticTextLineLength.Wrap(-1)
        bSizer183.Add(
            self.m_staticTextLineLength, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        bSizer66.Add(bSizer183, 0, 0, 0)

        bSizer184 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText58 = wx.StaticText(
            self, wx.ID_ANY, u"Nearest Data Value:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText58.Wrap(-1)
        bSizer184.Add(
            self.m_staticText58, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 5)

        self.m_staticTextNearestDataValue = wx.StaticText(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(260, -1), 0)
        self.m_staticTextNearestDataValue.Wrap(-1)
        bSizer184.Add(
            self.m_staticTextNearestDataValue, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        bSizer66.Add(bSizer184, 0, 0, 0)

        self.SetSizer(bSizer66)
        self.Layout()

    def __del__(self):
        pass
