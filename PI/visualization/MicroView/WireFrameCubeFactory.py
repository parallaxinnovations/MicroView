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
This factory is used to draw a wire frame outline around a cube.
"""

from vtkAtamai.ActorFactory import *


class WireFrameCubeFactory(ActorFactory):

    def __init__(self, UseTubes=1):

        ActorFactory.__init__(self)

        self._Input = None

        self._CubeExists = 0
        self.SetRadius(0.3)
        self._WireFrameCube = vtk.vtkOutlineSource()
        self._WireFrameCubeProperty = vtk.vtkProperty()

        self._UseTubes = UseTubes

#
#  This code is badly broken
#
    def SetRadius(self, radius):
        self._radius = radius
        try:
            self._tubes.SetRadius(self.GetRadius())
        except:
            pass

    def GetRadius(self):
        return self._radius

    def SetInput(self, input):
        if input is None:
            return

        self._Input = input

        ActorFactory.SetTransform(self, self._Input._Transform)

        self.Modified()

    def GetInput(self):
        return self._Input

    def SetBounds(self, x1, x2, y1, y2, z1, z2):

        self._minX = min(x1, x2)
        self._minY = min(y1, y2)
        self._minZ = min(z1, z2)
        self._maxX = max(x1, x2)
        self._maxY = max(y1, y2)
        self._maxZ = max(z1, z2)

        self._WireFrameCube.SetROIBounds(
            self._minX, self._maxX, self._minY, self._maxY, self._minZ, self._maxZ)

        self._CubeExists = 1

    # Return the two coordinate points defining the cube
    def GetBounds(self):
        if self._CubeExists == 1:
            return [self._minX, self._maxX, self._minY, self._maxY, self._minZ, self._maxZ]
        else:
            return None

    def SetColor(self, *args):
        # we don't have to call Modified() because
        # ActorFactory.GetMTime() already includes _Property.GetMTime()
        if len(args) == 1:
            args = args[0]
        apply(self._WireFrameCubeProperty.SetColor, args)

    def GetColor(self):
        return self._WireFrameCubeProperty.GetColor()

    def SetOpacity(self, opacity):
        self._WireFrameCubeProperty.SetOpacity(opacity)

    def GetOpacity(self, opacity):
        self._WireFrameCubeProperty.GetOpacity()

    def _MakeActors(self):
        actors = []

        actor = self._NewActor()
        actor.PickableOff()
        actor.SetProperty(self._WireFrameCubeProperty)

        if (self._UseTubes == 1):
            # remove duplicate points
            cleaner = vtk.vtkCleanPolyData()
            cleaner.SetInput(self._WireFrameCube.GetOutput())

            self._tubes = vtk.vtkTubeFilter()
            self._tubes.SetInput(cleaner.GetOutput())
            self._tubes.SetRadius(self.GetRadius())
            self._tubes.SetNumberOfSides(6)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInput(self._tubes.GetOutput())
        else:
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInput(self._WireFrameCube.GetOutput())

        actor.SetMapper(mapper)
        actors.append(actor)

        return actors
