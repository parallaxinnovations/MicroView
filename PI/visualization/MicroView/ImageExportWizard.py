# -*- coding: utf-8 -*-

###########################################################################
# Python code generated with wxFormBuilder (version Nov  6 2013)
# http://www.wxformbuilder.org/
##
# PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.wizard

###########################################################################
# Class ImageExportWizard
###########################################################################


class ImageExportWizard (wx.wizard.Wizard):

    def __init__(self, parent):
        wx.wizard.Wizard.__init__(self, parent, id=wx.ID_ANY, title=u"Image Export...", bitmap=wx.Bitmap(
            u"Icons/export_wizard_1.png", wx.BITMAP_TYPE_ANY), pos=wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
        self.m_pages = []

        self.m_wizPageIntro = wx.wizard.WizardPageSimple(
            self, None, None, wx.NullBitmap)
        self.add_page(self.m_wizPageIntro)

        bSizer73 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText69 = wx.StaticText(
            self.m_wizPageIntro, wx.ID_ANY, u"Use this wizard to export the current image as a stack of 2D slices.\nIf you want to save the image in a native 3D format instead, select\nFile -> Save Image As... from the application menu.", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText69.Wrap(800)
        bSizer73.Add(self.m_staticText69, 0, 0, 5)

        self.m_wizPageIntro.SetSizer(bSizer73)
        self.m_wizPageIntro.Layout()
        bSizer73.Fit(self.m_wizPageIntro)
        self.m_wizPageDownsample = wx.wizard.WizardPageSimple(self)
        self.add_page(self.m_wizPageDownsample)

        bSizer72 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText74 = wx.StaticText(
            self.m_wizPageDownsample, wx.ID_ANY, u"Should the image be downsampled before exporting?\nPerforming this step will effect the list of available output formats.", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText74.Wrap(-1)
        bSizer72.Add(self.m_staticText74, 0, wx.ALL, 5)

        bSizer72.AddSpacer((0, 30), 0, wx.EXPAND, 5)

        bSizer160 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText195 = wx.StaticText(
            self.m_wizPageDownsample, wx.ID_ANY, u"Downsample to:", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText195.Wrap(-1)
        bSizer160.Add(
            self.m_staticText195, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        m_choiceDownsampleChoices = [
            u"8-bit unsigned char", u"16-bit signed int"]
        self.m_choiceDownsample = wx.Choice(
            self.m_wizPageDownsample, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choiceDownsampleChoices, 0)
        self.m_choiceDownsample.SetSelection(0)
        bSizer160.Add(self.m_choiceDownsample, 0, wx.ALL, 5)

        bSizer72.Add(bSizer160, 0, wx.EXPAND, 5)

        self.m_wizPageDownsample.SetSizer(bSizer72)
        self.m_wizPageDownsample.Layout()
        bSizer72.Fit(self.m_wizPageDownsample)
        self.m_wizPageSelectFormat = wx.wizard.WizardPageSimple(self)
        self.add_page(self.m_wizPageSelectFormat)

        bSizer76 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText70 = wx.StaticText(
            self.m_wizPageSelectFormat, wx.ID_ANY, u"Choose an export file format from the list below.\nDownsampling the image in the previous step of this wizard\nmay provide additional formats.", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText70.Wrap(400)
        bSizer76.Add(self.m_staticText70, 0, wx.ALL, 5)

        m_listBoxFormatsChoices = []
        self.m_listBoxFormats = wx.ListBox(
            self.m_wizPageSelectFormat, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBoxFormatsChoices, 0)
        bSizer76.Add(self.m_listBoxFormats, 1, wx.ALL | wx.EXPAND, 5)

        self.m_wizPageSelectFormat.SetSizer(bSizer76)
        self.m_wizPageSelectFormat.Layout()
        bSizer76.Fit(self.m_wizPageSelectFormat)
        self.m_wizPageComplete = wx.wizard.WizardPageSimple(self)
        self.add_page(self.m_wizPageComplete)

        bSizer77 = wx.BoxSizer(wx.VERTICAL)

        self.m_staticText75 = wx.StaticText(
            self.m_wizPageComplete, wx.ID_ANY, u"Select an output directory. Image slices will be written into\nthe selected directory with an export-*.* style name.", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText75.Wrap(-1)
        bSizer77.Add(self.m_staticText75, 0, wx.ALL, 5)

        bSizer77.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self.m_dirPickerForExport = wx.DirPickerCtrl(
            self.m_wizPageComplete, wx.ID_ANY, wx.EmptyString, u"Select a folder", wx.DefaultPosition, wx.DefaultSize, wx.DIRP_DEFAULT_STYLE)
        bSizer77.Add(self.m_dirPickerForExport, 0, wx.ALL | wx.EXPAND, 5)

        bSizer77.AddSpacer((0, 0), 1, wx.EXPAND, 5)

        self.m_wizPageComplete.SetSizer(bSizer77)
        self.m_wizPageComplete.Layout()
        bSizer77.Fit(self.m_wizPageComplete)
        self.Centre(wx.BOTH)

        # Connect Events
        self.Bind(wx.EVT_INIT_DIALOG, self.onInitDialog)
        self.Bind(wx.wizard.EVT_WIZARD_FINISHED, self.onWizardFinished)
        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGED, self.onWizardPageChanged)
        self.m_listBoxFormats.Bind(
            wx.EVT_LISTBOX_DCLICK, self.onListBoxDoubleClick)

    def add_page(self, page):
        if self.m_pages:
            previous_page = self.m_pages[-1]
            page.SetPrev(previous_page)
            previous_page.SetNext(page)
        self.m_pages.append(page)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def onInitDialog(self, event):
        event.Skip()

    def onWizardFinished(self, event):
        event.Skip()

    def onWizardPageChanged(self, event):
        event.Skip()

    def onListBoxDoubleClick(self, event):
        event.Skip()
