import StatisticsGUI
import logging
import collections
import StockItems
from zope import component
# don't change this
from PI.visualization.MicroView.interfaces import IMicroViewOutput


class StatisticsGUIC(StatisticsGUI.StatisticsGUI):

    def __init__(self, parent):

        StatisticsGUI.StatisticsGUI.__init__(self, parent)
        stockicons = StockItems.StockIconFactory()

        self.m_toolBar1.GetToolByPos(1).SetNormalBitmap(
            stockicons.getToolbarBitmap("scissors9"))
        self.m_toolBar1.Realize()
        self.Layout()

        # keep track of row insertion point
        self.current_row = 0

        # a dictionary of labels
        self._field_index = collections.OrderedDict()

        # map header label to column number
        for n in xrange(self.m_gridStatistics.GetNumberCols()):
            val = self.m_gridStatistics.GetColLabelValue(n)
            self._field_index[val] = n

    def insertRow(self, args):

        # add row if we need one
        if self.current_row >= 5:
            logging.debug('add a row')
            self.m_gridStatistics.AppendRows()

        for key in args:
            if key not in self._field_index:
                # append a column at the end
                self.m_gridStatistics.AppendCols()
                n = self.m_gridStatistics.GetNumberCols()
                self._field_index[key] = n
            col = self._field_index[key]
            self.m_gridStatistics.SetCellValue(
                self.current_row, col, str(args[key]))
            if key not in ('Caption', 'Comment'):
                self.m_gridStatistics.SetReadOnly(self.current_row, col, True)

        self.m_gridStatistics.AutoSize()
        self.m_gridStatistics.SetColSize(self._field_index['Comment'], 500)

        # keep track of row -- first append a blank comment

        self.current_row += 1

    def onToolClicked(self, event):

        if event.GetId() == StatisticsGUI.STATS_SAVE:
            self.onFileSaveAs(event)
        elif event.GetId() == StatisticsGUI.STATS_CLEAR:
            self.onResultsClear(event)

    def onFileSaveAs(self, event):

        # get a global object that can manage saving results to disk
        object = component.getUtility(IMicroViewOutput)
        data = []

        nrows = self.m_gridStatistics.GetNumberRows()
        ncols = self.m_gridStatistics.GetNumberCols()

        # get header
        row = []
        for n in xrange(ncols):
            row.append(self.m_gridStatistics.GetColLabelValue(n))
        data.append(row)

        for nrow in xrange(nrows):
            row = []
            for ncol in xrange(ncols):
                row.append(self.m_gridStatistics.GetCellValue(nrow, ncol))
            data.append(row)

        object.SaveStatisticsToDisk(data)

    def onResultsClear(self, event):

        # Clear results
        self.m_gridStatistics.ClearGrid()
        self.current_row = 0
        self._results = []
        logging.info("Statistical results cleared")
