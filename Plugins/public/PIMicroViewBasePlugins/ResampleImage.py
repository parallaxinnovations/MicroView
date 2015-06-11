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
ResampleImage - a plugin for reducing image size by resampling.
"""

import vtk
import wx
import os
import datetime
from zope import component, interface
from vtkEVS import EVSFileDialog
from PI.visualization.vtkMultiIO import MVImage
from PI.visualization.MicroView.interfaces import IPlugin, ICurrentImage, ICurrentMicroViewInput
from PI.visualization.MicroView.events import CurrentImageChangeEvent, NoImagesLoadedEvent
from PI.visualization.MicroView import MicroViewPlugIn

import ResampleImageGUIC


class ResampleImage(MicroViewPlugIn.MicroViewPlugIn):

    interface.implements(IPlugin)

    __classname__ = "Resample Image..."
    __label__ = "Resample"
    __shortname__ = "ResampleImage"
    __description__ = "Resample the image based on the factor specified by the user"
    __iconname__ = "stock_resample"
    __menuentry__ = "Process|Resample Volume"
    __managergroup__ = None
    __tabname__ = "Resample"

    def __init__(self, parent):
        MicroViewPlugIn.MicroViewPlugIn.__init__(self, parent)

        self._helpLink = 'image-resample-tool'

        # create a gui container for this plugin
        MicroViewPlugIn.MicroViewPlugIn.CreatePluginDialogFrame(self, parent)

        # get panel
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.gui = ResampleImageGUIC.ResampleImageGUIC(self._Dialog)
        vbox.Add(self.gui)
        self._Dialog.SetSizer(vbox)

        # wire up events
        self.gui.m_textCtrlResampleFactor.Bind(wx.EVT_TEXT, self.UpdateGUI)
        self.gui.m_buttonResample.Bind(wx.EVT_BUTTON, self.Resample)

        self._default_write_extension = 'vff'

        # listen to certain zope events
        component.provideHandler(self.OnImageChangeEvent)
        component.provideHandler(self.OnNoImagesLoadedEvent)

        # disable/enable GUI
        try:
            image = component.getUtility(ICurrentImage)
        except:
            self.gui.Enable(False)

        # Invoke an event to react to currently loaded image
        self.InvokeImageLoadedEvent()

    def OnPluginClose(self):
        # unregister our zope handlers
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.OnImageChangeEvent)
        gsm.unregisterHandler(self.OnNoImagesLoadedEvent)

    def UpdateGUI(self, event):
        self.UpdateConversionText()

    @component.adapter(CurrentImageChangeEvent)
    def OnImageChangeEvent(self, evt):
        self.gui.Enable(True)
        self.UpdateConversionText()

    @component.adapter(NoImagesLoadedEvent)
    def OnNoImagesLoadedEvent(self, evt):
        self.gui.Enable(False)

    def UpdateConversionText(self, factor=None):
        in_spacing = component.getUtility(ICurrentImage).GetSpacing()
        if factor is not None:
            self.gui.m_textCtrlResampleFactor.SetValue(str(factor))
        try:
            f = float(self.gui.m_textCtrlResampleFactor.GetValue())
            out_spacing = [in_spacing[0] * f, in_spacing[
                1] * f, in_spacing[2] * f]
            self.gui.m_staticTextOriginalSize.SetLabel("%0.3f x %0.3f x %0.3f" % (
                in_spacing[0], in_spacing[1], in_spacing[2]))
            self.gui.m_staticTextResampledSize.SetLabel("%0.3f x %0.3f x %0.3f" % (
                out_spacing[0], out_spacing[1], out_spacing[2]))
            self.gui.m_buttonResample.Enable(True)
        except:
            self.gui.m_staticTextOriginalSize.SetLabel("%0.3f x %0.3f x %0.3f" % (
                in_spacing[0], in_spacing[1], in_spacing[2]))
            self.gui.m_staticTextResampledSize.SetLabel("-- invalid input --")
            self.gui.m_buttonResample.Enable(False)

    def Resample(self, event):

        FactorValue = float(self.gui.m_textCtrlResampleFactor.GetValue())

        resample = vtk.vtkImageResample()
        for i in range(3):
            resample.SetAxisMagnificationFactor(i, 1.0 / FactorValue)

        # next line ensures that the image is padded with a reasonable value
        image = component.getUtility(ICurrentImage)
        header = image.GetHeader()

        try:
            background = header['water']
        except:
            background = 0

        resample.SetBackgroundLevel(background)
        resample.SetInterpolationModeToCubic()
        resample.SetInput(image.GetRealImage())

        # Update header
        header['date'] = datetime.datetime.now().isoformat()

        # Modify title
        if 'title' in header:
            header['title'] = '%s (Resampled)' % (header['title'])
        else:
            header[
                'title'] = "Generated by Parallax Innovations MicroView (Resampled)"

        # make sure output image origin is correct
        o = image.GetOrigin()
        f = vtk.vtkImageChangeInformation()
        f.SetInput(resample.GetOutput())
        f.SetOutputOrigin(o)

        output = MVImage.MVImage(f.GetOutputPort(), input=image)
        output.UpdateInformation()

        self.GetMicroView().SetInput(output)

##########################################################################


def createPlugin(panel):
    return ResampleImage(panel)
