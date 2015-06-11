# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  6 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

SHOW_AXES = 1000
SHOW_BORDERS = 1001
SHOW_ANATOMICAL_LABELS = 1002
SHOW_AXIAL_PLANE = 1003
SHOW_CORONAL_PLANE = 1004
SHOW_SAGITTAL_PLANE = 1005
SHOW_VOLUME_OUTLINE = 1006
SHOW_IMAGE_ORIENTATION_WIDGET = 1007
USE_IMAGE_INTERP = 1008
USE_DICOM_COORD_SYSTEM = 1009
MEASUREMENT_UNIT = 1010
ENABLE_INTEGER_STEPPING = 1011
USE_MINMAX = 1012
DISPLAY_SPLASHSCREEN = 1013

###########################################################################
## Class ApplicationSettingsGUI
###########################################################################

class ApplicationSettingsGUI ( wx.Panel ):

    def __init__( self, parent ):
	    wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 284,486 ), style = wx.TAB_TRAVERSAL )
	
	    bSizer67 = wx.BoxSizer( wx.VERTICAL )
	
	    self.m_notebook1 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_scrolledWindowDisplay = wx.ScrolledWindow( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
	    self.m_scrolledWindowDisplay.SetScrollRate( 5, 5 )
	    bSizer68 = wx.BoxSizer( wx.VERTICAL )
	
	    self.m_checkBox14 = wx.CheckBox( self.m_scrolledWindowDisplay, SHOW_AXES, u"Show Intersection Lines (e)", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkBox14.SetToolTipString( u"Indicate the positions of perpendicular cut planes with red, green and blue lines.\n" )
	
	    bSizer68.Add( self.m_checkBox14, 0, wx.ALL, 5 )
	
	    self.m_checkBox15 = wx.CheckBox( self.m_scrolledWindowDisplay, SHOW_BORDERS, u"Show Plane Borders (f)", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkBox15.SetToolTipString( u"Highlight axial, sagittal and coronal planes with red, green and blue borders." )
	
	    bSizer68.Add( self.m_checkBox15, 0, wx.ALL, 5 )
	
	    self.m_checkBox17 = wx.CheckBox( self.m_scrolledWindowDisplay, SHOW_ANATOMICAL_LABELS, u"Show Axes Labels (o)", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkBox17.SetToolTipString( u"Display (L)eft/(R)ight, (A)nterior/(P)osterior and (I)nferior/(S)uperior labels." )
	
	    bSizer68.Add( self.m_checkBox17, 0, wx.ALL, 5 )
	
	    self.m_checkBox18 = wx.CheckBox( self.m_scrolledWindowDisplay, SHOW_AXIAL_PLANE, u"Show Axial Plane (k)", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkBox18.SetToolTipString( u"Toggles the display of the axial cut plane." )
	
	    bSizer68.Add( self.m_checkBox18, 0, wx.ALL, 5 )
	
	    self.m_checkBox19 = wx.CheckBox( self.m_scrolledWindowDisplay, SHOW_CORONAL_PLANE, u"Show Coronal Plane (j)", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkBox19.SetToolTipString( u"Toggles the display of the coronal cut plane." )
	
	    bSizer68.Add( self.m_checkBox19, 0, wx.ALL, 5 )
	
	    self.m_checkBox20 = wx.CheckBox( self.m_scrolledWindowDisplay, SHOW_SAGITTAL_PLANE, u"Show Sagittal Plane (i)", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkBox20.SetToolTipString( u"Toggles the display of the sagittal cut plane." )
	
	    bSizer68.Add( self.m_checkBox20, 0, wx.ALL, 5 )
	
	    self.m_checkBox21 = wx.CheckBox( self.m_scrolledWindowDisplay, SHOW_VOLUME_OUTLINE, u"Show Volume Outline", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkBox21.SetToolTipString( u"Display a yellow boundary around the entire volume." )
	
	    bSizer68.Add( self.m_checkBox21, 0, wx.ALL, 5 )
	
	    self.m_checkBox69 = wx.CheckBox( self.m_scrolledWindowDisplay, SHOW_IMAGE_ORIENTATION_WIDGET, u"Show Image Orientation Widget", wx.DefaultPosition, wx.DefaultSize, 0 )
	    bSizer68.Add( self.m_checkBox69, 0, wx.ALL, 5 )
	
	    self.m_checkBox23 = wx.CheckBox( self.m_scrolledWindowDisplay, USE_IMAGE_INTERP, u"Use Image Interpolation", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkBox23.SetToolTipString( u"Use image interpolation on cut plane images." )
	
	    bSizer68.Add( self.m_checkBox23, 0, wx.ALL, 5 )
	
	    self.m_checkBoxUseDICOMCoords = wx.CheckBox( self.m_scrolledWindowDisplay, USE_DICOM_COORD_SYSTEM, u"Use DICOM coord system", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkBoxUseDICOMCoords.SetToolTipString( u"Use DICOM coordinate system" )
	
	    bSizer68.Add( self.m_checkBoxUseDICOMCoords, 0, wx.ALL, 5 )
	
	
	    self.m_scrolledWindowDisplay.SetSizer( bSizer68 )
	    self.m_scrolledWindowDisplay.Layout()
	    bSizer68.Fit( self.m_scrolledWindowDisplay )
	    self.m_notebook1.AddPage( self.m_scrolledWindowDisplay, u"Display", True )
	    self.m_scrolledWindowMiscellaneous = wx.ScrolledWindow( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
	    self.m_scrolledWindowMiscellaneous.SetScrollRate( 5, 5 )
	    bSizer69 = wx.BoxSizer( wx.VERTICAL )
	
	    self.m_checkBox24 = wx.CheckBox( self.m_scrolledWindowMiscellaneous, MEASUREMENT_UNIT, u"Show measurements in mm", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkBox24.SetToolTipString( u"Display all positions and distance measurements in either millimeters, or pixels." )
	
	    bSizer69.Add( self.m_checkBox24, 0, wx.ALL, 5 )
	
	    self.m_checkBox25 = wx.CheckBox( self.m_scrolledWindowMiscellaneous, ENABLE_INTEGER_STEPPING, u"Enable Integer Stepping (z)", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkBox25.SetToolTipString( u"If enabled, image cut plane positions are constrained to lie at the boundary of voxels.  If disabled, planes may be positioned at intermediate locations." )
	
	    bSizer69.Add( self.m_checkBox25, 0, wx.ALL, 5 )
	
	    self.m_checkBox26 = wx.CheckBox( self.m_scrolledWindowMiscellaneous, USE_MINMAX, u"Use Min/Max for W/L control", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkBox26.SetToolTipString( u"Controls how image brightness/contrast are manipulated. Turn this feature on to make adjustments by selecting min/max image values to display.  When deselected, adjust the settings by entering 'window' and 'level' values." )
	
	    bSizer69.Add( self.m_checkBox26, 0, wx.ALL, 5 )
	
	    self.m_checkBox28 = wx.CheckBox( self.m_scrolledWindowMiscellaneous, DISPLAY_SPLASHSCREEN, u"Display Splash at Startup", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkBox28.SetToolTipString( u"If enabled, MicroView will display a splash screen during program startup." )
	
	    bSizer69.Add( self.m_checkBox28, 0, wx.ALL, 5 )
	
	
	    self.m_scrolledWindowMiscellaneous.SetSizer( bSizer69 )
	    self.m_scrolledWindowMiscellaneous.Layout()
	    bSizer69.Fit( self.m_scrolledWindowMiscellaneous )
	    self.m_notebook1.AddPage( self.m_scrolledWindowMiscellaneous, u"Miscellaneous", False )
	
	    bSizer67.Add( self.m_notebook1, 1, wx.EXPAND |wx.ALL, 5 )
	
	    bSizer208 = wx.BoxSizer( wx.HORIZONTAL )
	
	    self.m_buttonSaveDefault = wx.Button( self, wx.ID_ANY, u"Save as Default", wx.DefaultPosition, wx.DefaultSize, 0 )
	    bSizer208.Add( self.m_buttonSaveDefault, 0, wx.ALL, 5 )
	
	
	    bSizer67.Add( bSizer208, 0, wx.EXPAND, 5 )
	
	
	    self.SetSizer( bSizer67 )
	    self.Layout()
	
	    # Connect Events
	    self.m_checkBox14.Bind( wx.EVT_CHECKBOX, self.onCheckBoxChange )
	    self.m_checkBox15.Bind( wx.EVT_CHECKBOX, self.onCheckBoxChange )
	    self.m_checkBox17.Bind( wx.EVT_CHECKBOX, self.onCheckBoxChange )
	    self.m_checkBox18.Bind( wx.EVT_CHECKBOX, self.onCheckBoxChange )
	    self.m_checkBox19.Bind( wx.EVT_CHECKBOX, self.onCheckBoxChange )
	    self.m_checkBox20.Bind( wx.EVT_CHECKBOX, self.onCheckBoxChange )
	    self.m_checkBox21.Bind( wx.EVT_CHECKBOX, self.onCheckBoxChange )
	    self.m_checkBox69.Bind( wx.EVT_CHECKBOX, self.onCheckBoxChange )
	    self.m_checkBox23.Bind( wx.EVT_CHECKBOX, self.onCheckBoxChange )
	    self.m_checkBoxUseDICOMCoords.Bind( wx.EVT_CHECKBOX, self.onCheckBoxChange )
	    self.m_checkBox24.Bind( wx.EVT_CHECKBOX, self.onCheckBoxChange )
	    self.m_checkBox25.Bind( wx.EVT_CHECKBOX, self.onCheckBoxChange )
	    self.m_checkBox26.Bind( wx.EVT_CHECKBOX, self.onCheckBoxChange )
	    self.m_checkBox28.Bind( wx.EVT_CHECKBOX, self.onCheckBoxChange )
	    self.m_buttonSaveDefault.Bind( wx.EVT_BUTTON, self.onSaveDefaultButton )

    def __del__( self ):
	    pass

    # Virtual event handlers, overide them in your derived class
    def onCheckBoxChange( self, event ):
	    event.Skip()

    def onSaveDefaultButton( self, event ):
	    event.Skip()


