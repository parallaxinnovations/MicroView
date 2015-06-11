# =========================================================================
#
# Copyright (c) 2011-2015 Parallax Innovations Inc.
#
# =========================================================================


"""
A class for showing a 3D path.

Derived From:

  ActorFactor

"""

import math
import vtk
from vtkAtamai import ActorFactory


class PathFactory(ActorFactory.ActorFactory):

    def __init__(self):
        ActorFactory.ActorFactory.__init__(self)

        # Create a green line
        self._Points = vtk.vtkPoints()
        self._Lines = vtk.vtkCellArray()
        self._Poly = vtk.vtkPolyData()

        self._Poly.SetPoints(self._Points)
        self._Poly.SetLines(self._Lines)

        self._PathProperty = vtk.vtkProperty()
        self._PathProperty.SetColor(0, 1, 0)
        self._PathProperty.SetOpacity(0.0)

        # turn the line into a cylinder
        self._tube = vtk.vtkTubeFilter()

        # VTK-6
        if vtk.vtkVersion().GetVTKMajorVersion() > 5:
            self._tube.SetInputData(self._Poly)
        else:
            self._tube.SetInput(self._Poly)

        self._tube.SetNumberOfSides(3)
        self._tube.SetRadius(2.5)

    def Modified(self):
        self._tube.Modified()
        ActorFactory.ActorFactory.Modified(self)

    def AddPoint(self, point):
        self._Points.InsertNextPoint(*point)
        self.updateCellInfo()

    def updateCellInfo(self):

        num = self._Points.GetNumberOfPoints()

        # recreate cell info
        self._Lines.Reset()
        if num > 1:
            self._Lines.InsertNextCell(num)
            for i in range(num):
                self._Lines.InsertCellPoint(i)

        self.Modified()

    def UpdatePoint(self, index, point):
        self._Points.SetPoint(index, *point)
        self.Modified()

    def DeletePoint(self, idx):

        # we must recreate things here
        points = vtk.vtkPoints()
        num = self._Points.GetNumberOfPoints()
        for i in range(num):
            if i != idx:
                point = self._Points.GetPoint(i)
                points.InsertNextPoint(point)

        self._Points = points
        self._Poly.SetPoints(self._Points)

        self.updateCellInfo()

    def DeleteAll(self):
        self._Points.Reset()
        self.updateCellInfo()

    def tearDown(self):

        ActorFactory.ActorFactory.tearDown(self)

        self.RemoveAllObservers()
        self.RemoveAllEventHandlers()

        del self._Points
        del self._Lines
        del self._Poly
        del self._PathProperty
        del self._tube

    # Hide the path.
    def ClearPath(self):
        self._PathProperty.SetOpacity(0)
        self.Modified()

    def SetPathOpacity(self, opacity):
        self._PathProperty.SetOpacity(opacity)
        self.Modified()

    def GetPathOpacity(self):
        return self._PathProperty.GetOpacity()

    def _MakeActors(self):
        actor = self._NewActor()
        actor.SetProperty(self._PathProperty)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self._tube.GetOutputPort())
        actor.SetMapper(mapper)
        return [actor]

    def AddToRenderer(self, renderer):
        ActorFactory.ActorFactory.AddToRenderer(self, renderer)
        renderer.AddObserver('StartEvent', self.OnRenderEvent)

    def OnRenderEvent(self, renderer, event):
        """Update scale for path actor"""

        p1 = [0, 0, 0]
        p2 = [1, 1, 1]
        x, y, z = (0.5 * (p1[0] + p2[0]),
                   0.5 * (p1[1] + p2[1]),
                   0.5 * (p1[2] + p2[2]))
        camera = renderer.GetActiveCamera()
        if camera.GetParallelProjection():
            world_size = camera.GetParallelScale()
        else:
            cx, cy, cz = camera.GetPosition()
            d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2)
            world_size = 2 * d * math.tan(0.5 * camera.GetViewAngle() / 57.296)
        windowWidth, windowHeight = renderer.GetSize()

        if windowWidth > 0 and windowHeight > 0:
            pitch = world_size / windowHeight
            self._tube.SetRadius(pitch)
