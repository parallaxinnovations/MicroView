#!/usr/bin/env python

"""
LUT Controls

These controls deal with Look-up table selection, histogram display and
opacity interactive selection

* LutPanel: A dumb widget for displaying a LUT

* LutCtrl: LUT selection widget
Use the spin or drop down selector to choose a new LUT. An event is
generated.

* HistogramCtrl: Displays a histogram with LUT overlayed
This widget displays a histogram and allows min/max selection.
Right click displays a list of LUTs. Double click inside the selection
expands the selection to min/max. Clicking and dragging the left or
right handle modifies the selection. Clicking and dragging inside both
handles simultaneously.

* OpacityCtrl: Opacity function definition
Opacity is combined with LUT selection to provide full interactive
RGBA selection. This can then be used with VTK or any other module that
requires RGBA Look-up tables.
- A look-up table is displayed on top of a checker background image.
  Dragging the nodes up increases opacity, down decreases. Depending on
  opacity, the background may or may not be visible through the look-up
  table image.
- Double click adds or removes a node.
- At the moment, right click displays an add/remove node menu
- The +/= or - keys can also be used.


Original LUT data located on http://rsb.info.nih.gov/ij/download/luts/
Rasband, W.S., ImageJ, U. S. National Institutes of Health, Bethesda,
Maryland, USA, http://rsb.info.nih.gov/ij/, 1997-2005.

The latest version of this file is stored in my google code repository:
    http://code.google.com/p/ezwidgets/

Copyright (c) 2007 Egor Zindy <ezindy@gmail.com>

Released under the MIT licence.
"""
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

__author__ = "Egor Zindy <ezindy@gmail.com>"
__copyright__ = "Copyright (c) 2007 Egor Zindy"
__license__ = "MIT"
__version__ = "1.1"
__date = "2010-01-10"
__status__ = "Production"

import wx
import wx.lib.newevent
import numpy as np
import math
import enum


class DrawingMode(enum.Enum):
    not_set = 1
    composite = 2
    isosurface = 3


RangeEvent, EVT_RANGE = wx.lib.newevent.NewEvent()
UpdateEvent, EVT_UPDATE = wx.lib.newevent.NewEvent()
LutEvent, EVT_LUT = wx.lib.newevent.NewEvent()
SubmitEvent, EVT_SUBMIT = wx.lib.newevent.NewEvent()

# styles for LutCtrl
LUT_CHOICE = 1
LUT_SPIN = 2

# alternate color1/color2 d-wide squares and return the w-h image
# rectangle as a RGBA string.


def make_checker(w, h, d, color1=(255, 255, 255), color2=(0, 0, 0)):

    if w <= 0 or h <= 0:
        return None

    nx = int(math.ceil(float(w) / 2. / d))
    ny = int(math.ceil(float(h) / 2. / d))

    # colours with alpha:
    c1 = list(color1) + [255]
    c2 = list(color2) + [255]

    # only need one line... (RGBA)
    line = np.array(((c1 * d) + (c2 * d)) * (nx + 1), dtype=np.uint8)

    # these are the two rows of squares:
    row1 = np.array([line[:-d * 4]] * d)
    row2 = np.array([line[d * 4:]] * d)

    # now do an image and return it as a string...
    image = np.vstack([row1, row2] * ny)
    return image[:h, :w * 4].tostring()


class LutPanel(wx.Panel):

    def __init__(self, parent, LutData, lut_index=0, size=(-1, 24)):
        wx.Panel.__init__(self, parent, -1, size=size, style=wx.SUNKEN_BORDER)

        self.LutData = LutData

        if lut_index >= self.LutData.get_count():
            lut_index = 0

        self.SetLutIndex(lut_index, redraw=0)

        self.box = wx.BoxSizer(wx.VERTICAL)
        self.sb = wx.StaticBitmap(self, -1)
        self.box.Add(self.sb, 1, wx.EXPAND)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.box.Layout()
        self.SetSizer(self.box)

    def OnSize(self, evt):
        self.Redraw()

    def Redraw(self):
        w, h = self.GetClientSize()
        if self.img is None or w <= 0 or h <= 0:
            return

        self.sb.SetToolTip(wx.ToolTip(self.LutData._names[
                           self.lut_index] + " (%d)" % self.lut_index))
        self.sb.SetBitmap(self.img.Scale(w, h).ConvertToBitmap())
        self.Refresh()

    def GetLutCount(self):
        return len(self.LutData._names)

    def GetLutIndex(self):
        return self.lut_index

    def GetLutNames(self):
        return self.LutData._names

    def GetLutName(self):
        return self.LutData.get_name(self.lut_index)

    def GetLut(self):
        return self.LutData.get_lut(self.lut_index)

    def GetLutRGB(self):
        return self.LutData.get_rgb(self.lut_index)

    # select a LUT to display
    def SetLutIndex(self, lut_index, redraw=1):
        self.lut_index = lut_index

        self.SetToolTipString(self.GetLutName())

        s = self.LutData.get_lut(lut_index)
        image = wx.EmptyImage(256, 1)
        image.SetData(s)

        self.img = image

        if redraw:
            self.Redraw()


class LutCtrl(wx.Panel):

    def __init__(self, parent, LutData, lut_index=0, size=(-1, 24), style=LUT_SPIN):
        wx.Panel.__init__(self, parent, -1)

        self.LutData = LutData

        self.box = wx.BoxSizer(wx.HORIZONTAL)
        self.lp = LutPanel(self, LutData, lut_index, size=size)
        self.lut_index = lut_index
        self.spin = None
        self.ch = None

        # do the choice style...
        if style & LUT_CHOICE > 0:
            self.ch = wx.Choice(self, -1, size=wx.Size(
                90, -1), choices=self.lp.GetLutNames())
            self.ch.SetSelection(lut_index)
            self.box.Add(self.ch, 0)
            self.Bind(wx.EVT_CHOICE, self.OnChoice, self.ch)

        self.box.Add(self.lp, 1, wx.EXPAND)

        # do the spin style
        if style & LUT_SPIN > 0:
            height = size[1]
            self.spin = wx.SpinButton(self, -1, size=(
                height * .67, height), style=wx.SP_VERTICAL)
            self.spin.SetRange(0, self.lp.GetLutCount() - 1)
            self.spin.SetValue(lut_index)
            self.box.Add(self.spin, 0, wx.EXPAND)
            self.Bind(wx.EVT_SPIN, self.OnSpin, self.spin)

        self.box.Layout()
        self.SetSizer(self.box)

        self.GetLutCount = self.lp.GetLutCount
        self.GetLutIndex = self.lp.GetLutIndex
        self.GetLutRGB = self.lp.GetLutRGB
        self.GetLut = self.lp.GetLut
        self.GetLutName = self.lp.GetLutName

    def GetValue(self):
        return self.GetLutIndex()

    def SetValue(self, lut_index):
        self.SetLutIndex(lut_index)

    def SetLutIndex(self, lut_index, redraw=1):
        self.lp.SetLutIndex(lut_index, redraw)
        if self.ch is not None:
            self.ch.SetSelection(lut_index)

    def OnChoice(self, evt):
        lut_index = self.ch.GetSelection()
        self.DoEvent(lut_index)
        self.Update(lut_index)

    def OnSpin(self, evt):
        lut_index = evt.GetPosition()
        self.DoEvent(lut_index)
        self.Update(lut_index)

    def DoEvent(self, lut_index):
        if lut_index != self.lut_index:
            self.lut_index = lut_index
            self.SetLutIndex(lut_index, redraw=1)

            lut_event = LutEvent(
                GetLut=self.GetLut,
                GetLutCount=self.GetLutCount,
                GetLutIndex=self.GetLutIndex,
                GetLutRGB=self.GetLutRGB,
                GetLutName=self.GetLutName)
            wx.PostEvent(self, lut_event)

    def Update(self, lut_index=None):
        if lut_index is None:
            lut_index = self.lut_index

        if self.spin is not None:
            self.spin.SetValue(lut_index)

        if self.ch is not None:
            self.ch.SetSelection(lut_index)


class HistogramCtrl(wx.ScrolledWindow):

    """\brief The histogram control, a scrolled window"""

    histogram = None
    histogram_scaled = None
    nbins = None
    bmp_histogram = None
    img_lut = None
    bmp_bg = None

    buffer = None

    absolute_range = None
    current_range = None
    stored_range = None

    left_dc = 0
    right_dc = 255

    min_span = 0.01

    x_delta = 0
    y_delta = 0

    active_bar = None

    def __init__(self, parent, LutData, lut_index=0, histogram=None, absolute_range=[0, 255], current_range=[0, 255], minspan=0.01, size=(-1, 50)):
        wx.ScrolledWindow.__init__(
            self, parent, -1, size=size, style=wx.SUNKEN_BORDER)

        self.histo_image = None

        self.LutData = LutData
        if lut_index >= LutData.get_count():
            lut_index = 0

        # set the absolute range...
        self.SetAbsoluteRange(absolute_range)
        self.SetCurrentRange(current_range)

        self.SetLutIndex(lut_index, redraw=0)
        self.SetHistogram(histogram)

        self.potential_bar = -1
        self.flag_clicked = 0

        self.min_span = minspan
        self.x = self.y = 0
        self.drawing = False
        self.tt = wx.ToolTip("")
        self.SetToolTip(self.tt)

        self.SetSelCursor()

        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseEvent)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClickEvent)
        self.Bind(wx.EVT_LEFT_UP,   self.OnMouseEvent)
        self.Bind(wx.EVT_RIGHT_UP,   self.OnRightUpEvent)
        self.Bind(wx.EVT_MOTION,    self.OnMouseEvent)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

    def SetData(self, data, nbins=None, absolute_range=None, current_range=None):
        if self.nbins is None and nbins is None:
            self.nbins = 512
        elif nbins is not None:
            self.nbins = nbins

        h, b = np.histogram(data, self.nbins, absolute_range)
        h = h.astype(np.float)

        if absolute_range is None:
            ami = min(b)
            ama = max(b)
            absolute_range = (ami, ama)

        if self.current_range is None:
            if current_range is None:
                current_range = absolute_range
            else:
                current_range = self.current_range

        self.SetHistogram(h, absolute_range, current_range)

    def SetHistogram(self, histogram=None, image=None, absolute_range=None, current_range=None):

        if histogram is None and self.histogram is None:
            return

        if histogram is None:
            histogram = self.histogram

        if absolute_range is None:
            lar, rar = self.absolute_range
        else:
            lar, rar = absolute_range
            self.absolute_range = absolute_range

        if current_range is None:
            lcr, rcr = self.current_range
        else:
            lcr, rcr = current_range

        # reassessing the ranges...
        if (lcr <= lar and rcr <= lar) or (lcr >= rar and rcr >= rar):
            # both outside the absolute range?
            lcr, rcr = lar, rar
        else:
            # current too far left?
            if lcr < lar:
                lcr = lar
            elif lcr > rar:
                lcr = rar

            # current too far right?
            if rcr > rar:
                rcr = rar
            elif rcr < lar:
                rcr = lar

        self.current_range = [lcr, rcr]
        self.histogram = histogram
        self.histogram_max = max(histogram)
        if image is not None:
            sz = np.squeeze(image).shape
            image = np.repeat(image, 3)  # broadcast out to form an RGB image
            image2 = wx.EmptyImage(sz[1], sz[0])
            image2.SetData(image.tostring())
            self.histo_image = image2

        self.MakeBgBmp()
        self.MakeHistogramBmp()
        self.MakeLeftRightDC()
        self.UpdateDrawing()

    def getWidth(self):
        return self.maxWidth

    def getHeight(self):
        return self.maxHeight

    def GetLeft(self):
        return self.left

    def GetRight(self):
        return self.right

    def OnSize(self, evt):
        dc_size = self.GetClientSize()
        dc_w, dc_h = dc_size

        if dc_w > 0 and dc_h > 0:
            self.maxWidth = dc_w
            self.maxHeight = dc_h

            self.MakeLeftRightDC(dc_size)
            self.MakeHistogramBmp(dc_size)
            self.MakeLutImage(dc_size)
            self.MakeBgBmp(dc_size)

            # Initialize the buffer bitmap.  No real DC is needed at this point.
            # self.buffer = wx.EmptyBitmapRGBA(dc_w,dc_h,0,0,0,255)
            self.buffer = wx.EmptyBitmap(self.maxWidth, self.maxHeight)
            self.UpdateDrawing()

    def OnLeaveWindow(self, evt):
        if not self.drawing:
            self.active_bar = -2
            self.potential_bar = -2
            self.UpdateDrawing()

    def OnPaint(self, evt):
        # Create a buffered paint DC.  It will create the real
        # wx.PaintDC and then blit the bitmap to it when dc is
        # deleted.  Since we don't need to draw anything else
        # here that's all there is to it.
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_CLIENT_AREA)

    def DoDrawing(self, dc, printing=False):
        self.DrawCheckerBoard(dc)
        self.DrawLut(dc)
        self.DrawHistogram(dc)
        self.DrawBars(dc)
        dc.EndDrawing()

    def MakeBgBmp(self, size=None):
        if size is None:
            w, h = self.GetClientSize()
        else:
            w, h = size

        if w <= 0 or h <= 0:
            return

        self.bmp_bg = wx.BitmapFromBufferRGBA(w, h, make_checker(
            w, h, 16, (150, 150, 150), (220, 220, 220)))

    def MakeLeftRightDC(self, size=None):
        if size is None:
            w, h = self.GetClientSize()
        else:
            w, h = size

        absolute_width = self.absolute_range[1] - self.absolute_range[0]
        current_width = self.current_range[1] - self.current_range[0]

        factor = w / float(absolute_width)
        self.left_dc = (self.current_range[
                        0] - self.absolute_range[0]) * factor
        self.right_dc = (self.current_range[
                         1] - self.absolute_range[0]) * factor

        if self.left_dc < 0:
            self.left_dc = 0

        if self.right_dc > w - 1:
            self.right_dc = w - 1

    def MakeHistogramBmp(self, size=None):

        # need to expand the number of points to fill the client size...
        if self.histogram is None:
            return

        if size is None:
            w, h = self.GetClientSize()
        else:
            w, h = size

        if w <= 0:
            return
        if h <= 0:
            return

        # short circuit if we've been provided with a histogram image already
        if self.histo_image is not None:
            # resize image and make a bitmap
            buffer = self.histo_image.Scale(w, h).ConvertToBitmap()
        else:
            n_bins = self.histogram.shape[0]

            # scale the histogram (used for the tooltip)
            indexes = (np.arange(w, dtype=np.float) * float(
                n_bins) / float(w)).astype(np.int)
            self.histogram_scaled = np.take(self.histogram, indexes)

            rect_list = np.zeros((n_bins, 4))
            w_rect = int(float(w) / (n_bins))
            missing = w - w_rect * n_bins

            hist = self.histogram / self.histogram_max * h
            y = h
            x = 0
            for i in range(n_bins):
                w_temp = w_rect
                if missing > 0:
                    w_temp += 1
                    missing -= 1

                rect_list[i, :] = [x, h - hist[i], w_temp, h]
                x += w_temp

            # White image, black columns, will use black as the mask
            buffer = wx.EmptyBitmapRGBA(w, h, 255, 255, 255, 255)
            dc = wx.BufferedDC(None, buffer)
            dc.SetPen(wx.Pen("BLACK", 1))
            dc.SetBrush(wx.Brush("BLACK"))
            dc.DrawRectangleList(rect_list)
            dc.EndDrawing()

            # This avoids the following error:
            # wx._core.PyAssertionError: C++ assertion "!bitmap.GetSelectedInto()" failed
            # at ..\..\src\msw\bitmap.cpp(1509) in wxMask::Create():
            # bitmap can't be selected in another DC
            del dc

        mask = wx.Mask(buffer, wx.BLACK)
        buffer.SetMask(mask)

        self.bmp_histogram = buffer

    def MakeLutImage(self, size=None):
        if size is None:
            w, h = self.GetClientSize()
        else:
            w, h = size

        s = self.LutData.get_lut(self.lut_index)
        so = np.zeros(256, dtype=np.uint8)
        so.fill(255)

        image = wx.EmptyImage(256, 1)
        image.SetData(s)
        image.SetAlphaData(so.tostring())

        self.img_lut = image

    def DrawHistogram(self, dc):
        if self.bmp_histogram is None:
            return

        mdc = wx.MemoryDC()
        mdc.SelectObject(self.bmp_histogram)
        w, h = self.bmp_histogram.GetSize()
        dc.Blit(0, 0, w, h, mdc, 0, 0, wx.COPY, True)

    def DrawBars(self, dc):
        w, h = self.GetClientSize()

        if self.flag_clicked == 1:
            if self.active_bar == 1 or self.active_bar == 0:
                pen_left = wx.Pen("RED", 2)
            else:
                pen_left = wx.Pen("BLACK", 1)

            if self.active_bar == 1 or self.active_bar == 2:
                pen_right = wx.Pen("RED", 2, style=wx.SOLID)
            else:
                pen_right = wx.Pen("BLACK", 1)
        else:
            if self.potential_bar == 1 or self.potential_bar == 0:
                pen_left = wx.Pen("RED", 1)
            else:
                pen_left = wx.Pen("BLACK", 1)

            if self.potential_bar == 1 or self.potential_bar == 2:
                pen_right = wx.Pen("RED", 1)
            else:
                pen_right = wx.Pen("BLACK", 1)

        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(pen_left)
        dc.DrawLine(int(self.left_dc), 0, int(self.left_dc), h)
        dc.SetPen(pen_right)
        dc.DrawLine(int(self.right_dc), 0, int(self.right_dc), h)

    def DrawLut(self, dc):
        w, h = self.GetClientSize()

        if w <= 0:
            return
        if h <= 0:
            return

        absolute_width = self.absolute_range[1] - self.absolute_range[0]
        current_width = self.current_range[1] - self.current_range[0]
        factor = w / float(absolute_width)
        dc_width = math.ceil(current_width * factor)

        if dc_width <= 0:
            return

        img_scaled = self.img_lut.Scale(dc_width, h)
        dc.DrawBitmap(img_scaled.ConvertToBitmap(), self.left_dc, 0, 255)

    def DrawCheckerBoard(self, dc):
        """
        Draws a checkerboard on a wx.DC.
        Used for the Alpha channel control and the colour panels.
        """
        if self.bmp_bg is None:
            return

        dc.DrawBitmap(self.bmp_bg, 0, 0)

    def SetXY(self, evt):
        self.x, self.y = self.ConvertEventCoords(evt)

    def ConvertEventCoords(self, evt):
        newpos = self.CalcUnscrolledPosition(evt.GetX(), evt.GetY())
        return newpos

    def OnLeftDClickEvent(self, evt):
        lcr, rcr = self.GetRange()
        lar, rar = self.GetAbsoluteRange()

        if self.stored_range is None:
            lsr, rsr = self.GetAbsoluteRange()
        else:
            lsr, rsr = self.stored_range

        self.stored_range = [lcr, rcr]

        new_range = [lsr, rsr]
        if self.potential_bar == -1:
            # double click left expands the left
            if lcr != lar:
                new_range = [lar, rcr]
        elif self.potential_bar == 3:
            # double click right expands the right
            if rcr != rar:
                new_range = [lcr, rar]
        else:
            # clicked in the middle:
            if lcr != lar or rcr != rar:
                new_range = [lar, rar]

        self.SetCurrentRange(new_range)

        # do an event...
        range_event = RangeEvent(
            GetAbsoluteRange=self.GetAbsoluteRange,
            GetRange=self.GetRange,
        )
        wx.PostEvent(self, range_event)

    def OnRightUpEvent(self, evt):
        coords = [self.x, self.y]
        if self.drawing:
            return

        menu = wx.Menu()
        popup = wx.NewId()
        self._popup = popup
        for i in range(self.LutData.get_count()):
            self.Bind(wx.EVT_MENU, self.OnLutMenu, id=popup + i)
            s = self.LutData._names[i] + " (%d)" % i
            menu.Append(popup + i, s)

        self.PopupMenu(menu, coords)
        menu.Destroy()

        lut_event = LutEvent(
            GetLut=self.GetLut,
            GetLutName=self.GetLutName)
        wx.PostEvent(self, lut_event)

    def OnMouseEvent(self, evt):
        self.SetXY(evt)
        coords = [self.x, self.y]
        w, h = self.GetClientSize()

        old_active = self.active_bar
        n = self.hit_bars(coords)

        if n != self.potential_bar:
            self.potential_bar = n
            self.UpdateDrawing()

        if evt.Moving and not self.drawing:
            if n == 0 or n == 2:
                self.SetCursor(self._CursorSel)
            elif n == 1:
                self.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))
            else:
                self.SetCursor(wx.NullCursor)

        if evt.LeftDown():
            self.SetFocus()
            if n == 0 or n == 2 or n == 1:
                self.active_bar = n
                self.flag_clicked = 1
                self.CaptureMouse()
                self.drawing = True
                self.click_coords = coords
                self.UpdateDrawing()

        elif evt.Dragging() and self.drawing:
            if self.flag_clicked == 1:
                self.drag_bars(coords)
                self.UpdateDrawing()

                # do an event...
                range_event = RangeEvent(
                    GetAbsoluteRange=self.GetAbsoluteRange,
                    GetRange=self.GetRange,
                )
                wx.PostEvent(self, range_event)

        elif evt.LeftUp() and self.drawing:
            self.ReleaseMouse()
            self.drawing = False
            self.flag_clicked = 0
            self.UpdateDrawing()

        if self.histogram_scaled is not None:
            # do the tooltip
            if self.flag_clicked == 1 and self.active_bar == 1:
                s = "%.2f , %.2f" % (self.current_range[
                                     0], self.current_range[1])
                flag = 0
            else:
                factor = (self.absolute_range[1] - self.absolute_range[0])
                if self.x >= 0 and self.x < self.histogram_scaled.shape[0]:
                    hval = self.histogram_scaled[self.x]
                    s = "%.2f, %d" % ((factor * self.x / float(
                        w) + self.absolute_range[0]), hval)
                else:
                    s = ""

            self.tt.SetTip(s)

    def OnLutMenu(self, evt):
        self.SetLutIndex(evt.GetId() - self._popup, redraw=1)

    def GetAbsoluteRange(self):
        return self.absolute_range

    def GetRange(self):
        return self.current_range

    def UpdateDrawing(self):
        if self.buffer is None:
            return

        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        self.DoDrawing(dc)

    def SetCurrentRange(self, current_range, redraw=1):
        self.current_range = current_range
        self.MakeLeftRightDC()

        if redraw:
            self.UpdateDrawing()

    def SetAbsoluteRange(self, absolute_range):
        self.absolute_range = absolute_range

    def GetLut(self):
        return self.LutData.get_lut(self.lut_index)

    def GetLutName(self):
        return self.LutData.get_name(self.lut_index)

    def GetLutIndex(self):
        return self.lut_index

    def SetLutName(self, name):
        names = self.LutData.get_names()
        try:
            idx = names.index(name)
        except ValueError:
            idx = 0
        self.SetLutIndex(idx)

    def SetLutIndex(self, lut_index, redraw=1):
        self.lut_index = lut_index
        s = self.LutData.get_lut(lut_index)

        image = wx.EmptyImage(256, 1)
        image.SetData(s)

        self.img = image
        self.MakeLutImage()

        w, h = self.GetClientSize()

        if 1:
            # FIXME this causes problems!!
            if self.histo_image is None:
                self.buffer = wx.EmptyBitmapRGBA(w, h, 0, 0, 0, 1)
        else:
            img = wx.EmptyImage(1, 1)
            img.SetData("\xff\xff\xff")
            img_scaled = img.Scale(w, h)
            self.buffer = img_scaled.ConvertToBitmap()

        if redraw:
            self.UpdateDrawing()

    def SetSelCursor(self, cur=wx.CURSOR_SIZEWE):
        """ Sets link cursor properties. """
        self._CursorSel = wx.StockCursor(cur)

    def GetSelCursor(self):
        """ Gets the link cursor. """
        return self._CursorSel

    # return -1, 0, 1 for no bar, left or right
    def hit_bars(self, coords):
        # hit
        hx, hy = coords

        l_hit = hx - self.left_dc
        r_hit = hx - self.right_dc

        if abs(l_hit) < 3:
            n = 0
        elif abs(r_hit) < 3:
            n = 2
        elif l_hit < 0:
            n = -1
        elif r_hit > 0:
            n = 3
        else:
            n = 1

        # if n < 0:
        #    self.active_bar = None
        # else:
        #    self.active_bar = n

        return n

    def drag_bars(self, coords):
        w, h = self.GetClientSize()
        if w <= 0 or self.active_bar == -1 or self.active_bar == 3:
            return

        absolute_width = self.absolute_range[1] - self.absolute_range[0]
        factor = float(absolute_width) / w

        if self.active_bar == 0 or self.active_bar == 2:
            # use the center...
            cx = coords[0] - self.x_delta
            cy = coords[1] - self.y_delta

            # convert cx to ...
            rx = cx * factor + self.absolute_range[0]

            if self.active_bar == 0:
                if cx <= 0:
                    self.left_dc = 0
                    self.current_range[0] = self.absolute_range[0]
                elif self.current_range[1] - rx > self.min_span:
                    self.left_dc = cx
                    self.current_range[0] = rx
                else:
                    self.left_dc = self.right_dc - \
                        self.min_span * w / float(absolute_width)
                    self.current_range[
                        0] = self.current_range[1] - self.min_span

            elif self.active_bar == 2:
                if cx >= w:
                    self.right_dc = w - 1
                    self.current_range[1] = self.absolute_range[1]
                elif rx - self.current_range[0] > self.min_span:
                    self.right_dc = cx
                    self.current_range[1] = rx
                else:
                    self.right_dc = self.left_dc + \
                        self.min_span * w / float(absolute_width)
                    self.current_range[
                        1] = self.current_range[0] + self.min_span
        else:
            # how far from click?
            d = coords[0] - self.click_coords[0]
            range_dc = self.right_dc - self.left_dc
            range_current = self.current_range[1] - self.current_range[0]

            left_dc = self.left_dc + d
            right_dc = self.right_dc + d

            if left_dc <= 0:
                self.left_dc = 0
                self.right_dc = range_dc
                self.current_range[0] = self.absolute_range[0]
                self.current_range[1] = self.absolute_range[0] + range_current
            elif right_dc >= w:
                self.right_dc = w - 1
                self.left_dc = w - 1 - range_dc
                self.current_range[1] = self.absolute_range[1]
                self.current_range[0] = self.absolute_range[1] - range_current
            else:
                self.right_dc = right_dc
                self.left_dc = left_dc
                self.current_range[
                    1] = right_dc * factor + self.absolute_range[0]
                self.current_range[
                    0] = left_dc * factor + self.absolute_range[0]

            self.click_coords = coords

    def SetMinimumSpan(self, ms):
        self.min_span = ms


class OpacityCtrl(wx.ScrolledWindow):

    """\brief The canvas object, a scrolled window"""

    buffer = None
    n_nodes = None
    nodes_array = None
    nodes_screen = None
    active_node = None
    node_size = 9
    x_delta = 0
    y_delta = 0
    left_range = 0
    right_range = 255

    def __init__(self, parent, LutData, lut_index=0, nodes_array=None, size=(-1, 100)):
        wx.ScrolledWindow.__init__(
            self, parent, -1, size=size, style=wx.SUNKEN_BORDER)

        self.LutData = LutData
        if lut_index >= LutData.get_count():
            lut_index = 0

        self.SetLutIndex(lut_index, redraw=0)
        self.SetNodes(nodes_array)

        self.x = self.y = 0
        self.drawing = False
        self.tt = wx.ToolTip("")
        self.SetToolTip(self.tt)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseEvent)
        self.Bind(wx.EVT_LEFT_UP,   self.OnMouseEvent)
        self.Bind(wx.EVT_RIGHT_UP,   self.OnMouseEvent)
        self.Bind(wx.EVT_MOTION,    self.OnMouseEvent)
        self.Bind(wx.EVT_LEFT_DCLICK,    self.OnMouseEvent)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CHAR, self.OnKeyDown)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)

        self._drawing_mode = DrawingMode.not_set
        self.SetDrawingModeToComposite()

        self.MakeLutImage()

    def SetDrawingModeToComposite(self):
        if self._drawing_mode != DrawingMode.composite:
            self._drawing_mode = DrawingMode.composite
            self.nodes_array = np.array(
                [[0, 0], [0.333, 0.333], [0.666, 0.666], [1, 1]])
            self.SetNodes()
            self.UpdateDrawing()

    def SetDrawingModeToIsosurface(self):
        if self._drawing_mode != DrawingMode.isosurface:
            self._drawing_mode = DrawingMode.isosurface
            nodes_array = np.array([[0, 0], [0.5, 0], [0.5, 1], [1, 1]])
            self.SetNodes(nodes_array)
            self.UpdateDrawing()

    def SetNodes(self, nodes_array=None):
        w, h = self.GetClientSize()

        if nodes_array is None:
            nodes_array = self.nodes_array

        if nodes_array is None:
            n_nodes = 2
            nodes_array = np.zeros((n_nodes, 2), np.float)
            nodes_array[:, 0] = np.arange(n_nodes) / float(n_nodes - 1)
            nodes_array[:, 1] = 1
            self.nodes_array = nodes_array
            self.n_nodes = n_nodes
        else:
            self.nodes_array = np.array(nodes_array, np.float)
            self.n_nodes = self.nodes_array.shape[0]

        self.CalcScreenNodes()

    def CalcScreenNodes(self):
        w, h = self.GetClientSize()
        nodes_array = self.nodes_array
        n_nodes = self.n_nodes

        nodes_screen = np.zeros((n_nodes, 2))
        nodes_screen[:, 0] = nodes_array[:, 0] * float(w)
        nodes_screen[:, 1] = h - nodes_array[:, 1] * float(h)
        self.nodes_screen = nodes_screen

    def getWidth(self):
        return self.maxWidth

    def getHeight(self):
        return self.maxHeight

    def OnPopupRemove(self, evt):
        self.RemoveNode(self.active_node)
        self.CalcScreenNodes()
        self.MakeLutImage()
        self.UpdateDrawing()

    def OnPopupAdd(self, evt):
        l, r = self.GetLeftRight(self.x)
        self.AddNode(l, r, (self.x, self.y))
        self.CalcScreenNodes()
        self.MakeLutImage()
        self.UpdateDrawing()

    def OnKeyDown(self, evt):
        k = evt.GetKeyCode()
        av = self.active_node
        coords = [self.x, self.y]

        if k == 45:
            if av != 0 and av != self.n_nodes - 1 and av is not None:
                self.RemoveNode(av)
                self.CalcScreenNodes()
                self.MakeLutImage()
                self.UpdateDrawing()

        elif k == 61 or k == 43:
            if self.hit_node(coords) == -1:
                l, r = self.GetLeftRight(self.x)
                self.AddNode(l, r, (self.x, self.y))
                self.CalcScreenNodes()
                self.MakeLutImage()
                self.hit_node(coords)
                self.UpdateDrawing()

        evt.Skip()

    def GetActiveOpacity(self):
        return self.nodes_array[self.active_node, 1]

    def GetActivePosition(self):
        return (self.right_range - self.left_range) * self.nodes_array[self.active_node, 0] + self.left_range

    def GetActiveIndex(self):
        return self.active_node

    def OnLeaveWindow(self, evt):
        if not self.drawing:
            # if drawing and dragging then fine, there's no problem with
            # identifying the node
            self.active_node = None
            self.UpdateDrawing()

    def SetOpacity(self, arr):
        self.nodes_array = arr
        self.n_nodes = arr.shape[0]
        self.active_node = None
        self.CalcScreenNodes()
        self.UpdateDrawing()

    def GetOpacity(self, r=None):
        na = self.nodes_array.copy()

        if r is None:
            lr = self.left_range
            rr = self.right_range
        else:
            lr, rr = r

        t = na[:, 0]
        t = (t * (rr - lr)) + float(lr)

        na[:, 0] = t

        return na

    def GetLeftRight(self, x):
        w, h = self.GetClientSize()
        x = x / float(w)
        for i in range(0, self.n_nodes - 1):
            if x >= self.nodes_array[i, 0] and x <= self.nodes_array[i + 1, 0]:
                break

        l = i
        r = i + 1

        return l, r

    def RemoveNode(self, i):
        # On rare occasion, the node can be unselected while the menu is up.
        # This prevents the function from doing anything stupid.
        if i is None:
            return

        if self._drawing_mode == DrawingMode.isosurface:
            return

        self.nodes_array = np.vstack([self.nodes_array[
            :i, :], self.nodes_array[i + 1:, :]])
        self.n_nodes = self.nodes_array.shape[0]
        self.active_node = None

        self.DoEvent()

    def AddNode(self, l, r, pt=None):

        if self._drawing_mode == DrawingMode.isosurface:
            return

        self.n_nodes += 1
        if pt is None:
            xnew = (self.nodes_array[l, 0] + self.nodes_array[r, 0]) / 2.
            ynew = (self.nodes_array[l, 1] + self.nodes_array[r, 1]) / 2.
        else:
            w, h = self.GetClientSize()
            x, y = pt
            xnew = float(x) / w
            ynew = 1. - float(y) / h

        self.nodes_array = np.vstack([self.nodes_array[
            :l + 1, :], [xnew, ynew], self.nodes_array[r:, :]])
        self.active_node = l + 1

        self.DoEvent()

    def OnSize(self, evt):
        dc_size = self.GetClientSize()
        dc_w, dc_h = dc_size

        if dc_w > 0 and dc_h > 0:
            self.maxWidth = dc_w
            self.maxHeight = dc_h

            self.SetNodes()

            self.MakeLutImage()
            self.MakeBgBmp()

            # Initialize the buffer bitmap.  No real DC is needed at this
            # point.
            self.buffer = wx.EmptyBitmap(self.maxWidth, self.maxHeight)
            dc = wx.BufferedDC(None, self.buffer)
            self.UpdateDrawing()

    def OnPaint(self, evt):
        # Create a buffered paint DC.  It will create the real
        # wx.PaintDC and then blit the bitmap to it when dc is
        # deleted.  Since we don't need to draw anything else
        # here that's all there is to it.
        # sys.exit()
        dc = wx.BufferedPaintDC(self, self.buffer, wx.BUFFER_CLIENT_AREA)

    def DoDrawing(self, dc, printing=False):
        self.DrawCheckerBoard(dc)
        self.DrawLut(dc)
        self.DrawNodes(dc)
        dc.EndDrawing()

    def MakeBgBmp(self):
        w, h = self.GetClientSize()

        if w <= 0 or h <= 0:
            return

        self.bmp_bg = wx.BitmapFromBufferRGBA(w, h, make_checker(
            w, h, 16, (150, 150, 150), (220, 220, 220)))

    def MakeLutImage(self):
        if self.nodes_array is None:
            return

        w, h = self.GetClientSize()

        s = self.LutData.get_lut(self.lut_index)
        image = wx.EmptyImage(256, 1)

        image.SetData(s)

        # Original LUT data is 256x1
        ax256 = np.arange(256) / 255.
        oi = np.interp(ax256, self.nodes_array[
            :, 0], self.nodes_array[:, 1] * 255.)
        ois = oi.astype(np.uint8).tostring()
        image.SetAlphaData(ois)

        img_scaled = image.Scale(w, h)
        self.img_lut = img_scaled

    def DrawLut(self, dc):
        bmp = self.img_lut.ConvertToBitmap()
        dc.DrawBitmap(bmp, 0, 0)

    def DrawCheckerBoard(self, dc):
        """
        Draws a checkerboard on a wx.DC.
        Used for the Alpha channel control and the colour panels.
        """
        if self.bmp_bg is None:
            return

        dc.DrawBitmap(self.bmp_bg, 0, 0)

    def DrawNodes(self, dc):
        s = self.node_size

        nodes_screen = np.zeros((self.n_nodes, 4))
        nodes_screen[:, 0] = self.nodes_screen[:, 0] - s / 2.
        nodes_screen[:, 1] = self.nodes_screen[:, 1] - s / 2.
        nodes_screen[:, 2] = s
        nodes_screen[:, 3] = s
        brushes = [wx.TRANSPARENT_BRUSH] * self.n_nodes

        if self.active_node is not None:
            if self.drawing:
                brushes[self.active_node] = wx.Brush(
                    wx.NamedColour('RED'), style=wx.SOLID)
            else:
                brushes[self.active_node] = wx.Brush(
                    wx.NamedColour('WHITE'), style=wx.SOLID)

        dc.DrawRectangleList(nodes_screen, pens=wx.Pen(
            wx.NamedColour('BLACK'), 1, style=wx.SOLID), brushes=brushes)

        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.Pen("RED", 1))
        dc.DrawLines(self.nodes_screen)

    def SetXY(self, evt):
        self.x, self.y = self.ConvertEventCoords(evt)

    def ConvertEventCoords(self, evt):
        newpos = self.CalcUnscrolledPosition(evt.GetX(), evt.GetY())
        return newpos

    def OnMouseEvent(self, evt):
        self.SetXY(evt)
        coords = [self.x, self.y]
        w, h = self.GetClientSize()

        if evt.Moving and not self.drawing:
            old_active = self.active_node
            self.hit_node(coords)

            if self.active_node != old_active:
                self.UpdateDrawing()

        if evt.RightUp():
            if self.active_node == 0 or self.active_node == self.n_nodes - 1:
                return

            # with this, node stays active when pointer moves to the menu...
            self.drawing = 1

            menu = wx.Menu()
            popup = wx.NewId()
            if self.active_node is not None:
                self.Bind(wx.EVT_MENU, self.OnPopupRemove, id=popup)
                menu.Append(popup, "Remove node")
            else:
                self.Bind(wx.EVT_MENU, self.OnPopupAdd, id=popup)
                menu.Append(popup, "Add node")

            if self._drawing_mode == DrawingMode.isosurface:
                menu.Enable(popup, False)

            self.PopupMenu(menu, coords)
            menu.Destroy()
            self.drawing = 0

        if evt.LeftDown():
            self.SetFocus()
            if self.hit_node(coords) > -1:
                self.flag_clicked = 1

                self.CaptureMouse()
                self.drawing = True
                self.UpdateDrawing()

        elif evt.Dragging() and self.drawing:
            if self.flag_clicked == 1:
                # calculate left limit
                if self.active_node == 0:
                    coords[0] = self.x_delta
                elif self.active_node == self.n_nodes - 1:
                    # calculate right limit
                    coords[0] = w + self.x_delta
                else:
                    if coords[0] - self.x_delta < self.nodes_screen[self.active_node - 1, 0] + 1:
                        coords[0] = self.nodes_screen[
                            self.active_node - 1, 0] + self.x_delta + 1
                    elif coords[0] - self.x_delta > self.nodes_screen[self.active_node + 1, 0] - 1:
                        coords[0] = self.nodes_screen[
                            self.active_node + 1, 0] + self.x_delta - 1
                    elif coords[0] - self.x_delta < 0:
                        coords[0] = self.x_delta
                    elif coords[0] - self.x_delta > w:
                        coords[0] = w + self.x_delta

                # do up and down...
                if coords[1] - self.y_delta < 0:
                    coords[1] = self.y_delta
                elif coords[1] - self.y_delta > h:
                    coords[1] = h + self.y_delta

                # adjust for isosurface behaviour
                change_drawing = True

                if self._drawing_mode == DrawingMode.isosurface:
                    # end-nodes are fixed in place
                    if self.active_node == 0 or self.active_node == self.n_nodes - 1:
                        change_drawing = False
                    elif self.active_node == 1:
                        coords[1] = self.y_delta + h
                    elif self.active_node == 2:
                        coords[1] = self.y_delta

                if change_drawing:
                    self.drag_node(coords)
                    if self._drawing_mode == DrawingMode.isosurface:
                        # adjust other node
                        if self.active_node == 1:
                            self.nodes_array[
                                2, 0] = self.nodes_array[1, 0] + 0.01
                            self.nodes_array[2, 1] = 1.0
                            self.nodes_screen[2, 0] = self.nodes_array[
                                2, 0] * float(w)
                            self.nodes_screen[2, 1] = 0
                        elif self.active_node == 2:
                            self.nodes_array[
                                1, 0] = self.nodes_array[2, 0] - 0.01
                            self.nodes_array[1, 1] = 0.0
                            self.nodes_screen[1, 0] = self.nodes_array[
                                1, 0] * float(w)
                            self.nodes_screen[1, 1] = h
                    self.UpdateDrawing()

                self.DoEvent()

        elif evt.LeftUp() and self.drawing:
            self.ReleaseMouse()
            self.drawing = False
            self.hit_node(coords)
            self.UpdateDrawing()
            self.flag_clicked = 0

        elif evt.LeftDClick():
            hn = self.hit_node(coords)
            if hn == 0 or hn == self.n_nodes - 1:
                return

            if hn > -1:
                self.RemoveNode(self.active_node)
            else:
                l, r = self.GetLeftRight(self.x)
                self.AddNode(l, r, (self.x, self.y))
                self.flag_clicked = 1
                self.drawing = True
                self.CaptureMouse()
            self.CalcScreenNodes()
            self.MakeLutImage()
            self.UpdateDrawing()

        if self.active_node is not None:
            s = "%.2f , %d%%" % (self.nodes_array[
                                 self.active_node, 0], self.nodes_array[self.active_node, 1] * 100)
        else:
            opa_percent = 100 - (self.y * 100. / h)
            if opa_percent < 0:
                opa_percent = 0
            elif opa_percent > 100:
                opa_percent = 100

            s = "%.2f , %d%%" % ((self.right_range - self.left_range) * self.x / float(
                w) + self.left_range, opa_percent)

        self.tt.SetTip(s)

    def UpdateDrawing(self):
        if self.buffer is None:
            return

        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        self.DoDrawing(dc)

    def SetRange(self, mi, ma, redraw=1):
        self.left_range = mi
        self.right_range = ma

        if redraw:
            self.UpdateDrawing()

    def SetLutIndex(self, lut_index, redraw=1):
        self.lut_index = lut_index

        s = self.LutData.get_lut(lut_index)

        image = wx.EmptyImage(256, 1)
        image.SetData(s)

        self.img = image
        self.MakeLutImage()

        if redraw:
            self.UpdateDrawing()

    def drag_node(self, coords, active_node=None):

        if active_node is None:
            active_node = self.active_node

        w, h = self.GetClientSize()

        # use the center...
        cx = coords[0] - self.x_delta
        cy = coords[1] - self.y_delta

        # put the node back in the screen array...
        self.nodes_screen[active_node, 0] = cx
        self.nodes_screen[active_node, 1] = cy

        # now do nodes_arr...
        self.nodes_array[active_node, 0] = cx / float(w)
        self.nodes_array[active_node, 1] = (h - cy) / float(h)

        self.MakeLutImage()

    def hit_node(self, coords):
        # first get the hull points...
        s = self.node_size
        n_nodes = self.n_nodes

        # hit
        hx, hy = coords

        n = -1
        for i in range(n_nodes):
            cx = self.nodes_screen[i, 0]
            cy = self.nodes_screen[i, 1]
            rect = wx.Rect(cx - s / 2, cy - s / 2, s, s)

            if rect.InsideXY(hx, hy):
                self.active_node = i
                self.x_delta, self.y_delta = hx - cx, hy - cy
                n = i
                break

        if n == -1:
            self.active_node = None

        return n

    def DoEvent(self):
        ev = UpdateEvent(
            GetOpacity=self.GetOpacity,
            GetActiveIndex=self.GetActiveIndex,
            GetActivePosition=self.GetActivePosition,
            GetActiveOpacity=self.GetActiveOpacity
        )
        wx.PostEvent(self, ev)
