import LUTSelectionDialog
import ctrl
import data
import wx
import numpy


class LUTSelectionDialogC(LUTSelectionDialog.LUTSelectionDialog):

    def __init__(self, parent):
        LUTSelectionDialog.LUTSelectionDialog.__init__(self, parent)

        # create remaining GUI
        box = box = wx.BoxSizer(wx.VERTICAL)

        self.LD = data.LutData()

        self.lutControl = ctrl.LutCtrl(
            self.m_panelPalette, self.LD, 14, style=ctrl.LUT_CHOICE | ctrl.LUT_SPIN)
        box.Add(self.lutControl, 0, wx.EXPAND | wx.ALL, 2)
        self.m_panelPalette.SetSizer(box)

    def GetLUTIndex(self):
        return self.lutControl.GetValue()

    def SetLUTIndex(self, idx):
        self.lutControl.SetValue(idx)

    def GetLUT(self):
        rgb = self.LD.get_rgb(self.lutControl.GetValue())
        rgb2 = numpy.zeros([len(rgb[0]), 3], dtype='uint8')
        for i in range(3):
            rgb2[:, i] = numpy.fromstring(rgb[i], dtype='uint8')
        return rgb2
