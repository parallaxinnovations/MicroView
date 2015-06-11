import logging
import StockItems
import LogWindowGUI
from zope import component
# don't change this
from PI.visualization.MicroView.interfaces import IMicroViewOutput


class LogWindowGUIC(LogWindowGUI.LogWindowGUI):

    def __init__(self, parent):
        LogWindowGUI.LogWindowGUI.__init__(self, parent)
        stockicons = StockItems.StockIconFactory()

        self.m_toolBar2.GetToolByPos(1).SetNormalBitmap(
            stockicons.getToolbarBitmap("scissors9"))
        self.m_toolBar2.Realize()
        self.Layout()

    def WriteText(self, text):
        self.m_textCtrlLog.AppendText(text)

    def GetTextControl(self):
        return self.m_textCtrlLog

    def onToolClicked(self, event):

        if event.GetId() == LogWindowGUI.LOG_SAVE:
            self.onFileSaveAs(event)
        elif event.GetId() == LogWindowGUI.LOG_CLEAR:
            self.onResultsClear(event)

    def onFileSaveAs(self, event):

        # get a global object that can manage saving logging results to disk
        object = component.getUtility(IMicroViewOutput)
        object.SaveLogToDisk(self.m_textCtrlLog.GetValue())

    def onResultsClear(self, event):

        # Clear results
        self.m_textCtrlLog.Clear()
        logging.info("Log results cleared")
