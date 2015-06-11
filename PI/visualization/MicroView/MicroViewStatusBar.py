# =========================================================================
#
# Copyright (c) 2011-2015 Parallax Innovations Inc.
#
# Use, modification and redistribution of the software, in source or
# binary forms, are permitted provided that the following terms and
# conditions are met:
#
# 1) Redistribution of the source code, in verbatim or modified
#   form, must retain the above copyright notice, this license,
#   the following disclaimer, and any notices that refer to this
#   license and/or the following disclaimer.
#
# 2) Redistribution in binary form must include the above copyright
#    notice, a copy of this license and the following disclaimer
#   in the documentation or with other materials provided with the
#   distribution.
#
# 3) Modified copies of the source code must be clearly marked as such,
#   and must not be misrepresented as verbatim copies of the source code.
#
# EXCEPT WHEN OTHERWISE STATED IN WRITING BY THE COPYRIGHT HOLDERS AND/OR
# OTHER PARTIES, THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE
# SOFTWARE "AS IS" WITHOUT EXPRESSED OR IMPLIED WARRANTY INCLUDING, BUT
# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE.  IN NO EVENT UNLESS AGREED TO IN WRITING WILL
# ANY COPYRIGHT HOLDER OR OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
# THE SOFTWARE UNDER THE TERMS OF THIS LICENSE BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, LOSS OF DATA OR DATA BECOMING INACCURATE OR LOSS OF PROFIT OR
# BUSINESS INTERRUPTION) ARISING IN ANY WAY OUT OF THE USE OR INABILITY TO
# USE THE SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
#
# =========================================================================

import logging
import vtk
import wx
import wx.lib.stattext
import StockItems
from zope import component, event
from collections import OrderedDict
from PI.visualization.MicroView.interfaces import ICurrentOrthoView, ICurrentImage
from PI.visualization.MicroView.events import ShowWindowLevelDialogEvent, WindowLevelPresetEvent

logger = logging.getLogger(__name__)


class StatusBarMenu(wx.lib.stattext.GenStaticText):

    """A static text control that acts like a menu for use in MicroView's status bar"""

    def __init__(self, *args, **kw):

        wx.lib.stattext.GenStaticText.__init__(self, *args, **kw)

        # load static icon
        self.up_down_bitmap = StockItems.StockIconFactory().getBitmap(
            'up-down-arrows')

        self.full_rect = None

    def SetRect(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        """
        self.full_rect = args[0]
        wx.lib.stattext.GenStaticText.SetRect(self, args[0])

    def SetWindowLevelLabel(self, label):
        self.SetLabel(label)
        self.Update()

    def OnPaint(self, evt):

        # repaint full area
        self.SetClientRect(self.full_rect)

        BUFFERED = 1
        if BUFFERED:
            dc = wx.BufferedPaintDC(self)
        else:
            dc = wx.PaintDC(self)

        width = self.full_rect.width
        height = self.full_rect.height

        if not width or not height:
            return

        if BUFFERED:
            clr = self.GetBackgroundColour()
            self.defBackClr = clr
            if wx.Platform == "__WXMAC__" and clr == self.defBackClr:
                # if colour is still the default then use the theme's
                # background on Mac
                themeColour = wx.MacThemeColour(1)
                backBrush = wx.Brush(themeColour)
            else:
                backBrush = wx.Brush(clr, wx.SOLID)
            dc.SetBackground(backBrush)
            dc.Clear()

        if self.IsEnabled():
            dc.SetTextForeground(self.GetForegroundColour())
        else:
            dc.SetTextForeground(
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))

        dc.SetFont(self.GetFont())
        label = self.GetLabel()
        style = self.GetWindowStyleFlag()

        x = y = 0
        # TODO: figure out a platform agnostic way to do this
        if wx.Platform == "__WXMAC__":
            y -= 3

        for line in label.split('\n'):
            if line == '':
                w, h = self.GetTextExtent('W')  # empty lines have height too
            else:
                w, h = self.GetTextExtent(line)
            if style & wx.ALIGN_RIGHT:
                x = width - w
            if style & wx.ALIGN_CENTER:
                x = (width - w) / 2
            dc.DrawText(line, x, y)
            y += h

        # draw arrow (either using native methods or by using a bitmap)
        if 0:
            # draw native rendered arrow
            renderer = wx.RendererNative.Get()

            w = 16
            h = height
            x = width - 1 - w
            y = (height - h) / 2

            renderer.DrawDropArrow(self, dc, (x, y, w, y), wx.CONTROL_CURRENT)
        else:
            # draw bitmap arrow
            width = self.full_rect.width
            height = self.full_rect.height
            w, h = self.up_down_bitmap.GetSize()
            x = width - 1 - w
            y = (height - h) / 2

            dc.DrawBitmap(self.up_down_bitmap, x, y, useMask=False)


class MicroViewStatusBar(wx.StatusBar):

    """A specialized StatusBar that draws itself to add popup menus etc."""

    def __init__(self, parent):

        wx.StatusBar.__init__(self, parent)

        # wire up events early
        component.provideHandler(self.onWindowLevelPresetEvent)

        # pre-sets
        self._current_windowlevel_preset = None
        self.window_level_presets = OrderedDict([('Auto-adjust (99%)', [99, 99]),
                                                 ('Auto-adjust (90%)',
                                                  [90, 90]),
                                                 ('Brain', [80, 50]),
                                                 ('Lung', [1400, 400]),
                                                 ('Bone', [1800, 800]),
                                                 ('Skull', [3500, 1000]),
                                                 ('Abdomen', [998, 720])])

        self.SetFieldsCount(6)
        self.SetInitialSize()

        # decide on initial sizes for everything

        f = self.GetFont()
        dc = wx.WindowDC(self)
        dc.SetFont(f)

        # first width
        main_width, height = dc.GetTextExtent(
            'Save a reformatted copy of the image')
        main_width = int(main_width * 1.25)

        # remaining widths
        progress_width, height = dc.GetTextExtent("100.0 %")
        gray_width, height = dc.GetTextExtent("Gray Scale Value: 32767.000")
        pos1_width, height = dc.GetTextExtent(
            "Pos(X,Y): %0.3f, %0.3f %s" % (5000.000, 5000.000, 'mm'))
        pos2_width, height = dc.GetTextExtent("Wavelength: %0.3f mm" % 500.000)
        pos3_width, height = dc.GetTextExtent(
            "Window/Level: 10000.00 / 10000.00")

        self.SetStatusWidths(
            [main_width, progress_width, gray_width, pos1_width, pos2_width, pos3_width])

        # default status
        self.SetStatusText("Ready", 0)

        # default percentage
        self.SetStatusText("", 1)

        # default Graylevel value
        self.SetStatusText("Value:", 2)

        # default position:
        self.SetStatusText("Pos(X,Y):", 3)
        self.SetStatusText("Pos(Z):", 4)

        self.window_level_text = StatusBarMenu(self, -1, "Window/Level:")
        self.window_level_text.Bind(
            wx.EVT_LEFT_DOWN, self.onWindowLevelButtonPressed)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.PlaceObjects()

    def __del__(self):
        # unregister our zope handlers
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.onWindowLevelPresetEvent)

    def GetWindowLevelText(self):
        return self.window_level_text

    def SetWindowLevelText(self, label):
        self.window_level_text.SetWindowLevelLabel(label)

    def onWindowLevelButtonPressed(self, evt):
        """Event handler when user first clicks on W/L label"""

        # display a popup menu
        menu = wx.Menu()

        _id = wx.NewId()
        menu.Append(
            _id, "Edit Window/Level Properties", "Edit Window/Level Properties")
        self.Bind(wx.EVT_MENU, self.onEditWindowLevelProperties, id=_id)
        menu.AppendSeparator()

        count = 0
        for key in self.window_level_presets:
            # put a separator after auto-level entries
            if count == 2:
                menu.AppendSeparator()
            _id = wx.NewId()
            menu.Append(_id, key, "%s preset window/level" %
                        key, kind=wx.ITEM_CHECK)
            menu.Check(_id, key == self._current_windowlevel_preset)
            self.Bind(
                wx.EVT_MENU, lambda evt, val=key: self.onWindowLevelPreset(evt, val), id=_id)
            count += 1

        rect = self.window_level_text.GetRect()

        if wx.Platform == '__WXMAC__':
            offset = 0
        else:
            offset = 32

        pos = (rect[0] - 4, rect[1] - offset)
        self.PopupMenu(menu, pos)
        menu.Destroy()

    def onWindowLevelPreset(self, evt, modename):
        """Set Window/Level to a preset value"""
        event.notify(WindowLevelPresetEvent(modename))

    @component.adapter(WindowLevelPresetEvent)
    def onWindowLevelPresetEvent(self, evt):

        self._current_windowlevel_preset = modename = evt.GetPreset()

        if modename in ('Auto-adjust (90%)', 'Auto-adjust (99%)'):
            level = self.window_level_presets[modename][0]
            image = component.getUtility(ICurrentImage)

            stats = image.GetHistogramStatistics()
            stats.SetAutoRangePercentiles(100 - level, level)
            stats.Update()
            _min, _max = stats.GetAutoRange()

        else:
            w, l = self.window_level_presets[modename]
            _min = l - w / 2
            _max = l + w / 2

        orthoview = component.getUtility(ICurrentOrthoView)
        orthoview.GetLookupTable().SetTableRange(_min, _max)

        # force a redraw
        orthoview.Render()

    def onEditWindowLevelProperties(self, evt):
        """Event handler for user selecting 'Edit Properties' menu item"""

        self._current_windowlevel_preset = None
        event.notify(ShowWindowLevelDialogEvent())

    def displayEditWindowLevelDialog(self):
        """Override me"""
        pass

    def PlaceObjects(self):
        """Place objects at correct locations"""
        # only the popup menu needs to be positioned

        rect = self.GetFieldRect(5)
        rect.x += 4
        rect.y += 3
        rect.width -= 4
        rect.height -= 3
        self.window_level_text.SetRect(rect)

    def OnSize(self, evt):
        """Adjust the size of internal objects when window is sized"""
        evt.Skip()
        self.PlaceObjects()
