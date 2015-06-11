import ResultsWindowGUI
import logging
import StockItems
import wx
from zope import interface, component
from PI.visualization.MicroView.interfaces import IResultWindow, IMicroViewOutput


class ResultsWindowGUIC(ResultsWindowGUI.ResultsWindowGUI):

    interface.implements(IResultWindow)

    def __init__(self, parent):

        ResultsWindowGUI.ResultsWindowGUI.__init__(self, parent)

        stockicons = StockItems.StockIconFactory()

        self.m_toolBar2.GetToolByPos(1).SetNormalBitmap(
            stockicons.getToolbarBitmap("scissors9"))
        self.m_toolBar2.Realize()
        self.Layout()

    def WriteText(self, text):

        for line in text.split('\n'):
            if (line.startswith('=') or line.startswith('#')):
                self.m_textCtrlLog.SetDefaultStyle(wx.TextAttr(wx.BLUE))
            else:
                self.m_textCtrlLog.SetDefaultStyle(wx.TextAttr(wx.BLACK))
            self.m_textCtrlLog.AppendText(line + '\n')

    def GetTextControl(self):
        return self.m_textCtrlLog

    def onToolClicked(self, event):

        if event.GetId() == ResultsWindowGUI.LOG_SAVE:
            self.onFileSaveAs(event)
        elif event.GetId() == ResultsWindowGUI.LOG_CLEAR:
            self.onResultsClear(event)

    def onFileSaveAs(self, event):

        # get a global object that can manage saving logging results to disk
        object = component.getUtility(IMicroViewOutput)
        object.SaveResultsToDisk(self.m_textCtrlLog.GetValue())

    def onResultsClear(self, event):

        # Clear results
        self.m_textCtrlLog.Clear()
        logging.info("Results window cleared")
