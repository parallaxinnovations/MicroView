# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  6 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class StandardROIGUI
###########################################################################

class StandardROIGUI ( wx.Panel ):

    def __init__( self, parent ):
	    wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 371,595 ), style = wx.TAB_TRAVERSAL )
	
	    bSizer83 = wx.BoxSizer( wx.VERTICAL )
	
	    bSizer165 = wx.BoxSizer( wx.VERTICAL )
	
	    fgSizer42 = wx.FlexGridSizer( 0, 3, 0, 0 )
	    fgSizer42.SetFlexibleDirection( wx.BOTH )
	    fgSizer42.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
	
	    self.m_staticText185 = wx.StaticText( self, wx.ID_ANY, u"Tool:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText185.Wrap( -1 )
	    fgSizer42.Add( self.m_staticText185, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
	
	    m_choiceToolChoices = [ u"Box", u"Cylinder", u"Ellipsoid" ]
	    self.m_choiceTool = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choiceToolChoices, 0 )
	    self.m_choiceTool.SetSelection( 0 )
	    fgSizer42.Add( self.m_choiceTool, 0, wx.ALL|wx.EXPAND, 5 )
	
	    self.m_checkBoxAllowArbOrientation = wx.CheckBox( self, wx.ID_ANY, u"Link Image Plane", wx.DefaultPosition, wx.DefaultSize, 0 )
	    fgSizer42.Add( self.m_checkBoxAllowArbOrientation, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_staticText186 = wx.StaticText( self, wx.ID_ANY, u"Orientation:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText186.Wrap( -1 )
	    fgSizer42.Add( self.m_staticText186, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
	
	    m_choiceOrientationChoices = [ u"X", u"Y", u"Z" ]
	    self.m_choiceOrientation = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choiceOrientationChoices, 0 )
	    self.m_choiceOrientation.SetSelection( 2 )
	    fgSizer42.Add( self.m_choiceOrientation, 0, wx.ALL|wx.EXPAND, 5 )
	
	
	    fgSizer42.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
	
	    self.m_staticText187 = wx.StaticText( self, wx.ID_ANY, u"Units:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText187.Wrap( -1 )
	    fgSizer42.Add( self.m_staticText187, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
	
	    m_choiceUnitsChoices = [ u"mm", u"pixels" ]
	    self.m_choiceUnits = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choiceUnitsChoices, 0 )
	    self.m_choiceUnits.SetSelection( 0 )
	    fgSizer42.Add( self.m_choiceUnits, 0, wx.ALL|wx.EXPAND, 5 )
	
	
	    bSizer165.Add( fgSizer42, 0, 0, 5 )
	
	
	    bSizer83.Add( bSizer165, 0, wx.EXPAND, 5 )
	
	    sbSizer37 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"ROI Size" ), wx.VERTICAL )
	
	    bSizer173 = wx.BoxSizer( wx.HORIZONTAL )
	
	    fgSizer43 = wx.FlexGridSizer( 0, 3, 0, 0 )
	    fgSizer43.SetFlexibleDirection( wx.BOTH )
	    fgSizer43.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
	
	    self.m_staticText188 = wx.StaticText( self, wx.ID_ANY, u"X:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText188.Wrap( -1 )
	    fgSizer43.Add( self.m_staticText188, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_textCtrlROISizeX = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 60,-1 ), wx.TE_PROCESS_ENTER )
	    fgSizer43.Add( self.m_textCtrlROISizeX, 0, wx.ALL, 5 )
	
	    self.m_sliderSizeX = wx.Slider( self, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
	    fgSizer43.Add( self.m_sliderSizeX, 1, wx.ALL, 5 )
	
	    self.m_staticText1881 = wx.StaticText( self, wx.ID_ANY, u"Y:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText1881.Wrap( -1 )
	    fgSizer43.Add( self.m_staticText1881, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_textCtrlROISizeY = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 60,-1 ), wx.TE_PROCESS_ENTER )
	    fgSizer43.Add( self.m_textCtrlROISizeY, 0, wx.ALL, 5 )
	
	    self.m_sliderSizeY = wx.Slider( self, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
	    fgSizer43.Add( self.m_sliderSizeY, 0, wx.ALL, 5 )
	
	    self.m_staticText18811 = wx.StaticText( self, wx.ID_ANY, u"Z:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText18811.Wrap( -1 )
	    fgSizer43.Add( self.m_staticText18811, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_textCtrlROISizeZ = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 60,-1 ), wx.TE_PROCESS_ENTER )
	    fgSizer43.Add( self.m_textCtrlROISizeZ, 0, wx.ALL, 5 )
	
	    self.m_sliderSizeZ = wx.Slider( self, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
	    fgSizer43.Add( self.m_sliderSizeZ, 0, wx.ALL, 5 )
	
	
	    bSizer173.Add( fgSizer43, 0, wx.EXPAND, 5 )
	
	    self.m_toggleBtnSizeLinking = wx.ToggleButton( self, wx.ID_ANY, u"Link X/Y", wx.DefaultPosition, wx.DefaultSize, 0 )
	    bSizer173.Add( self.m_toggleBtnSizeLinking, 0, wx.ALL, 5 )
	
	
	    sbSizer37.Add( bSizer173, 1, wx.EXPAND, 5 )
	
	    self.m_staticTextErrorMessage1 = wx.StaticText( self, wx.ID_ANY, u"Invalid Entry", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticTextErrorMessage1.Wrap( -1 )
	    self.m_staticTextErrorMessage1.SetForegroundColour( wx.Colour( 255, 0, 0 ) )
	
	    sbSizer37.Add( self.m_staticTextErrorMessage1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	
	    bSizer83.Add( sbSizer37, 0, wx.ALL|wx.EXPAND, 5 )
	
	    sbSizer371 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"ROI Center" ), wx.VERTICAL )
	
	    fgSizer431 = wx.FlexGridSizer( 0, 3, 0, 0 )
	    fgSizer431.SetFlexibleDirection( wx.BOTH )
	    fgSizer431.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
	
	    self.m_staticText1882 = wx.StaticText( self, wx.ID_ANY, u"X:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText1882.Wrap( -1 )
	    fgSizer431.Add( self.m_staticText1882, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_textCtrlROICenterX = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 60,-1 ), wx.TE_PROCESS_ENTER )
	    fgSizer431.Add( self.m_textCtrlROICenterX, 0, wx.ALL, 5 )
	
	    self.m_sliderCenterX = wx.Slider( self, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
	    fgSizer431.Add( self.m_sliderCenterX, 0, wx.ALL, 5 )
	
	    self.m_staticText18812 = wx.StaticText( self, wx.ID_ANY, u"Y:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText18812.Wrap( -1 )
	    fgSizer431.Add( self.m_staticText18812, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_textCtrlROICenterY = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 60,-1 ), wx.TE_PROCESS_ENTER )
	    fgSizer431.Add( self.m_textCtrlROICenterY, 0, wx.ALL, 5 )
	
	    self.m_sliderCenterY = wx.Slider( self, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
	    fgSizer431.Add( self.m_sliderCenterY, 0, wx.ALL, 5 )
	
	    self.m_staticText188111 = wx.StaticText( self, wx.ID_ANY, u"Z:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText188111.Wrap( -1 )
	    fgSizer431.Add( self.m_staticText188111, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_textCtrlROICenterZ = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 60,-1 ), wx.TE_PROCESS_ENTER )
	    fgSizer431.Add( self.m_textCtrlROICenterZ, 0, wx.ALL, 5 )
	
	    self.m_sliderCenterZ = wx.Slider( self, wx.ID_ANY, 50, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
	    fgSizer431.Add( self.m_sliderCenterZ, 0, wx.ALL, 5 )
	
	
	    sbSizer371.Add( fgSizer431, 0, wx.EXPAND, 5 )
	
	    self.m_staticTextErrorMessage2 = wx.StaticText( self, wx.ID_ANY, u"Invalid Entry", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticTextErrorMessage2.Wrap( -1 )
	    self.m_staticTextErrorMessage2.SetForegroundColour( wx.Colour( 255, 0, 0 ) )
	
	    sbSizer371.Add( self.m_staticTextErrorMessage2, 0, wx.ALL, 5 )
	
	
	    bSizer83.Add( sbSizer371, 0, wx.ALL|wx.EXPAND, 5 )
	
	    sbSizer70 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Commands" ), wx.VERTICAL )
	
	    bSizer85 = wx.BoxSizer( wx.HORIZONTAL )
	
	    self.m_selectWholeImageButton = wx.Button( self, wx.ID_ANY, u"Select Whole Image", wx.DefaultPosition, wx.DefaultSize, 0 )
	    bSizer85.Add( self.m_selectWholeImageButton, 0, wx.ALL, 5 )
	
	    self.m_centerROIButton = wx.Button( self, wx.ID_ANY, u"Center ROI", wx.DefaultPosition, wx.DefaultSize, 0 )
	    bSizer85.Add( self.m_centerROIButton, 0, wx.ALL, 5 )
	
	    self.m_buttonShow = wx.Button( self, wx.ID_ANY, u"Show ROI", wx.DefaultPosition, wx.DefaultSize, 0 )
	    bSizer85.Add( self.m_buttonShow, 0, wx.ALL, 5 )
	
	
	    sbSizer70.Add( bSizer85, 0, wx.EXPAND, 5 )
	
	
	    bSizer83.Add( sbSizer70, 0, wx.ALL|wx.EXPAND, 5 )
	
	    fgSizer60 = wx.FlexGridSizer( 0, 2, 0, 0 )
	    fgSizer60.SetFlexibleDirection( wx.BOTH )
	    fgSizer60.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
	
	    self.m_staticText86 = wx.StaticText( self, wx.ID_ANY, u"ROI Extent:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText86.Wrap( -1 )
	    fgSizer60.Add( self.m_staticText86, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
	
	    self.m_extentLabel = wx.StaticText( self, wx.ID_ANY, u"(0, 0, 0, 0, 0, 0)", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_extentLabel.Wrap( -1 )
	    fgSizer60.Add( self.m_extentLabel, 0, wx.ALL, 5 )
	
	    self.m_staticText242 = wx.StaticText( self, wx.ID_ANY, u"ROI Size:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText242.Wrap( -1 )
	    fgSizer60.Add( self.m_staticText242, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
	
	    self.m_staticTextFileSizeLabel = wx.StaticText( self, wx.ID_ANY, u"0 MiB", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticTextFileSizeLabel.Wrap( -1 )
	    fgSizer60.Add( self.m_staticTextFileSizeLabel, 0, wx.ALL, 5 )
	
	
	    bSizer83.Add( fgSizer60, 1, wx.EXPAND, 5 )
	
	
	    self.SetSizer( bSizer83 )
	    self.Layout()

    def __del__( self ):
	    pass



