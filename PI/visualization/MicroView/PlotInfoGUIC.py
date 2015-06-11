import wx
import PlotInfoGUI


class PlotInfoGUIC(PlotInfoGUI.PlotInfoGUI):

    """Custom PlotInfoGUI class that uses a wx.WrapSizer() to give us more flexibility"""

    def __init__(self, *args, **kw):

        PlotInfoGUI.PlotInfoGUI.__init__(self, *args, **kw)

        old_sizer = self.GetSizer()
        new_sizer = wx.WrapSizer()

        for si in old_sizer.GetChildren():
            sizer = si.GetSizer()
            old_sizer.Detach(sizer)
            new_sizer.Add(sizer, 0, 0, 0)

        self.SetSizer(new_sizer)
        self.Layout()
