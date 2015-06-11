import vtk
import math
from vtkAtamai import ActorFactory


class ROIIntersectionsFactory(ActorFactory.ActorFactory):

    """
    Intersections to be displayed on 2D renderpanes.
    This class has not been used yet, but keep here
    for development at next stage.
    """

    def __init__(self):
        ActorFactory.ActorFactory.__init__(self)
        self._Cutters = []
        self._Cube = None
        self._Plane = None
        self._properties = []

    def SetPlanes(self, planes):
        """Set a set of SlicePlaneFactory."""
        self._Planes = planes
        self._properties = []
        for i in range(len(self._Planes)):
            self._properties.append(vtk.vtkProperty())
        self._UpdateIntersections()

    def SetCubeSource(self, cube):
        self._Cube = cube
        self._UpdateIntersections()

    def _UpdateIntersections(self):
        if self._Planes is None:
            return
        if self._Cube is None:
            return

        self._Cutters = []
        for plane in self._Planes:
            cutter = vtk.vtkCutter()
            cutter.SetCutFunction(plane.GetPlaneEquation())
            cutter.SetInput(self._Cube.GetOutput())
            self._Cutters.append(cutter)

    def AddToRenders(self, renders):
        i = 0
        for cutter in range(len(self._Cutters)):
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInput(cutter.GetOutput())
            actor = self._NewActor()
            actor.SetProperty(self._properties[i])
            i += 1
            actor.SetMapper(mapper)
            self.AddChild(actor)

    def SetColor(self, *args):
        apply(self._Property.SetColor, args)

    def GetColor(self):
        return self._Property.GetColor()

    def HasChangedSince(self, sinceMTime):
        if ActorFactory.ActorFactory.HasChangedSince(self, sinceMTime):
            return 1

        for plane in self._Planes:
            if plane.HasChangedSince(sinceMTime):
                return 1
            if self._Property.GetMTime() > sinceMTime:
                return 1
        return 0

    def SetVisibility(self, yesno, renderer=None):
        if renderer is None:
            renderers = self._Renderers
        else:
            renderers = [renderer, ]

        for ren in renderers:
            for actor in self._ActorDict[ren]:
                actor.SetVisibility(yesno)

    def GetProperty(self):
        return self._Property

    def AddToRenderer(self, ren):
        ActorFactory.ActorFactory.AddToRenderer(self, ren)
        try:
            ren.AddObserver('StartEvent', self.OnRenderEvent)
        except:
            pass

    def OnRenderEvent(self, ren, evt):
        camera = ren.GetActiveCamera()
        v = camera.GetViewPlaneNormal()

        if camera.GetParallelProjection():
            d = camera.GetParallelScale() / 100
        else:
            d = camera.GetDistance() * \
                math.sin(camera.GetViewAngle() / 360.0 * math.pi) / \
                100

        v = self._Transform.GetInverse().TransformVector(
            v[0] * d, v[1] * d, v[2] * d)
        for actor in self._ActorDict[ren]:
            actor.SetPosition(v[0], v[1], v[2])

    def _MakeActors(self):
        actors = []

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self._Append.GetOutputPort())
        actor = self._NewActor()
        actor.SetProperty(self._Property)
        actor.SetMapper(mapper)
        actors.append(actor)

        return actors
