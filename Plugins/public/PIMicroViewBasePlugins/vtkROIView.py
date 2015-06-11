import vtk
import logging

from vtkAtamai import SphereMarkFactory

import ROICubeFactory
import ROICylinderFactory
import ROISphereFactory


class vtkROIView(object):

    """A class that manages three separate VTK ROI actors - a box, a spheroid and a cylinder"""

    def __init__(self):

        self._ROIVisibility = False
        self._ROIStencil = None
        self._IgnoreResetPoints = False
        self._Objects3D = []
        self.bIsConnected = False

        self._Math = vtk.vtkMath()
        self.__Cube = ROICubeFactory.ROICubeFactory()
        self.__Cylinder = ROICylinderFactory.ROICylinderFactory()
        self.__Sphere = ROISphereFactory.ROISphereFactory()

        self.__Cube.SetVisibility(True)
        self.__Cylinder.SetVisibility(False)
        self.__Sphere.SetVisibility(False)

        # two marks for visual cues for key 7 and 8
        self._Mark = []
        for i in range(2):
            m = SphereMarkFactory.SphereMarkFactory()
            m.SetColor(1.0, 1.0, 0.0)
            m.SetSize(10.)
            m.SetOpacity(0.)
            self._Mark.append(m)

        self._Objects3D.append(self.__Cylinder)
        self._Objects3D.append(self.__Cube)
        self._Objects3D.append(self.__Sphere)
        self._Objects3D.append(self._Mark[0])
        self._Objects3D.append(self._Mark[1])

        # Bind some events
        self.__Cube.AddObserver('StartAction', self.onStartAction)

    def GetCube(self):
        return self.__Cube

    def GetCylinder(self):
        return self.__Cylinder

    def GetSphere(self):
        return self.__Sphere

    def SetTransform(self, t):
        self.__Cube.GetTransform().SetInput(t)
        self.__Cylinder.GetTransform().SetInput(t)
        self.__Sphere.GetTransform().SetInput(t)

    def SetInput(self, input):
        x0, x1, y0, y1, z0, z1 = input.GetBounds()
        bounds = (min(x0, x1), max(x0, x1),
                  min(y0, y1), max(y0, y1),
                  min(z0, z1), max(z0, z1))

        # set maximum boundary on cube ROI
        self.__Cube.SetBounds(bounds)

    def IsConnected(self):
        return self.bIsConnected

    def Connect3DActorFactories(self, pane):

        for factory in self._Objects3D:
            pane.ConnectActorFactory(factory)

        self.bIsConnected = True

    def Disconnect3DActorFactories(self, pane):

        for factory in self._Objects3D:
            pane.DisconnectActorFactory(factory)

        self.bIsConnected = False

    def setViewROIBounds(self, bounds):

        assert(isinstance(bounds, tuple))

        # set model bounds
        self.__Cube.SetROIBounds(bounds)
        self.__Cylinder.SetROIBounds(bounds)
        self.__Sphere.SetROIBounds(bounds)

    def setViewROIControlPoints(self, points):

        assert(isinstance(points, tuple))

        for i in range(2):
            if points[i] is not None:
                self._Mark[i].SetOpacity(1.0)
                self._Mark[i].SetPosition(points[i])
            else:
                self._Mark[i].SetOpacity(0.0)

    def GetROIVisibility(self):
        return self._ROIVisibility

    def DisableROI(self):

        # hide actors
        self._ROIVisibility = False
        self.__Cylinder.SetVisibility(0)
        self.__Sphere.SetVisibility(0)
        self.__Cube.SetVisibility(0)
        self.__Cube.SetPickable(0)
        self._Mark[0].SetOpacity(0.0)
        self._Mark[1].SetOpacity(0.0)

        # clear setting
        self._ROIStencil = None

    def ShowROI(self, roi_type):
        """Show cube or cylinder according to ToolVar value.
        Also enable the interaction to the cube actor, and
        also fire up an EnableEvent.

        roi_type:
            1 -> Cube
            2 -> Cylinder
            3 -> Sphere
        """

        self._ROIVisibility = True
        self._Mark[0].SetOpacity(0.0)
        self._Mark[1].SetOpacity(0.0)

        if roi_type == 'box':
            self.__Cube.SetVisibility(1)
            self.__Cylinder.SetVisibility(0)
            self.__Sphere.SetVisibility(0)
            self.__Cube.SetOpacity(0.5)
            self.__Cube.SetEdgeOpacity(0.8)
            self.__Cube.SetPickable(1)
        elif roi_type == 'cylinder':
            self.__Cube.SetVisibility(0)
            self.__Cylinder.SetVisibility(1)
            self.__Sphere.SetVisibility(0)
            self.__Cylinder.SetOpacity(0.5)
        elif roi_type == 'ellipsoid':
            self.__Cube.SetVisibility(0)
            self.__Cylinder.SetVisibility(0)
            self.__Sphere.SetVisibility(1)
            self.__Sphere.SetOpacity(0.5)
        else:
            logging.warning('ShowROI: unknown ROI "%s"' % roi_type)

    def onStartAction(self, obj, evt):
        """Respond to user manipulating cube with middle mouse button"""

        # hide markers
        for i in range(2):
            self._Mark[i].SetOpacity(0.0)
