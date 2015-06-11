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
ViewportManager managers viewports of a PaneFrame, set RenderPanes
to viewports.
"""

import logging

from zope import component, event, interface

from vtkAtamai.wxPaneFrame import wxPaneFrame

from PI.visualization.MicroView.interfaces import IViewportManager, IImage
from PI.visualization.MicroView.events import ViewportModifiedEvent, ViewportModified2Event, SynchronizeEvent,\
    ViewportMouseDown
from PI.visualization.vtkMultiIO import MVImage
import ViewerState
import cStringIO


class ViewportManager(wxPaneFrame):

    interface.implements(IViewportManager)

    def GetPageState(self):
        return self._viewerState

    def __str__(self):
        s = cStringIO.StringIO()
        s.write('{0}:\n'.format(self.__class__))
        s.write('\tImage Index: {0}\n'.format(self.GetImageIndex()))
        for line in str(self.GetPageState()).split('\n'):
            s.write('\t{0}\n'.format(line))
        return s.getvalue()

    def __init__(self, parent, **kw):

        self._viewerState = ViewerState.ViewerState()
        self._defaultRenderPanes = None

        self._index = 0
        if 'index' in kw:
            self._index = kw['index']
            del(kw['index'])
        wxPaneFrame.__init__(self, parent, **kw)

        self._menuHeight = 0  # 17

        self._currentView = None
        self._lastView = '1Side3'
        self.SetViewName('All')
        self._lastviewname = 'All'

        self._currentPanes = None
        self._lastPanes = None
        self._mode = 'normal'
        self._appPanes = None   # application specified panes

        # For viewport synchronization
        self._synced_image_indices = []
        self.ignore_events = False

        self.BindEvent("<Double-ButtonPress-1>", self.EnlargePane)

        # listen to certain zope events
        component.provideHandler(self.onViewportModifiedEvent)
        component.provideHandler(self.onViewportModified2Event)
        component.provideHandler(self.onSynchronizeEvent)

    def OnButtonDown(self, evt):
        # intercept mouse button events - make sure this viewport is active in
        # MicroView's notebook
        event.notify(ViewportMouseDown(self))
        wxPaneFrame.OnButtonDown(self, evt)

    @component.adapter(ViewportModifiedEvent)
    def onViewportModifiedEvent(self, evt):
        """Respond to change in viewport layout - part 1 - occurs at beginning of e.g. double-click event"""

        if self.ignore_events:
            return

        if evt.GetImageIndex() in self._synced_image_indices:

            self.ignore_events = True

            idx = evt.GetPaneIndices()
            if evt._layout == '1Side3':
                self.SetViewTo1Side3(self._defaultRenderPanes, label='All')
            elif evt._layout == 'Single':
                self.SetViewToSingle(self._defaultRenderPanes[idx[0]])
            elif evt._layout == '2By2':
                self.SetViewTo2By2(self._defaultRenderPanes)
            else:
                logging.info("Unsupported synchronization mode!")

            self.ignore_events = False

    @component.adapter(ViewportModified2Event)
    def onViewportModified2Event(self, evt):
        """Respond to change in viewport layout - part 1 - occurs at beginning of e.g. double-click event"""
        pass

    @component.adapter(SynchronizeEvent)
    def onSynchronizeEvent(self, evt):
        """Respond to synchronization events"""

        idx = self.GetImageIndex()
        _old = evt.GetOldSyncList()
        _new = evt.GetNewSyncList()

        if idx in _old or idx in _new:
            if self.GetImageIndex() in _new:
                sl = _new[:]
                if idx in sl:
                    sl.remove(idx)
            else:
                sl = []
            self.setSyncList(sl)

    def setSyncList(self, image_indices):
        """Synchronize this viewport with the provided list of other viewports"""

        self._synced_image_indices = image_indices

        # debug
        idx = self.GetImageIndex()
        if image_indices:
            logging.info(
                "Viewport {0} synchronized with {1}".format(idx, image_indices))
        else:
            logging.info("Viewport {0} synchronization disabled".format(idx))

    def getSyncList(self):
        """Get a list of image indices to synchronize ourselves with"""
        return self._synced_image_indices

    def tearDown(self):

        # remove zope events
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.onViewportModifiedEvent)
        gsm.unregisterHandler(self.onViewportModified2Event)
        gsm.unregisterHandler(self.onSynchronizeEvent)

        del(self._defaultRenderPanes)
        del(self._lastPanes)
        del(self._currentPanes)
        del(self._CurrentPane)
        self._RenderPanes = []
        self.RemoveAllEventHandlers()

        wxPaneFrame.tearDown(self)

    def ResetView(self):
        for pane in self._RenderPanes:
            pane.ResetView()

    def GetImageIndex(self):
        return self._index

    def GetCurrentViewMode(self):
        return self._viewname

    def EnlargePane(self, evt):
        """Toggle single and default layout"""

        if not hasattr(evt, 'pane'):
            return

        pane = evt.pane
        idx = pane.GetImageIndex()

        # Disable viewport changes for 2D images
        image = component.getUtility(IImage, name='Image-%d' % idx)
        if image.GetDimensions()[2] == 1:
            return

        # Disable viewport changes for images where 3rd dimension isn't spatial
        dimension = image.GetDimensionInformation()[2]
        if not isinstance(dimension, MVImage.Distance):
            return

        if self._currentView == 'Single':
            if (self._lastView != 'Single') and (self._lastView is not None):
                self.SetViewToLastView()
            else:
                if self._defaultRenderPanes:
                    self.SetViewTo1Side3(self._defaultRenderPanes, label='All')
        else:
            if self._appPanes:
                N = len(self._appPanes) / 2
                i = self._appPanes.index(evt.pane)

            self.SetViewToSingle(pane)

    def _ConnectRenderPanesToViewports(self, renderPanes, viewports, offsets):

        self._lastPanes = self._currentPanes
        self._currentPanes = renderPanes

        # remove all old render panes first:
        while len(self.GetRenderPanes()):
            self.DisconnectRenderPane(self.GetRenderPanes()[-1])

        # connect all new render panes and set viewports for them
        offset = 0.0

        # eventing panes is useful for classes within this window, but for classes outside of this window, the
        # pane index is the only thing that's useful
        pane_indices = [self._defaultRenderPanes.index(p) for p in renderPanes]

        event.notify(ViewportModifiedEvent(
            self.GetImageIndex(), renderPanes, pane_indices, self._currentView))

        for i in range(len(renderPanes)):
            self.ConnectRenderPane(renderPanes[i])
            vp = list(viewports[i])
            vp[1] = offset + (1 - offset) * vp[1]
            vp[3] = offset + (1 - offset) * vp[3]
            renderPanes[i].SetViewport(vp)
            renderPanes[i].SetViewportOffsets(offsets[i])

        event.notify(ViewportModified2Event(self.GetImageIndex(), renderPanes))

        # finally, render all panes
        for pane in renderPanes:
            pane.Render()

    def SetViewName(self, viewname):
        self._viewname = viewname

    def SetViewTo(self, layout, renderPanes, label=None):

        self._lastviewname = self._viewname
        self.SetViewName(label)
        self._lastView = self._currentView
        self._currentView = layout
        if hasattr(self, 'SetViewTo' + layout):
            getattr(self, 'SetViewTo' + layout)(renderPanes, label)

    def SetViewToLastView(self):
        self.SetViewTo(
            self._lastView, self._lastPanes, label=self._lastviewname)

    def SetViewToSingle(self, renderPane, label=None):

        if self._defaultRenderPanes is None:
            self._defaultRenderPanes = [renderPane]

        self._lastviewname = self._viewname

        # render panes have a name - use it if needed
        if label is None:
            label = renderPane.GetName()

        self.SetViewName(label)
        self._lastView = self._currentView
        self._currentView = 'Single'
        menuoffset = -self._menuHeight
        viewports = ((0.00, 0.00, 1.00, 1.00),)
        offsets = ((0, 0, 0, menuoffset), )
        self._ConnectRenderPanesToViewports((renderPane,), viewports, offsets)

    def SetViewTo1Side3(self, renderPanes, label='All'):

        if self._defaultRenderPanes is None:
            self._defaultRenderPanes = renderPanes

        self._lastviewname = self._viewname
        self.SetViewName(label)
        self._defaultRenderPanes = renderPanes
        self._lastView = self._currentView
        self._currentView = '1Side3'
        if len(renderPanes) != 4:
            logging.error("wrong number of render panes")
            return

        menuoffset = -self._menuHeight
        viewports = ((0.00, 0.00, 0.67, 1.00),
                     (0.67, 0.67, 1.00, 1.00),
                     (0.67, 0.33, 1.00, 0.67),
                     (0.67, 0.00, 1.00, 0.33))
        offsets = ((0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset))

        self._ConnectRenderPanesToViewports(renderPanes, viewports, offsets)

    def SetViewTo1Over3(self, renderPanes, label='1Over3'):

        if self._defaultRenderPanes is None:
            self._defaultRenderPanes = renderPanes

        self._lastviewname = self._viewname
        self.SetViewName(label)
        self._lastView = self._currentView
        self._currentView = '1Over3'
        menuoffset = -self._menuHeight
        viewports = ((0.00, 0.33, 1.00, 1.00),
                     (0.00, 0.00, 0.33, 0.33),
                     (0.33, 0.00, 0.67, 0.00),
                     (0.67, 0.00, 1.00, 0.00))
        offsets = ((0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset))

        self._ConnectRenderPanesToViewports(renderPanes, viewports, offsets)

    def SetViewTo4Plus4(self, renderPanes, label=''):
        """Set layout to (1 over 3) plus (1 over 3)
            A A A  E E E
            A A A  E E E
            B C D  F G H
        """

        if self._defaultRenderPanes is None:
            self._defaultRenderPanes = renderPanes

        self._lastviewname = self._viewname
        self.SetViewName(label)
        self._lastView = self._currentView
        self._currentView = '4Plus4'
        menuoffset = -self._menuHeight
        viewports = ((0.00, 0.33, 0.50, 1.00),
                     (0.00, 0.00, 0.17, 0.33),
                     (0.17, 0.00, 0.33, 0.33),
                     (0.33, 0.00, 0.50, 0.33),
                     (0.50, 0.33, 1.00, 1.00),
                     (0.50, 0.00, 0.67, 0.33),
                     (0.67, 0.00, 0.83, 0.33),
                     (0.83, 0.00, 1.00, 0.33))
        offsets = ((0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset))

        self._ConnectRenderPanesToViewports(renderPanes, viewports, offsets)

    def SetViewTo4Plus4B(self, renderPanes, label=''):
        """ Set layout to (2 by 2) plus ( 2 by 2)
            A1 B1 A2 B2
            C1 D1 C2 D2
        This layout is used by Register plugin do display
        the views of two images side by side.
        """

        if self._defaultRenderPanes is None:
            self._defaultRenderPanes = renderPanes

        self._lastviewname = self._viewname
        self.SetViewName(label)
        self._lastView = self._currentView
        self._currentView = '4Plus4B'
        viewports = ((0.00, 0.50, 0.25, 1.00),
                     (0.25, 0.50, 0.50, 1.00),
                     (0.00, 0.00, 0.25, 0.50),
                     (0.25, 0.00, 0.50, 0.50),

                     (0.50, 0.50, 0.75, 1.00),
                     (0.75, 0.50, 1.00, 1.00),
                     (0.50, 0.00, 0.75, 0.50),
                     (0.75, 0.00, 1.00, 0.50))

        b = 10  # boundary offset between two images
        offsets = ((0, 0, 0, 0),
                   (0, 0, b, 0),
                   (0, 0, 0, 0),
                   (0, 0, b, 0),

                   (b, 0, 0, 0),
                   (0, 0, 0, 0),
                   (b, 0, 0, 0),
                   (0, 0, 0, 0))
        # the offsets is not working at the moment, don't know why.
        self._ConnectRenderPanesToViewports(renderPanes, viewports, offsets)

    def SetViewTo1Plus1(self, renderPanes, label=''):

        if self._defaultRenderPanes is None:
            self._defaultRenderPanes = renderPanes

        self._lastviewname = self._viewname
        self.SetViewName(label)
        self._lastView = self._currentView
        self._currentView = '1Plus1'
        menuoffset = -self._menuHeight
        viewports = ((0.00, 0.00, 0.50, 1.00),
                     (0.50, 0.00, 1.00, 1.00))

        offsets = ((0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset))

        self._ConnectRenderPanesToViewports(renderPanes, viewports, offsets)

    def SetViewTo2By2(self, renderPanes, label='2By2'):
        """ 0 1
            2 3
        """

        if self._defaultRenderPanes is None:
            self._defaultRenderPanes = renderPanes

        self._lastviewname = self._viewname
        self.SetViewName(label)
        self._lastView = self._currentView
        self._currentView = '2By2'
        menuoffset = -self._menuHeight
        viewports = ((0.00, 0.50, 0.50, 1.00),
                     (0.50, 0.50, 1.00, 1.00),
                     (0.00, 0.00, 0.50, 0.50),
                     (0.50, 0.00, 1.00, 0.50))

        offsets = ((0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset))

        self._ConnectRenderPanesToViewports(renderPanes, viewports, offsets)

    def SetViewTo2Plus2(self, renderPanes, label='2Plus2'):
        """ 0 2
            1 3
        """

        if self._defaultRenderPanes is None:
            self._defaultRenderPanes = renderPanes

        self._lastviewname = self._viewname
        self.SetViewName(label)
        self._lastView = self._currentView
        self._currentView = '2Plus2'
        menuoffset = -self._menuHeight
        viewports = ((0.00, 0.50, 0.50, 1.00),
                     (0.00, 0.00, 0.50, 0.50),
                     (0.50, 0.50, 1.00, 1.00),
                     (0.50, 0.00, 1.00, 0.50))

        offsets = ((0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset))

        self._ConnectRenderPanesToViewports(renderPanes, viewports, offsets)

    def SetViewTo3By2(self, renderPanes, label='3By2'):
        """ 0 3
            1 4
            2 5
        """

        if self._defaultRenderPanes is None:
            self._defaultRenderPanes = renderPanes

        self._lastviewname = self._viewname
        self.SetViewName(label)
        self._lastView = self._currentView
        self._currentView = '3By2'
        menuoffset = -self._menuHeight
        viewports = ((0.00, 0.67, 0.50, 1.00),
                     (0.00, 0.33, 0.50, 0.67),
                     (0.00, 0.00, 0.50, 0.33),
                     (0.50, 0.67, 1.00, 1.00),
                     (0.50, 0.33, 1.00, 0.67),
                     (0.50, 0.00, 1.00, 0.33))
        offsets = ((0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset))

        self._ConnectRenderPanesToViewports(renderPanes, viewports, offsets)

    def SetViewTo3Plus3(self, renderPanes):
        self.SetViewTo3By2(renderPanes)

    def SetViewTo3By3(self, renderPanes, label='3By3'):
        """ 0 3 6
            1 4 7
            2 5 8
        """

        if self._defaultRenderPanes is None:
            self._defaultRenderPanes = renderPanes

        self._lastviewname = self._viewname
        self.SetViewName(label)
        self._lastView = self._currentView
        self._currentView = '3By3'
        menuoffset = -self._menuHeight
        viewports = ((0.00, 0.67, 0.33, 1.00),
                     (0.00, 0.33, 0.33, 0.67),
                     (0.00, 0.00, 0.33, 0.33),
                     (0.33, 0.67, 0.67, 1.00),
                     (0.33, 0.33, 0.67, 0.67),
                     (0.33, 0.00, 0.67, 0.33),
                     (0.67, 0.67, 1.00, 1.00),
                     (0.67, 0.33, 1.00, 0.67),
                     (0.67, 0.00, 1.00, 0.33))

        offsets = ((0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset),
                   (0, 0, 0, menuoffset))

        self._ConnectRenderPanesToViewports(renderPanes, viewports, offsets)

    def SetApplicationMode(self, mode):
        """possible mode: 'normal', 'register' for now
        we my add 'volume rendering', etc later.
        """
        self._mode = mode
        if mode == 'normal':
            # clean up
            self._appPanes = None

    def SetApplicationPanes(self, panes):
        self._appPanes = panes

    def GetRenderWindowSize(self):
        return self._RenderWindow.GetSize()
