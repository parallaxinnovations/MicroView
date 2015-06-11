# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun  5 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.grid

STATS_SAVE = 1000
STATS_CLEAR = 1001

###########################################################################
## Class StatisticsGUI
###########################################################################

class StatisticsGUI ( wx.Panel ):

    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 927,563 ), style = wx.TAB_TRAVERSAL )

        bSizer79 = wx.BoxSizer( wx.VERTICAL )

        self.m_toolBar1 = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL )
        self.m_toolSaveStats = self.m_toolBar1.AddLabelTool( STATS_SAVE, u"tool", wx.ArtProvider.GetBitmap( wx.ART_FILE_SAVE_AS,  ), wx.NullBitmap, wx.ITEM_NORMAL, u"Save As...", u"Save statistics to a file", None )

        self.m_toolClearStats = self.m_toolBar1.AddLabelTool( STATS_CLEAR, u"tool", wx.ArtProvider.GetBitmap( wx.ART_CUT,  ), wx.NullBitmap, wx.ITEM_NORMAL, u"Clear results", u"Clear results", None )

        self.m_toolBar1.Realize()

        bSizer79.Add( self.m_toolBar1, 0, wx.EXPAND, 5 )

        self.m_gridStatistics = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

        # Grid
        self.m_gridStatistics.CreateGrid( 5, 17 )
        self.m_gridStatistics.EnableEditing( True )
        self.m_gridStatistics.EnableGridLines( True )
        self.m_gridStatistics.EnableDragGridSize( False )
        self.m_gridStatistics.SetMargins( 0, 0 )

        # Columns
        self.m_gridStatistics.SetColSize( 0, 79 )
        self.m_gridStatistics.SetColSize( 1, 92 )
        self.m_gridStatistics.SetColSize( 2, 33 )
        self.m_gridStatistics.SetColSize( 3, 33 )
        self.m_gridStatistics.SetColSize( 4, 33 )
        self.m_gridStatistics.SetColSize( 5, 33 )
        self.m_gridStatistics.SetColSize( 6, 32 )
        self.m_gridStatistics.SetColSize( 7, 32 )
        self.m_gridStatistics.SetColSize( 8, 50 )
        self.m_gridStatistics.SetColSize( 9, 80 )
        self.m_gridStatistics.SetColSize( 10, 41 )
        self.m_gridStatistics.SetColSize( 11, 45 )
        self.m_gridStatistics.SetColSize( 12, 47 )
        self.m_gridStatistics.SetColSize( 13, 67 )
        self.m_gridStatistics.SetColSize( 14, 45 )
        self.m_gridStatistics.SetColSize( 15, 85 )
        self.m_gridStatistics.AutoSizeColumns()
        self.m_gridStatistics.EnableDragColMove( False )
        self.m_gridStatistics.EnableDragColSize( True )
        self.m_gridStatistics.SetColLabelSize( 30 )
        self.m_gridStatistics.SetColLabelValue( 0, u"Caption" )
        self.m_gridStatistics.SetColLabelValue( 1, u"Time-stamp" )
        self.m_gridStatistics.SetColLabelValue( 2, u"Filename/Title" )
        self.m_gridStatistics.SetColLabelValue( 3, u"X" )
        self.m_gridStatistics.SetColLabelValue( 4, u"Y" )
        self.m_gridStatistics.SetColLabelValue( 5, u"Z" )
        self.m_gridStatistics.SetColLabelValue( 6, u"ROI-Width-X" )
        self.m_gridStatistics.SetColLabelValue( 7, u"ROI-Width-Y" )
        self.m_gridStatistics.SetColLabelValue( 8, u"ROI-Width-Z" )
        self.m_gridStatistics.SetColLabelValue( 9, u"Chan." )
        self.m_gridStatistics.SetColLabelValue( 10, u"ROI-VoxelCount" )
        self.m_gridStatistics.SetColLabelValue( 11, u"ROI-Min" )
        self.m_gridStatistics.SetColLabelValue( 12, u"ROI-Max" )
        self.m_gridStatistics.SetColLabelValue( 13, u"ROI-Mean" )
        self.m_gridStatistics.SetColLabelValue( 14, u"ROI-Stdev" )
        self.m_gridStatistics.SetColLabelValue( 15, u"ROI-Total" )
        self.m_gridStatistics.SetColLabelValue( 16, u"Comment" )
        self.m_gridStatistics.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )

        # Rows
        self.m_gridStatistics.EnableDragRowSize( True )
        self.m_gridStatistics.SetRowLabelSize( 80 )
        self.m_gridStatistics.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )

        # Label Appearance

        # Cell Defaults
        self.m_gridStatistics.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
        bSizer79.Add( self.m_gridStatistics, 0, wx.ALL|wx.EXPAND, 5 )


        self.SetSizer( bSizer79 )
        self.Layout()

        # Connect Events
        self.Bind( wx.EVT_TOOL, self.onToolClicked, id = self.m_toolSaveStats.GetId() )
        self.Bind( wx.EVT_TOOL, self.onToolClicked, id = self.m_toolClearStats.GetId() )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def onToolClicked( self, event ):
        event.Skip()



