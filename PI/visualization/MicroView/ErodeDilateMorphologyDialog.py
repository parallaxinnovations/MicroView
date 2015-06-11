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
# Class ErodeDilateMorphologyDialog
###########################################################################


class ErodeDilateMorphologyDialog (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Erode/Dilate Image",
                           pos=wx.DefaultPosition, size=wx.Size(372, 152), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer161 = wx.BoxSizer(wx.VERTICAL)

        bSizer161.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        bSizer162 = wx.BoxSizer(wx.HORIZONTAL)

        fgSizer46 = wx.FlexGridSizer(0, 2, 0, 0)
        fgSizer46.SetFlexibleDirection(wx.BOTH)
        fgSizer46.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.m_staticText198 = wx.StaticText(
            self, wx.ID_ANY, u"Number of Iterations:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText198.Wrap(-1)
        fgSizer46.Add(
            self.m_staticText198, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_spinCtrlNumberIterations = wx.SpinCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 1000, 1)
        self.m_spinCtrlNumberIterations.SetMinSize(wx.Size(70, -1))

        fgSizer46.Add(self.m_spinCtrlNumberIterations, 0, wx.ALL, 5)

        bSizer162.Add(fgSizer46, 0, 0, 5)

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
