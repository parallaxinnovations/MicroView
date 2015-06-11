# -*- coding: utf-8 -*-


import wx
import wx.lib.agw.aui

from zope import event

import vtkAtamai.RenderPane2D
import vtkEVS.GEWindowLevelInteractionMode

from PI.visualization.MicroView.events import ModePaletteEvent

import StockItems

###########################################################################
# Class MicroViewModePalette
###########################################################################


class MicroViewModePalette (wx.lib.agw.aui.AuiToolBar):

    def __init__(self, parent):

        self._Panes = []
        self._WindowLevelModes = [
            vtkEVS.GEWindowLevelInteractionMode.GEWindowLevelInteractionMode(), ]
        self._SectionIndex = [0, ]

        # stock item manager
        self._stockicons = StockItems.StockIconFactory()

        wx.lib.agw.aui.AuiToolBar.__init__(
            self, parent, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.lib.agw.aui.AUI_TB_HORZ_LAYOUT)

        self._ids = [wx.NewId() for i in range(7)]

        self.AddTool(self._ids[0], u"tool", self._stockicons.getBitmap(
            'rotate'), wx.NullBitmap, wx.ITEM_RADIO, wx.EmptyString, u"Rotate Image", None)
        self.AddTool(self._ids[1], u"tool", self._stockicons.getBitmap(
            'winlev'), wx.NullBitmap, wx.ITEM_RADIO, wx.EmptyString, u"Adjust window/level", None)
        self.AddTool(self._ids[2], u"tool", self._stockicons.getBitmap(
            'zoom'),   wx.NullBitmap, wx.ITEM_RADIO, wx.EmptyString, u"Adjust image zoom", None)
        self.AddTool(self._ids[3], u"tool", self._stockicons.getBitmap(
            'pan'),    wx.NullBitmap, wx.ITEM_RADIO, wx.EmptyString, u"Pan image", None)
        self.AddTool(self._ids[4], u"tool", self._stockicons.getBitmap(
            'slice'),  wx.NullBitmap, wx.ITEM_RADIO, wx.EmptyString, u"Adjust image slice position", None)
#        self.AddTool(self._ids[5], u"tool", self._stockicons.getBitmap(
#            'roi'),  wx.NullBitmap, wx.ITEM_RADIO, wx.EmptyString, u"Draw ROIs", None)
#        self.AddTool(self._ids[6], u"tool", self._stockicons.getBitmap(
#            'line_draw'),  wx.NullBitmap, wx.ITEM_RADIO, wx.EmptyString, u"Draw Line Propfile", None)

        self.Realize()

        # Connect Events
        self.Bind(wx.EVT_TOOL, self.onButtonRotate, id=self._ids[0])
        self.Bind(wx.EVT_TOOL, self.onButtonWinLevel, id=self._ids[1])
        self.Bind(wx.EVT_TOOL, self.onButtonZoom, id=self._ids[2])
        self.Bind(wx.EVT_TOOL, self.onButtonPan, id=self._ids[3])
        self.Bind(wx.EVT_TOOL, self.onButtonSlice, id=self._ids[4])
#        self.Bind(wx.EVT_TOOL, self.onButtonDrawROI, id=self._ids[5])
#        self.Bind(wx.EVT_TOOL, self.onButtonDrawLine, id=self._ids[6])

    def EnableRotate(self, state=True):
        self.EnableTool(self._ids[0], state)
        self.Realize()

    def EnableWindowLevel(self, state=True):
        self.EnableTool(self._ids[1], state)
        self.Realize()

    def EnableSlice(self, state=True):
        self.EnableTool(self._ids[4], state)
        self.Realize()

    def SendUserEvent(self, value):
        event.notify(ModePaletteEvent(value))

    def SetLookupTable(self, table, i=0):
        self._WindowLevelModes[i].SetLookupTable(table)

    def SetDataRange(self, dataRange, i=0):
        self._WindowLevelModes[i].SetDataRange(dataRange)

    def Reset(self):
        self.SetMode(1)

    def SetUseMinMaxForWinLev(self, bool):
        for wl in self._WindowLevelModes:
            wl.SetUseMinMax(bool)

    def SetMode(self, i):
        tool = self._ids[i - 1]
        self.ToggleTool(tool, True)

    def GetMode(self):
        for i in range(len(self._ids)):
            if self.GetToolToggled(self._ids[i]):
                return i + 1

    def AddPane(self, pane):
        self._Panes.append(pane)

    def RemovePane(self, pane):
        if pane in self._Panes:
            self._Panes.remove(pane)

    def activateMode(self, i):

        # self.SetMode(i+1)

        if i == 1:
            for pane in self._Panes:
                if isinstance(pane, vtkAtamai.RenderPane2D.RenderPane2D):
                    pane.BindPanToButton(1)
                    pane._B1Action = 'pan'
                else:
                    pane.BindRotateToButton(1)
                    pane._B1Action = 'rotate'
        elif i == 2:
            N_Sect = len(self._SectionIndex)
            for i_group in range(N_Sect):   # for each group
                idx1 = self._SectionIndex[i_group]
                if i_group + 1 < N_Sect:
                    idx2 = self._SectionIndex[i_group + 1]
                else:
                    idx2 = len(self._Panes)
                for j in range(idx1, idx2):
                    self._Panes[j].BindModeToButton(
                        self._WindowLevelModes[i_group], 1)
                    self._Panes[j]._B1Action = 'winlev'
        elif i == 3:
            for pane in self._Panes:
                pane.BindZoomToButton(1)
                pane._B1Action = 'zoom'
        elif i == 4:
            for pane in self._Panes:
                pane.BindPanToButton(1)
                pane._B1Action = 'pan'
        elif i == 5:
            for pane in self._Panes:
                if isinstance(pane, vtkAtamai.RenderPane2D.RenderPane2D):
                    pane.BindPushToButton(1)
                    pane._B1Action = 'push'
                else:
                    pane.BindActorToButton(1)
                    pane._B1Action = 'actor'

        self.SendUserEvent(i)

    def onButtonRotate(self, evt):
        self.activateMode(1)

    def onButtonZoom(self, evt):
        self.activateMode(3)

    def onButtonPan(self, evt):
        self.activateMode(4)

    def onButtonSlice(self, evt):
        self.activateMode(5)

    def onButtonDrawROI(self, evt):
        self.SendUserEvent(5)

    def onButtonDrawLine(self, evt):
        self.SendUserEvent(6)

    def onButtonWinLevel(self, evt):
        self.activateMode(2)
