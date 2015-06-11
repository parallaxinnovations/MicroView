# =========================================================================
#
# Copyright (c) 2000-2008 GE Healthcare
# Copyright (c) 2011-2015 Parallax Innovations Inc.
#
# Use, modification and redistribution of the software, in source or
# binary forms, are permitted provided that the following terms and
# conditions are met:
#
# 1) Redistribution of the source code, in verbatim or modified
#   form, must retain the above copyright notice, this license,
#   the following disclaimer, and any notices that refer to this
#   license and/or the following disclaimer.
#
# 2) Redistribution in binary form must include the above copyright
#    notice, a copy of this license and the following disclaimer
#   in the documentation or with other materials provided with the
#   distribution.
#
# 3) Modified copies of the source code must be clearly marked as such,
#   and must not be misrepresented as verbatim copies of the source code.
#
# EXCEPT WHEN OTHERWISE STATED IN WRITING BY THE COPYRIGHT HOLDERS AND/OR
# OTHER PARTIES, THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE
# SOFTWARE "AS IS" WITHOUT EXPRESSED OR IMPLIED WARRANTY INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE.  IN NO EVENT UNLESS AGREED TO IN WRITING WILL
# ANY COPYRIGHT HOLDER OR OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
# THE SOFTWARE UNDER THE TERMS OF THIS LICENSE BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, LOSS OF DATA OR DATA BECOMING INACCURATE OR LOSS OF PROFIT OR
# BUSINESS INTERRUPTION) ARISING IN ANY WAY OUT OF THE USE OR INABILITY TO
# USE THE SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
#
# =========================================================================

#
# This file represents a derivative work by Parallax Innovations Inc.
#

"""
OptionsDialog - plugin that manages program options.

Derived From:

  MicroViewPlugIn

Parameters:


Public Methods:

"""

import wx
import logging

from zope import component, event, interface
from PI.visualization.common import MicroViewSettings
from PI.visualization.common.events import MicroViewSettingsModifiedEvent
from PI.visualization.MicroView import MicroViewPlugIn
from PI.visualization.MicroView.interfaces import IPlugin

import ApplicationSettingsGUI


class ApplicationSettingsGUIC(ApplicationSettingsGUI.ApplicationSettingsGUI):

    plugin = None

    def setPlugin(self, plugin):
        self.plugin = plugin

    def onCheckBoxChange(self, evt):
        # pass events on to the plugin itself
        if self.plugin:
            self.plugin.onCheckBoxChange(evt)

    def onSaveDefaultButton(self, evt):
        # pass events on to the plugin itself
        if self.plugin:
            self.plugin.onSaveDefaultButton(evt)


class OptionsDialog(MicroViewPlugIn.MicroViewPlugIn):

    interface.implements(IPlugin)

    __classname__ = "Application Settings..."
    __label__ = "Settings"
    __shortname__ = "OptionsDialog"
    __description__ = "MicroView options"
    __iconname__ = "preferences"
    __menuentry__ = "|Edit|Application Settings"
    __managergroup__ = None
    __tabname__ = "Settings"

    def __init__(self, parent):
        MicroViewPlugIn.MicroViewPlugIn.__init__(self, parent)

        # create a gui container for this plugin
        MicroViewPlugIn.MicroViewPlugIn.CreatePluginDialogFrame(self, parent)

        # create GUI
        self.CreateGUI()

        # This dictionary maps between configuration file name and wx widget ID
        self.options = {
            'bShowAxes':                ApplicationSettingsGUI.SHOW_AXES,
            'bShowPlaneBorders':        ApplicationSettingsGUI.SHOW_BORDERS,
            'bShowAnatomicalLabels':    ApplicationSettingsGUI.SHOW_ANATOMICAL_LABELS,
            'bShowAxialPlane':          ApplicationSettingsGUI.SHOW_AXIAL_PLANE,
            'bShowCoronalPlane':        ApplicationSettingsGUI.SHOW_CORONAL_PLANE,
            'bShowSagittalPlane':       ApplicationSettingsGUI.SHOW_SAGITTAL_PLANE,
            'bShowVolumeOutline':       ApplicationSettingsGUI.SHOW_VOLUME_OUTLINE,
            'bInterpolateTextures':     ApplicationSettingsGUI.USE_IMAGE_INTERP,
            'bMeasurementUnitIsMM':     ApplicationSettingsGUI.MEASUREMENT_UNIT,
            'bUseMinMaxForWindowLevel': ApplicationSettingsGUI.USE_MINMAX,
            'bShowSplashScreen':        ApplicationSettingsGUI.DISPLAY_SPLASHSCREEN,
            'bShowImageOrientation':    ApplicationSettingsGUI.SHOW_IMAGE_ORIENTATION_WIDGET,
            'bUseDICOMCoordSystem':     ApplicationSettingsGUI.USE_DICOM_COORD_SYSTEM,
        }

        # This next line creates the inverse dictionary mapping
        self.inverse_options = dict([[v, k] for k, v in self.options.items()])
        self.ApplicationSettings = MicroViewSettings.MicroViewSettings.getObject()

        # make sure object is loaded
        val = self.ApplicationSettings.bShowAxes

        self.updateGUI()

        # listen to certain zope events
        component.provideHandler(self.ConfigModified)

    def GetHelpPageLink(self):
        """Override url for help"""
        return 'microview-options.html#microview-application-settings'

    def OnPluginClose(self):
        # unregister our zope handlers
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.ConfigModified)

    def CreateGUI(self):

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.gui = ApplicationSettingsGUIC(self._Dialog)
        self.gui.setPlugin(self)
        sizer.Add(self.gui, 1, wx.EXPAND)
        self._Dialog.SetSizer(sizer)

    def updateGUI(self):

        for key in self.options:
            try:
                wx.FindWindowById(self.options[key]).SetValue(
                    int(self.ApplicationSettings.__dict__[key]))
            except:
                logging.exception("OptionsDialog")

    def onCheckBoxChange(self, evt):
        option = self.inverse_options[evt.GetId()]
        self.ApplicationSettings.__dict__[option] = evt.IsChecked()
        event.notify(MicroViewSettingsModifiedEvent(self.ApplicationSettings))

    def onSaveDefaultButton(self, evt):
        logging.debug("TODO: implement OptionsDialog::onSaveDefaultButton()")

    def GetOptionSetting(self, key):
        try:
            wx.FindWindowById(self.options[key]).GetValue()
        except:
            logging.exception("GetOptionSetting")
            return False

    @component.adapter(MicroViewSettingsModifiedEvent)
    def ConfigModified(self, evt):
        self.updateGUI()

##########################################################################


def createPlugin(panel):
    return OptionsDialog(panel)
