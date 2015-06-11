import wx
import WindowLevelDialogGUI
from PI.visualization.MicroView import ctrl
from PI.visualization.MicroView.events import SetWindowLevelCommand
from PI.visualization.MicroView.data import LutData
from zope import event


class WindowLevelDialogGUIC(WindowLevelDialogGUI.WindowLevelDialogGUI):

    def __init__(self, parent, **kw):

        WindowLevelDialogGUI.WindowLevelDialogGUI.__init__(self, parent)

        self.lower_label = ['Window: ', 'Minimum: ']
        self.upper_label = ['Level: ', 'Maximum: ']
        self._mode = None
        self.__lut_index = 0

        # -- start -- add some addition components to GUI
        sizer = wx.FlexGridSizer(0, 2, 0, 0)
        sizer.SetFlexibleDirection(wx.BOTH)
        sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        self.m_staticTextMinLabel = wx.StaticText(
            self.m_panelThresholds, wx.ID_ANY, u"Minimum: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextMinLabel.Wrap(-1)
        sizer.Add(self.m_staticTextMinLabel, 0,
                  wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        # the increment size will be either 0.5 or one percent of range
        increment = 0.01

        self.m_spinCtrlLower = wx.SpinCtrlDouble(
            self.m_panelThresholds, -1, name='lower', inc=increment, initial=0.0)
        self.m_spinCtrlLower.SetDigits(2)

        sizer.Add(self.m_spinCtrlLower, 0, wx.ALL, 5)

        self.m_staticTextMaxLabel = wx.StaticText(
            self.m_panelThresholds, wx.ID_ANY, u"Maximum: ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticTextMaxLabel.Wrap(-1)
        sizer.Add(self.m_staticTextMaxLabel, 0,
                  wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.m_spinCtrlUpper = wx.SpinCtrlDouble(
            self.m_panelThresholds, -1, name='upper', inc=increment, initial=0.0)
        self.m_spinCtrlUpper.SetDigits(2)

        sizer.Add(self.m_spinCtrlUpper, 0, wx.ALL, 5)

        self.m_panelThresholds.SetSizer(sizer)

        # histogram control
        sizer = wx.BoxSizer(wx.VERTICAL)
        panel = self.getHistogramPanel()
        panel.SetSizer(sizer)

        lut_data = LutData()
        self.histogram_control = ctrl.HistogramCtrl(
            panel, lut_data, self.__lut_index, minspan=10)
        self.histogram_control.Bind(ctrl.EVT_RANGE, self.OnHistogram)
        sizer.Add(self.histogram_control, 1, wx.ALL | wx.EXPAND, 2)
        panel.Layout()

        # -- end -- add some addition components to GUI
        self.scalar_range = r = kw['scalar_range']
        self.current_range = _min, _max = kw['current_range']
        w = _max - _min
        l = (_min + _max) / 2.0
        self.current_wl = wl = (w, l)

        self.l_validators = ({'min':    0, 'max': r[1] - r[0]},  # w/l
                             {'min': r[0], 'max': r[1]})       # min/max
        self.u_validators = ({'min': r[0], 'max': r[1]},       # w/l
                             {'min': r[0], 'max': r[1]})       # min/max

        if kw['mode'] == 'Window/Level':
            idx = 0
        else:
            idx = 1

        # Add event handlers
        self.m_spinCtrlLower.Bind(wx.EVT_SPINCTRLDOUBLE, self.onSpinCtrlEvent)
        self.m_spinCtrlUpper.Bind(wx.EVT_SPINCTRLDOUBLE, self.onSpinCtrlEvent)

        self.m_radioBoxInteractionMode.SetSelection(idx)
        self.setMode(idx)

    def onSpinCtrlEvent(self, evt):

        # Adjust internals
        self.UpdateLevelsFromSpinControls()

        # Now update the histogram widget
        _min, _max = self.current_range
        self.histogram_control.SetCurrentRange([_min, _max])

    def onCancelButton(self, evt):
        evt.Skip()

    def onOkButton(self, evt):
        self.UpdateLevelsFromSpinControls()
        evt.Skip()

    def UpdateLevelsFromSpinControls(self):

        i = self.m_radioBoxInteractionMode.GetSelection()

        if i == 0:  # final setting was window/level
            w, l = self.current_wl = (
                self.m_spinCtrlLower.GetValue(), self.m_spinCtrlUpper.GetValue())
            self.current_range = (l - w / 2.0, l + w / 2.0)
        else:
            l = self.m_spinCtrlLower.GetValue()
            u = self.m_spinCtrlUpper.GetValue()
            if l >= u:
                err = 1
                dlg = wx.MessageDialog(
                    self, "Upper threshold must be greater than lower threshold!", 'Warning', wx.OK | wx.ICON_WARNING)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                self.current_wl = (u - l, (l + u) / 2.0)
                self.current_range = (l, u)

        _min, _max = self.current_range
        event.notify(SetWindowLevelCommand(_min, _max))

    def onIteractionModeChange(self, evt):

        # grab existing values and convert them
        v0 = self.m_spinCtrlLower.GetValue()
        v1 = self.m_spinCtrlUpper.GetValue()

        i = evt.GetInt()

        if i == 0:  # previous setting was min/max
            self.current_range = _min, _max = v0, v1
            w = _max - _min
            l = (_min + _max) / 2.0
            self.current_wl = (w, l)
            self.setMode(i)
        else:  # previous setting was window/level
            w, l = v0, v1
            self.current_range = _min, _max = (l - w / 2.0, l + w / 2.0)
            self.current_wl = (w, l)
            self.setMode(i)

    def getMode(self):
        return self._mode

    def setMode(self, idx):

        self._mode = idx
        i = idx

        self.m_staticTextMinLabel.SetLabel(self.lower_label[i])
        self.m_staticTextMaxLabel.SetLabel(self.upper_label[i])

        self.m_spinCtrlLower.SetRange(self.l_validators[
                                      idx]['min'], self.l_validators[idx]['max'])
        self.m_spinCtrlUpper.SetRange(self.u_validators[
                                      idx]['min'], self.u_validators[idx]['max'])

        if i == 0:
            v0, v1 = self.current_wl
            self.m_spinCtrlLower.SetIncrement(1.0)
            self.m_spinCtrlUpper.SetIncrement(0.5)
        else:
            v0, v1 = self.current_range
            self.m_spinCtrlLower.SetIncrement(1.0)
            self.m_spinCtrlUpper.SetIncrement(1.0)

        self.m_spinCtrlLower.SetValue(v0)
        self.m_spinCtrlUpper.SetValue(v1)

    def getWindowAndLevel(self):
        return self.current_wl

    def getTableRange(self):
        return self.current_range

    def getMode(self):
        return self.m_radioBoxInteractionMode.GetSelection()

    def getImmediateUpdates(self):
        return int(self.m_radioBoxUpdateMode.GetSelection() == 0)

    def getHistogramPanel(self):
        return self.m_panelHistogram

    def getHistogramControl(self):
        return self.histogram_control

    def OnHistogram(self, evt):
        _min, _max = evt.GetRange()

        if self.getMode() == 0:
            # w/l
            w = (_max - _min)
            l = (_max + _min) / 2.0
            _min, _max = w, l

        self.m_spinCtrlLower.SetValue(_min)
        self.m_spinCtrlUpper.SetValue(_max)
        self.UpdateLevelsFromSpinControls()
