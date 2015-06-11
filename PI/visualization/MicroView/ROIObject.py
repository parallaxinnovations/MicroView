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

"""
ROIObject is a utility class for holding information about ROIs created in MicroView
"""

import vtk
import logging
import os
import sys
from vtkAtamai import SurfaceObjectFactory

#
#
# Geometry Object class - this is taken from the Display Geometry plugin
# and is used to properly show the polydata geometry on the screen
#
#


class GeometryObject(object):

    def __init__(self, shortname, filename, connection):
        self._producer = connection.GetProducer()  # hold on to this
        self._geom = SurfaceObjectFactory.SurfaceObjectFactory()
        self._geom.SetInputConnection(connection)
        self._opacity = 0.25
        self.SetOpacity(self._opacity)
        self._iswireframe = True
        self._isvisible = False
        self.__shortname__ = shortname
        self._filename = filename

    def GetWireFrame(self):
        return self._iswireframe

    def SetWireFrameOn(self):
        self._iswireframe = True
        self._geom.GetProperty().SetRepresentationToWireframe()
        self._geom.SetBackfaceProperty(self._geom.GetProperty())

    def SetWireFrameOff(self):
        self._iswireframe = False
        self._geom.GetProperty().SetRepresentationToSurface()
        self._geom.SetBackfaceProperty(self._geom.GetProperty())
        self._geom.NormalGenerationOn()

    def SetColor(self, r, g, b):
        self._obj_colors = (r, g, b)
        self._geom.GetProperty().SetColor(r, g, b)

    def GetColor(self):
        return self._obj_colors

    def GetSurface(self):
        return self._geom

    def GetVisibility(self):
        return self._isvisible

    def SetVisibilityOn(self):
        self._isvisible = True

    def SetVisibilityOff(self):
        self._isvisible = False

    def GetFileName(self):
        return self._filename

    def GetShortName(self):
        return self.__shortname__

    def SetOpacity(self, opacity):
        self._opacity = opacity
        self._geom.GetProperty().SetOpacity(self._opacity)

    def ApplyOpacity(self):
        self._geom.GetProperty().SetOpacity(self._opacity)

    def GetOpacity(self):
        if self._geom:
            assert self._geom.GetProperty().GetOpacity() == self._opacity
        return self._opacity

    def ClearGeometry(self):
        del self._geom
        self._geom = None

    def SetInputConnection(self, connection):
        self._producer = connection.GetProducer()
        self._geom = SurfaceObjectFactory.SurfaceObjectFactory()
        self._geom.SetInputConnection(connection)
        self._geom.GetProperty().SetOpacity(self._opacity)

#
# ROIObject class
#


class ROIObject(object):

    def __init__(self, **kw):
        self._image = None
        self._stencil_data = None
        self._polydata = None
        self._imagemask = None
        self._type = ''
        self._name = ''
        self._shown = False
        self._color = (1, 1, 1)
        self._wireframe = True
        self.log = logging.getLogger(__name__)

    def SetImage(self, image):
        self._image = image

    def GetImage(self):
        return self._image

    def SetStencilData(self, stencil):
        self._stencil_data = stencil

    def GetStencilData(self):
        return self._stencil_data

    def GeneratePolyData(self):

        if self._imagemask:
            contour_filter = vtk.vtkMarchingCubes()
            contour_filter.ReleaseDataFlagOn()
            contour_filter.SetNumberOfContours(1)
            contour_filter.SetComputeScalars(0)
            contour_filter.SetComputeNormals(0)
            if vtk.vtkVersion().GetVTKMajorVersion() > 5:
                contour_filter.SetInputData(self._imagemask)
            else:
                contour_filter.SetInput(self._imagemask)
            contour_filter.SetValue(0, 128.0)

            try:
                contour_filter.Update()
            except:
                print sys.exc_type, sys.exc_value
                return False

            decimate = vtk.vtkDecimatePro()
            decimate.ReleaseDataFlagOn()
            decimate.SetInputConnection(contour_filter.GetOutputPort())
            decimate.PreserveTopologyOn()
            decimate.SetTargetReduction(0)
            try:
                decimate.Update()
            except:
                print sys.exc_type, sys.exc_value
                return False

            if self._polydata is None:
                self._polydata = GeometryObject(
                    self._name, self._name, decimate.GetOutputPort())
            else:
                self._polydata.SetInputConnection(decimate.GetOutputPort())

            if self._wireframe:
                self._polydata.SetWireFrameOn()
            else:
                self._polydata.SetWireFrameOff()
            self._polydata.SetVisibilityOff()

    #
    # Functions for setting/getting polydata - again, generate stencil and
    # image mask automatically so we can display more quickly
    #
    def SetPolyDataConnection(self, connection, imageData):
        if self._polydata is None:
            self._polydata = GeometryObject(self._name, self._name, connection)
        else:
            self._polydata.SetInputConnection(connection)

        self._polydata.SetWireFrameOn()
        self._polydata.SetVisibilityOff()

        # set proper tolerance for converter
        imageData.UpdateInformation()
        tolerance = 0.001 * min(imageData.GetSpacing())

        # update pipeline
        connection.GetProducer().Update()

        polyData = connection.GetProducer().GetOutputDataObject(0)

        b = polyData.GetBounds()
        s = imageData.GetSpacing()
        o = imageData.GetOrigin()
        extent = [int((b[0] - o[0]) / s[0]), int((b[1] - o[0]) / s[0]) + 1,
                  int((b[2] - o[1]) / s[1]), int((b[3] - o[1]) / s[1]) + 1,
                  int((b[4] - o[2]) / s[2]), int((b[5] - o[2]) / s[2]) + 1]

        stencil = vtk.vtkPolyDataToImageStencil()
        stencil.ReleaseDataFlagOn()
        stencil.SetTolerance(tolerance)
        stencil.SetInputConnection(connection)
        stencil.SetOutputSpacing(imageData.GetSpacing())
        stencil.SetOutputOrigin(imageData.GetOrigin())
        stencil.SetOutputWholeExtent(extent)

        # stencil.GetOutput().SetWholeExtent(extent)
        # stencil.GetOutput().SetUpdateExtentToWholeExtent()
        # stencil.GetOutput().SetExtent(imageData.GetExtent())
        # stencil.GetOutput().SetOrigin(imageData.GetOrigin())
        # stencil.GetOutput().SetSpacing(imageData.GetSpacing())
        try:
            stencil.GetOutput().Update()
        except:
            print sys.exc_type, sys.exc_value
            return -1

        self._stencil_data = stencil.GetOutput()
        self.ClearPolyData()

    def GetPolyData(self):
        return self._polydata

    def ClearPolyData(self):
        if self._polydata:
            self._polydata.ClearGeometry()

    def DeletePolyData(self):
        if self._polydata:
            del self._polydata
            self._polydata = None

    #
    # The image mask is the smallest representation to be used in display
    # and saved to disk
    #
    def SetImageMask(self, mask):
        self._imagemask = mask

    def GetImageMask(self):
        if self._imagemask:
            return self._imagemask

    def ClearImageMask(self):
        if self._imagemask:
            del self._imagemask
            self._imagemask = None

    #
    # File I/O
    #
    def SaveROIObject(self, filename):
        if self._imagemask:
            writer = vtk.vtkXMLImageDataWriter()
            writer.SetInput(self._imagemask)
            writer.SetFileName(filename)
            writer.Write()

    def LoadROIObject(self, filename):
        reader = vtk.vtkXMLImageDataReader()
        try:
            reader.SetFileName(filename)
        except UnicodeEncodeError:
            reader.SetFileName(
                filename.encode(sys.getfilesystemencoding() or 'UTF-8'))
        try:
            reader.Update()
        except:
            self.log.error('error reading ROIObject from file')

        self._type = 'custom'
        dir, name = os.path.split(filename)
        root, ext = os.path.splitext(name)
        self._name = root
        f1 = vtk.vtkImageToImageStencil()
        f1.SetInput(reader.GetOutput())
        f1.ThresholdByUpper(128)
        try:
            f1.Update()
            self.SetStencilData(f1.GetOutput())
        except:
            self.log.error('error generating stencil on LoadROIObject')

    #
    # Generic functions for setting/getting other class members
    #
    def SetType(self, type):
        self._type = type

    def GetType(self):
        return self._type

    def SetName(self, name):
        self._name = name

    def GetName(self):
        return self._name

    def SetShown(self):
        self._shown = True

    def ClearShown(self):
        self._shown = False

    def GetShown(self):
        return self._shown

    def ClearData(self):
        self.ClearPolyData()
        self.ClearImageMask()

    def SetColor(self, color):
        self._color = color

    def GetColor(self):
        return self._color

    def SetWireFrame(self, wireframe):
        self._wireframe = wireframe
        if self._polydata:
            if self._wireframe:
                self._polydata.SetWireFrameOn()
            else:
                self._polydata.SetWireFrameOff()
