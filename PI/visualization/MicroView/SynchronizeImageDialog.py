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
# Class SynchronizeImageDialog
###########################################################################


class SynchronizeImageDialog (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY, title=u"Synchronize Images",
                           pos=wx.DefaultPosition, size=wx.Size(289, 264), style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)

        bSizer126 = wx.BoxSizer(wx.VERTICAL)

        sbSizer65 = wx.StaticBoxSizer(
            wx.StaticBox(self, wx.ID_ANY, u"Synchronize"), wx.VERTICAL)

        m_listBoxImageListChoices = []
        self.m_listBoxImageList = wx.ListBox(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBoxImageListChoices, wx.LB_MULTIPLE)
        sbSizer65.Add(self.m_listBoxImageList, 1, wx.ALL | wx.EXPAND, 5)

        bSizer168 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_checkBoxDisableSync = wx.CheckBox(
            self, wx.ID_ANY, u"Disable", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer168.Add(
            self.m_checkBoxDisableSync, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        bSizer168.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self.m_buttonReset = wx.Button(
            self, wx.ID_ANY, u"Reset", wx.DefaultPosition, wx.DefaultSize, 0)
        bSizer168.Add(self.m_buttonReset, 0, wx.ALL, 5)

        sbSizer65.Add(bSizer168, 0, wx.EXPAND, 5)

        bSizer126.Add(sbSizer65, 1, wx.EXPAND, 5)

        m_sdbSizer8 = wx.StdDialogButtonSizer()
        self.m_sdbSizer8OK = wx.Button(self, wx.ID_OK)
        m_sdbSizer8.AddButton(self.m_sdbSizer8OK)
        self.m_sdbSizer8Cancel = wx.Button(self, wx.ID_CANCEL)
        m_sdbSizer8.AddButton(self.m_sdbSizer8Cancel)
        m_sdbSizer8.Realize()

        bSizer126.Add(m_sdbSizer8, 0, wx.ALL | wx.EXPAND | wx.RIGHT, 5)

        self.SetSizer(bSizer126)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.m_listBoxImageList.Bind(
            wx.EVT_LISTBOX_DCLICK, self.onListBoxDoubleClick)
        self.m_checkBoxDisableSync.Bind(wx.EVT_CHECKBOX, self.onCheckBox)
        self.m_buttonReset.Bind(wx.EVT_BUTTON, self.onButtonReset)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def onListBoxDoubleClick(self, event):
        event.Skip()

    def onCheckBox(self, event):
        event.Skip()

    def onButtonReset(self, event):
        event.Skip()
