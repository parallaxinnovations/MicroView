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
MicroViewRenderPane - Extends RenderPane with additional MicroView-specific functionality.

  It's customized to view OrthoPlanes and related actors.

Derived From:

    RenderPane
"""

import logging
import os
import pickle
import vtk
import wx
from zope import component, event

from PI.visualization.common import MicroViewSettings, CoordinateSystem
from PI.visualization.common.events import MicroViewSettingsModifiedEvent
from vtkAtamai import RenderPane
from PI.visualization.MicroView.interfaces import IMicroViewOutput, IMicroViewMainFrame
from PI.visualization.MicroView.events import OrthoCenterChangeEvent
import StockItems


class MicroViewRenderPane(RenderPane.RenderPane):

    def __init__(self, parent, **kw):
        RenderPane.RenderPane.__init__(self, parent, **kw)

        self._index = 0

        if 'index' in kw:
            self._index = kw['index']
        else:
            logging.error("MicroViewRenderPane requires an image index!")

        # The 'tracked' sliceplane is what gets displayed in the lower right of
        # each
        self._tracked_sliceplane_index = 2
        # viewport

        self._pane_name = kw['name']

        # keep reference to parent object
        self._parent = parent

        # what style of coordinate system?
        self._coordinate_system = CoordinateSystem.CoordinateSystem.vtk_coords

        # create an VTK event object
        self._eventObject = vtk.vtkObject()

        # keep a reference to OrthoPlanes
        self.__orthoPlanes = None

        self._lastActorFactory = None

        # keep track of whether mouse moved during right click events
        self._right_click_x = None
        self._right_click_y = None

        self._stockicons = StockItems.StockIconFactory()

        # button-1 action binding
        self._B1Action = 'rotate'

        # create some default cursors
        self._cursors = {'winlev': wx.StockCursor(wx.CURSOR_ARROW),
                         'rotate': wx.StockCursor(wx.CURSOR_ARROW),
                         'zoom': wx.StockCursor(wx.CURSOR_MAGNIFIER),
                         'pan': wx.StockCursor(wx.CURSOR_HAND),
                         'slice': wx.StockCursor(wx.CURSOR_ARROW),
                         'spin': wx.StockCursor(wx.CURSOR_ARROW),
                         }
        # override some of the default with cursor if we find them on disk
        for action in ('pan', 'winlev', 'zoom', 'slice', 'spin'):
            filename = os.path.join('Cursors', '%s.gif' % action)
            if os.path.exists(filename):
                try:
                    image = wx.Image(filename)
                    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 1)
                    image.SetOptionInt(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 1)
                    self._cursors[action] = wx.CursorFromImage(image)
                except:
                    logging.exception("MicroViewRenderPane")

        self._use_dicom_coordinates = False

        # ------------------------------------------------------------------------------------
        # Set up some zope event handlers
        # ---------------------------------------------------------------------
        component.provideHandler(self.OnConfigModified)

    def GetName(self):
        return self._pane_name

    def GetImageIndex(self):
        return self._index

    def GetTrackedSliceIndex(self):
        return self._tracked_sliceplane_index

    def SetTrackedSlicePlaneIndex(self, idx):
        self._tracked_sliceplane_index = idx

    def tearDown(self):

        # disconnect orthoplanes
        self.DisconnectActorFactory(self.__orthoPlanes)

        RenderPane.RenderPane.tearDown(self)

        for actor in self.GetActorFactories():
            if actor is None:
                logging.error("tearDown: GetActorFactories() contains None.  {0}".format(
                    self.GetActorFactories()))
            else:
                actor.RemoveFromRenderer(self._Renderer)
        self._ActorFactories = []

        self._eventObject.RemoveAllObservers()
        self._Renderer.RemoveAllObservers()

        # unregister our zope handlers
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.OnConfigModified)

        del(self._eventObject)
        del(self.__orthoPlanes)
        del(self._parent)
        del(self._Renderer)

    def GetObjectState(self):
        class MicroViewRenderPaneData(object):
            pass
        obj = MicroViewRenderPaneData()
        camera = self._Renderer.GetActiveCamera()
        obj.c_cr = camera.GetClippingRange()
        obj.c_dist = camera.GetDistance()
        obj.c_fp = camera.GetFocalPoint()
        obj.c_pos = camera.GetPosition()
        obj.c_vu = camera.GetViewUp()
        return obj

    def SetObjectState(self, obj):
        camera = self._Renderer.GetActiveCamera()
        camera.SetPosition(obj.c_pos)
        camera.SetFocalPoint(obj.c_fp)
        camera.SetViewUp(obj.c_vu)
        camera.SetClippingRange(obj.c_cr)
        camera.ComputeViewPlaneNormal()

    def AddObserver(self, evt, callback):
        self._eventObject.AddObserver(evt, callback)

    def ConnectOrthoPlanes(self, orthoPlanes):
        self.__orthoPlanes = orthoPlanes
        self.ConnectActorFactory(orthoPlanes)
        self.ResetView()

    def BindSetOrthoCenterToButton(self, button=1, modifier=None):
        self.BindModeToButton((None,
                               self.SetOrthoCenter,
                               None),
                              button, modifier)

    def SetOrthoCenter(self, evt):
        if self.__orthoPlanes:
            pos = self.GetCursorPositionOnOrthoPlanes(evt)
            if pos:
                self.__orthoPlanes.SetOrthoCenter(pos)
                # send out an event indicating our center has moved
                event.notify(OrthoCenterChangeEvent(pos))

    def DoPickActor(self, evt):

        RenderPane.RenderPane.DoPickActor(self, evt)

        if self._CurrentActorFactory is not None:
            if evt.num > 0:
                try:
                    action = self.GetOrthoPlanes(
                    )._OrthoPlanesFactory__UserAction
                except:
                    action = ''
                curs = {'Push': 'slice', 'Spin': 'spin', 'Rotate': 'spin'}
                if action in curs:
                    cur = self._cursors[curs[action]]
                else:
                    cur = wx.StockCursor(wx.CURSOR_ARROW)
                self._parent.SetCursor(cur)

    def DoReleaseActor(self, evt):

        RenderPane.RenderPane.DoReleaseActor(self, evt)
        if evt.num > 0:
            self._parent.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def DoStartMotion(self, evt):

        if evt.num == 1:
            if evt.state == 1:  # Shift key
                curs = self._cursors['pan']
            else:
                curs = self._cursors[self._B1Action]
        elif evt.num == 2:
            curs = self._cursors['slice']
        elif evt.num == 3:

            # keep track of current mouse position - we want to differentiate
            # between zooming and context sensitive menu
            self._right_click_x = evt.x
            self._right_click_y = evt.y

            curs = self._cursors['zoom']

        if evt.num in (1, 2):
            self._parent.SetCursor(curs)

        RenderPane.RenderPane.DoStartMotion(self, evt)

    def DoEndMotion(self, evt):

        # keep track of current mouse position - we want to differentiate
        # between zooming and context sensitive menu
        if self._right_click_x is not None:
            if (evt.x == self._right_click_x) and (evt.y == self._right_click_y):
                # a right click menu should be displayed
                self.ShowContextSensitiveMenu()
        self._right_click_x = None
        self._right_click_y = None

        curs = wx.StockCursor(wx.CURSOR_ARROW)
        self._parent.SetCursor(curs)
        RenderPane.RenderPane.DoEndMotion(self, evt)

    def ShowContextSensitiveMenu(self):

        menu = wx.Menu()

        for l in ('x', 'y', 'z'):
            L = l.capitalize()

            # positive
            _id = wx.NewId()
            item = wx.MenuItem(menu, _id, 'View +%s' %
                               L, 'Orient image along positive %s-axis' % l)
            wx.EVT_MENU(
                menu, _id, lambda evt, label=L: self.ResetView(view='+' + label, reset_planes=False))
            item.SetBitmap(
                self._stockicons.getMenuBitmap('stock_arrow_%s' % l))
            menu.AppendItem(item)

            # negative
            _id = wx.NewId()
            item = wx.MenuItem(menu, _id, 'View -%s' %
                               L, 'Orient image along negative %s-axis' % l)
            wx.EVT_MENU(
                menu, _id, lambda evt, label=L: self.ResetView(view='-' + label, reset_planes=False))
            item.SetBitmap(
                self._stockicons.getMenuBitmap('stock_arrow_%s' % l))
            menu.AppendItem(item)

        self._main.PopupMenu(menu)
        menu.Destroy()

    def DoCameraZoom(self, evt):
        """Mouse motion handler for zooming the scene."""

        if (self._right_click_x != None):
            # we should change cursor here
            self._parent.SetCursor(self._cursors['zoom'])
            self._right_click_x = None
            self._right_click_y = None

        RenderPane.RenderPane.DoCameraZoom(self, evt)

    def EnableMotionMonitoring(self):
        self.BindEvent("<Motion>", self.DoMouseMove)

    def DisableMotionMonitoring(self):
        self.BindEvent("<Motion>", None)

    # Bind key and mouse events
    def BindDefaultInteraction(self):

        RenderPane.RenderPane.BindDefaultInteraction(self)

        # mark the point and display its coordinates and gray scale value
        self.EnableMotionMonitoring()

        # save the scene in the main view port to an image file
        self.BindEvent("<KeyPress-t>", self._SaveMainViewPortAsImage)

        # keypress binding for other interactions
        self.BindEvent("<Up>", lambda evt: self._PushPlaneBySteps(1))
        self.BindEvent("<Down>", lambda evt: self._PushPlaneBySteps(-1))
        self.BindEvent("<Right>", lambda evt: self._PushPlaneBySteps(1))
        self.BindEvent("<Left>", lambda evt: self._PushPlaneBySteps(-1))

        self.BindEvent("<Prior>", lambda evt: self._PushPlaneBySteps(10))
        self.BindEvent("<Next>", lambda evt: self._PushPlaneBySteps(-10))

        self.BindEvent("<Home>", lambda evt: self._PushPlaneBySteps(-10000))
        self.BindEvent("<End>", lambda evt: self._PushPlaneBySteps(10000))

        self.BindSetOrthoCenterToButton(1, modifier='Control')

    def DoStartAction(self, evt):
        self._LastX = evt.x
        self._LastY = evt.y
        self._Action = 1

    def DoEndAction(self, evt):
        self._Action = 0

    def _PushPlaneBySteps(self, steps=1):

        plane = self.__orthoPlanes.GetPickedPlane()
        if plane is None:
            return
        input = plane.GetInput()
        # input.UpdateInformation()  # TODO: VTK-6 figure out what to do with
        # this
        spacing = input.GetSpacing()

        Normal = plane.GetNormal()
        old_UseSpacing = plane.GetUseSpacing()
        if old_UseSpacing is False:
            plane.SetUseSpacing(True)

        if Normal[0] == 0 and Normal[1] == 0:
            distance = spacing[2] * steps
        elif Normal[0] == 0 and Normal[2] == 0:
            distance = -spacing[1] * steps
        else:
            distance = spacing[0] * steps

        plane.Push(distance)
        if old_UseSpacing is False:
            plane.SetUseSpacing(old_UseSpacing)

        # is this still needed??
        # plane.Render()  # self.renderPanes[0].GetRenderer())

    def ResetView(self, view=None, reset_planes=True):
        """Resets the view of orthoPlanes."""
        if not self.__orthoPlanes:
            return

        # if orthoviews are locked, bail
        if self.__orthoPlanes.GetRotateAndSpin() is True:
            return

        imageData = self.__orthoPlanes.GetInput()
        if not imageData:
            return

        # imageData.Update()
        extent = imageData.GetExtent()
        spacing = imageData.GetSpacing()
        origin = imageData.GetOrigin()
        renderer = self.GetRenderer()
        camera = renderer.GetActiveCamera()

        if view is None:
            if self.GetCoordinateSystem() == CoordinateSystem.CoordinateSystem.dicom_coords:
                view = '-Z'
            else:
                view = '+Z'

        if self.GetCoordinateSystem() == CoordinateSystem.CoordinateSystem.dicom_coords:
            camera.SetViewUp(0, -1, 0)
        else:
            camera.SetViewUp(0, 1, 0)

        bounds = [origin[0] + (extent[0] - 0.5) * spacing[0],
                  origin[0] + (extent[1] + 0.5) * spacing[0],
                  origin[1] + (extent[2] - 0.5) * spacing[1],
                  origin[1] + (extent[3] + 0.5) * spacing[1],
                  origin[2] + (extent[4] - 0.5) * spacing[2],
                  origin[2] + (extent[5] + 0.5) * spacing[2]]

        xc, yc, zc = ((bounds[0] + bounds[1]) / 2.,
                      (bounds[2] + bounds[3]) / 2.,
                      (bounds[4] + bounds[5]) / 2.)
        camera.SetFocalPoint(xc, yc, zc)

        # position camera so that it can see object regardless of whether
        # image is 2D or 3D

        positive = (view[0] == '+')

        axis = {'X': 0, 'Y': 1, 'Z': 2}[view[1]]

        for i in range(len(extent) / 2):
            if extent[2 * i] == extent[2 * i + 1]:
                axis = i

        pos = [xc, yc, zc]
        if positive:
            pos[axis] = bounds[axis * 2 + 1] * 2
        else:
            pos[axis] = bounds[axis * 2] * 2

        camera.SetPosition(pos[0], pos[1], pos[2])
        renderer.ResetCamera(bounds)

        if reset_planes:
            self.__orthoPlanes.SetOrthoCenter(xc, yc, zc)
            self.__orthoPlanes.DoResetPlanes(None)

        self.Render()

# following are for backward compatibility
    def _DecrementPush(self, evt, factor=1):
        self._PushPlaneBySteps(-factor)

    def _IncrementPush(self, evt, factor=1):
        self._PushPlaneBySteps(factor)

    def _PriorIncrementPush(self, evt):
        self._PushPlaneBySteps(10)

    def _NextDecrementPush(self, evt):
        self._PushPlaneBySteps(-10)

    def _HomeDecrementPush(self, evt):
        self._PushPlaneBySteps(-10000)

    def _EndIncrementPush(self, evt):
        self._PushPlaneBySteps(10000)
# end of backward compatibility

    def _SaveMainViewPortAsImage(self, evt):
        """Save the scene in the main view port to an image file."""
        self.SaveMainViewPortSnapShot()

    def GetCurrentDirectory(self):
        # determine working directory
        curr_dir = os.getcwd()

        config = MicroViewSettings.MicroViewSettings.getObject()

        # over-ride with system-wide directory
        try:
            curr_dir = config.GlobalCurrentDirectory or curr_dir
        except:
            config.GlobalCurrentDirectory = curr_dir

        try:
            curr_dir = config.CurrentSnapshotDirectory or curr_dir
        except:
            config.CurrentSnapshotDirectory = curr_dir

        return curr_dir

    def SaveCurrentDirectory(self, curr_dir):

        config = MicroViewSettings.MicroViewSettings.getObject()
        config.CurrentSnapshotDirectory = curr_dir

    def SaveMainViewPortSnapShot(self, filename=None):

        # get a global object that can manage saving image to disk
        object = component.getUtility(IMicroViewOutput)
        object.SaveViewPortSnapShot(self._Renderer, filename)

    def GetCursorPositionOnOrthoPlanes(self, evt):
        """Return cursor position on OrthoPlanes."""

        self.DoPickActor(evt)
        infoList = self._PickInformationList
        if len(infoList) > 0:
            for info in infoList:
                if info.factory.IsA('OrthoPlanesFactory') or \
                        info.factory.IsA('SlicePlaneFactory'):
                    return info.position
        return None

    def GetCursorPosition(self, evt):
        """Return cursor position on first object test ray hits. -- Ignore LineSegmentSelectionFactories"""

        self.DoSmartPick(evt)
        infoList = self._PickInformationList
        if len(infoList) > 0:
            for info in infoList:
                if not info.factory.IsA('LineSegmentSelectionFactory'):
                    return info.position
        return None

    def DoMouseMove(self, evt):
        """
        Call back method for tk mouse Motion event
        It's a bit twisted here.
        RenderPane has a method DoCursorMotion that was disabled
        to speed Volume Rendering.

        We need this method here to broadcast the event
        """
        position = self.GetCursorPositionOnOrthoPlanes(evt)
        self._eventObject.position = position

        if self._CurrentActorFactory != self._lastActorFactory:
            if self._lastActorFactory:
                evt.type = 8
                self._lastActorFactory.HandleEvent(evt)
            if self._CurrentActorFactory:
                evt.type = 7
                self._CurrentActorFactory.HandleEvent(evt)
            self._lastActorFactory = self._CurrentActorFactory

        self._eventObject.InvokeEvent("MouseMoveEvent")

    def GetOrthoPlanes(self):
        """an alternative to call self.GetMicroView().OrthoPlane
        be careful with the reference count.
        """
        return self.__orthoPlanes

    def SetCoordinateSystem(self, val):
        self._coordinate_system = val

    def GetCoordinateSystem(self):
        return self._coordinate_system

    @component.adapter(MicroViewSettingsModifiedEvent)
    def OnConfigModified(self, evt):

        return # TODO

        # we only care if MicroView wants DICOM coords
        if evt.GetConfig().bUseDICOMCoordSystem:
            coord_system = CoordinateSystem.CoordinateSystem.dicom_coords
        else:
            coord_system = CoordinateSystem.CoordinateSystem.vtk_coords

        if coord_system != self.GetCoordinateSystem():
            self.SetCoordinateSystem(coord_system)
            # reset
            self.ResetView()

# def SetPointSelection(self, PointSelection):
##         self._PointSelection = PointSelection

    def GetEventObject(self):
        """returns the event object used to generate user events"""
        return self._eventObject

    def GetMicroView(self):
        # transitional routine - this should go away
        return component.getUtility(IMicroViewMainFrame)

    def SetPaneName(self, PaneName):
        self.PaneName = PaneName

    def RegBindSpace(self):
        "Bind the space bar.  Space bar is used to select landmarks for registration."
        self.BindEvent("<space>", self.RegPickPointVol2)

    def RegUnbindSpace(self):
        "Unbind the space bar because the registration plugin has been toggled off."
        self.BindEvent("<space>", None)

    def RegPickPointVol2(self, evt):
        """Pick a point from volume 2 and send this information to other
        viewer for registration.
        """
        self.DoPickActor(evt)
        try:
            x = self._PickInformationList[0].position[0]
            y = self._PickInformationList[0].position[1]
            z = self._PickInformationList[0].position[2]
        except IndexError:
            return

        try:
            origin = self.GetMicroView().ImageData.GetOrigin()
            EditingAllowed = self.subordinate.RegPickPointVol2(x, y, z, origin)
        except:
            return

        if EditingAllowed:
            sphere = self.GetMicroView().RegLandmarks.GetSphereToEdit()
            self.GetMicroView().RegLandmarks.UpdateSphere(sphere, x, y, z)
