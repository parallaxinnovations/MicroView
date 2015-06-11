import math
import vtk
from vtkAtamai import PaneFrame, ClippingCubeFactory


class ROICubeFactory(ClippingCubeFactory.ClippingCubeFactory):

    def __init__(self):
        ClippingCubeFactory.ClippingCubeFactory.__init__(self)

        self._moving = False

        self._ROIBounds = None
        self.GetFaceProperty().SetRepresentationToSurface()
        self.GetFaceProperty().SetColor(1.0, 1.0, 0.0)
        self.GetEdgeProperty().SetColor(1.0, 1.0, 0.0)

        self.BindEvent("<Shift-ButtonPress>", self.DoStartAction)
        self.BindEvent("<Shift-ButtonRelease>", self.DoEndAction)
        self.BindEvent("<Shift-Motion>", self.DoTranslate)

        # code to highlight object when user selects it
        self._HighlightFaceProperty = vtk.vtkProperty()
        self._HighlightFaceProperty.SetOpacity(0.5)
        self._HighlightFaceProperty.SetRepresentationToSurface()
        self._HighlightFaceProperty.SetColor(1.0, 0.0, 0.0)

        self._visibility = True

    def _SetVerticesFromROIBounds(self):
        bounds = self._ROIBounds
        vertices = self._Vertices
        for i in range(8):
            for j in range(3):
                if (i % (2 ** (j + 1)) < 2 ** j):
                    inc = 0
                else:
                    inc = 1
                vertices[i][j] = bounds[2 * j + inc]

    def _SetROIBoundsFromVertices(self):

        p = self._Vertices[0]
        q = self._Vertices[7]
        self._ROIBounds = (p[0], q[0],
                           p[1], q[1],
                           p[2], q[2])

    def SetBounds(self, bounds):
        """over ride parent method."""

        assert(isinstance(bounds, tuple))

        x0, x1, y0, y1, z0, z1 = bounds
        bounds = (min(x0, x1), max(x0, x1),
                  min(y0, y1), max(y0, y1),
                  min(z0, z1), max(z0, z1))
        self._Bounds = tuple(bounds)
       # self._SetVerticesFromBounds()
        # self._ResetPlanes()

    def SetROIBounds(self, bounds):

        assert(isinstance(bounds, tuple))

        if self._ROIBounds == bounds:
            return

        self._ROIBounds = bounds
        self._SetVerticesFromROIBounds()
        self._ResetPlanes()
        self.Modified()
        PaneFrame.RenderAll()

    def HandleEvent(self, evt):

        if evt.type == 7:
            self.DoEnter(evt)
        elif evt.type == 8:
            self.DoLeave(evt)
        else:
            ClippingCubeFactory.ClippingCubeFactory.HandleEvent(self, evt)

    def DoEnter(self, evt):
        self._oldwidth = self._EdgeProperty.GetLineWidth()
        self._EdgeProperty.SetLineWidth(self._oldwidth * 1.5)

    def DoLeave(self, evt):
        self._EdgeProperty.SetLineWidth(self._oldwidth)

    def DoStartAction(self, evt):
        """Override parent method to highlight cube face"""
        index = list(self._ActorDict[evt.renderer]).index(evt.actor)
        self._ActorDict[evt.renderer][
            index].SetProperty(self._HighlightFaceProperty)
        if evt.state & 1:
            self._moving = True
            index = [1, 0, 3, 2, 5, 4][index]
            self._ActorDict[evt.renderer][
                index].SetProperty(self._HighlightFaceProperty)
        else:
            self._moving = False
        ClippingCubeFactory.ClippingCubeFactory.DoStartAction(self, evt)

        # invoke an event to notify the observers.
        self._MTime.InvokeEvent('StartAction')

    def DoEndAction(self, evt):
        """Override parent method to invoke ModifiedEvent."""
        index = list(self._ActorDict[evt.renderer]).index(evt.actor)
        self._ActorDict[evt.renderer][index].SetProperty(self._FaceProperty)
        if self._moving:
            self._moving = False
            index = [1, 0, 3, 2, 5, 4][index]
            self._ActorDict[evt.renderer][
                index].SetProperty(self._FaceProperty)
        ClippingCubeFactory.ClippingCubeFactory.DoEndAction(self, evt)

        # update self._ROIBounds
        self._SetROIBoundsFromVertices()

        # invoke an event to notify the observers.
        self._MTime.InvokeEvent('EndAction')

    def DoTranslate(self, evt):
        if self._Plane is None:
            return

        renderer = evt.renderer
        camera = renderer.GetActiveCamera()

        # find intersection of viewing ray with the plane
        lx, ly, lz = self._Plane.IntersectWithViewRay(self._LastX,
                                                      self._LastY,
                                                      renderer)

        # find depth-buffer value for point
        renderer.SetWorldPoint(lx, ly, lz, 1.0)
        renderer.WorldToDisplay()
        z = renderer.GetDisplayPoint()[2]

        # and use it to find the world coords of current x,y coord
        # (i.e. the mouse moves solely in x,y plane)
        renderer.SetDisplayPoint(evt.x, evt.y, z)
        renderer.DisplayToWorld()
        wx, wy, wz, w = renderer.GetWorldPoint()
        wx, wy, wz = (wx / w, wy / w, wz / w)

        # mouse motion vector, in world coords
        dx, dy, dz = (wx - lx, wy - ly, wz - lz)

        # check to make sure that plane is not facing camera (use untransformed
        # here)
        nx, ny, nz = self._Plane.GetNormal()

        vx, vy, vz = camera.GetViewPlaneNormal()
        n_dot_v = nx * vx + ny * vy + nz * vz

        if (abs(n_dot_v) < 0.9):
            # drag plane to exactly match cursor motion
            dd = (dx * (nx - vx * n_dot_v) + dy * (ny - vy * n_dot_v) + dz * (nz - vz * n_dot_v)) / \
                 (1.0 - n_dot_v * n_dot_v)
        else:
            # plane is perpendicular to viewing ray, so just push by distance
            dd = math.sqrt(dx * dx + dy * dy + dz * dz)
            if (evt.x + evt.y - self._LastX - self._LastY < 0):
                dd = -dd

        trans = (dd * nx, dd * ny, dd * nz)
        vertices = self._Vertices
        for vertex in self._Vertices:
            for i in range(3):
                vertex[i] = vertex[i] + trans[i]

        self._LastX = evt.x
        self._LastY = evt.y

        self._ResetPlanes()
        self.Modified()

    def GetROIBounds(self):
        return self._ROIBounds

    def SetEdgeOpacity(self, opacity):
        self._EdgeProperty.SetOpacity(opacity)
        self.Modified()

    def SetCubeOpacity(self, opacity):
        self._FaceProperty.SetOpacity(opacity)
        self.Modified()

    def SetVisibility(self, yesno, renderer=None):

        self._visibility = yesno

        if renderer is None:
            renderers = self._Renderers
        else:
            renderers = [renderer, ]

        for ren in renderers:
            for actor in self._ActorDict[ren]:
                actor.SetVisibility(yesno)

        self.Modified()

    def SetEdgeVisibility(self, yesno, renderer=None):
        if renderer is None:
            renderers = self._Renderers
        else:
            renderers = [renderer, ]

        for ren in renderers:
            for i in range(6):
                self._ActorDict[ren][i].SetVisibility(yesno)

        self.Modified()

    def SetEdgeVisibility(self, yesno, renderer=None):
        if renderer is None:
            renderers = self._Renderers
        else:
            renderers = [renderer, ]

        for ren in renderers:
            for i in range(12):
                self._ActorDict[ren][i + 6].SetVisibility(yesno)

        self.Modified()

    def _MakeActors(self):
        actors = ClippingCubeFactory.ClippingCubeFactory._MakeActors(self)
        actors[0].SetVisibility(self._visibility)
        return actors
