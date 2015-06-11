import wx
import HistogramInfoGUI


class HistogramInfoGUIC(HistogramInfoGUI.HistogramInfoGUI):

    """Custom HistogramInfoGUI class that uses a wx.WrapSizer() to give us more flexibility"""

    def __init__(self, *args, **kw):

        HistogramInfoGUI.HistogramInfoGUI.__init__(self, *args, **kw)

        old_sizer = self.GetSizer()
        new_sizer = wx.WrapSizer()

        for si in old_sizer.GetChildren():
            sizer = si.GetSizer()
            old_sizer.Detach(sizer)
            new_sizer.Add(sizer, 0, 0, 0)

        self.SetSizer(new_sizer)

        bSizerLower = wx.BoxSizer(wx.HORIZONTAL)
        bSizerUpper = wx.BoxSizer(wx.HORIZONTAL)

        m_staticTextLower = wx.StaticText(
            self, wx.ID_ANY, u"Lower:", wx.DefaultPosition, wx.DefaultSize, 0)
        m_staticTextLower.Wrap(-1)
        bSizerLower.Add(
            m_staticTextLower, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_spinCtrlLower = wx.SpinCtrlDouble(
            self, -1, inc=0.01, name='lower')
        self.m_spinCtrlLower.SetDigits(2)
        bSizerLower.Add(
            self.m_spinCtrlLower, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        new_sizer.Add(bSizerLower, 0, 0, 5)

        m_staticTextUpper = wx.StaticText(
            self, wx.ID_ANY, u"Upper:", wx.DefaultPosition, wx.DefaultSize, 0)
        m_staticTextUpper.Wrap(-1)
        bSizerUpper.Add(
            m_staticTextUpper, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.m_spinCtrlUpper = wx.SpinCtrlDouble(
            self, -1, inc=0.01, name='upper')
        self.m_spinCtrlUpper.SetDigits(2)
        bSizerUpper.Add(
            self.m_spinCtrlUpper, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        new_sizer.Add(bSizerUpper, 0, 0, 5)

        self.Layout()
