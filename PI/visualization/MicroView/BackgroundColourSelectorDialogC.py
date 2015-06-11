import BackgroundColourSelectorDialog


class ColourState(object):

    def __init__(self):
        self.top_colour = (35, 89, 136)
        self.bottom_colour = (127, 127, 127)
        self.bGradientOn = True
        self.bKeybindingNew = True

    def set(self, obj):
        self.top_colour = obj.GetTopColour()
        self.bottom_colour = obj.GetBottomColour()
        self.bGradientOn = obj.GetGradientState()
        self.bKeybindingNew = obj.GetKeybindingState()

    def copy(self):

        c = ColourState()
        c.top_colour = self.top_colour
        c.bottom_colour = self.bottom_colour
        c.bGradientOn = self.bGradientOn
        c.bKeybindingNew = self.bKeybindingNew

        return c

    def SetTopColour(self, c):
        self.top_colour = c

    def SetBottomColour(self, c):
        self.bottom_colour = c

    def SetGradientState(self, state):
        self.bGradientOn = state

    def GetTopColour(self):
        return self.top_colour

    def GetBottomColour(self):
        return self.bottom_colour

    def GetGradientState(self):
        return self.bGradientOn

    def GetKeybindingState(self):
        return self.bKeybindingNew


class BackgroundColourSelectorDialogC(BackgroundColourSelectorDialog.BackgroundColourSelectorDialog):

    def __init__(self, parent, state=None):

        BackgroundColourSelectorDialog.BackgroundColourSelectorDialog.__init__(
            self, parent)

        if state is None:
            state = ColourState()
        self._state = state.copy()

        # initialize values
        self.m_colourPickerTop.SetColour(self._state.top_colour)
        self.m_colourPickerBottom.SetColour(self._state.bottom_colour)
        self.m_checkBoxApplyGradient.SetValue(self._state.bGradientOn)
        self.m_staticText115.Enable(self._state.bGradientOn)
        self.m_colourPickerBottom.Enable(self._state.bGradientOn)

        self.m_radioBoxKeyBinding.SetSelection({
                                               True: 0, False: 1}[self._state.bKeybindingNew])

        # auto layout
        self.SetSize(self.GetBestSize())

    def onApplyGradient(self, evt):
        state = evt.IsChecked()
        self.m_staticText115.Enable(state)
        self.m_colourPickerBottom.Enable(state)
        self._state.bGradientOn = state

    def GetState(self):
        return self._state

    def onTopColourChanged(self, evt):
        self._state.top_colour = evt.GetColour()[0:3]

    def onBottomColourChanged(self, evt):
        self._state.bottom_colour = evt.GetColour()[0:3]

    def onKeyBindingChanged(self, evt):
        self._state.bKeybindingNew = {0: True, 1: False}[evt.GetSelection()]
