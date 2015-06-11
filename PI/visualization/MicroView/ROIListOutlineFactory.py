import vtk
from vtkAtamai import ActorFactory, OutlineFactory

#
# A collection of rectangular outlines, appropriate for defining multiple ROIs
#


class ROIListOutlineFactory(ActorFactory.ActorFactory):

    def __init__(self):

        ActorFactory.ActorFactory.__init__(self)

        self.sourceList = []                        # list of cube sources
        self.outlineList = []                       # outlines of the cubes

    def GetNumberOfROIs(self):
        return len(self.sourceList)

    def getROIWidths(self, index):
        try:
            cube = self.sourceList[index]
            return [cube.GetXLength(), cube.GetYLength(), cube.GetZLength()]
        except:
            return [-1, -1, -1]

    def AddROI(self, position, _size):
        """Add a new ROI"""

        cube = vtk.vtkCubeSource()
        cube.SetXLength(_size[0])
        cube.SetYLength(_size[1])
        cube.SetZLength(_size[2])
        cube.SetCenter(position)

        outline = OutlineFactory.OutlineFactory()
        outline.SetInputData(cube.GetOutput())

        self.sourceList.append(cube)
        self.outlineList.append(outline)

        self.AddChild(outline)
        self.Modified()

    def updateROI(self, index, position, _size):

        try:
            cube = self.sourceList[index]
        except IndexError:
            return self.AddROI(position, _size)

        outline = self.outlineList[index]

        cube.SetCenter(position)
        cube.SetXLength(_size[0])
        cube.SetYLength(_size[1])
        cube.SetZLength(_size[2])

        self.Modified()

    def SetROIVisibility(self, visible):

        for outline in self.outlineList:
            outline.SetVisibility(visible)

        self.Modified()

    def DeleteAll(self):

        for outline in self.outlineList:
            self.RemoveChild(outline)

        self.sourceList = []
        self.outlineList = []
