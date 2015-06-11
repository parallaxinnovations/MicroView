import ViewerState
import vtk
from vtk.wx import wxVTKRenderWindow
from PI.visualization.MicroView.interfaces import IViewer
from zope import interface


class SliceViewportManager(wxVTKRenderWindow.wxVTKRenderWindow):

    interface.implements(IViewer)

    def Freeze2(self):
        # TODO: implement me
        pass

    def Thaw2(self):
        # TODO: implement me
        pass

    def __init__(self, parent, **kw):
        self._index = kw.get('index', 0)
        self._viewerState = ViewerState.ViewerState()
        wxVTKRenderWindow.wxVTKRenderWindow.__init__(self, parent, -1)

        # Add some dummy objects etc.
        ren = vtk.vtkRenderer()
        self.GetRenderWindow().AddRenderer(ren)

        cone = vtk.vtkConeSource()
        cone.SetResolution(8)

        coneMapper = vtk.vtkPolyDataMapper()
        coneMapper.SetInputConnection(cone.GetOutputPort())

        coneActor = vtk.vtkActor()
        coneActor.SetMapper(coneMapper)

        ren.AddActor(coneActor)

    def GetImageIndex(self):
        return self._index

    def GetPageState(self):
        return self._viewerState

    def SetViewTo1Side3(self, *args, **kw):
        pass
