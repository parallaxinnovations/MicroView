import ChooseFilterRadiusDialog


class ChooseFilterRadiusDialogC(ChooseFilterRadiusDialog.ChooseFilterRadiusDialog):

    def __init__(self, parent, filtername, radius, image3d):
        ChooseFilterRadiusDialog.ChooseFilterRadiusDialog.__init__(
            self, parent)
        self.SetFilterName(filtername)
        self.SetRadius(radius)
        self.Set3DFilterCheckboxState(image3d)
        self.Layout()

    def SetFilterName(self, name):
        self.m_staticTextVersionMessage.SetLabel(
            "Enter {0} filter radius:".format(name))

    def SetRadius(self, radius):
        self.m_textCtrlRadius.SetValue(radius)

    def GetRadius(self):
        return self.m_textCtrlRadius.GetValue()

    def Set3DFilterCheckboxState(self, val):
        self.m_checkBox3DFilter.SetValue(val)

    def Get3DFilterCheckboxState(self):
        return self.m_checkBox3DFilter.GetValue()
