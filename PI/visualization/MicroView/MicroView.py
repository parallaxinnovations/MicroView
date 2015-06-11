# =========================================================================
#
# Copyright (c) 2000-2008 GE Healthcare
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

#
# This file represents a derivative work by Parallax Innovations Inc.
#

"""
MicroView is the main class.  MicroView allows the visualization and quantification of image data.
"""

#import cProfile
#global profile

#profile = cProfile.Profile()
# profile.enable()


# Initialize logging
import logging
import sys
import traceback


class RavenLoggingHandler(logging.Handler):

    """Python log handler for raven.error errors"""

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):

        # avoid recursion by disabling raven
        logger = logging.getLogger()
        for i in range(len(logger.handlers)):
            if isinstance(logger.handlers[i], SentryHandler):
                logger.handlers.remove(logger.handlers[i])
                break


try:
    from raven.handlers.logging import SentryHandler
    USE_SENTRY = True
except:
    USE_SENTRY = False

# capture uncaught exceptions


def microview_global_exception_handler(ex_cls, ex, tb):
    print(''.join(traceback.format_tb(tb)))
    print('{0}: {1}'.format(ex_cls, ex))
    logging.critical(''.join(traceback.format_tb(tb)))
    logging.critical('{0}: {1}'.format(ex_cls, ex))

# if app is frozen, add sentry logger
if 0:  # hasattr(sys, 'frozen') and USE_SENTRY:
    # All errors and exceptions should be logged to sentry
    handler = SentryHandler('http://fa69fda2ef694765979deb65fbcf88f6:735d4d95ed3a429b8eb6545a4017ff0b@' +
                            'sentry.parallax-innovations.com/sentry/3', level=logging.ERROR)
    logger = logging.getLogger()
    logger.addHandler(handler)
    sys.excepthook = microview_global_exception_handler

    # prevent recursive issue with raven if it can't reach server
    logger = logging.getLogger('sentry.errors')
    handler = RavenLoggingHandler()
    logger.addHandler(handler)

# Initialize wx and twisted
import wx
import wx.lib.masked

# Workaround to remove the reactor module created by PyInstaller twisted rthook.
# Otherwise you will get error
# twisted.internet.error.ReactorAlreadyInstalledError: reactor already
# installed
if 'twisted.internet.reactor' in sys.modules:
    del sys.modules['twisted.internet.reactor']

from twisted.internet import wxreactor
wxreactor.install()
from twisted.internet import reactor

# This next line is needed for pyinstaller to work on Mac
import distutils.util

# continue with loading of minimal modules
import os
import ConfigParser

# This next line pulls in package version and SHA1
from PI.visualization.MicroView import PACKAGE_VERSION, PACKAGE_SHA1

from PI.visualization.common import MicroViewSettings

import MicroViewSplashScreen


class MicroViewApp(wx.App):

    """The main wx.App() class"""

    def __init__(self, *args, **kw):

        # the installation directory
        self.installdir = os.path.abspath(sys.path[0])
        wx.App.__init__(self, *args, **kw)
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)

    def OnActivate(self, evt):
        if bool(evt.GetActive()):
            self.BringWindowToFront()
        evt.Skip()

    def BringWindowToFront(self):
        """Helper method for OS X integration"""
        try:
            self.GetTopWindow().Raise()
        except:
            pass

    def MacReopenApp(self):
        """Helper method for OS X integration"""
        self.BringWindowToFront()

    def MacNewFile(self):
        """Helper method for OS X integration"""
        pass

    def MacOpenFiles(self, filenames):
        """Helper method for OS X integration"""
        self.BringWindowToFront()
        for filename in filenames[1:]:
            self.frame.OnFileOpen(filename)

    def OnInit(self):
        # software name
        sw_name = "Standard"
        sw_full_name = 'MicroView ' + sw_name + ' ' + PACKAGE_VERSION

        #---------------------------------------------------
        # display splashscreen if we're configured to do so
        #---------------------------------------------------
        self.splash = None

        config = MicroViewSettings.MicroViewSettings.getObject()

        try:
            show_splash = config.bShowSplashScreen
        except:
            show_splash = config.bShowSplashScreen = True

        bitmap = None
        splash_name = 'unknown'

        if show_splash:
            basename = 'MicroView-splash.gif'

            try:
                splash_name = os.path.join(self.installdir, 'Icons', basename)
                f = open(splash_name, 'rb')
                bitmap = wx.ImageFromStream(f).ConvertToBitmap()
            except:
                logging.error(
                    "Unable to read splash image '%s'" % splash_name)
                show_splash = False

        if show_splash:
            #---------------------------------------------------
            # now display the splashscreen
            #---------------------------------------------------
            self.splash = MicroViewSplashScreen.MicroViewSplashScreen(
                sw_version=sw_full_name, parent=None, bitmap=bitmap, timeout=3000)
            wx.SafeYield()

        # ----------------------------------------------
        # Go on with the creation of the rest of the app
        # ----------------------------------------------
        # don't load this until we've got the splash screen up
        import MicroViewMain

        self.frame = MicroViewMain.MicroViewMainFrame(
            self.splash, sw_name=sw_name)
        self.frame.SetName("MicroViewMainFrame1")

        # ------------------------------------------------------------------------------------
        # Set up an icon for the application
        # ---------------------------------------------------------------------
        bn = 'parallax-innovations.ico'
        filename = os.path.join(self.installdir, 'Icons', bn)

        if os.path.exists(filename):
            icon = wx.Icon(filename, wx.BITMAP_TYPE_ICO)
            self.frame.SetIcon(icon)
        else:
            logging.error("Unable to find application icon '%s'" % filename)

        self.SetTopWindow(self.frame)
        self.frame.Show(True)

        # Load first image passed on commandline
        create_tab = False
        for f in sys.argv[1:]:
            if not f.startswith('-psn'):
                self.frame.OnFileOpen(f, create_tab=create_tab)
                create_tab = True

        return True


def main():
    """main entry point into MicroView"""

    # Run the main application
    app = MicroViewApp(False)
    reactor.registerWxApp(app)
    reactor.run()

# This bit makes it easier to distribute MicroView as a python egg
if __name__ == '__main__':
    main()
    # profile.disable()
    # profile.dump_stats('profile-startup')
