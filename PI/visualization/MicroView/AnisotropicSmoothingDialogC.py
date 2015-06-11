import AnisotropicSmoothingDialog
import wx


class AnisotropicSmoothingDialogC(AnisotropicSmoothingDialog.AnisotropicSmoothingDialog):

    def __init__(self, parent, **kw):

        AnisotropicSmoothingDialog.AnisotropicSmoothingDialog.__init__(
            self, parent, **kw)

        # OS X bug workaround
        val = self.m_spinCtrlNumIterations.GetValue()
        self.m_spinCtrlNumIterations.SetValue(val)

    def GetResults(self):

        try:
            return (int(self.m_spinCtrlNumIterations.GetValue()),
                    float(self.m_textCtrlDiffusionThreshold.GetValue()),
                    float(self.m_textCtrlDiffusionFactor.GetValue()),
                    self.m_checkBoxUseFaces.GetValue(),
                    self.m_checkBoxUseEdges.GetValue(),
                    self.m_checkBoxUseCorners.GetValue(),
                    int(self.m_radioBox9.GetSelection()))
        except ValueError:
            return None

    def set_update_callback(self, callback):
        """set up a callback for the update button"""
        self.m_buttonUpdate.Bind(
            wx.EVT_BUTTON, lambda evt, d=self: callback(evt, d))
