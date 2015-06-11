# =========================================================================
#
# Copyright (c) 2000-2002 Enhanced Vision Systems
# Copyright (c) 2002-2008 GE Healthcare
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

import os
import sys
import logging
import wx

from zope import component, event, interface
from PI.visualization.common import MicroViewSettings
from PI.visualization.MicroView.interfaces import IMicroViewMainFrame, IPlugin,\
    IPluginManager, IStockIconProvider, IViewportManager, ISpreadsheet  # don't change this
from PI.visualization.common.events import ProgressEvent
from PI.visualization.MicroView.events import CurrentImageChangeEvent, NoImagesLoadedEvent


class MicroViewPlugIn(object):

    interface.implements(IPlugin)

    __classname__ = "YourClassName"
    __shortname__ = "Your plugin name"
    __label__ = "A label useful for choice boxes etc"
    __description__ = "Your plugin description"
    __iconname__ = None
    __tabname__ = "The name you want to appear on the tab"
    __menuentry__ = None
    __managergroup__ = None

    @classmethod
    def GetClassName(cls):
        """class method that returns the classname of this plugin"""
        return cls.__classname__

    @classmethod
    def GetShortName(cls):
        """class method that returns a short descriptive name for this plugin"""
        return cls.__shortname__

    @classmethod
    def GetLabel(cls):
        """class method that returns a short descriptive name for this plugin"""
        return cls.__label__

    @classmethod
    def GetDescription(cls):
        """class method that returns a longer description for this plugin"""
        return cls.__description__

    @classmethod
    def GetMenuBitmap(cls):
        """class method that returns a menu-sized bitmap for this plugin"""
        if cls.__iconname__ is None:
            return None
        pkg = cls.__module__.split('.')[0] + '.Icons'
        return component.getUtility(IStockIconProvider).getMenuBitmap(cls.__iconname__, package=pkg)

    @classmethod
    def GetToolbarBitmap(cls):
        """class method that returns a toolbar-sized bitmap for this plugin"""
        if cls.__iconname__ is None:
            return None
        pkg = cls.__module__.split('.')[0] + '.Icons'
        return component.getUtility(IStockIconProvider).getToolbarBitmap(cls.__iconname__, package=pkg)

    @classmethod
    def GetMenuEntry(cls):
        return cls.__menuentry__

    @classmethod
    def GetManagerGroup(cls):
        return cls.__managergroup__

    @classmethod
    def GetTabName(cls):
        return cls.__tabname__

    def __init__(self, parent):

        self._Objects2D = []
        self._Objects3D = []
        self._helpLink = ''
        self._isManaged = False
        self._stockicons = component.getUtility(IStockIconProvider)
        self._icon = None
        self._Dialog = None
        self._isManaged = True
        self._userAction = None
        self.log = logging.getLogger(__name__)

    def __del__(self):
        pass

    def GetObjectState(self):
        """Returns a pickleable representation of this plugin"""
        return None

    def SetObjectState(self, o):
        """Sets up the plugin based on a pickleable class rep. object"""
        pass

    def Serialize(self):
        """Serialize the state of a plugin to a string"""
        pass

    def DeSerialize(self, s):
        """Deserialize the state of the plugin from a file"""
        pass

    def GetIcon(self, size=None):
        """Returns the wx bitmap resource defined for this plugin"""
        # load icon if we haven't already done so
        if self._icon is None and self.__iconname__ is not None:
            pkg = self.__module__.split('.')[0] + '.Icons'
            self._icon = self._stockicons.getBitmap(self.__iconname__,
                                                    size=size, package=pkg)
        return self._icon

    def GetMenuIcon(self):
        """Returns the wx menu icon resource defined for this plugin"""
        if sys.platform == 'win32' or sys.platform == 'darwin':
            return None
        else:
            # load icon if we haven't already done so
            if self._icon is None and self.__iconname__ is not None:
                self._icon = self._stockicons.getBitmap(self.__iconname__)
            return self._icon

    def GetCurrentDirectory(self):
        # determine working directory

        config = MicroViewSettings.MicroViewSettings.getObject()

        curr_dir = os.getcwd()

        # over-ride with system-wide directory
        try:
            curr_dir = config.GlobalCurrentDirectory or curr_dir
        except:
            config.GlobalCurrentDirectory = curr_dir

        return curr_dir

    def SaveCurrentDirectory(self, curr):
        config = MicroViewSettings.MicroViewSettings.getObject()
        try:
            config.GlobalCurrentDirectory = curr
        except:
            logging.error("Unable to write to database")

    def GetHelpPageLink(self):
        val = 'tools-and-plugins.html'
        if self._helpLink:
            val = val + '#' + self._helpLink
        return val

    def ActionEvent(self, evt):
        """Place holder - override in a plugin to perform special functionality
            whenever spacebar is pressed"""
        pass

    def GetUserAction(self):
        """Returns method invoked on user Action"""
        return self._userAction

    def InvokeProgressEvent(self,  progress, progressText):
        """Post a zope progress event"""
        event.notify(ProgressEvent(progressText, progress))

    def OnPluginClose(self):
        """Override this method to permit the plugin to close itself cleanly"""
        logging.error("OnPluginClose must be implemented!")

    def OnPluginOpen(self):
        """Override this method to permit the plugin to perform tasks
        when the plugin is _first_ activated"""
        pass

    def ActivatePlugin(self):
        """Plugin has been activated by the plugin manager"""
        return True

    def DeactivatePlugin(self):
        """Plugin has been deactivated by the plugin manager"""
        return True

    def OnApplicationClose(self):
        """Override this method to permit the plugin to perform tasks
        when the application is closed.  Routine must return True if all
        is okay; False if the plugin requests an app shutdown abort."""

        return True

    def HandleVTKProgressEvent(self, obj, evt):
        """
        A VTK object generated a progress event - convert it to a zope-style
        event
        """
        self.InvokeProgressEvent(obj.GetProgress(), obj.GetProgressText())

    def isManaged(self):
        """Returns True if this plugin is embedded"""
        return self._isManaged

    def GetPluginManager(self):
        """Convenience method: return a pointer to the plugin manager"""
        return component.getUtility(IPluginManager)

    def GetMicroView(self):
        """Convenience method: returns a pointer to the main frame (deprecated)"""
        return component.getUtility(IMicroViewMainFrame)

    def showHelp(self, evt=None):
        """Show help for this plugin"""
        self.GetMicroView().showHelp(self.GetHelpPageLink())

    def CreatePluginDialogFrame(self, parent, **kw):
        """Create dialog frame for this plugin.

        Optional arg: managed=False makes the dialog appear in it's own top window.
        """

        managed = kw.get('managed', True)

        if managed:
            self._isManaged = True
            self._Dialog = parent
        else:
            # plugin should appear in a toplevel frame
            self._Dialog = wx.Frame(parent,  -1)
            self._Dialog.SetTitle(self.__shortname__)

    def InvokeImageLoadedEvent(self):
        """Utility method - force an 'image change' event

        Useful on startup of the plugin"""

        mv = component.getUtility(IMicroViewMainFrame)
        current_image = mv.GetCurrentImageIndex()
        number_images_displayed = mv.GetNumberOfImagesCurrentlyLoaded()
        page_title = mv.GetCurrentImageTitle()

        # one of two events are generated, depending on whether an image is
        # currently loaded or not
        if number_images_displayed == 0:
            self.OnNoImagesLoadedEvent(NoImagesLoadedEvent())
        else:
            self.OnImageChangeEvent(CurrentImageChangeEvent(
                current_image, number_images_displayed, page_title))

    def getImageList(self):
        """Gets the full list of loaded images

        Returns:
            list: A list of tuples.  Each tuple is a (int, str) pair

        """
        return self.GetMicroView().getImageList()

    def getSpreadsheetList(self):
        """Gets the full list of loaded spreadsheets

        Returns:
            list: A list of tuples.  Each tuple is a (int, str) pair

        """
        return self.GetMicroView().getSpreadsheetList()

    def OnNoImagesLoadedEvent(self, evt):
        """Default method to call when last image is closed"""
        pass

    def OnImageChangeEvent(self, evt):
        """Default method to call when an image change has occurred"""
        pass

    def UpdateROIValues(self, evt=None):
        """A hook to allow plugins to get hold of the currently selected region
        of interest"""
        pass

    def UpdateROIListConsumerControls(self):
        """Override method for ROI list consumers"""
        pass
