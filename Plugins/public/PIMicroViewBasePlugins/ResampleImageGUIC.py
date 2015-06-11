import wx
import ResampleImageGUI


class ResampleImageGUIC(ResampleImageGUI.ResampleImageGUI):

    def __init__(self, parent):

        ResampleImageGUI.ResampleImageGUI.__init__(self, parent)

        self.SetSize(self.GetBestSize())

    def onResampleButton(self, event):
        event.Skip()
