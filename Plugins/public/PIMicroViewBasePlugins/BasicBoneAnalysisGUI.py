# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Jun  5 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class BasicBoneAnalysisGUI
###########################################################################

class BasicBoneAnalysisGUI ( wx.Panel ):

    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 383,419 ), style = wx.TAB_TRAVERSAL )

        bSizer6 = wx.BoxSizer( wx.VERTICAL )

        bSizer98 = wx.BoxSizer( wx.VERTICAL )

        VOI = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Volume of Interest" ), wx.VERTICAL )

        bSizer8 = wx.BoxSizer( wx.HORIZONTAL )

        bSizer8.SetMinSize( wx.Size( 300,-1 ) )
        m_choiceROIPluginChoices = []
        self.m_choiceROIPlugin = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choiceROIPluginChoices, 0 )
        self.m_choiceROIPlugin.SetSelection( 0 )
        bSizer8.Add( self.m_choiceROIPlugin, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_buttonActivateROI = wx.Button( self, wx.ID_ANY, u"Activate ROI", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.m_buttonActivateROI, 0, wx.ALL, 5 )

        self.m_buttonClearROI = wx.Button( self, wx.ID_ANY, u"Clear ROI", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.m_buttonClearROI, 0, wx.ALL, 5 )


        VOI.Add( bSizer8, 1, wx.EXPAND, 5 )


        bSizer98.Add( VOI, 0, wx.EXPAND, 5 )

        Threshold = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Threshold" ), wx.VERTICAL )

        bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_buttonAutoThreshold = wx.Button( self, wx.ID_ANY, u"Auto Threshold", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer9.Add( self.m_buttonAutoThreshold, 0, wx.ALL, 5 )

        self.m_textCtrlThreshold = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_textCtrlThreshold.SetMaxLength( 0 )
        bSizer9.Add( self.m_textCtrlThreshold, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )


        Threshold.Add( bSizer9, 0, wx.EXPAND, 5 )


        bSizer98.Add( Threshold, 0, wx.EXPAND, 5 )

        BoneParams = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Bone Parameters" ), wx.VERTICAL )

        bSizer19 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_checkBoxBMD = wx.CheckBox( self, wx.ID_ANY, u"BMD", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_checkBoxBMD.SetValue(True)
        bSizer19.Add( self.m_checkBoxBMD, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_checkBoxStereology = wx.CheckBox( self, wx.ID_ANY, u"Stereology", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_checkBoxStereology.SetValue(True)
        bSizer19.Add( self.m_checkBoxStereology, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_buttonAdvancedOptions = wx.Button( self, wx.ID_ANY, u"Advanced Options", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer19.Add( self.m_buttonAdvancedOptions, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        BoneParams.Add( bSizer19, 0, wx.EXPAND, 5 )


        bSizer98.Add( BoneParams, 0, wx.EXPAND, 5 )

        sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Output File" ), wx.VERTICAL )

        bSizer14 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_checkBoxAppend = wx.CheckBox( self, wx.ID_ANY, u"Append", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_checkBoxAppend.SetValue(True)
        bSizer14.Add( self.m_checkBoxAppend, 0, wx.ALL|wx.EXPAND, 5 )

        self.m_filePicker = wx.FilePickerCtrl( self, wx.ID_ANY, wx.EmptyString, u"Select a file", u"Text files (*.txt)|*.txt|All files (*)|*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_OVERWRITE_PROMPT|wx.FLP_SAVE|wx.FLP_USE_TEXTCTRL )
        bSizer14.Add( self.m_filePicker, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


        sbSizer9.Add( bSizer14, 0, 0, 5 )


        bSizer98.Add( sbSizer9, 0, wx.EXPAND, 5 )

        bSizer7 = wx.BoxSizer( wx.HORIZONTAL )

        self.m_buttonRun = wx.Button( self, wx.ID_ANY, u"Run", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_buttonRun.Enable( False )

        bSizer7.Add( self.m_buttonRun, 0, wx.ALL, 5 )

        self.m_buttonShowResults = wx.Button( self, wx.ID_ANY, u"Show Results", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer7.Add( self.m_buttonShowResults, 0, wx.ALL, 5 )


        bSizer98.Add( bSizer7, 0, 0, 5 )


        bSizer6.Add( bSizer98, 1, 0, 5 )


        self.SetSizer( bSizer6 )
        self.Layout()

    def __del__( self ):
        pass


