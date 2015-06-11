import ErodeDilateMorphologyDialog


class ErodeDilateMorphologyDialogC(ErodeDilateMorphologyDialog.ErodeDilateMorphologyDialog):

    def __init__(self, parent):
        ErodeDilateMorphologyDialog.ErodeDilateMorphologyDialog.__init__(
            self, parent)

        # OS X bug workaround
        val = self.m_spinCtrlNumberIterations.GetValue()
        self.m_spinCtrlNumberIterations.SetValue(val)

    def GetNumberIterations(self):
        """Gets the number of iterations selected by user"""
        return self.m_spinCtrlNumberIterations.GetValue()
