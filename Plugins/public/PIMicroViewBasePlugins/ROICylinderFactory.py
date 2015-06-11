import vtk
from vtkAtamai import ActorFactory


class ROICylinderFactory(ActorFactory.ActorFactory):

    def __init__(self):
        ActorFactory.ActorFactory.__init__(self)

        # share property across all the actors
        self._cylinder = vtk.vtkCylinderSource()
        self._cylinder.SetResolution(40)
        self._cylinder.CappingOn()

        self._Property = vtk.vtkProperty()
        self._Property.SetColor(1, 1, 0)

        self._bounds = (-1, 1, -1, 1, -1, 1)
        self._orientation = 'z'
# self.GetTransform().RotateX(90)
        self._visibility = True

    def SetROIBounds(self, bounds):
        """Set the bounds that defines the cylinder."""

        self._bounds = bounds
        self._Update()

    def _Update(self):
        """Update cylinder to fit into the new bounding box,
        according to the orientation.
        """
        x0, x1, y0, y1, z0, z1 = self._bounds
        # cylinder parameters
        if self._orientation == 'x':
            height = (x1 - x0)
            radius = (y1 - y0) * 0.5
            if y1 - y0 == 0:
                return
            scale = (z1 - z0) / (y1 - y0)
        elif self._orientation == 'y':
            height = (y1 - y0)
            radius = (x1 - x0) * 0.5
            if x1 - x0 == 0:
                return
            scale = (z1 - z0) / (x1 - x0)
        else:
            height = (z1 - z0)
            radius = (x1 - x0) * 0.5
            if x1 - x0 == 0:
                return
            scale = (y1 - y0) / (x1 - x0)

        self._cylinder.SetRadius(radius)
        self._cylinder.SetHeight(height)
        self._cylinder.Update()

        # the center of the cylinder
        center = ((x1 + x0) * 0.5,
                  (y1 + y0) * 0.5,
                  (z1 + z0) * 0.5)
        self._UpdateTransform((1, 1, scale), center)

    def GetOrientation(self):
        return self._orientation

    def SetOrientationToX(self):
        """Set the cylinder axis to align with x axis."""
        self._orientation = 'x'
        self.Modified()

    def SetOrientationToY(self):
        """Set the cylinder axis to align with y axis, which is
        the orientation of vtkCylinderSource.
        """
        self._orientation = 'y'
        self.Modified()

    def SetOrientationToZ(self):
        """Set the cylinder axis to align with z axis."""
        self._orientation = 'z'
        self.Modified()

    def _UpdateTransform(self, scale, center):

        self.GetTransform().Identity()
        self.GetTransform().Translate(center)

        if self._orientation == 'x':
            self.GetTransform().RotateZ(90)
        elif self._orientation == 'y':
            pass
        elif self._orientation == 'z':
            self.GetTransform().RotateX(90)

        self.GetTransform().Scale(scale)
        self.Modified()

    def GetPolyData(self):
        """Return a vtkPolyData that bounding the ROI."""

        trans = vtk.vtkTransformPolyDataFilter()
        trans.SetInput(self._cylinder.GetOutput())
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
        mapper.SetInputConnection(self._cylinder.GetOutputPort())
        actor.SetMapper(mapper)
        self._Actor = actor
        return actor
