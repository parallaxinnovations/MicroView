import OpenCloseMorphologyDialog


class OpenCloseMorphologyDialogC(OpenCloseMorphologyDialog.OpenCloseMorphologyDialog):

    def __init__(self, parent):

        OpenCloseMorphologyDialog.OpenCloseMorphologyDialog.__init__(
            self, parent)
        # OS X bug workaround
        val = self.m_spinCtrlX.GetValue()
        self.m_spinCtrlX.SetValue(val)
        val = self.m_spinCtrlY.GetValue()
        self.m_spinCtrlY.SetValue(val)
        val = self.m_spinCtrlZ.GetValue()
        self.m_spinCtrlZ.SetValue(val)

        # make sure we fit properly
        self.Fit()

    def GetResults(self):

        # return results from dialog
        return {
            'KernelSizeX': self.m_spinCtrlX.GetValue(),
            'KernelSizeY': self.m_spinCtrlY.GetValue(),
            'KernelSizeZ': self.m_spinCtrlZ.GetValue(),
            'OpenValue': float(self.m_textCtrlOpenValue.GetValue()),
            'CloseValue': float(self.m_textCtrlCloseValue.GetValue()),
        }
