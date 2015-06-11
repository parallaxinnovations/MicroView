import AdaptiveOtsuThresholdDialog


class AdaptiveOtsuThresholdDialogC(AdaptiveOtsuThresholdDialog.AdaptiveOtsuThresholdDialog):

    def __init__(self, parent, **kw):

        AdaptiveOtsuThresholdDialog.AdaptiveOtsuThresholdDialog.__init__(
            self, parent, **kw)

        self.m_textCtrlLowerCutoff.SetValue('-1000.0')
        self.m_spinCtrlChunkSize.SetValue(64)

        # OS X bug workaround
        val = self.m_spinCtrlChunkSize.GetValue()
        self.m_spinCtrlChunkSize.SetValue(val)

    def GetResults(self):

        try:
            return (float(self.m_textCtrlLowerCutoff.GetValue()), int(self.m_spinCtrlChunkSize.GetValue()))
        except ValueError:
            return None
