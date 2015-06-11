from zope import interface
from PI.visualization.MicroView.interfaces import IPageState
import cStringIO


class PageState(object):

    interface.implements(IPageState)

    def __init__(self):

        self.__filename = None
        self._title = None
        self._type = None
        self._closing = False

    def __str__(self):
        s = cStringIO.StringIO()
        s.write('{0}:\n'.format(self.__class__))
        s.write('\tFilename: {0}\n'.format(self.__filename))
        s.write('\tTitle: {0}\n'.format(self._title))
        s.write('\tType: {0}\n'.format(self._type))
        return s.getvalue()

    def GetPageType(self):
        return self._type

    def SetFileName(self, filename):
        self.__filename = filename

    def GetFileName(self):
        return self.__filename

    def GetTitle(self):
        return self._title

    def SetTitle(self, title):
        self._title = title

    # These next two methods allow us to track whether a page is in the process of being closed
    # We need this here as a kludge to allow is_page_saveable() to properly determine whether the
    # page is saveable or not
    def setClosing(self, b):
        self._closing = b

    def getClosing(self):
        return self._closing
