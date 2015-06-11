import RescaleImageGUI


class RescaleImageGUIC(RescaleImageGUI.RescaleImageGUI):

    def __init__(self, parent):

        RescaleImageGUI.RescaleImageGUI.__init__(self, parent)
        self.SetSize(self.GetBestSize())

    def onTextValidate(self, event):

        event.Skip()

        enabled = False

        try:
            i = float(self.m_textCtrlOldValue1.GetValue())
            i = float(self.m_textCtrlOldValue2.GetValue())
            i = float(self.m_textCtrlNewValue1.GetValue())
            i = float(self.m_textCtrlNewValue2.GetValue())
            enabled = True
        except:
            pass

        self.m_buttonRescale.Enable(enabled)
