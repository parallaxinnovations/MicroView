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
## Class ImageImportDialog
###########################################################################

class ImageImportDialog ( wx.Dialog ):

    def __init__( self, parent ):
	    wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"File Import...", pos = wx.DefaultPosition, size = wx.Size( 513,567 ), style = wx.DEFAULT_DIALOG_STYLE )
	
	    self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
	
	    bSizer1 = wx.BoxSizer( wx.VERTICAL )
	
	    bSizer136 = wx.BoxSizer( wx.HORIZONTAL )
	
	    self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Filename Template:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText1.Wrap( -1 )
	    bSizer136.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_filePicker = wx.FilePickerCtrl( self, wx.ID_ANY, u"image###.png", u"Select a file", u"*", wx.DefaultPosition, wx.Size( 400,-1 ), wx.FLP_DEFAULT_STYLE )
	    bSizer136.Add( self.m_filePicker, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
	
	    self.m_buttonExamineFolder = wx.Button( self, wx.ID_ANY, u"Examine", wx.DefaultPosition, wx.DefaultSize, 0 )
	    bSizer136.Add( self.m_buttonExamineFolder, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	
	    bSizer1.Add( bSizer136, 0, wx.EXPAND, 5 )
	
	    self.m_panelMainDialog = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
	    bSizer181 = wx.BoxSizer( wx.VERTICAL )
	
	    bSizer159 = wx.BoxSizer( wx.HORIZONTAL )
	
	    self.m_staticText194 = wx.StaticText( self.m_panelMainDialog, wx.ID_ANY, u"Image Title:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText194.Wrap( -1 )
	    bSizer159.Add( self.m_staticText194, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_textCtrlImageTitle = wx.TextCtrl( self.m_panelMainDialog, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
	    bSizer159.Add( self.m_textCtrlImageTitle, 0, wx.ALL, 5 )
	
	
	    bSizer181.Add( bSizer159, 0, wx.EXPAND, 5 )
	
	    bSizer137 = wx.BoxSizer( wx.HORIZONTAL )
	
	    sbSizer38 = wx.StaticBoxSizer( wx.StaticBox( self.m_panelMainDialog, wx.ID_ANY, u"Slice Indices" ), wx.VERTICAL )
	
	    fgSizer22 = wx.FlexGridSizer( 0, 2, 0, 0 )
	    fgSizer22.SetFlexibleDirection( wx.BOTH )
	    fgSizer22.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
	
	    self.m_staticText5 = wx.StaticText( self.m_panelMainDialog, wx.ID_ANY, u"First number:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText5.Wrap( -1 )
	    fgSizer22.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_spinCtrlFirstNum = wx.SpinCtrl( self.m_panelMainDialog, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 100,-1 ), wx.SP_ARROW_KEYS, 0, 100000, 0 )
	    fgSizer22.Add( self.m_spinCtrlFirstNum, 0, wx.ALL, 5 )
	
	    self.m_staticText6 = wx.StaticText( self.m_panelMainDialog, wx.ID_ANY, u"Last number:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText6.Wrap( -1 )
	    fgSizer22.Add( self.m_staticText6, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_spinCtrlLastNum = wx.SpinCtrl( self.m_panelMainDialog, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 100,-1 ), wx.SP_ARROW_KEYS, 0, 100000, 0 )
	    fgSizer22.Add( self.m_spinCtrlLastNum, 0, wx.ALL, 5 )
	
	
	    sbSizer38.Add( fgSizer22, 1, wx.EXPAND, 5 )
	
	
	    bSizer137.Add( sbSizer38, 0, wx.EXPAND|wx.RIGHT, 5 )
	
	    Spacing = wx.StaticBoxSizer( wx.StaticBox( self.m_panelMainDialog, wx.ID_ANY, u"Spacing Parameters" ), wx.VERTICAL )
	
	    fgSizer23 = wx.FlexGridSizer( 0, 2, 0, 0 )
	    fgSizer23.SetFlexibleDirection( wx.BOTH )
	    fgSizer23.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
	
	    self.m_staticText2 = wx.StaticText( self.m_panelMainDialog, wx.ID_ANY, u"X spacing (mm):", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText2.Wrap( -1 )
	    fgSizer23.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_textCtrlXSpacing = wx.TextCtrl( self.m_panelMainDialog, wx.ID_ANY, u"1", wx.DefaultPosition, wx.Size( 75,-1 ), 0 )
	    self.m_textCtrlXSpacing.SetMaxLength( 0 ) 
	    fgSizer23.Add( self.m_textCtrlXSpacing, 0, wx.ALL, 5 )
	
	    self.m_staticText3 = wx.StaticText( self.m_panelMainDialog, wx.ID_ANY, u"Y spacing (mm):", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText3.Wrap( -1 )
	    fgSizer23.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_textCtrlYSpacing = wx.TextCtrl( self.m_panelMainDialog, wx.ID_ANY, u"1", wx.DefaultPosition, wx.Size( 75,-1 ), 0 )
	    self.m_textCtrlYSpacing.SetMaxLength( 0 ) 
	    fgSizer23.Add( self.m_textCtrlYSpacing, 0, wx.ALL, 5 )
	
	    self.m_staticText4 = wx.StaticText( self.m_panelMainDialog, wx.ID_ANY, u"Z spacing (mm):", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText4.Wrap( -1 )
	    fgSizer23.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_textCtrlZSpacing = wx.TextCtrl( self.m_panelMainDialog, wx.ID_ANY, u"1", wx.DefaultPosition, wx.Size( 75,-1 ), 0 )
	    self.m_textCtrlZSpacing.SetMaxLength( 0 ) 
	    fgSizer23.Add( self.m_textCtrlZSpacing, 0, wx.ALL, 5 )
	
	
	    Spacing.Add( fgSizer23, 0, wx.EXPAND, 5 )
	
	
	    bSizer137.Add( Spacing, 1, wx.EXPAND, 5 )
	
	
	    bSizer181.Add( bSizer137, 0, wx.EXPAND, 5 )
	
	    Options = wx.StaticBoxSizer( wx.StaticBox( self.m_panelMainDialog, wx.ID_ANY, u"Import Options" ), wx.VERTICAL )
	
	    bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
	
	    self.m_checkRawImage = wx.CheckBox( self.m_panelMainDialog, wx.ID_ANY, u"Raw image", wx.DefaultPosition, wx.DefaultSize, 0 )
	    bSizer3.Add( self.m_checkRawImage, 0, wx.ALL, 5 )
	
	    self.m_checkBoxFlipImage = wx.CheckBox( self.m_panelMainDialog, wx.ID_ANY, u"Flip image", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkBoxFlipImage.Enable( False )
	
	    bSizer3.Add( self.m_checkBoxFlipImage, 0, wx.ALL, 5 )
	
	    self.m_checkConvertToGrayscale = wx.CheckBox( self.m_panelMainDialog, wx.ID_ANY, u"Convert to grayscale", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_checkConvertToGrayscale.Enable( False )
	
	    bSizer3.Add( self.m_checkConvertToGrayscale, 0, wx.ALL, 5 )
	
	    self.m_check3DImage = wx.CheckBox( self.m_panelMainDialog, wx.ID_ANY, u"3D image", wx.DefaultPosition, wx.DefaultSize, 0 )
	    bSizer3.Add( self.m_check3DImage, 0, wx.ALL, 5 )
	
	
	    Options.Add( bSizer3, 0, wx.EXPAND, 5 )
	
	    fgSizer21 = wx.FlexGridSizer( 0, 2, 0, 0 )
	    fgSizer21.SetFlexibleDirection( wx.BOTH )
	    fgSizer21.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
	
	
	    Options.Add( fgSizer21, 1, wx.EXPAND, 5 )
	
	
	    bSizer181.Add( Options, 0, wx.EXPAND, 5 )
	
	    MemoryRequired = wx.BoxSizer( wx.HORIZONTAL )
	
	    self.m_staticText7 = wx.StaticText( self.m_panelMainDialog, wx.ID_ANY, u"Memory Required:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText7.Wrap( -1 )
	    MemoryRequired.Add( self.m_staticText7, 0, wx.ALL, 5 )
	
	    self.m_staticTextMemoryLabel = wx.StaticText( self.m_panelMainDialog, wx.ID_ANY, u"0.0 MB", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticTextMemoryLabel.Wrap( -1 )
	    self.m_staticTextMemoryLabel.SetForegroundColour( wx.Colour( 0, 255, 0 ) )
	
	    MemoryRequired.Add( self.m_staticTextMemoryLabel, 0, wx.ALL, 5 )
	
	
	    bSizer181.Add( MemoryRequired, 0, wx.EXPAND, 5 )
	
	    self.m_panelOptions = wx.Panel( self.m_panelMainDialog, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
	    bSizer134 = wx.BoxSizer( wx.HORIZONTAL )
	
	    self.m_panelRawParameters = wx.Panel( self.m_panelOptions, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
	    RawParams = wx.StaticBoxSizer( wx.StaticBox( self.m_panelRawParameters, wx.ID_ANY, u"Raw Image Parameters" ), wx.VERTICAL )
	
	    gSizer2 = wx.GridSizer( 0, 2, 0, 0 )
	
	    self.m_staticText9 = wx.StaticText( self.m_panelRawParameters, wx.ID_ANY, u"Header size:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText9.Wrap( -1 )
	    gSizer2.Add( self.m_staticText9, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 0 )
	
	    self.m_textCtrlHeaderSize = wx.TextCtrl( self.m_panelRawParameters, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_textCtrlHeaderSize.SetMaxLength( 0 ) 
	    gSizer2.Add( self.m_textCtrlHeaderSize, 0, wx.ALL, 5 )
	
	    self.m_staticText10 = wx.StaticText( self.m_panelRawParameters, wx.ID_ANY, u"Data type:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText10.Wrap( -1 )
	    gSizer2.Add( self.m_staticText10, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    m_choiceDataTypeChoices = [ u"unsigned char", u"unsigned short", u"short", u"int", u"float", u"double" ]
	    self.m_choiceDataType = wx.Choice( self.m_panelRawParameters, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choiceDataTypeChoices, 0 )
	    self.m_choiceDataType.SetSelection( 2 )
	    gSizer2.Add( self.m_choiceDataType, 0, wx.ALL, 5 )
	
	    self.m_staticText11 = wx.StaticText( self.m_panelRawParameters, wx.ID_ANY, u"Data endian:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText11.Wrap( -1 )
	    gSizer2.Add( self.m_staticText11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    m_choiceDataEndianChoices = [ u"little endian", u"big endian" ]
	    self.m_choiceDataEndian = wx.Choice( self.m_panelRawParameters, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choiceDataEndianChoices, 0 )
	    self.m_choiceDataEndian.SetSelection( 0 )
	    gSizer2.Add( self.m_choiceDataEndian, 0, wx.ALL, 5 )
	
	    self.m_staticText12 = wx.StaticText( self.m_panelRawParameters, wx.ID_ANY, u"Number of channels:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText12.Wrap( -1 )
	    gSizer2.Add( self.m_staticText12, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_textCtrlNumberChannels = wx.TextCtrl( self.m_panelRawParameters, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_textCtrlNumberChannels.SetMaxLength( 1 ) 
	    gSizer2.Add( self.m_textCtrlNumberChannels, 0, wx.ALL, 5 )
	
	    self.m_staticText13 = wx.StaticText( self.m_panelRawParameters, wx.ID_ANY, u"X size:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText13.Wrap( -1 )
	    gSizer2.Add( self.m_staticText13, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_textCtrlXSize = wx.TextCtrl( self.m_panelRawParameters, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_textCtrlXSize.SetMaxLength( 0 ) 
	    gSizer2.Add( self.m_textCtrlXSize, 0, wx.ALL, 5 )
	
	    self.m_staticText14 = wx.StaticText( self.m_panelRawParameters, wx.ID_ANY, u"Y size:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText14.Wrap( -1 )
	    gSizer2.Add( self.m_staticText14, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_textCtrlYSize = wx.TextCtrl( self.m_panelRawParameters, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_textCtrlYSize.SetMaxLength( 0 ) 
	    gSizer2.Add( self.m_textCtrlYSize, 0, wx.ALL, 5 )
	
	    self.m_staticText48 = wx.StaticText( self.m_panelRawParameters, wx.ID_ANY, u"Z size:", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_staticText48.Wrap( -1 )
	    gSizer2.Add( self.m_staticText48, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
	
	    self.m_textCtrlZSize = wx.TextCtrl( self.m_panelRawParameters, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_textCtrlZSize.SetMaxLength( 0 ) 
	    gSizer2.Add( self.m_textCtrlZSize, 0, wx.ALL, 5 )
	
	
	    RawParams.Add( gSizer2, 0, wx.EXPAND, 5 )
	
	
	    self.m_panelRawParameters.SetSizer( RawParams )
	    self.m_panelRawParameters.Layout()
	    RawParams.Fit( self.m_panelRawParameters )
	    bSizer134.Add( self.m_panelRawParameters, 1, wx.ALL|wx.EXPAND|wx.RIGHT, 5 )
	
	    self.m_panel34 = wx.Panel( self.m_panelOptions, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
	    sbSizer51 = wx.StaticBoxSizer( wx.StaticBox( self.m_panel34, wx.ID_ANY, u"Preview" ), wx.VERTICAL )
	
	    self.m_bitmapPreview = wx.StaticBitmap( self.m_panel34, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
	    sbSizer51.Add( self.m_bitmapPreview, 1, wx.ALL|wx.EXPAND, 5 )
	
	    self.m_buttonUpdate = wx.Button( self.m_panel34, wx.ID_ANY, u"Update", wx.DefaultPosition, wx.DefaultSize, 0 )
	    sbSizer51.Add( self.m_buttonUpdate, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
	
	
	    self.m_panel34.SetSizer( sbSizer51 )
	    self.m_panel34.Layout()
	    sbSizer51.Fit( self.m_panel34 )
	    bSizer134.Add( self.m_panel34, 1, wx.EXPAND |wx.ALL, 5 )
	
	
	    self.m_panelOptions.SetSizer( bSizer134 )
	    self.m_panelOptions.Layout()
	    bSizer134.Fit( self.m_panelOptions )
	    bSizer181.Add( self.m_panelOptions, 1, wx.EXPAND |wx.ALL, 0 )
	
	
	    self.m_panelMainDialog.SetSizer( bSizer181 )
	    self.m_panelMainDialog.Layout()
	    bSizer181.Fit( self.m_panelMainDialog )
	    bSizer1.Add( self.m_panelMainDialog, 1, wx.EXPAND |wx.ALL, 5 )
	
	    self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
	    bSizer1.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )
	
	    bSizer182 = wx.BoxSizer( wx.HORIZONTAL )
	
	
	    bSizer182.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
	
	    self.m_buttonOK = wx.Button( self, wx.ID_OK, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
	    bSizer182.Add( self.m_buttonOK, 0, wx.ALL, 3 )
	
	    self.m_buttonCancel = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
	    self.m_buttonCancel.SetDefault() 
	    bSizer182.Add( self.m_buttonCancel, 0, wx.ALL, 3 )
	
	
	    bSizer1.Add( bSizer182, 0, wx.EXPAND, 0 )
	
	
	    self.SetSizer( bSizer1 )
	    self.Layout()
	
	    self.Centre( wx.BOTH )
	
	    # Connect Events
	    self.m_filePicker.Bind( wx.EVT_CHAR, self.OnFilePickerChanged )
	    self.m_filePicker.Bind( wx.EVT_FILEPICKER_CHANGED, self.OnFilePickerChanged )
	    self.m_buttonExamineFolder.Bind( wx.EVT_BUTTON, self.onButtonExamine )
	    self.m_spinCtrlFirstNum.Bind( wx.EVT_SPINCTRL, self.updateButtonState )
	    self.m_spinCtrlFirstNum.Bind( wx.EVT_TEXT, self.updateButtonState )
	    self.m_spinCtrlLastNum.Bind( wx.EVT_SPINCTRL, self.updateButtonState )
	    self.m_spinCtrlLastNum.Bind( wx.EVT_TEXT, self.updateButtonState )
	    self.m_textCtrlXSpacing.Bind( wx.EVT_TEXT, self.updateButtonState )
	    self.m_textCtrlYSpacing.Bind( wx.EVT_TEXT, self.updateButtonState )
	    self.m_textCtrlZSpacing.Bind( wx.EVT_TEXT, self.updateButtonState )
	    self.m_checkRawImage.Bind( wx.EVT_CHECKBOX, self.ToggleRawImageReader )
	    self.m_checkConvertToGrayscale.Bind( wx.EVT_CHECKBOX, self.ToggleGrayScale )
	    self.m_check3DImage.Bind( wx.EVT_CHECKBOX, self.ToggleRaw3D )
	    self.m_textCtrlHeaderSize.Bind( wx.EVT_TEXT, self.updateButtonState )
	    self.m_choiceDataType.Bind( wx.EVT_CHOICE, self.updateMemoryUsage )
	    self.m_textCtrlNumberChannels.Bind( wx.EVT_TEXT, self.updateMemoryUsage )
	    self.m_textCtrlXSize.Bind( wx.EVT_TEXT, self.updateButtonState )
	    self.m_textCtrlYSize.Bind( wx.EVT_TEXT, self.updateMemoryUsage )
	    self.m_textCtrlZSize.Bind( wx.EVT_TEXT, self.updateButtonState )
	    self.m_buttonUpdate.Bind( wx.EVT_BUTTON, self.onButtonUpdate )

    def __del__( self ):
	    pass


    # Virtual event handlers, overide them in your derived class
    def OnFilePickerChanged( self, event ):
	    event.Skip()


    def onButtonExamine( self, event ):
	    event.Skip()

    def updateButtonState( self, event ):
	    event.Skip()







    def ToggleRawImageReader( self, event ):
	    event.Skip()

    def ToggleGrayScale( self, event ):
	    event.Skip()

    def ToggleRaw3D( self, event ):
	    event.Skip()


    def updateMemoryUsage( self, event ):
	    event.Skip()





    def onButtonUpdate( self, event ):
	    event.Skip()



