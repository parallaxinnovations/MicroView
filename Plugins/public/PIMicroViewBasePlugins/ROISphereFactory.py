import vtk
from vtkAtamai import ActorFactory


class ROISphereFactory(ActorFactory.ActorFactory):

    def __init__(self):
        ActorFactory.ActorFactory.__init__(self)

        # share property across all the actors
        self._sphere = vtk.vtkSphereSource()
        self._sphere.SetThetaResolution(40)
        self._sphere.SetPhiResolution(40)
        self._visibility = True

        self._Property = vtk.vtkProperty()
        self._Property.SetColor(1, 1, 0)

        self._bounds = (-1, 1, -1, 1, -1, 1)

    def SetROIBounds(self, bounds):
        """Set the bounds that defines the ellipsoid."""

        self._bounds = bounds
        self._Update()

    def _Update(self):
        """Update ellipsoid to fit into the new bounding box"""
        x0, x1, y0, y1, z0, z1 = self._bounds
        self._sphere.SetRadius(1.0)

        scale0 = (x1 - x0) / 2.0
        scale1 = (y1 - y0) / 2.0
        scale2 = (z1 - z0) / 2.0

        self._sphere.Update()

        # the center of the ellipsoid
        center = ((x1 + x0) * 0.5,
                  (y1 + y0) * 0.5,
                  (z1 + z0) * 0.5)
        self._UpdateTransform((scale0, scale1, scale2), center)

    def GetOrientation(self):
        return self._orientation

    def _UpdateTransform(self, scale, center):
        self.GetTransform().Identity()
        self.GetTransform().Translate(center)
        self.GetTransform().Scale(scale)
        self.Modified()

    def GetPolyData(self):
        """Return a vtkPolyData that bounding the ROI."""

        trans = vtk.vtkTransformPolyDataFilter()
        trans.SetInput(self._sphere.GetOutput())
        trans.SetTransform(self.GetTransform())
        return trans.GetOutput()

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

    def SetOpacity(self, theOpacity):
        self._Property.SetOpacity(theOpacity)
        self.Modified()

    def GetOpacity(self):
        return self._Property.GetOpacity()

    def SetColor(self, *args):
        apply(self._Property.SetColor, args)
        self.Modified()

    def GetColor(self):
        return self._Property.GetColor()

    def GetActor(self):
        return self._Actor

    def _MakeActors(self):
        actor = self._NewActor()
        actor.SetProperty(self._Property)
        actor.SetVisibility(self._visibility)
        return [actor]

    def _NewActor(self):
        actor = ActorFactory.ActorFactory._NewActor(self)
        actor.PickableOff()
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self._sphere.GetOutputPort())
        actor.SetMapper(mapper)
        self._Actor = actor
        return actor
