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
StandardROITool - a plugin that allows the user to select a region of
interest. The user can select a cylindrical, rectangular or ellipsoidal region
of interest.
"""

import logging
import wx
from zope import component, interface
from PI.visualization.MicroView import MicroViewPlugIn

import StandardROIGUIC
import ROIController

from PI.visualization.MicroView.interfaces import IStandardROIProvider, IPlugin, ICurrentImage
from PI.visualization.MicroView.events import ROIEnabledEvent, \
    CurrentImageChangeEvent, StandardROIChangeExtentCommandEvent, StandardROIChangeBoundsCommandEvent,\
    ROIModifiedEvent

"""

ROI Definition:
   In this implementation, ROI is always defined with a VTK Extent. For example:
   an extent (0, 4, 0, 4, 0, 4) defines a 5x5x5 cube with a total of 25 voxels
   included.

   When millimeters are chosen as the measuring unit, the bounds, or the two corner
   points of the ROI, are converted to Extent. The pixels that are closest to
   the two corner points within the bounding box are used for the Extent.

   Note that the displayed ROI cube face planes are the 'real' boundaries of the ROI.
   For example, an ROI with extent (0,4, 0,4, 0,4), its bounds are displayed at
   (-0.5,4.5,-0.5,4.5,-0.5,4.5), which is theoretically and visually correct!

"""


class StandardROITool(MicroViewPlugIn.MicroViewPlugIn):

    # This class is both a plugin and an ROI provider
    interface.implements(IStandardROIProvider, IPlugin)

    __classname__ = "Standard ROI Tool..."
    __shortname__ = "StandardROITool"
    __label__ = "Standard ROI"
    __description__ = "Volume of interest selection tool"
    __iconname__ = "standard_roi"
    __menuentry__ = "|Tools|Standard ROI"
    __managergroup__ = "Tools"
    __tabname__ = "Standard ROI"
    __keybindings__ = [
        'KeyPress-7', 'KeyPress-8', 'Control-KeyPress-7', 'Control-KeyPress-8']

    def __init__(self, parent):

        MicroViewPlugIn.MicroViewPlugIn.__init__(self, parent)
        self._helpLink = 'standardroi-standard-roi-tool'

        # create a gui container for this plugin
        MicroViewPlugIn.MicroViewPlugIn.CreatePluginDialogFrame(self, parent)

        # This will hold an MVC controller object
        self._ROIController = None

        self.CreateGUI()

        # listen to certain zope events
        component.provideHandler(self.OnROIEnabledEvent)
        component.provideHandler(self.OnROIModifiedEvent)
        component.provideHandler(self.OnImageChangeEvent)
        component.provideHandler(self.onROIChangeExtentRequested)
        component.provideHandler(self.onROIChangeBoundsRequested)

        # fake our first change input event
        self.InvokeImageLoadedEvent()

    def CreateGUI(self):

        # create GUI in the standard way
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.gui = StandardROIGUIC.StandardROIGUIC(self._Dialog)
        self.sizer.Add(self.gui)
        self._Dialog.SetSizer(self.sizer)

        # create ROI Controller MVC object
        self._ROIController = ROIController.ROIController(self, self.gui)

    def getController(self):
        return self._ROIController

    @component.adapter(CurrentImageChangeEvent)
    def OnImageChangeEvent(self, evt):
        """Respond to a zope event that indicates current image has changed.

        The standard ROI tool uses an MVC model - defer most logic to the controller
        """
        self.getController().OnImageChangeEvent(evt)

    def CheckAndDisableROI(self, evt):
        image = component.getUtility(ICurrentImage)
        if image.GetStencilDataOwner() != "StandardROITool":
            if evt.GetPluginName() != self.GetShortName():
                self.getController().DisableROI(evt.GetImageIndex())

    @component.adapter(ROIEnabledEvent)
    def OnROIEnabledEvent(self, evt):
        self.CheckAndDisableROI(evt)

    @component.adapter(ROIModifiedEvent)
    def OnROIModifiedEvent(self, evt):
        self.CheckAndDisableROI(evt)

    @component.adapter(StandardROIChangeExtentCommandEvent)
    def onROIChangeExtentRequested(self, evt):
        """Someone external has requested that the standard ROI extent be changed"""
        self.getController().GetModel().setModelROIExtent(evt.GetExtent())

    @component.adapter(StandardROIChangeBoundsCommandEvent)
    def onROIChangeBoundsRequested(self, evt):
        """Someone external has requested that the standard ROI extent be changed"""
        self.getController().GetModel().setModelROIBounds(evt.GetBounds())

    def OnPluginClose(self):

        self.getController().DisableAllROIs()
        self.getController().OnPluginClose()

        # unregister our zope handlers
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.OnROIEnabledEvent)
        gsm.unregisterHandler(self.OnROIModifiedEvent)
        gsm.unregisterHandler(self.OnImageChangeEvent)
        gsm.unregisterHandler(self.onROIChangeExtentRequested)
        gsm.unregisterHandler(self.onROIChangeBoundsRequested)

    def ActivatePlugin(self):
        """Activate the plugin"""
        self.getController().EnableROI()

    def DisableROI(self, image_index):
        """Clear ROI for a particular image index"""
        self.getController().DisableROI(image_index)

    def GetROIBounds(self, image_index):
        """return the ROI bounds"""
        return self.getController().GetROIBounds(image_index)

    def GetROIExtent(self, image_index):
        """return the ROI extent"""
        return self.getController().GetROIExtent(image_index)

    def GetROIType(self, image_index):
        """return the ROI type"""
        return self.getController().GetROIType(image_index)

    def GetROIStencil(self, image_index):
        """Return a vtkImageStencilData built from ROI."""
        return self.getController().GetROIStencil(image_index)

    def GetModelROICenterInPixels(self, image_index=None):
        return self.getController().GetModelROICenterInPixels(image_index)

    def GetModelROICenterInMillimeters(self, image_index=None):
        return self.getController().GetModelROICenterInMillimeters(image_index)

    def GetModelROISizeInPixels(self, image_index=None):
        return self.getController().GetModelROISizeInPixels(image_index)

    def GetModelROISizeInMillimeters(self, image_index=None):
        return self.getController().GetModelROISizeInMillimeters(image_index)

    def SetModelROICenterInPixels(self, center, image_index=None):
        return self.getController().SetModelROICenterInPixels(center, image_index=image_index)

    def SetModelROICenterInMillimeters(self, center, image_index=None):
        return self.getController().SetModelROICenterInPixels(center, image_index=image_index)

    def _ResetROIPoints(self):
        if self._IgnoreResetPoints:
            return
        self._Point = [None, None]
        for i in range(2):
            self._Mark[i].SetOpacity(0.0)

    def SetROIType(self, roi_type):
        self.getController().SetROIType(roi_type)

    def SetROIPoints(self, point1, point2):
        """Set ROI by two diagonal corner points."""

        self.getController().SetPoints(point1, point2)

    def UpdateROIValues(self, evt=None):
        self._UpdateSizeEntries()
        self._UpdatePositionEntries()

##########################################################################


def createPlugin(panel):
    return StandardROITool(panel)
