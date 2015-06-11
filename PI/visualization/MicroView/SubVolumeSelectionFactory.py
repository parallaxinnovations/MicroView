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
#
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

import vtk
from vtkAtamai import ActorFactory
import SphereMarkFactory
import WireFrameCubeFactory
from vtkEVS import EVSSolidCubeFactory


class SubVolumeSelectionFactory(ActorFactory.ActorFactory):

    def __init__(self):
        ActorFactory.ActorFactory.__init__(self)

        self._WireFrameCube = WireFrameCubeFactory.WireFrameCubeFactory()
        self._SolidCube = EVSSolidCubeFactory.EVSSolidCubeFactory()

        self._CubePropertiesAreSet = 0

        self._SphereMark1 = SphereMarkFactory.SphereMarkFactory()
        self._SphereMark1IsSet = 0

        self._SphereMark2 = SphereMarkFactory.SphereMarkFactory()
        self._SphereMark2IsSet = 0

        self._Property = vtk.vtkProperty()

    def GetWireFrame(self):
        return self._WireFrameCube

    # Draw a sphere at the first corner defining the cube.  If the second
    # sphere has also been set, draw the cube based on the two points.
    def SetFirstPoint(self, x1, y1, z1):

        self._SphereMark1.SetPosition((x1, y1, z1))

        # set the sphere's colour, size, and opacity only once
        if self._SphereMark1IsSet == 0:
            self._SphereMark1IsSet = 1
            self._SphereMark1.SetSize(2)
            self._SphereMark1.SetOpacity(1.0)
            self._SphereMark1.SetColor(1.0, 1.0, 0.0)

        # draw the cube if the second point has also been set
        if self._SphereMark2IsSet == 1:
            (x2, y2, z2) = self._SphereMark2.GetPosition()

            # draw the cube
            self._WireFrameCube.SetBounds(x1, x2, y1, y2, z1, z2)
            self._SolidCube.SetBounds(x1, x2, y1, y2, z1, z2)

            # if the cube's colour, and opacity haven't been set, set them now
            if self._CubePropertiesAreSet == 0:
                self._CubePropertiesAreSet = 1

                self._WireFrameCube.SetColor(1.0, 1.0, 0.0)
                self._WireFrameCube.SetOpacity(1.0)

                self._SolidCube.SetColor(1.0, 1.0, 0.0)
                self._SolidCube.SetOpacity(0.25)

    # Draw a sphere at the second corner defining the cube.  If the first
    # sphere has also been set, draw the cube based on the two points.
    def SetSecondPoint(self, x2, y2, z2):

        self._SphereMark2.SetPosition((x2, y2, z2))

        # set the sphere's colour, size, and opacity only once
        if self._SphereMark2IsSet == 0:
            self._SphereMark2IsSet = 1
            self._SphereMark2.SetSize(2)
            self._SphereMark2.SetOpacity(1.0)
            self._SphereMark2.SetColor(0.70, 0.70, 0.2)

        # draw the cube if the first point has also been set
        if self._SphereMark1IsSet == 1:
            (x1, y1, z1) = self._SphereMark1.GetPosition()

            # draw the cube
            self._WireFrameCube.SetBounds(x1, x2, y1, y2, z1, z2)
            self._SolidCube.SetBounds(x1, x2, y1, y2, z1, z2)

            # if the cube's colour, and opacity haven't been set, set them now
            if self._CubePropertiesAreSet == 0:
                self._CubePropertiesAreSet = 1

                self._WireFrameCube.SetColor(1.0, 1.0, 0.0)
                self._WireFrameCube.SetOpacity(1.0)

                self._SolidCube.SetColor(1.0, 1.0, 0.0)
                self._SolidCube.SetOpacity(0.25)

    def SetColor(self, *args):
        # we don't have to call Modified() because
        # ActorFactory.ActorFactory.GetMTime() already includes
        # _Property.GetMTime()
        if len(args) == 1:
            args = args[0]
        apply(self._Property.SetColor, args)

    def GetColor(self):
        return self._Property.GetColor()

#  def HasChangedSince(self,sinceMTime):
#      if (ActorFactory.ActorFactory.HasChangedSince(self,sinceMTime)):
#          return 1
#      if (self._Input and self._Input.GetMTime > sinceMTime):
#          return 1
#      if (self._Input and self._Input.HasChangedSince(sinceMTime)):
#          return 1
#      return 0
    def SetSphereOpacity(self, opacity):
        # wtf?? self._Property.SetOpacity(opacity)
        self._SphereMark1.SetOpacity(opacity)
        self._SphereMark2.SetOpacity(opacity)

    def GetSphereOpacity(self, opacity):
        self._Property.GetOpacity(opacity)

    def SetWireFrameOpacity(self, opacity):
        self._WireFrameCube.SetOpacity(opacity)

    def SetCubeOpacity(self, opacity):
        self._SolidCube.SetOpacity(opacity)

    # Set the bounds of the cubes
    def SetBounds(self, x1, x2, y1, y2, z1, z2):
        self._WireFrameCube.SetBounds(x1, x2, y1, y2, z1, z2)
        self._SolidCube.SetBounds(x1, x2, y1, y2, z1, z2)

    # Save the bounds of the cube to disk, in the following format:
    # minX minY minZ
    # sizeX sizeY sizeZ
    def SaveSubVolumeCoordinatesToDisk(self, FileName):
        coords = self._WireFrameCube.GetBounds()

        if coords is None:
            print "A sub volume is not yet selected.  No file was written."
            return

        (x1, y1, z1) = (coords[0], coords[2], coords[4])
        (x2, y2, z2) = (coords[1], coords[3], coords[5])

        # find the maxes and mins
        minX = min(x1, x2)
        minY = min(y1, y2)
        minZ = min(z1, z2)
        maxX = max(x1, x2)
        maxY = max(y1, y2)
        maxZ = max(z1, z2)

        # find absolute so there is no negative zero
        strOutOrigin = str(round(abs(minX - self._VolOrigin[0]), 3)) + " " + str(round(abs(
            minY - self._VolOrigin[1]), 3)) + " " + str(round(abs(minZ - self._VolOrigin[2]), 3))
        strOutSize = str(round(abs(maxX - minX), 3)) + " " + str(round(
            abs(maxY - minY), 3)) + " " + str(round(abs(maxZ - minZ), 3))

        file = open(FileName, 'wt')
        file.write(strOutOrigin)
        file.write("\n")
        file.write(strOutSize)
        file.close()

        print "The subvolume coordinates have been saved."
        print ""

    def SetFullVolumeDimensions(self, X, Y, Z):
        self._FullVolumeDimensions = [X, Y, Z]

    def SetOrigin(self, X, Y, Z):
        self._VolOrigin = [X, Y, Z]

    # Add the actors to the display list and hide them until they're needed
    def _MakeActors(self):
        actors = []

        # add the objects to the display list
        self.AddChild(self._SphereMark1)
        self.AddChild(self._SphereMark2)
        self.AddChild(self._WireFrameCube)
        self.AddChild(self._SolidCube)

        # hide the objects for now
        self._SphereMark1.SetOpacity(0)
        self._SphereMark2.SetOpacity(0)
        self._WireFrameCube.SetOpacity(0)
        self._SolidCube.SetOpacity(0)

        return actors
