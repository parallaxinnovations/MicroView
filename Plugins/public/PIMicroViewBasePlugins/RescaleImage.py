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

import logging
import vtk
import wx

from zope import component, interface

from PI.visualization.MicroView.interfaces import IPlugin, ICurrentImage
from PI.visualization.MicroView.events import CurrentImageChangeEvent, NoImagesLoadedEvent
from PI.visualization.MicroView import MicroViewPlugIn
from PI.visualization.vtkMultiIO import MVImage
import RescaleImageGUIC


class RescaleImage(MicroViewPlugIn.MicroViewPlugIn):

    interface.implements(IPlugin)

    __classname__ = "Rescale Image"
    __label__ = "Rescale"
    __shortname__ = "RescaleImage"
    __description__ = "Rescale image with shift and scale"
    __iconname__ = "stock_rescale"
    __menuentry__ = "Process|Rescale Volume"
    __managergroup__ = None
    __tabname__ = "Rescale"

    def __init__(self, parent):

        MicroViewPlugIn.MicroViewPlugIn.__init__(self, parent)
        self._helpLink = ''

        # create a gui container for this plugin
        MicroViewPlugIn.MicroViewPlugIn.CreatePluginDialogFrame(self, parent)

        self.CreateGUI()

        # Bind events
        self.gui.m_buttonRescale.Bind(
            wx.EVT_BUTTON, self.onRescaleImageButton)

        # listen to certain zope events
        component.provideHandler(self.OnImageChangeEvent)
        component.provideHandler(self.OnNoImagesLoadedEvent)

        # disable/enable GUI
        try:
            image = component.getUtility(ICurrentImage)
        except:
            self.gui.Enable(False)

    @component.adapter(CurrentImageChangeEvent)
    def OnImageChangeEvent(self, evt):
        self.gui.Enable(True)

    @component.adapter(NoImagesLoadedEvent)
    def OnNoImagesLoadedEvent(self, evt):
        self.gui.Enable(False)

    def CreateGUI(self):

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self._Dialog.SetSizer(self.sizer)
        self.gui = RescaleImageGUIC.RescaleImageGUIC(self._Dialog)

    def OnPluginClose(self):
        # unregister our zope handlers
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.OnImageChangeEvent)
        gsm.unregisterHandler(self.OnNoImagesLoadedEvent)

    def Get_filter(self):

        x1 = float(self.gui.m_textCtrlOldValue1.GetValue())
        y1 = float(self.gui.m_textCtrlOldValue2.GetValue())
        x2 = float(self.gui.m_textCtrlNewValue1.GetValue())
        y2 = float(self.gui.m_textCtrlNewValue2.GetValue())

        if x1 == x2 and y1 == y2:
            logging.info(
                "Current values will have no effect.")
            return None

        if x1 == y1 or x2 == y2:
            logging.info("Cannot satisfy these shift/scale")
            return None

        shift = x2 - x1
        scale = (y2 - x2) / (y1 - x1)

        _type = [vtk.VTK_CHAR,
                 vtk.VTK_UNSIGNED_CHAR,
                 vtk.VTK_SHORT,
                 vtk.VTK_UNSIGNED_SHORT,
                 vtk.VTK_INT,
                 vtk.VTK_FLOAT,
                 vtk.VTK_DOUBLE][self.gui.m_choiceScalarType.GetSelection()]

        _filter = vtk.vtkImageShiftScale()
        _filter.SetInput(component.getUtility(ICurrentImage).GetRealImage())
        _filter.SetOutputScalarType(_type)
        _filter.SetScale(scale)
        _filter.SetShift(shift)
        _filter.SetClampOverflow(int(
            self.gui.m_checkBoxClampOverflow.GetValue()))

        return _filter

    def onRescaleImageButton(self, event):

        image = component.getUtility(ICurrentImage)
        _filter = self.Get_filter()

        if _filter is None:
            return

        with wx.BusyCursor():
            self.GetMicroView().SetInput(
                MVImage.MVImage(_filter.GetOutputPort(), input=image))


##########################################################################

def createPlugin(panel):
    return RescaleImage(panel)
