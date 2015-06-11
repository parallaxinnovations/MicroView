import logging
import vtk
from vtkAtamai import ActorFactory, SphereMarkFactory
import math


class MySphereMarkFactory(SphereMarkFactory.SphereMarkFactory):

    def __init__(self):
        SphereMarkFactory.SphereMarkFactory.__init__(self)
        self.__caption = 'undefined'
        self._captionActor = None
        self.bCaptionVisibility = False

    def SetCaption(self, caption=''):
        """Set the caption associated with the given sphere marker"""

        self.__caption = caption or 'undefined'

        for renderer in self._Renderers:
            for actor in self._ActorDict[renderer]:
                # differentiate between 2D actor (caption) and 3D actor
                # (sphere)
                if actor.IsA('vtkCaptionActor2D'):
                    actor.SetCaption(self.__caption)

    def GetCaption(self):
        return self.__caption

    def SetVisibility(self, renderer, visible):

        for actor in self._ActorDict[renderer]:
            # differentiate between 2D actor (caption) and 3D actor (sphere)
            if not actor.IsA('vtkCaptionActor2D'):
                actor.SetVisibility(visible)

    def SetCaptionVisibility(self, visible):

        self.bCaptionVisibility = visible

        if self._captionActor:
            self._captionActor.SetVisibility(visible)

            for renderer in self._Renderers:
                for actor in self._ActorDict[renderer]:
                    # differentiate between 2D actor (caption) and 3D actor
                    # (sphere)
                    if actor.IsA('vtkCaptionActor2D'):
                        actor.SetVisibility(visible)

    def _MakeActors(self):
        # create the original marker
        actors = SphereMarkFactory.SphereMarkFactory._MakeActors(self)

        # now append a caption actor
        self._captionActor = vtk.vtkCaptionActor2D()
        self._captionActor.SetAttachmentPoint(self.GetPosition())
        self._captionActor.SetCaption(self.GetCaption())
        self._captionActor.SetThreeDimensionalLeader(False)
        self._captionActor.SetWidth(0.25 / 3.0)
        self._captionActor.SetHeight(0.10 / 3.0)
        self._captionActor.SetVisibility(self.bCaptionVisibility)

        text_actor = self._captionActor.GetTextActor()
        # text_actor.SetTextScaleModeToNone()  # set absolute scaling mode

        p = self._captionActor.GetCaptionTextProperty()
        p.SetColor((0, 1, 0.2))
        p.BoldOff()
        p.ItalicOff()
        p.SetFontSize(15)
        p.ShadowOff()

        actors.append(self._captionActor)

        return actors


class SphereMarkListFactory(ActorFactory.ActorFactory):

    def tearDown(self):
        self._markTransform.AddObserver('ModifiedEvent', None)
        del(self._markTransform)
        self.DeleteAll()
        del(self.markList)

    def __init__(self):

        ActorFactory.ActorFactory.__init__(self)

        self.markList = []
        self.positionList = []          # none transformed position list
        self.captions = []
        self.activeIndex = None
        self._defaultCaptionVisibility = False
        self.cursorMark = None
        self.curpos = None

        # sizes
        self.markSize = 10.
        self.cursorMarkSize = 12.

        # colors
        self.cursorMarkColor = (1, 0, 0)    # red
        self.markColor = (1, 1, 0)          # yellow

        self._markTransform = vtk.vtkTransform()
        self._markTransform.AddObserver(
            'ModifiedEvent', self._OnTransformModified)
        self._transformedView = False

        self.eventObject = vtk.vtkObject()

    def AddObserver(self, evt, method):
        self.eventObject.AddObserver(evt, method)

    def SetTransformedView(self, b):
        self._transformedView = b
        self._ChangeView()

    def SetMarkerVisibility(self, visible):
        for renderer in self._Renderers:
            for marker in self.markList:
                marker.SetVisibility(renderer, visible)
        self.Modified()

    def SetCaptionVisibility(self, visible):

        self._defaultCaptionVisibility = visible

        for marker in self.markList:
            marker.SetCaptionVisibility(visible)
        self.Modified()

    def GetNumberOfMarks(self):
        return len(self.markList)

    def GetMarkPosition(self, i):
        """Return the current position of mark i"""
        return self.markList[i].GetPosition()

    def GetMarkPosition(self, i):
        """Returns the coordinate of a give marker"""
        return self.markList[i].GetPosition()

    def GetMarkPositions(self):
        """Return a list of current mark positions"""
        pos = []
        for m in self.markList:
            pos.append(m.GetPosition())
        return pos

    def GetPositionList(self, transformed=False):
        """Return the position list of marks.
        By default, return the non-transformed list.
        """
        if transformed:
            _list = []
            for m in self.markList:
                _list.append(m.GetPosition())
                return tuple(_list)
        else:
            return self.positionList

    def SetPositionList(self, _list):
        """Populate the marks at the positions in the list.
        The list should be non-transformed positions
        """
        self.DeleteAll()
        if self._transformedView:
            trans = self._markTransform
            for pos in _list:
                self.AddMark(trans.TransformPoint(pos))
        else:
            for pos in _list:
                self.AddMark(pos)
        self.positionList = _list  # avoid double transform errors

    def AddToRenderPane(self, pane, type=None):
        """Add this factory to pane and bind interactions"""

        pane.ConnectActorFactory(self)
        # pane.BindEvent("<KeyPress-space>", self._MoveCursorMark) -- this
        # collide with MicroView's 'ActionEvent'

        # cursor mark
        self.cursorMark = SphereMarkFactory.SphereMarkFactory()
        self.cursorMark.SetSize(self.cursorMarkSize)
        self.cursorMark.SetColor(self.cursorMarkColor)
        self.AddChild(self.cursorMark)
        self.cursorMark.SetOpacity(0)

    def RemoveFromRenderPane(self, pane, type='2D'):

        # pane.BindEvent("<KeyPress-space>", None) -- this collide with
        # MicroView's 'ActionEvent'
        pane.DisconnectActorFactory(self)

    def _MoveCursorMark(self, evt=None):
        """Move Cursor Mark when space bar is pressed"""

        if evt:
            curpos = evt.pane.GetCursorPosition(evt)
            self.curpos = curpos
        else:
            curpos = self.curpos

        self.SetCursorMark(curpos)

    def GetCursorMark(self):
        return self.curpos

    def SetCursorMark(self, curpos):

        if curpos:
            # round the z value in case it's 2D image
            curpos = list(curpos)
            curpos[2] = round(curpos[2], 10)
            self.curpos = curpos

            self.cursorMark.SetPosition(curpos)
            self.cursorMark.SetOpacity(1)
            self.cursorMark.Modified()
            self.eventObject.position = curpos
            self.eventObject.InvokeEvent("ModifiedEvent")

    def GetCursorMarkOpacity(self):
        return self.cursorMark.GetOpacity()

    def HideCursorMark(self):
        if self.cursorMark:
            self.cursorMark.SetOpacity(0)
            self.Modified()

    def SetCursorMarkPosition(self, pos):
        self.cursorMark.SetPosition(pos)
        self.cursorMark.SetOpacity(1)
        self.cursorMark.Modified()

    def SetActiveIndex(self, i):
        """Set cursor to the location of mark i, for browsing
        or editing (no editing now)"""
# restore the color for the last active mark
# if self.activeIndex is not None:
# self.markList[self.activeIndex].SetOpacity(1)
# else:
# self.cursorMark.SetOpacity(0)

        # color change for current active mark
        if i >= 0 and i < len(self.markList):
            self.cursorMark.SetPosition(self.markList[i].GetPosition())
            self.activeIndex = i
            self.cursorMark.SetOpacity(0)
        else:
            self.activeIndex = None
            # self.cursorMark.SetOpacity(1)

    def AddMark(self, position=None, caption=''):
        """Add a new mark."""

        if position is None:
            position = self.curpos

        if position is None:
            return

        self.cursorMark.SetOpacity(0)

        mark = MySphereMarkFactory()
        mark.SetPosition(position)
        mark.SetSize(self.markSize)
        mark.SetColor(self.markColor)
        mark.SetCaption(caption)

        # should caption be displayed immediately?
        mark.SetCaptionVisibility(self._defaultCaptionVisibility)

        self.markList.append(mark)
        self.AddChild(mark)
        self.lastMarkIndex = None

        # keep a record of none transformed positionList
        transform = self._markTransform.GetInverse()
        self.positionList.append(transform.TransformPoint(position))

    def MoveMark(self, i, position=None, caption=''):
        """Move mark with index i to cursor mark position."""

        if position is None:
            position = self.curpos
        if position is None:
            return

        self.markList[i].SetPosition(position)
        self.markList[i].SetOpacity(1)
        self.markList[i].SetCaption(caption)
        self.markList[i].Modified()
        self.activeIndex = i

        # keep a record of none transformed positionList
        transform = self._markTransform.GetInverse()
        self.positionList[i] = transform.TransformPoint(position)

    def DeleteMark(self, i):
        if i >= len(self.markList):
            logging.debug("DeleteMark: list index out of range: %d" % i)
            return
        self.RemoveChild(self.markList[i])
        del self.markList[i]
        del self.positionList[i]
        self.activeIndex = None

    def DeleteAll(self):

        for mark in self.markList:
            self.RemoveChild(mark)

        self.markList = []
        self.positionList = []
        self.activeIndex = None

    def _OnTransformModified(self, obj, evt):
        self._ChangeView()

    def _ChangeView(self):
        if self._transformedView:
            for i in range(len(self.positionList)):
                pos1 = self._markTransform.TransformPoint(self.positionList[i])
                self.markList[i].SetPosition(pos1)
        else:
            for i in range(len(self.positionList)):
                self.markList[i].SetPosition(self.positionList[i])

        self.Modified()

    def GetMarkTransform(self):
        """Use this method to access self._markTransform:
        e.g markList.GetMarkTransform().SetMatrix(matrix).
        There is no SetMarkTransform method.
        """
        return self._markTransform

    def GetActiveIndex(self):
        return self.activeIndex
