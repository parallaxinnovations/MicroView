# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  6 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.grid

###########################################################################
## Class SpreadsheetGUI
###########################################################################

class SpreadsheetGUI ( wx.Panel ):

    def __init__( self, parent ):
	    wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 544,416 ), style = wx.TAB_TRAVERSAL )
	
	    bSizer100 = wx.BoxSizer( wx.VERTICAL )
	
	    self.m_grid = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
	
	    # Grid
	    self.m_grid.CreateGrid( 1, 26 )
	    self.m_grid.EnableEditing( True )
	    self.m_grid.EnableGridLines( True )
	    self.m_grid.EnableDragGridSize( False )
	    self.m_grid.SetMargins( 0, 0 )
	
	    # Columns
	    self.m_grid.EnableDragColMove( False )
	    self.m_grid.EnableDragColSize( True )
	    self.m_grid.SetColLabelSize( 30 )
	    self.m_grid.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
	
	    # Rows
	    self.m_grid.EnableDragRowSize( True )
	    self.m_grid.SetRowLabelSize( 80 )
	    self.m_grid.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
	
	    # Label Appearance
	
	    # Cell Defaults
	    self.m_grid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
	    bSizer100.Add( self.m_grid, 1, wx.ALL|wx.EXPAND, 5 )
	
	
	    self.SetSizer( bSizer100 )
	    self.Layout()
	
	    # Connect Events
	    self.m_grid.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.onGridCellRightClick )
	    self.m_grid.Bind( wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.onGridLabelLeftDClick )
	    self.m_grid.Bind( wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.onGridLabelRightClick )

    def __del__( self ):
	    pass


    # Virtual event handlers, overide them in your derived class
    def onGridCellRightClick( self, event ):
	    event.Skip()

    def onGridLabelLeftDClick( self, event ):
	    event.Skip()

    def onGridLabelRightClick( self, event ):
	    event.Skip()



