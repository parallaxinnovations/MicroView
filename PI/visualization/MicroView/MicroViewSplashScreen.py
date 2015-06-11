import wx
import logging
import sys
from zope import interface, component
from PI.visualization.MicroView.interfaces import IMicroViewSplashScreen


AS_TIMEOUT = 1
AS_NOTIMEOUT = 2
AS_CENTER_ON_SCREEN = 4
AS_CENTER_ON_PARENT = 8
AS_NO_CENTER = 16
AS_SHADOW_BITMAP = 32


class SplashTextHandler(logging.Handler):

    def __init__(self, splash):
        logging.Handler.__init__(self)
        self.splash = splash

    def emit(self, record):
        self.splash.SetText(record.getMessage())


class SplashProgressHandler(logging.Handler):

    def __init__(self, splash):
        logging.Handler.__init__(self)
        self.splash = splash

    def emit(self, record):
        self.splash.SetProgress(record.msg)


class MicroViewSplashScreen(wx.Frame):

    interface.implements(IMicroViewSplashScreen)

    def __del__(self):

        # unregister our zope handlers
        gsm = component.getGlobalSiteManager()
        gsm.unregisterUtility(self, IMicroViewSplashScreen)

    def __init__(
        self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize,
        style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP,
        bitmap=None, timeout=5000, sw_version='',
        agwStyle=AS_CENTER_ON_SCREEN,
            shadowcolour=wx.NullColour):

        # add custom logging handlers
        self.add_custom_loggers()

        # register ourselves with the zope object registry
        component.getGlobalSiteManager().registerUtility(
            self, IMicroViewSplashScreen)

        self.sw_version = sw_version

        wx.Frame.__init__(self, parent, id, "", pos, size, style)

        if not bitmap or not bitmap.IsOk():
            raise Exception(
                "\nERROR: Bitmap Passed To AdvancedSplash Is Invalid.")

        self.bmp = bitmap

        self._agwStyle = agwStyle

        # Setting Initial Properties
        self.SetText()
        self.SetTextFont()
        self.SetTextPosition()
        self.SetTextColour()
        self.SetProgress()

        # Calculate The Shape Of AdvancedSplash Using The Input-Modified Bitmap
        self.reg = wx.RegionFromBitmap(self.bmp)

        # Don't Know If It Works On Other Platforms!!
        # Tested Only In Windows XP/2000

        # if wx.Platform == "__WXGTK__":
        #    self.Bind(wx.EVT_WINDOW_CREATE, self.SetSplashShape)
        # else:
        #    self.SetSplashShape()

        w = self.bmp.GetWidth()
        h = self.bmp.GetHeight()

        # Set The AdvancedSplash Size To The Bitmap Size
        self.SetClientSize((w, h))

        if agwStyle & AS_CENTER_ON_SCREEN:
            self.CenterOnScreen()
        elif agwStyle & AS_CENTER_ON_PARENT:
            self.CenterOnParent()

        if agwStyle & AS_TIMEOUT:
            # Starts The Timer. Once Expired, AdvancedSplash Is Destroyed
            self._splashtimer = wx.PyTimer(self.OnNotify)
            self._splashtimer.Start(timeout)

        # Catch Some Mouse Events, To Behave Like wx.SplashScreen
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)
        self.Bind(wx.EVT_CHAR, self.OnCharEvents)

        # Text should be white and in the default font
        self.SetTextColour(wx.WHITE)

        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.SetTextFont(font)

        # Calculate space taken by sw name + 25 additional spaces
        w, h = bitmap.GetWidth(), bitmap.GetHeight()
        memDC = wx.MemoryDC()
        memDC.SetFont(font)
        text_width, text_height = memDC.GetTextExtent(
            self.sw_version + 'X' * 25)
        x = w - text_width - 50
        y = 120
        self.SetTextPosition((x, y))

        self._progress_line_width, _ = memDC.GetTextExtent(
            self.sw_version + ': Loading Plugins...')
        # put progress bar 3 pixels below text
        self._progress_bar_height = y + text_height + 3

        # Display default text
        self.SetText('Loading...')

        self.Show()

    def add_custom_loggers(self):
        # set up custom loggers
        logr = logging.getLogger('splash')
        logr.setLevel(logging.DEBUG)
        self._splash_log_text_hdlr = SplashTextHandler(self)
        logr.addHandler(self._splash_log_text_hdlr)

        logr = logging.getLogger('splash-progress')
        logr.propagate = 0  # don't send messages to other logger handlers
        logr.setLevel(logging.DEBUG)
        self._splash_log_progress_hdlr = SplashProgressHandler(self)
        logr.addHandler(self._splash_log_progress_hdlr)

    def remove_custom_loggers(self):

        # set up custom loggers
        logr = logging.getLogger('splash')
        logr.removeHandler(self._splash_log_text_hdlr)
        logr = logging.getLogger('splash-progress')
        logr.removeHandler(self._splash_log_progress_hdlr)

    def SetSplashShape(self, event=None):
        """
        Sets L{AdvancedSplash} shape using the region created from the bitmap.

        :param `event`: a `wx.WindowCreateEvent` event (GTK only, as GTK supports setting
         the window shape only during window creation).
        """

        self.SetShape(self.reg)

        if event is not None:
            event.Skip()

    def OnPaint(self, event):
        """
        Handles the ``wx.EVT_PAINT`` event for L{AdvancedSplash}.

        :param `event`: a `wx.PaintEvent` to be processed.
        """

        dc = wx.PaintDC(self)

        # Here We Redraw The Bitmap Over The Frame
        dc.DrawBitmap(self.bmp, 0, 0, True)

        # We draw the text anyway, whether it is empty ("") or not
        textcolour = self.GetTextColour()
        textfont = self.GetTextFont()
        textpos = self.GetTextPosition()
        text = '%s: %s' % (self.sw_version, self.GetText())

        dc.SetFont(textfont[0])
        dc.SetTextForeground(textcolour)
        dc.DrawText(text, textpos[0], textpos[1])

        # draw progress bar here
        if self._progress > 0.0:
            dc.SetPen(wx.Pen(wx.WHITE, 1))
            linepos = (textpos[0], self._progress_bar_height)
            dc.DrawLine(linepos[0], linepos[1],
                        linepos[0] + (self._progress / 100.0) * self._progress_line_width, linepos[1])

        # Seems like this only helps on OS X.
        if wx.Platform == "__WXMAC__":
            wx.SafeYield(self, True)

    def OnNotify(self):
        """ Handles the timer expiration, and calls the `Close()` method. """

        self.Close()

    def OnMouseEvents(self, event):
        """
        Handles the ``wx.EVT_MOUSE_EVENTS`` events for L{AdvancedSplash}.

        :param `event`: a `wx.MouseEvent` to be processed.

        :note: This reproduces the behavior of `wx.SplashScreen`.
        """

        if event.LeftDown() or event.RightDown():
            self.Close()

        event.Skip()

    def OnCharEvents(self, event):
        """
        Handles the ``wx.EVT_CHAR`` event for L{AdvancedSplash}.

        :param `event`: a `wx.KeyEvent` to be processed.

        :note: This reproduces the behavior of `wx.SplashScreen`.
        """

        self.Close()

    def OnCloseWindow(self, event):
        """
        Handles the ``wx.EVT_CLOSE`` event for L{AdvancedSplash}.

        :param `event`: a `wx.CloseEvent` to be processed.

        :note: This reproduces the behavior of `wx.SplashScreen`.
        """

        if hasattr(self, "_splashtimer"):
            self._splashtimer.Stop()
            del self._splashtimer

        self.Destroy()

    def SetProgress(self, progress_text=None):
        """Sets progress percentage"""
        if progress_text is None:
            progress_text = '0.0'
        progress = float(progress_text)

        self._progress = progress

        self.Refresh()
        self.Update()

    def SetText(self, text=None):
        """
        Sets the text to be displayed on L{AdvancedSplash}.

        :param `text`: the text we want to display on top of the bitmap. If `text` is
         set to ``None``, nothing will be drawn on top of the bitmap.
        :type text: string or ``None``
        """

        if text is None:
            text = ""

        self._text = text

        self.Refresh()
        self.Update()

    def GetText(self):
        """
        Returns the text displayed on L{AdvancedSplash}.

        :return: A string representing the text drawn on top of the L{AdvancedSplash} bitmap.
        """

        return self._text

    def SetTextFont(self, font=None):
        """
        Sets the font for the text in L{AdvancedSplash}.

        :param `font`: the font to use while drawing the text on top of our bitmap. If `font`
         is ``None``, a simple generic font is generated.
        :type font: `wx.Font` or ``None``
        """

        if font is None:
            self._textfont = wx.Font(1, wx.SWISS, wx.NORMAL, wx.BOLD, False)
            self._textsize = 10.0
            self._textfont.SetPointSize(self._textsize)
        else:
            self._textfont = font
            self._textsize = font.GetPointSize()
            self._textfont.SetPointSize(self._textsize)

        self.Refresh()
        self.Update()

    def GetTextFont(self):
        """
        Gets the font for the text in L{AdvancedSplash}.

        :return: An instance of `wx.Font` to draw the text and a `wx.Size` object containing
         the text width an height, in pixels.
        """

        return self._textfont, self._textsize

    def SetTextColour(self, colour=None):
        """
        Sets the colour for the text in L{AdvancedSplash}.

        :param `colour`: the text colour to use while drawing the text on top of our
         bitmap. If `colour` is ``None``, then ``wx.BLACK`` is used.
        :type colour: `wx.Colour` or ``None``
        """

        if colour is None:
            colour = wx.BLACK

        self._textcolour = colour
        self.Refresh()
        self.Update()

    def GetTextColour(self):
        """
        Gets the colour for the text in L{AdvancedSplash}.

        :return: An instance of `wx.Colour`.
        """

        return self._textcolour

    def SetTextPosition(self, position=None):
        """
        Sets the text position inside L{AdvancedSplash} frame.

        :param `position`: the text position inside our bitmap. If `position` is ``None``,
         the text will be placed at the top-left corner.
        :type position: tuple or ``None``
        """

        if position is None:
            position = (0, 0)

        self._textpos = position
        self.Refresh()
        self.Update()

    def GetTextPosition(self):
        """
        Returns the text position inside L{AdvancedSplash} frame.

        :return: A tuple containing the text `x` and `y` position inside the L{AdvancedSplash} frame.
        """

        return self._textpos

    def GetSplashStyle(self):
        """
        Returns a list of strings and a list of integers containing the styles.

        :return: Two Python lists containing the style name and style values for L{AdvancedSplash}.
        """

        stringstyle = []
        integerstyle = []

        if self._agwStyle & AS_TIMEOUT:
            stringstyle.append("AS_TIMEOUT")
            integerstyle.append(AS_TIMEOUT)

        if self._agwStyle & AS_NOTIMEOUT:
            stringstyle.append("AS_NOTIMEOUT")
            integerstyle.append(AS_NOTIMEOUT)

        if self._agwStyle & AS_CENTER_ON_SCREEN:
            stringstyle.append("AS_CENTER_ON_SCREEN")
            integerstyle.append(AS_CENTER_ON_SCREEN)

        if self._agwStyle & AS_CENTER_ON_PARENT:
            stringstyle.append("AS_CENTER_ON_PARENT")
            integerstyle.append(AS_CENTER_ON_PARENT)

        if self._agwStyle & AS_NO_CENTER:
            stringstyle.append("AS_NO_CENTER")
            integerstyle.append(AS_NO_CENTER)

        if self._agwStyle & AS_SHADOW_BITMAP:
            stringstyle.append("AS_SHADOW_BITMAP")
            integerstyle.append(AS_SHADOW_BITMAP)

        return stringstyle, integerstyle

##########################################################################


def getObject():
    return component.getUtility(IMicroViewSplashScreen)
