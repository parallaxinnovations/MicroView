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
#    form, must retain the above copyright notice, this license,
#    the following disclaimer, and any notices that refer to this
#    license and/or the following disclaimer.
#
# 2) Redistribution in binary form must include the above copyright
#    notice, a copy of this license and the following disclaimer
#    in the documentation or with other materials provided with the
#    distribution.
#
# 3) Modified copies of the source code must be clearly marked as such,
#    and must not be misrepresented as verbatim copies of the source code.
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
Displays arrows and lines indicating where the planes intersect.

Derived From:

  ActorFactory

See Also:

  MicroViewRenderPane, OrthoPlanesFactory, RenderPane2D, SlicePlaneFactory

Parameters:

  plane      - the plane displayed in this viewport

  planes     - all three planes
"""

from vtkAtamai.ActorFactory import *
import math


class PlaneIntersectionFactory(ActorFactory):

    def __init__(self, plane, planes):
        ActorFactory.__init__(self)

        self._Plane = plane
        self._Planes = planes

        self._xcolor = (1, 0, 0)
        self._ycolor = (0, 1, 0)
        self._zcolor = (0, 0, 1)

        self._TrianglePoints = []
        self._Triangle = []
        self._TriangleGrid = []
        self._TriangleProperty = []

        for i in range(4):
            TrianglePoints = vtk.vtkPoints()
            self._TrianglePoints.append(TrianglePoints)
            self._TrianglePoints[i].SetNumberOfPoints(3)
            for j in range(3):
                self._TrianglePoints[i].InsertPoint(j, 0, 0, 0)

            Triangle = vtk.vtkTriangle()
            self._Triangle.append(Triangle)
            for j in range(3):
                self._Triangle[i].GetPointIds().SetId(j, j)

            TriangleGrid = vtk.vtkPolyData()
            self._TriangleGrid.append(TriangleGrid)
            self._TriangleGrid[i].Allocate(1, 1)
            self._TriangleGrid[i].InsertNextCell(
                self._Triangle[i].GetCellType(),
                self._Triangle[i].GetPointIds())
            self._TriangleGrid[i].SetPoints(self._TrianglePoints[i])

            # TriangleProperty = vtk.vtkProperty()
            TriangleProperty = vtk.vtkProperty2D()
            self._TriangleProperty.append(TriangleProperty)
            self._TriangleProperty[i].SetOpacity(0.75)

        self._LinePoints = []
        self._Line = []
        self._LineGrid = []
        self._LineProperty = []
        self._LineOpacity = 0

        for i in range(2):
            LinePoints = vtk.vtkPoints()
            self._LinePoints.append(LinePoints)
            self._LinePoints[i].SetNumberOfPoints(2)
            self._LinePoints[i].InsertPoint(0, 0, 0, 0)
            self._LinePoints[i].InsertPoint(1, 0, 0, 0)

            Line = vtk.vtkLine()
            self._Line.append(Line)
            self._Line[i].GetPointIds().SetId(0, 0)
            self._Line[i].GetPointIds().SetId(1, 1)

            LineGrid = vtk.vtkPolyData()
            self._LineGrid.append(LineGrid)
            self._LineGrid[i].Allocate(1, 1)
            self._LineGrid[i].InsertNextCell(self._Line[i].GetCellType(),
                                             self._Line[i].GetPointIds())
            self._LineGrid[i].SetPoints(self._LinePoints[i])

            LineProperty = vtk.vtkProperty2D()
            self._LineProperty.append(LineProperty)
            self._LineProperty[i].SetOpacity(self._LineOpacity)

    def SetXColor(self, color):
        self._xcolor = color

    def SetYColor(self, color):
        self._ycolor = color

    def SetZColor(self, color):
        self._zcolor = color

    # Draw the arrows and axes.
    def UpdatePlaneIntersections(self, renderer):
        x = self._Planes.GetSagittalPlane().GetSlicePosition()
        y = self._Planes.GetCoronalPlane().GetSlicePosition()
        z = self._Planes.GetAxialPlane().GetSlicePosition()

        # Draw the arrows
        if (self._Plane == self._Planes.GetAxialPlane()):
            # make sure the left arrow stays within the viewport
            bp1 = [self._Extent[0] * self._Spacing[0] + self._Origin[0], y, z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp1[0], bp1[1], bp1[2], 1.0)
            p1 = self._Transform.GetMatrix().MultiplyPoint(
                (bp1[0], bp1[1], bp1[2], 1.0))

            renderer.SetWorldPoint(p1[0], p1[1], p1[2], 1.0)
            renderer.WorldToDisplay()
            dp1 = renderer.GetDisplayPoint()

            if (dp1[0] >= 10):
                self._TrianglePoints[0].InsertPoint(0, dp1[0], dp1[1], 0)
                self._TrianglePoints[0].InsertPoint(
                    1, dp1[0] - 10, dp1[1] + 5, 0)
                self._TrianglePoints[0].InsertPoint(
                    2, dp1[0] - 10, dp1[1] - 5, 0)
            else:
                self._TrianglePoints[0].InsertPoint(0, 10, dp1[1], 0)
                self._TrianglePoints[0].InsertPoint(1, 0, dp1[1] + 5, 0)
                self._TrianglePoints[0].InsertPoint(2, 0, dp1[1] - 5, 0)
            self._TriangleProperty[0].SetColor(self._ycolor)  # 0.0,1.0,0.0)

            # make sure the right arrow stays within the viewport
            bp2 = [self._Extent[1] * self._Spacing[0] + self._Origin[0], y, z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp2[0], bp2[1], bp2[2], 1.0)
            p2 = self._Transform.GetMatrix().MultiplyPoint(
                (bp2[0], bp2[1], bp2[2], 1.0))

            renderer.SetWorldPoint(p2[0], p2[1], p2[2], 1.0)
            renderer.WorldToDisplay()
            dp2 = renderer.GetDisplayPoint()

            if (dp2[0] <= (self._viewsize[0] - 10)):
                self._TrianglePoints[1].InsertPoint(0, dp2[0], dp2[1], 0)
                self._TrianglePoints[1].InsertPoint(
                    1, dp2[0] + 10, dp2[1] - 5, 0)
                self._TrianglePoints[1].InsertPoint(
                    2, dp2[0] + 10, dp2[1] + 5, 0)
            else:
                self._TrianglePoints[1].InsertPoint(
                    0, self._viewsize[0] - 10, dp2[1], 0)
                self._TrianglePoints[1].InsertPoint(
                    1, self._viewsize[0], dp2[1] - 5, 0)
                self._TrianglePoints[1].InsertPoint(
                    2, self._viewsize[0], dp2[1] + 5, 0)
            self._TriangleProperty[1].SetColor(self._ycolor)

            # make sure the bottom arrow stays within the viewport
            bp3 = [x, self._Extent[2] * self._Spacing[1] + self._Origin[1], z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp3[0], bp3[1], bp3[2], 1.0)
            p3 = self._Transform.GetMatrix().MultiplyPoint(
                (bp3[0], bp3[1], bp3[2], 1.0))

            renderer.SetWorldPoint(p3[0], p3[1], p3[2], 1.0)
            renderer.WorldToDisplay()
            dp3 = renderer.GetDisplayPoint()

            if (dp3[1] >= 10):
                self._TrianglePoints[2].InsertPoint(0, dp3[0], dp3[1], 0)
                self._TrianglePoints[2].InsertPoint(
                    1, dp3[0] - 5, dp3[1] - 10, 0)
                self._TrianglePoints[2].InsertPoint(
                    2, dp3[0] + 5, dp3[1] - 10, 0)
            else:
                self._TrianglePoints[2].InsertPoint(0, dp3[0], 10, 0)
                self._TrianglePoints[2].InsertPoint(1, dp3[0] - 5, 0, 0)
                self._TrianglePoints[2].InsertPoint(2, dp3[0] + 5, 0, 0)
            self._TriangleProperty[2].SetColor(self._xcolor)

            # make sure the top arrow stays within the viewport
            bp4 = [x, self._Extent[3] * self._Spacing[1] + self._Origin[1], z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp4[0], bp4[1], bp4[2], 1.0)
            p4 = self._Transform.GetMatrix().MultiplyPoint(
                (bp4[0], bp4[1], bp4[2], 1.0))

            renderer.SetWorldPoint(p4[0], p4[1], p4[2], 1.0)
            renderer.WorldToDisplay()
            dp4 = renderer.GetDisplayPoint()

            if (dp4[1] <= (self._viewsize[1] - 10)):
                self._TrianglePoints[3].InsertPoint(0, dp4[0], dp4[1], 0)
                self._TrianglePoints[3].InsertPoint(
                    1, dp4[0] + 5, dp4[1] + 10, 0)
                self._TrianglePoints[3].InsertPoint(
                    2, dp4[0] - 5, dp4[1] + 10, 0)
            else:
                self._TrianglePoints[3].InsertPoint(
                    0, dp4[0], self._viewsize[1] - 10, 0)
                self._TrianglePoints[3].InsertPoint(
                    1, dp4[0] + 5, self._viewsize[1], 0)
                self._TrianglePoints[3].InsertPoint(
                    2, dp4[0] - 5, self._viewsize[1], 0)
            self._TriangleProperty[3].SetColor(self._xcolor)

        elif (self._Plane == self._Planes.GetCoronalPlane()):
            # make sure the left arrow stays within the viewport
            bp1 = [self._Extent[0] * self._Spacing[0] + self._Origin[0], y, z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp1[0], bp1[1], bp1[2], 1.0)
            p1 = self._Transform.GetMatrix().MultiplyPoint(
                (bp1[0], bp1[1], bp1[2], 1.0))

            renderer.SetWorldPoint(p1[0], p1[1], p1[2], 1.0)
            renderer.WorldToDisplay()
            dp1 = renderer.GetDisplayPoint()

            if (dp1[0] >= 10):
                self._TrianglePoints[0].InsertPoint(0, dp1[0], dp1[1], 0)
                self._TrianglePoints[0].InsertPoint(
                    1, dp1[0] - 10, dp1[1] + 5, 0)
                self._TrianglePoints[0].InsertPoint(
                    2, dp1[0] - 10, dp1[1] - 5, 0)
            else:
                self._TrianglePoints[0].InsertPoint(0, 10, dp1[1], 0)
                self._TrianglePoints[0].InsertPoint(1, 0, dp1[1] + 5, 0)
                self._TrianglePoints[0].InsertPoint(2, 0, dp1[1] - 5, 0)
            self._TriangleProperty[0].SetColor(self._zcolor)

            # make sure the right arrow stays within the viewport
            bp2 = [self._Extent[1] * self._Spacing[0] + self._Origin[0], y, z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp2[0], bp2[1], bp2[2], 1.0)
            p2 = self._Transform.GetMatrix().MultiplyPoint(
                (bp2[0], bp2[1], bp2[2], 1.0))

            renderer.SetWorldPoint(p2[0], p2[1], p2[2], 1.0)
            renderer.WorldToDisplay()
            dp2 = renderer.GetDisplayPoint()

            if (dp2[0] <= (self._viewsize[0] - 10)):
                self._TrianglePoints[1].InsertPoint(0, dp2[0], dp2[1], 0)
                self._TrianglePoints[1].InsertPoint(
                    1, dp2[0] + 10, dp2[1] - 5, 0)
                self._TrianglePoints[1].InsertPoint(
                    2, dp2[0] + 10, dp2[1] + 5, 0)
            else:
                self._TrianglePoints[1].InsertPoint(
                    0, self._viewsize[0] - 10, dp2[1], 0)
                self._TrianglePoints[1].InsertPoint(
                    1, self._viewsize[0], dp2[1] - 5, 0)
                self._TrianglePoints[1].InsertPoint(
                    2, self._viewsize[0], dp2[1] + 5, 0)
            self._TriangleProperty[1].SetColor(self._zcolor)

            # make sure the bottom arrow stays within the viewport
            bp3 = [x, y, self._Extent[4] * self._Spacing[2] + self._Origin[2]]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp3[0], bp3[1], bp3[2], 1.0)
            p3 = self._Transform.GetMatrix().MultiplyPoint(
                (bp3[0], bp3[1], bp3[2], 1.0))

            renderer.SetWorldPoint(p3[0], p3[1], p3[2], 1.0)
            renderer.WorldToDisplay()
            dp3 = renderer.GetDisplayPoint()

            if (dp3[1] >= 10):
                self._TrianglePoints[2].InsertPoint(0, dp3[0], dp3[1], 0)
                self._TrianglePoints[2].InsertPoint(
                    1, dp3[0] - 5, dp3[1] - 10, 0)
                self._TrianglePoints[2].InsertPoint(
                    2, dp3[0] + 5, dp3[1] - 10, 0)
            else:
                self._TrianglePoints[2].InsertPoint(0, dp3[0], 10, 0)
                self._TrianglePoints[2].InsertPoint(1, dp3[0] - 5, 0, 0)
                self._TrianglePoints[2].InsertPoint(2, dp3[0] + 5, 0, 0)
            self._TriangleProperty[2].SetColor(self._xcolor)

            # make sure top arrow  stays within the viewport
            bp4 = [x, y, self._Extent[5] * self._Spacing[2] + self._Origin[2]]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp4[0], bp4[1], bp4[2], 1.0)
            p4 = self._Transform.GetMatrix().MultiplyPoint(
                (bp4[0], bp4[1], bp4[2], 1.0))

            renderer.SetWorldPoint(p4[0], p4[1], p4[2], 1.0)
            renderer.WorldToDisplay()
            dp4 = renderer.GetDisplayPoint()

            if (dp4[1] <= (self._viewsize[1] - 10)):
                self._TrianglePoints[3].InsertPoint(0, dp4[0], dp4[1], 0)
                self._TrianglePoints[3].InsertPoint(
                    1, dp4[0] + 5, dp4[1] + 10, 0)
                self._TrianglePoints[3].InsertPoint(
                    2, dp4[0] - 5, dp4[1] + 10, 0)
            else:
                self._TrianglePoints[3].InsertPoint(
                    0, dp3[0], self._viewsize[1] - 10, 0)
                self._TrianglePoints[3].InsertPoint(
                    1, dp3[0] + 5, self._viewsize[1], 0)
                self._TrianglePoints[3].InsertPoint(
                    2, dp3[0] - 5, self._viewsize[1], 0)
            self._TriangleProperty[3].SetColor(self._xcolor)

        elif (self._Plane == self._Planes.GetSagittalPlane()):
            # make sure the left arrow stays within the viewport
            bp1 = [x, self._Extent[2] * self._Spacing[1] + self._Origin[1], z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp1[0], bp1[1], bp1[2], 1.0)
            p1 = self._Transform.GetMatrix().MultiplyPoint(
                (bp1[0], bp1[1], bp1[2], 1.0))

            renderer.SetWorldPoint(p1[0], p1[1], p1[2], 1.0)
            renderer.WorldToDisplay()
            dp1 = renderer.GetDisplayPoint()

            if (dp1[0] >= 10):
                self._TrianglePoints[0].InsertPoint(0, dp1[0], dp1[1], 0)
                self._TrianglePoints[0].InsertPoint(
                    1, dp1[0] - 10, dp1[1] + 5, 0)
                self._TrianglePoints[0].InsertPoint(
                    2, dp1[0] - 10, dp1[1] - 5, 0)
            else:
                self._TrianglePoints[0].InsertPoint(0, 10, dp1[1], 0)
                self._TrianglePoints[0].InsertPoint(1, 0, dp1[1] + 5, 0)
                self._TrianglePoints[0].InsertPoint(2, 0, dp1[1] - 5, 0)
            self._TriangleProperty[0].SetColor(self._zcolor)

            # make sure the right arrow stays within the viewport
            bp2 = [x, self._Extent[3] * self._Spacing[1] + self._Origin[1], z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp2[0], bp2[1], bp2[2], 1.0)
            p2 = self._Transform.GetMatrix().MultiplyPoint(
                (bp2[0], bp2[1], bp2[2], 1.0))

            renderer.SetWorldPoint(p2[0], p2[1], p2[2], 1.0)
            renderer.WorldToDisplay()
            dp2 = renderer.GetDisplayPoint()

            if (dp2[0] <= (self._viewsize[0] - 10)):
                self._TrianglePoints[1].InsertPoint(0, dp2[0], dp2[1], 0)
                self._TrianglePoints[1].InsertPoint(
                    1, dp2[0] + 10, dp2[1] - 5, 0)
                self._TrianglePoints[1].InsertPoint(
                    2, dp2[0] + 10, dp2[1] + 5, 0)
            else:
                self._TrianglePoints[1].InsertPoint(
                    0, self._viewsize[0] - 10, dp2[1], 0)
                self._TrianglePoints[1].InsertPoint(
                    1, self._viewsize[0], dp2[1] - 5, 0)
                self._TrianglePoints[1].InsertPoint(
                    2, self._viewsize[0], dp2[1] + 5, 0)
            self._TriangleProperty[1].SetColor(self._zcolor)

            # make sure the bottom arrow stays within the viewport
            bp3 = [x, y, self._Extent[4] * self._Spacing[2] + self._Origin[2]]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp3[0], bp3[1], bp3[2], 1.0)
            p3 = self._Transform.GetMatrix().MultiplyPoint(
                (bp3[0], bp3[1], bp3[2], 1.0))

            renderer.SetWorldPoint(p3[0], p3[1], p3[2], 1.0)
            renderer.WorldToDisplay()
            dp3 = renderer.GetDisplayPoint()

            if (dp3[1] >= 10):
                self._TrianglePoints[2].InsertPoint(0, dp3[0], dp3[1], 0)
                self._TrianglePoints[2].InsertPoint(
                    1, dp3[0] - 5, dp3[1] - 10, 0)
                self._TrianglePoints[2].InsertPoint(
                    2, dp3[0] + 5, dp3[1] - 10, 0)
            else:
                self._TrianglePoints[2].InsertPoint(0, dp3[0], 10, 0)
                self._TrianglePoints[2].InsertPoint(1, dp3[0] - 5, 0, 0)
                self._TrianglePoints[2].InsertPoint(2, dp3[0] + 5, 0, 0)
            self._TriangleProperty[2].SetColor(self._ycolor)

            # make sure the top arrow stays within the viewport
            bp4 = [x, y, self._Extent[5] * self._Spacing[2] + self._Origin[2]]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp4[0], bp4[1], bp4[2], 1.0)
            p4 = self._Transform.GetMatrix().MultiplyPoint(
                (bp4[0], bp4[1], bp4[2], 1.0))

            renderer.SetWorldPoint(p4[0], p4[1], p4[2], 1.0)
            renderer.WorldToDisplay()
            dp4 = renderer.GetDisplayPoint()

            if (dp4[1] <= (self._viewsize[1] - 10)):
                self._TrianglePoints[3].InsertPoint(0, dp4[0], dp4[1], 0)
                self._TrianglePoints[3].InsertPoint(
                    1, dp4[0] + 5, dp4[1] + 10, 0)
                self._TrianglePoints[3].InsertPoint(
                    2, dp4[0] - 5, dp4[1] + 10, 0)
            else:
                self._TrianglePoints[3].InsertPoint(
                    0, dp4[0], self._viewsize[1] - 10, 0)
                self._TrianglePoints[3].InsertPoint(
                    1, dp4[0] + 5, self._viewsize[1], 0)
                self._TrianglePoints[3].InsertPoint(
                    2, dp4[0] - 5, self._viewsize[1], 0)
            self._TriangleProperty[3].SetColor(self._ycolor)

        else:
            print "Warning: No Plane"

        for i in range(4):
            self._TriangleGrid[i].Modified()

        # Draw the axes
        if (self._Plane == self._Planes.GetAxialPlane()):
            # Calculate endpoints points for the x axes
            bp1 = [self._Extent[0] * self._Spacing[0] + self._Origin[0], y, z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp1[0], bp1[1], bp1[2], 1.0)
            p1 = self._Transform.GetMatrix().MultiplyPoint(
                (bp1[0], bp1[1], bp1[2], 1.0))

            renderer.SetWorldPoint(p1[0], p1[1], p1[2], 1.0)
            renderer.WorldToDisplay()
            dp1 = renderer.GetDisplayPoint()

            bp2 = [self._Extent[1] * self._Spacing[0] + self._Origin[0], y, z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp2[0], bp2[1], bp2[2], 1.0)
            p2 = self._Transform.GetMatrix().MultiplyPoint(
                (bp2[0], bp2[1], bp2[2], 1.0))

            renderer.SetWorldPoint(p2[0], p2[1], p2[2], 1.0)
            renderer.WorldToDisplay()
            dp2 = renderer.GetDisplayPoint()

            self._LinePoints[0].InsertPoint(0, dp1[0], dp1[1], 0)
            self._LinePoints[0].InsertPoint(1, dp2[0], dp2[1], 0)
            self._LineProperty[0].SetColor(self._ycolor)

            # Calculate endpoints points for the y axes
            bp3 = [x, self._Extent[2] * self._Spacing[1] + self._Origin[1], z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp3[0], bp3[1], bp3[2], 1.0)
            p3 = self._Transform.GetMatrix().MultiplyPoint(
                (bp3[0], bp3[1], bp3[2], 1.0))

            renderer.SetWorldPoint(p3[0], p3[1], p3[2], 1.0)
            renderer.WorldToDisplay()
            dp3 = renderer.GetDisplayPoint()

            bp4 = [x, self._Extent[3] * self._Spacing[1] + self._Origin[1], z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp4[0], bp4[1], bp4[2], 1.0)
            p4 = self._Transform.GetMatrix().MultiplyPoint(
                (bp4[0], bp4[1], bp4[2], 1.0))

            renderer.SetWorldPoint(p4[0], p4[1], p4[2], 1.0)
            renderer.WorldToDisplay()
            dp4 = renderer.GetDisplayPoint()

            self._LinePoints[1].InsertPoint(0, dp3[0], dp3[1], 0)
            self._LinePoints[1].InsertPoint(1, dp4[0], dp4[1], 0)
            self._LineProperty[1].SetColor(self._xcolor)
        elif (self._Plane == self._Planes.GetCoronalPlane()):
            # Calculate endpoints points for the x axes
            bp1 = [self._Extent[0] * self._Spacing[0] + self._Origin[0], y, z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp1[0], bp1[1], bp1[2], 1.0)
            p1 = self._Transform.GetMatrix().MultiplyPoint(
                (bp1[0], bp1[1], bp1[2], 1.0))

            renderer.SetWorldPoint(p1[0], p1[1], p1[2], 1.0)
            renderer.WorldToDisplay()
            dp1 = renderer.GetDisplayPoint()

            bp2 = [self._Extent[1] * self._Spacing[0] + self._Origin[0], y, z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp2[0], bp2[1], bp2[2], 1.0)
            p2 = self._Transform.GetMatrix().MultiplyPoint(
                (bp2[0], bp2[1], bp2[2], 1.0))

            renderer.SetWorldPoint(p2[0], p2[1], p2[2], 1.0)
            renderer.WorldToDisplay()
            dp2 = renderer.GetDisplayPoint()

            self._LinePoints[0].InsertPoint(0, dp1[0], dp1[1], 0)
            self._LinePoints[0].InsertPoint(1, dp2[0], dp2[1], 0)
            self._LineProperty[0].SetColor(self._zcolor)

            # Calculate endpoints points for the z axes
            bp3 = [x, y, self._Extent[4] * self._Spacing[2] + self._Origin[2]]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp3[0], bp3[1], bp3[2], 1.0)
            p3 = self._Transform.GetMatrix().MultiplyPoint(
                (bp3[0], bp3[1], bp3[2], 1.0))

            renderer.SetWorldPoint(p3[0], p3[1], p3[2], 1.0)
            renderer.WorldToDisplay()
            dp3 = renderer.GetDisplayPoint()

            bp4 = [x, y, self._Extent[5] * self._Spacing[2] + self._Origin[2]]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp4[0], bp4[1], bp4[2], 1.0)
            p4 = self._Transform.GetMatrix().MultiplyPoint(
                (bp4[0], bp4[1], bp4[2], 1.0))

            renderer.SetWorldPoint(p4[0], p4[1], p4[2], 1.0)
            renderer.WorldToDisplay()
            dp4 = renderer.GetDisplayPoint()

            self._LinePoints[1].InsertPoint(0, dp3[0], dp3[1], 0)
            self._LinePoints[1].InsertPoint(1, dp4[0], dp4[1], 0)
            self._LineProperty[1].SetColor(self._xcolor)
        elif (self._Plane == self._Planes.GetSagittalPlane()):
            # Calculate endpoints points for y axis
            bp1 = [x, self._Extent[2] * self._Spacing[1] + self._Origin[1], z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp1[0], bp1[1], bp1[2], 1.0)
            p1 = self._Transform.GetMatrix().MultiplyPoint(
                (bp1[0], bp1[1], bp1[2], 1.0))

            renderer.SetWorldPoint(p1[0], p1[1], p1[2], 1.0)
            renderer.WorldToDisplay()
            dp1 = renderer.GetDisplayPoint()

            bp2 = [x, self._Extent[3] * self._Spacing[1] + self._Origin[1], z]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp2[0], bp2[1], bp2[2], 1.0)
            p2 = self._Transform.GetMatrix().MultiplyPoint(
                (bp2[0], bp2[1], bp2[2], 1.0))

            renderer.SetWorldPoint(p2[0], p2[1], p2[2], 1.0)
            renderer.WorldToDisplay()
            dp2 = renderer.GetDisplayPoint()

            self._LinePoints[0].InsertPoint(0, dp1[0], dp1[1], 0)
            self._LinePoints[0].InsertPoint(1, dp2[0], dp2[1], 0)
            self._LineProperty[0].SetColor(self._zcolor)

            # Calculate endpoints points for the z axes
            bp3 = [x, y, self._Extent[4] * self._Spacing[2] + self._Origin[2]]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp3[0], bp3[1], bp3[2], 1.0)
            p3 = self._Transform.GetMatrix().MultiplyPoint(
                (bp3[0], bp3[1], bp3[2], 1.0))

            renderer.SetWorldPoint(p3[0], p3[1], p3[2], 1.0)
            renderer.WorldToDisplay()
            dp3 = renderer.GetDisplayPoint()

            bp4 = [x, y, self._Extent[5] * self._Spacing[2] + self._Origin[2]]

            self._Transform.PostMultiply()
            # self._Transform.SetPoint(bp4[0], bp4[1], bp4[2], 1.0)
            p4 = self._Transform.GetMatrix().MultiplyPoint(
                (bp4[0], bp4[1], bp4[2], 1.0))

            renderer.SetWorldPoint(p4[0], p4[1], p4[2], 1.0)
            renderer.WorldToDisplay()
            dp4 = renderer.GetDisplayPoint()

            self._LinePoints[1].InsertPoint(0, dp3[0], dp3[1], 0)
            self._LinePoints[1].InsertPoint(1, dp4[0], dp4[1], 0)
            self._LineProperty[1].SetColor(self._ycolor)

        else:
            print "Warning: No plane"

        self.Modified()
        self.Render()

    def DoRotation(self, center, rotateaxis, angle):
        self._Transform.PostMultiply()
        self._Transform.Translate(-center[0], -center[1], -center[2])
        self._Transform.RotateWXYZ(angle,
                                   rotateaxis[0], rotateaxis[1], rotateaxis[2])
        self._Transform.Translate(center[0], center[1], center[2])
        self.Modified()
        self.Render()

    def DoSpin(self, center, normal, angle):
        self._Transform.PostMultiply()
        self._Transform.Translate(-center[0], -center[1], -center[2])
        self._Transform.RotateWXYZ(angle,
                                   normal[0], normal[1], normal[2])
        self._Transform.Translate(center[0], center[1], center[2])
        self.Modified()
        self.Render()

    def DoReset(self):
        self._Transform.Identity()
        self.Modified()
        self.Render()

    def SetInput(self, input):
        self._Extent = input.GetWholeExtent()
        self._Origin = input.GetOrigin()
        self._Spacing = input.GetSpacing()

        # Do not remove this code.  Without this code the arrows and lines rotate in the
        # wrong manner - otherwise this code is not needed.
        self._polyVertexPoints = vtk.vtkPoints()
        self._polyVertexPoints.SetNumberOfPoints(1)
        x = self._Planes.GetSagittalPlane().GetSlicePosition()
        y = self._Planes.GetCoronalPlane().GetSlicePosition()
        z = self._Planes.GetAxialPlane().GetSlicePosition()
        if (self._Plane == self._Planes.GetAxialPlane()):
            self._polyVertexPoints.InsertPoint(0, -self._Extent[1] / 2.0, y, z)

        self._aPolyVertex = vtk.vtkPolyVertex()
        self._aPolyVertex.GetPointIds().SetNumberOfIds(1)
        self._aPolyVertex.GetPointIds().SetId(0, 0)

        self._aPolyVertexGrid = vtk.vtkUnstructuredGrid()
        self._aPolyVertexGrid.Allocate(1, 1)
        self._aPolyVertexGrid.InsertNextCell(
            self._aPolyVertex.GetCellType(), self._aPolyVertex.GetPointIds())
        self._aPolyVertexGrid.SetPoints(self._polyVertexPoints)

        self._VertexProperty = vtk.vtkProperty()
        self._VertexProperty.SetOpacity(0)

    def SetLineOpacity(self, opacity):
        for i in range(2):
            self._LineProperty[i].SetOpacity(opacity)
        self.Modified()

    def ToggleLineOpacity(self):
        if (self._LineOpacity == 0):
            self._LineOpacity = 0.5
        else:
            self._LineOpacity = 0
        self.SetLineOpacity(self._LineOpacity)
        self.Render()

    def GetLineOpacity(self):
        return self._LineOpacity

    def _MakeActors(self):
        actors = []

        NewActorList = []
        MapperList = []
        for i in range(4):
            actorArrow = self._NewActor2()
            NewActorList.append(actorArrow)
            NewActorList[i].PickableOff()
            NewActorList[i].SetProperty(self._TriangleProperty[i])
            mapperArrow = vtk.vtkPolyDataMapper2D()
            MapperList.append(mapperArrow)
            MapperList[i].SetInput(self._TriangleGrid[i])
            NewActorList[i].SetMapper(MapperList[i])
            actors.append(NewActorList[i])

        NewActorList = []
        MapperList = []
        for i in range(2):
            actorArrow = self._NewActor2()
            NewActorList.append(actorArrow)
            NewActorList[i].PickableOff()
            NewActorList[i].SetProperty(self._LineProperty[i])
            mapperArrow = vtk.vtkPolyDataMapper2D()
            MapperList.append(mapperArrow)
            MapperList[i].SetInput(self._LineGrid[i])
            NewActorList[i].SetMapper(MapperList[i])
            actors.append(NewActorList[i])

        # Do not remove this code.  Without this code the arrows and lines rotate in the
        # wrong manner - otherwise this code is not needed.
        actorVertex = self._NewActor()
        actorVertex.PickableOff()
        self._VertexProperty.SetOpacity(0)
        actorVertex.SetProperty(self._VertexProperty)
        mapperVertex = vtk.vtkDataSetMapper()
        mapperVertex.SetInput(self._aPolyVertexGrid)
        actorVertex.SetMapper(mapperVertex)
        actors.append(actorVertex)

        return actors

    def AddToRenderer(self, renderer):
        ActorFactory.AddToRenderer(self, renderer)
        renderer.AddObserver('StartEvent', self.OnRenderEvent)

    def OnRenderEvent(self, renderer, event):
        # Update scale for cones
        camera = renderer.GetActiveCamera()
        worldsize = camera.GetParallelScale()
        self._viewsize = renderer.GetSize()
        pitch = worldsize / math.sqrt(renderer.GetSize()[0] *
                                      renderer.GetSize()[1])
        self.UpdatePlaneIntersections(renderer)

    def _NewActor2(self):
        actor = vtk.vtkActor2D()
        return actor
