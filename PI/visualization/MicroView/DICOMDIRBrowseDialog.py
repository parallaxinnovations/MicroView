# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun  5 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.propgrid as pg

###########################################################################
## Class DICOMDIRBrowseDialog
###########################################################################

class DICOMDIRBrowseDialog ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"DICOMDIR Browser", pos = wx.DefaultPosition, size = wx.Size( 812,602 ), style = wx.DEFAULT_DIALOG_STYLE )

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

        bSizer145 = wx.BoxSizer( wx.VERTICAL )

        bSizer199 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_panelMainArea = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_panelMainArea.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) )

        bSizer199.Add( self.m_panelMainArea, 1, wx.EXPAND |wx.ALL, 5 )

        bSizer197 = wx.BoxSizer( wx.VERTICAL )

        bSizer197.SetMinSize( wx.Size( -1,180 ) )
        sbSizer77 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Details" ), wx.VERTICAL )

        self.m_propertyGrid = pg.PropertyGrid(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.propgrid.PG_AUTO_SORT|wx.propgrid.PG_DEFAULT_STYLE)
        sbSizer77.Add( self.m_propertyGrid, 1, wx.EXPAND, 5 )

        self.m_searchCtrl = wx.SearchCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        self.m_searchCtrl.ShowSearchButton( True )
        self.m_searchCtrl.ShowCancelButton( True )
        sbSizer77.Add( self.m_searchCtrl, 0, wx.BOTTOM|wx.EXPAND|wx.TOP, 5 )


        bSizer197.Add( sbSizer77, 1, wx.EXPAND|wx.RIGHT, 5 )

        sbSizer76 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Preview" ), wx.VERTICAL )

        sbSizer76.SetMinSize( wx.Size( 260,260 ) )
        self.m_bitmapPreview = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
        sbSizer76.Add( self.m_bitmapPreview, 1, wx.EXPAND, 5 )


        bSizer197.Add( sbSizer76, 0, wx.BOTTOM|wx.EXPAND|wx.RIGHT, 5 )


        bSizer199.Add( bSizer197, 0, wx.EXPAND, 5 )


        bSizer145.Add( bSizer199, 1, wx.EXPAND, 5 )

        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        bSizer145.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize();

        bSizer145.Add( m_sdbSizer1, 0, wx.BOTTOM|wx.EXPAND, 5 )


        self.SetSizer( bSizer145 )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.m_searchCtrl.Bind( wx.EVT_SEARCHCTRL_CANCEL_BTN, self.onSearchCancel )
        self.m_searchCtrl.Bind( wx.EVT_SEARCHCTRL_SEARCH_BTN, self.onSearch )
        self.m_searchCtrl.Bind( wx.EVT_TEXT_ENTER, self.onSearch )

    def __del__( self ):
        pass


    # Virtual event handlers, overide them in your derived class
    def onSearchCancel( self, event ):
        event.Skip()

    def onSearch( self, event ):
        event.Skip()



