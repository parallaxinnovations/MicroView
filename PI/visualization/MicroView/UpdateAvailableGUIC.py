import UpdateAvailableGUI


class UpdateAvailableGUIC(UpdateAvailableGUI.UpdateAvailableGUI):

    def __init__(self, parent):

        UpdateAvailableGUI.UpdateAvailableGUI.__init__(self, parent)

    def SetVersion(self, version_string):

        s = "A new version of MicroView is available for download!\nVersion %s can be downloaded by using the following link:" % version_string
        self.m_staticTextVersionMessage.SetLabel(s)
        self.Layout()

    def SetShouldCheck(self, val):

        self.m_checkBoxShowDialog.SetValue(val)

    def getCheckboxState(self):

        return self.m_checkBoxShowDialog.GetValue()
