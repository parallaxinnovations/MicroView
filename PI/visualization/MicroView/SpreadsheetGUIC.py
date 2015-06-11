import SpreadsheetGUI
import SpreadsheetState
from PI.visualization.MicroView.interfaces import ISpreadsheet
from zope import interface
import wx


class SpreadsheetGUIC(SpreadsheetGUI.SpreadsheetGUI):

    interface.implements(ISpreadsheet)

    def __init__(self, parent, **kw):

        self._index = 0
        if 'index' in kw:
            self._index = kw['index']
            del(kw['index'])

        SpreadsheetGUI.SpreadsheetGUI.__init__(self, parent)
        self._viewerState = SpreadsheetState.SpreadsheetState()

    def GetPageState(self):
        return self._viewerState

    def GetSpreadsheetIndex(self):
        return self._index

    def GetTable(self):

        ncols = self.m_grid.GetNumberCols()
        nrows = self.m_grid.GetNumberRows()

        data_table = []
        for j in xrange(nrows):
            row = []
            for i in xrange(ncols):
                row.append(self.m_grid.GetCellValue(j, i))
            data_table.append(row)

        return data_table

    def onGridLabelLeftDClick( self, event ):
        """allow user to edit column label"""
        col = event.GetCol()
        label = self.m_grid.GetColLabelValue(col)

        if col != -1:

            dlg = wx.TextEntryDialog(
                self, 'Column Label:',
                'Enter new column label', 'Column Label')

            dlg.SetValue(label)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    value = dlg.GetValue()
                else:
                    return
            finally:
                dlg.Destroy()

            self.m_grid.SetColLabelValue(col, value)

    def onGridLabelRightClick( self, event ):

        # present user with a context-sensitive popup menu
        rows = self.m_grid.GetSelectedRows()
        cols = self.m_grid.GetSelectedCols()

        # display a popenu
        menu = wx.Menu()

        if len(rows) > 0:
            _id = wx.NewId()
            if len(rows) == 1:
                menu.Append(_id, "Add Row", "Add a row below the selected row")
                self.Bind(wx.EVT_MENU, lambda e, rows=rows: self.AddRow(rows[0]), id=_id)

            # permit deletion only if contiguous
            _min = min(rows)
            _max = max(rows)
            if len(rows) == (_max - _min + 1):
                # contiguous

                _id = wx.NewId()
                if len(rows) == 1:
                    menu.Append(_id, "Delete Row", "Delete the selected row")
                else:
                    menu.Append(_id, "Delete Rows", "Delete the selected rows")
                self.Bind(wx.EVT_MENU, lambda e, rows=rows: self.DeleteRows(_min, len(rows)), id=_id)

        if len(cols) > 0:
            if len(cols) == 1:
                _id = wx.NewId()
                menu.Append(_id, "Add Column", "Add a column to the right of the selected column")
                self.Bind(wx.EVT_MENU, lambda e, cols=cols: self.AddColumn(cols[0]), id=_id)
    
            # permit deletion only if contiguous
            _min = min(cols)
            _max = max(cols)
            if len(cols) == (_max - _min + 1):
                # contiguous    
    
                _id = wx.NewId()
                if len(cols) == 1:
                    menu.Append(_id, "Delete Column", "Delete the selected column")
                else:
                    menu.Append(_id, "Delete Columns", "Delete the selected columns")
                self.Bind(wx.EVT_MENU, lambda e, cols=cols: self.DeleteColumns(_min, len(cols)), id=_id)

        self.PopupMenu(menu)
        menu.Destroy()        

    def AddRow(self, row):
        self.m_grid.InsertRows(pos=row+1)

    def DeleteRows(self, row, num):
        self.m_grid.DeleteRows(pos=row, numRows=num)
        
    def AddColumn(self, column):
        self.m_grid.InsertCols(pos=column+1)

    def DeleteColumns(self, col, num):
        self.m_grid.DeleteCols(pos=col, numCols=num)

