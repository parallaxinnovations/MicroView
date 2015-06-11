# =========================================================================
#
# Copyright (c) 2000-2002 Enhanced Vision Systems
# Copyright (c) 2002-2008 GE Healthcare
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
A class for measuring distance and plotting a line profile.

LineSegmentSelectionFactory allows the user to specify the two end points of a
line segment.  A profile of the line indicating the gray scale values along
different points of the line can be plotted.

Derived From:

  ActorFactor

"""

import collections
import math
import os
import sys
import logging
import vtk
import datetime
from zope import component

from vtkAtamai import ActorFactory
from vtkEVS import ConeMarkerFactory2, EVSFileDialog
from PI.visualization.common import MicroViewSettings
from PI.visualization.MicroView.interfaces import ICurrentViewportManager
from PI.visualization.MicroView import PACKAGE_VERSION, PACKAGE_SHA1


class LineSegmentSelectionFactory(ActorFactory.ActorFactory):

    def SetInput(self, img):
        self._ImageData = img

    def tearDown(self):

        ActorFactory.ActorFactory.tearDown(self)

        self.RemoveAllObservers()
        self.RemoveAllEventHandlers()

        del(self._Line)
        del(self._LineProperty)
        del(self._Mark1)
        del(self._Mark2)

    def SetTransform(self, t):
        """Sets a transform used when measuring a warped image"""
        self._t = t

    def DeleteTransform(self):
        """Removes the assigned transform"""
        self._t = None

    def __init__(self):
        ActorFactory.ActorFactory.__init__(self)
        # the default is not apply any transforms
        self._t = None

        # Create the line
        self._Line = vtk.vtkLineSource()
        self._Line.SetResolution(25)
        self._LineProperty = vtk.vtkProperty()
        self._LineProperty.SetColor(
            0.933, 0.505, 0.0)        # default to orange
        self.SetLineOpacity(0.0)

        self._LineLength = 0
        self._MarkersEnabled = True

        # Create the spheres
        self._Mark1 = ConeMarkerFactory2.ConeMarkerFactory2()
        self._Mark2 = ConeMarkerFactory2.ConeMarkerFactory2()
        self._Mark1.SetSize(16)
        self._Mark2.SetSize(16)

        self._Mark1.SetColor(0.0, 0.6, 1.0)         # default to blue
        self._Mark2.SetColor(0.0, 1.0, 0.0)         # default to green

        # Add them as children of this factory
        self.AddChild(self._Mark1)
        self.AddChild(self._Mark2)
        self.HideEndMarkers()
        # Set opacity of balls to 0.0

        self._Mark1IsSet = 0
        self._Mark2IsSet = 0

        self._Mark1Position = None
        self._Mark2Position = None

        self._ElementSize = 1     # Brad made this one instead of zero

        self._SelectedActor = None
        self._lastSelectedMark = None
        self._sMeasurementUnit = 'pixels'

        self.BindEvent("<ButtonPress>", self.StartMoveMark)
        self.BindEvent("<ButtonRelease>", self.StopMoveMark)
        self.BindEvent("<B2-Motion>", self.DoMoveMark)
        self.BindEvent("<B1-Motion>", self.DoMoveMark)
        self.BindEvent("<Key-Delete>", self.ClearLineSegment)

    #
    # It seems only Widgets can bind to <Leave> and <Enter> events.  What a pity.
    # The next three methods try to overcome this limitation
    #

    def HandleEvent(self, event):
        if event.type == 7:
            self.DoEnter(event)
        elif event.type == 8:
            self.DoLeave(event)
        else:
            ActorFactory.ActorFactory.HandleEvent(self, event)

    def DoEnter(self, event):
        for mark in [self._Mark1, self._Mark2]:
            if event.actor in mark.GetActors(event.renderer):
                mark.HighlightOn()
                self._lastSelectedMark = mark
        # if we didn't enter an end marker, it must be the line itself
        if self._lastSelectedMark is None:
            self._lastSelectedMark = self
            self.HighlightOn()

    def HighlightOn(self):
        self._old = self._LineProperty.GetColor()
        self.SetLineColor(1, 1, 0)

    def HighlightOff(self):
        self.SetLineColor(self._old)

    def DoLeave(self, event):
        if self._lastSelectedMark:
            self._lastSelectedMark.HighlightOff()
            self._lastSelectedMark = None

    def SetPickableOn(self, event):
        """Enable object picking"""
        for obj in [self._Mark1, self._Mark2, self]:
            for actor in obj.GetActors(event.renderer):
                actor.PickableOn()

    def SetPickableOff(self, event):
        """Disable object picking"""
        for obj in [self._Mark1, self._Mark2, self]:
            for actor in obj.GetActors(event.renderer):
                actor.PickableOff()

    def EnableMarkers(self):
        self._MarkersEnabled = True
        self._Mark1.SetOpacity(self._Mark1IsSet)
        self._Mark2.SetOpacity(self._Mark2IsSet)
        self._Line.Modified()

    def GetStatus(self):
        """See if all marks are set"""
        return self._Mark1IsSet and self._Mark2IsSet

    def DisableMarkers(self):
        self._MarkersEnabled = False
        self.HideEndMarkers()
        self._Line.Modified()

    def HideEndMarkers(self):
        self._Mark1.SetOpacity(0)
        self._Mark2.SetOpacity(0)

    def ShowEndMarkers(self):
        self._Mark1.SetOpacity(1)
        self._Mark2.SetOpacity(1)

    def StartMoveMark(self, event):

        for mark in [self._Mark1, self._Mark2, self]:
            if event.actor in mark.GetActors(event.renderer):
                self._LastX = event.x
                self._LastY = event.y
                self._SelectedActor = mark
                break
        if self._SelectedActor:

            self.SetPickableOff(event)

            # find the initial position on the slice plane
            picker = event.picker
            picker.Pick(event.x, event.y, 0.0, event.renderer)
            self._LastPos = picker.GetPickPosition()

            # highlight object
            if self._SelectedActor in [self._Mark1, self._Mark2]:
                self._oldColour = self._SelectedActor.GetColor()
                self._SelectedActor.SetColor(1, 0, 0)
            else:
                self._oldColour = self._LineProperty.GetColor()
                self._LineProperty.SetColor(1, 0, 0)

    def StopMoveMark(self, event):

        self.SetPickableOn(event)
        if self._SelectedActor in [self._Mark1, self._Mark2]:
            self._SelectedActor.SetColor(self._oldColour)
        else:
            self._LineProperty.SetColor(self._oldColour)

    def DoMoveMark(self, event):
        picker = event.picker
        picker.Pick(event.x,
                    event.y,
                    0.0,
                    event.renderer)
        position = picker.GetPickPosition()
        LastPos = self._LastPos
        self._LastPos = position
        if position is None:
            self.PickableOn(event)
            return

        x, y, z = position

        origin = self._ImageData.GetOrigin()
        spacing = self._ImageData.GetSpacing()
        extent = self._ImageData.GetWholeExtent()

        # check bounds
        bounds_min = [origin[0] + extent[0] * spacing[0],
                      origin[1] + extent[2] * spacing[1],
                      origin[2] + extent[4] * spacing[2]]
        bounds_max = [origin[0] + extent[1] * spacing[0],
                      origin[1] + extent[3] * spacing[1],
                      origin[2] + extent[5] * spacing[2]]
        if self._SelectedActor == self._Mark1:
            if ((x > bounds_max[0]) or (x < bounds_min[0]) or
                (y > bounds_max[1]) or (y < bounds_min[1]) or
                    (z > bounds_max[2]) or (z < bounds_min[2])):
                return
            self.SetPoint(0, x, y, z)
        if self._SelectedActor == self._Mark2:
            if ((x > bounds_max[0]) or (x < bounds_min[0]) or
                (y > bounds_max[1]) or (y < bounds_min[1]) or
                    (z > bounds_max[2]) or (z < bounds_min[2])):
                return
            self.SetPoint(1, x, y, z)
        if self._SelectedActor == self:
            dx = position[0] - LastPos[0]
            dy = position[1] - LastPos[1]
            dz = position[2] - LastPos[2]
            p0 = self.GetFirstPoint()
            p1 = self.GetSecondPoint()

            if ((p0[0] + dx > bounds_max[0]) or (p0[0] + dx < bounds_min[0]) or
                (p0[1] + dy > bounds_max[1]) or (p0[1] + dy < bounds_min[1]) or
                    (p0[2] + dz > bounds_max[2]) or (p0[2] + dz < bounds_min[2])):
                return
            if ((p1[0] + dx > bounds_max[0]) or (p1[0] + dx < bounds_min[0]) or
                (p1[1] + dy > bounds_max[1]) or (p1[1] + dy < bounds_min[1]) or
                    (p1[2] + dz > bounds_max[2]) or (p1[2] + dz < bounds_min[2])):
                return

            self.Translate(dx, dy, dz)

    # Clear the line.
    def ClearLineSegment(self):
        self._Mark1IsSet = 0
        self._Mark2IsSet = 0
        self.HideEndMarkers()

        self._LineLength = 0
        self.SetLineOpacity(0.0)
        self._Line.Modified()

    def SaveLineLengthToFile(self, FileName):

        if self._Mark1IsSet == 0 or self._Mark2IsSet == 0:
            return

        results_logger = logging.getLogger('results')

        LineLength = self.GetLength()

        try:
            _file = open(FileName, 'at')
            if self._sMeasurementUnit == "mm":
                text = "%4.3f mm" % LineLength
            else:
                text = "%4.3f %s" % (LineLength, "pixels")

            _file.write(text + '\n')
            results_logger.info(text)

            _file.close()
        except:
            pass

        logging.info("Saved line length to '%s'" % FileName)

    def SavePointsToFile(self):
        if self._Mark1IsSet == 0 or self._Mark2IsSet == 0:
            return

        results_logger = logging.getLogger('results')

        # Get a filename to save points to
        ft = collections.OrderedDict()
        ft["text file"] = ["*.txt", "*.TXT"]

        curr_dir = self.GetCurrentDirectory()
        filename = EVSFileDialog.asksaveasfilename(
            message='Save Points', filetypes=ft, defaultdir=curr_dir, defaultextension='.txt')

        pt1 = self.GetFirstPoint()
        pt2 = self.GetSecondPoint()

        origin = self._ImageData.GetOrigin()
        spacing = self._ImageData.GetSpacing()

        if self._sMeasurementUnit == "mm":
            pt1 = (round(pt1[0], 3), round(pt1[1], 3), round(pt1[2], 3))
            pt2 = (round(pt2[0], 3), round(pt2[1], 3), round(pt2[2], 3))
            str1 = "(%0.3f,%0.3f,%0.3f) (%0.3f,%0.3f,%0.3f) (mm)" % (pt1[0], pt1[1], pt1[2],
                                                                     pt2[0], pt2[1], pt2[2])
        else:
            pt1 = (round(pt1[0], 3), round(pt1[1], 3), round(pt1[2], 3))
            pt2 = (round(pt2[0], 3), round(pt2[1], 3), round(pt2[2], 3))
            pt1 = ((pt1[0] - origin[0]) / spacing[0], (pt1[1] - origin[
                   1]) / spacing[1], (pt1[2] - origin[2]) / spacing[2])
            pt2 = ((pt2[0] - origin[0]) / spacing[0], (pt2[1] - origin[
                   1]) / spacing[1], (pt2[2] - origin[2]) / spacing[2])
            str1 = "(%0.1f,%0.1f,%0.1f) (%0.1f,%0.1f,%0.1f) (%s)" % (
                pt1[0], pt1[1], pt1[2], pt2[0], pt2[1], pt2[2], "pixels")

        if filename:
            try:
                file = open(filename, 'at')
                file.write(str1)
                file.write("\n")
                file.close()
                results_logger.info(str1)
                logging.info("Saved line length to '%s'" % filename)
            except:
                pass

    def AddObserver(self, event, method):
        # wire observer to the underlying line
        self._Line.AddObserver(event, method)

    def RemoveAllObservers(self):
        self._Line.RemoveAllObservers()

    def RemoveObserver(self, handle):
        # wire observer to the underlying line
        self._Line.RemoveObserver(handle)

    def GetAngles(self):
        if (self._Mark1IsSet == 0) or (self._Mark2IsSet == 0):
            return -1, -1, -1
        p1 = self.GetFirstPoint()
        p2 = self.GetSecondPoint()
        u = [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]]
        d = math.sqrt(u[0] ** 2 + u[1] ** 2 + u[2] ** 2)
        if d > 0:
            x = math.acos(u[0] / d) * 180 / math.pi
            y = math.acos(u[1] / d) * 180 / math.pi
            z = math.acos(u[2] / d) * 180 / math.pi
        else:
            x, y, z = 0.0, 0.0, 0.0

        return x, y, z

    # Draw a small sphere at the point specified.  If the other sphere has
    # already been placed, then draw a line between the two spheres
    def SetPoint(self, pointid, vtkX, vtkY, vtkZ):

        vtkX = round(vtkX, 2)
        vtkY = round(vtkY, 2)
        vtkZ = round(vtkZ, 2)

        if pointid == 0:
            self._Mark1Position = (vtkX, vtkY, vtkZ)
            self._Mark1IsSet = 1
            self._Mark1.SetOpacity(1.0)

        else:
            self._Mark2Position = (vtkX, vtkY, vtkZ)
            self._Mark2IsSet = 1
            self._Mark2.SetOpacity(1.0)
        self._Update()

    def SetFirstPoint(self, x, y, z):
        self.SetPoint(0, x, y, z)

    def SetSecondPoint(self, x, y, z):
        self.SetPoint(1, x, y, z)

    def Translate(self, dx, dy, dz):
        """Translate both sphere marks and line."""
        self._Mark1Position = (self._Mark1Position[0] + dx,
                               self._Mark1Position[1] + dy,
                               self._Mark1Position[2] + dz)

        self._Mark2Position = (self._Mark2Position[0] + dx,
                               self._Mark2Position[1] + dy,
                               self._Mark2Position[2] + dz)

        self._Update()

    def _Update(self):
        """Internal method to update mark and line positions.
        This method is used by SetPoint and Translate to update
        marks and line positions.
        """

        if not (self._Mark1Position and self._Mark2Position):
            return

        x1, y1, z1 = self._Mark1Position
        x2, y2, z2 = self._Mark2Position

        dx, dy, dz = x2 - x1, y2 - y1, z2 - z1

        # sphere marks
        self._Mark1.SetPosition(self._Mark1Position)
        self._Mark1.SetNormal((dx, dy, dz))
        self._Line.SetPoint1(self._Mark1Position)

        self._Mark2.SetPosition(self._Mark2Position)
        self._Mark2.SetNormal((-dx, -dy, -dz))
        self._Line.SetPoint2(self._Mark2Position)

        # draw the line between the two spheres
        self.SetLineOpacity(1)

    # Returns the position of the fist end of the line
    def GetFirstPoint(self):
        return self._Mark1.GetPosition()

    # Returns the position of the second end of the line
    def GetSecondPoint(self):
        return self._Mark2.GetPosition()

    def TransformVector(self, x1, y1, z1):
        # Convert a screen coordinate, returned by a pick event into a warped
        # coordinate.  Used when image is being warped.
        o = self._ImageData.GetOrigin()
        oo = self._ImageData.GetDimensions()
        s = self._ImageData.GetSpacing()
        x = (x1 - o[0]) / s[0] - oo[0] / 2.
        y = (y1 - o[1]) / s[1] - oo[1] / 2.
        z = (z1 - o[2]) / s[2] - oo[2] / 2.
        a, b, c = self._t.GetInverse().TransformVector(x, y, z)
        x1 = (a + oo[0] / 2.) * s[0] + o[0]
        y1 = (b + oo[1] / 2.) * s[1] + o[1]
        z1 = (c + oo[2] / 2.) * s[2] + o[2]
        return x1, y1, z1

    def TriLinearInterpolation(self, x1, y1, z1):
        spacing = self._ImageData.GetSpacing()
        extent = self._ImageData.GetWholeExtent()
        origin = self._ImageData.GetOrigin()

        # now that we have the option for transforms, point data needs to be
        # converted
        if (self._t != None):
            x1, y1, z1 = self.TransformVector(x1, y1, z1)

        xfloor = math.floor((x1 - origin[0]) / spacing[0])
        yfloor = math.floor((y1 - origin[1]) / spacing[1])
        zfloor = math.floor((z1 - origin[2]) / spacing[2])
        xceil = math.ceil((x1 - origin[0]) / spacing[0])
        yceil = math.ceil((y1 - origin[1]) / spacing[1])
        zceil = math.ceil((z1 - origin[2]) / spacing[2])

        if xfloor < extent[0]:
            xfloor = extent[0]
            xceil = extent[0] + 1
        if yfloor < extent[2]:
            yfloor = extent[2]
            yceil = extent[2] + 1
        if zfloor < extent[4]:
            zfloor = extent[4]
            zceil = extent[4] + 1

        if xceil > extent[1]:
            xfloor = extent[1] - 1
            xceil = extent[1]
        if yceil > extent[3]:
            yfloor = extent[3] - 1
            yceil = extent[3]
        if zceil > extent[5]:
            zfloor = extent[5] - 1
            zceil = extent[5]

        x = (x1 - origin[0]) / spacing[0] - xfloor
        y = (y1 - origin[1]) / spacing[1] - yfloor
        z = (z1 - origin[2]) / spacing[2] - zfloor

        if self._ImageData.GetExtent()[5] - self._ImageData.GetExtent()[4] == 0:
            zfloor = self._ImageData.GetExtent()[4]

        func = self._ImageData.GetScalarComponentAsDouble

        GS000 = func(int(xfloor), int(yfloor), int(zfloor), 0)
        GS100 = func(int(xceil), int(yfloor), int(zfloor), 0)
        GS010 = func(int(xfloor), int(yceil), int(zfloor), 0)
        GS001 = func(int(xfloor), int(yfloor), int(zceil), 0)
        GS101 = func(int(xceil), int(yfloor), int(zceil), 0)
        GS011 = func(int(xfloor), int(yceil), int(zceil), 0)
        GS110 = func(int(xceil), int(yceil), int(zfloor), 0)
        GS111 = func(int(xceil), int(yceil), int(zceil), 0)

        InterpolatedGS = (GS000 * (1 - x) * (1 - y) * (1 - z) + GS100 * x * (1 - y) * (1 - z) +
                          GS010 * (1 - x) * y * (1 - z) + GS001 * (1 - x) * (1 - y) * z +
                          GS101 * x * (1 - y) * z + GS011 * (1 - x) * y * z +
                          GS110 * x * y * (1 - z) + GS111 * x * y * z)

        return InterpolatedGS

    def GetCurrentDirectory(self):
            # determine working directory
        curr_dir = os.getcwd()
        config = MicroViewSettings.MicroViewSettings.getObject()

        # over-ride with system-wide directory
        try:
            curr_dir = config.GlobalCurrentDirectory
        except:
            config.GlobalCurrentDirectory = curr_dir
        # over-ride with specific app directory
        try:
            curr_dir = config.LineSegmentCurrentDirectory or curr_dir
        except:
            config.LineSegmentCurrentDirectory = curr_dir

        return curr_dir

    def SaveCurrentDirectory(self, curr_dir):
        config = MicroViewSettings.MicroViewSettings.getObject()
        config.LineSegmentCurrentDirectory = curr_dir

    def WriteFileHeader(self, _file):
        # write out a header
        _file.write('#\n')
        _file.write('# Creation Date: %s\n' %
                    datetime.datetime.now().isoformat())

        # determine image filename
        filename = component.getUtility(
            ICurrentViewportManager).GetPageState().GetFileName()

        if filename:
            filename = filename.encode(sys.getfilesystemencoding() or 'UTF-8')
        else:
            filename = '(unknown)'

        _file.write('# Image filename: %s\n' % filename)
        _file.write('# MicroView Software Version: %s\n' % PACKAGE_VERSION)
        _file.write('# MicroView Software SHA1: %s\n' % PACKAGE_SHA1)
        _file.write('#\n')

    # Write the gray scale values along the line to an ascii file
    def SaveLineGrayScaleValues(self, fmt):

        if (self._Mark1IsSet != 1) or (self._Mark2IsSet != 1):
            return

        x1, y1, z1 = self._Mark1.GetPosition()
        x2, y2, z2 = self._Mark2.GetPosition()

        # calculate the length of the line in pixels
        spacing = self._ImageData.GetSpacing()
        LineLength = math.sqrt(math.pow((x1 - x2) / spacing[0], 2) +
                               math.pow((y1 - y2) / spacing[1], 2) +
                               math.pow((z1 - z2) / spacing[2], 2))

        line = vtk.vtkLineSource()
        line.SetPoint1(x1, y1, z1)
        line.SetPoint2(x2, y2, z2)
        if LineLength < 100:
            NumSegments = 100
        else:
            NumSegments = math.ceil(LineLength)
        line.SetResolution(NumSegments)
        line.Update()

        ft = collections.OrderedDict()
        ft["text file"] = ["*.txt", "*.TXT"]

        curr_dir = self.GetCurrentDirectory()
        filename = EVSFileDialog.asksaveasfilename(
            message='Save Points', filetypes=ft, defaultdir=curr_dir, defaultextension='.txt')

        if not filename:
            return

        curr_dir = os.path.dirname(os.path.abspath(filename))
        if filename:
            self.SaveCurrentDirectory(os.path.abspath(curr_dir))

        if filename:
            if os.path.splitext(filename)[-1].lower() != '.txt':
                filename += ".txt"

            _file = open(filename, 'wt')

            # Write the header.
            self.WriteFileHeader(_file)

            origin = self._ImageData.GetOrigin()
            if self._sMeasurementUnit == "mm":
                # Calculate the length of the line in mm
                LineLength = math.sqrt(math.pow(x1 - x2, 2) + math.pow(
                    y1 - y2, 2) + math.pow(z1 - z2, 2))

                # Calculate point size in mm
                PointSize = LineLength / float(NumSegments)

                _file.write('# %s: %4.3f mm\n' % ("Line Length", LineLength))
                _file.write('# %s: (%4.3f, %4.3f, %4.3f) mm\n' % ("Point 1",
                                                                  x1 -
                                                                  origin[0],
                                                                  y1 -
                                                                  origin[1],
                                                                  z1 - origin[2]))
                _file.write('# %s: (%4.3f, %4.3f, %4.3f) mm\n' % ("Point 2",
                                                                  x2 -
                                                                  origin[0],
                                                                  y2 -
                                                                  origin[1],
                                                                  z2 - origin[2]))
                _file.write('# %s: %7.6f\n#\n' % ("Point Size", PointSize))
            else:
                # Calculate point size in pixels
                PointSize = LineLength / float(NumSegments)

                s = self._ImageData.GetSpacing()
                _file.write('# %s: %4.3f %s\n' % (
                    "Line Length", LineLength, "pixels"))
                _file.write('# %s: (%2.1f, %2.1f, %2.1f) %s\n' % ("Point 1",
                                                                  (x1 - origin[
                                                                      0]) / (
                                                                      float)(
                                                                          s[0]),
                                                                  (y1 - origin[
                                                                      1]) / (
                                                                      float)(
                                                                          s[1]),
                                                                  (z1 - origin[2]) / (
                                                                      float)(
                                                                      s[2]),
                                                                  "pixels"))
                _file.write('# %s: (%2.1f, %2.1f, %2.1f) %s\n' % ("Point 2",
                                                                  (x2 - origin[0]) / (
                                                                      float)(
                                                                      s[0]),
                                                                  (y2 - origin[1]) / (
                                                                      float)(
                                                                      s[1]),
                                                                  (z2 - origin[2]) / (
                                                                      float)(
                                                                      s[2]),
                                                                  "pixels"))
                _file.write('# %s: %7.6f %s\n' % (
                    "Point Size", PointSize, "pixels"))

            # Write the data.
            numScalars = line.GetOutput().GetNumberOfPoints()
            for n in range(numScalars):
                point = line.GetOutput().GetPoint(n)
                GrayScaleValue = self.TriLinearInterpolation(
                    point[0], point[1], point[2])
                if fmt:
                    _file.write("%7.6f, %s" % (
                        PointSize * n, str(GrayScaleValue)))
                else:
                    _file.write(str(GrayScaleValue))
                if n != NumSegments:
                    if fmt:
                        _file.write("\n")
                    else:
                        _file.write(",")

            _file.close()

    def SetLineColor(self, *args):
        if len(args) == 1:
            args = args[0]
        apply(self._LineProperty.SetColor, args)

    def GetLineColor(self):
        return self._LineProperty.GetColor()

    def SetMarker1Color(self, *args):
        if len(args) == 1:
            args = args[0]
        apply(self._Mark1.SetColor, args)

    def GetMarker1Color(self):
        return self._Mark1.GetColor()

    def SetMarker2Color(self, *args):
        if len(args) == 1:
            args = args[0]
        apply(self._Mark1.SetColor, args)

    def GetMarker2Color(self):
        return self._Mark1.GetColor()

    def SetLineOpacity(self, opacity):
        self._LineProperty.SetOpacity(opacity)
        self._Line.Modified()

    def GetLineOpacity(self):
        self._LineProperty.GetOpacity()

    def SetElementSize(self, ElementSize):
        self._ElementSize = ElementSize

    def GetIsLineSet(self):
        return (self._Mark1IsSet == 1) and (self._Mark2IsSet)

    def GetLength(self):
        self._Mark1.GetPosition()
        if (self._Mark1IsSet == 1) and (self._Mark2IsSet):
            (x1, y1, z1) = self._Mark1.GetPosition()
            (x2, y2, z2) = self._Mark2.GetPosition()

            # calculate the length of the line
            if self._sMeasurementUnit == "mm":
                self._LineLength = math.sqrt(math.pow(
                    x1 - x2, 2) + math.pow(y1 - y2, 2) + math.pow(z1 - z2, 2))
            else:
                self._LineLength = math.sqrt(math.pow(x1 / self._ImageData.GetSpacing()[0] - x2 / self._ImageData.GetSpacing()[0], 2) +
                                             math.pow(y1 / self._ImageData.GetSpacing()[1] - y2 / self._ImageData.GetSpacing()[1], 2) +
                                             math.pow(z1 / self._ImageData.GetSpacing()[2] - z2 / self._ImageData.GetSpacing()[2], 2))
        else:
            self._LineLength = 0
        return self._LineLength

    # set this to either "mm" or "pixels"
    def SetMeasurementUnits(self, sMeasurementUnit):
        self._sMeasurementUnit = sMeasurementUnit
        self._Line.Modified()  # notify the observers of self._Line

    def GetPlotWindow(self):
        return self._plotwindow

    def _MakeActors(self):
        actor = self._NewActor()
        actor.SetProperty(self._LineProperty)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(self._Line.GetOutputPort())
        actor.SetMapper(mapper)
        return [actor]

    def AddToRenderer(self, renderer):
        ActorFactory.ActorFactory.AddToRenderer(self, renderer)
        for actor in self._Mark1.GetActors(renderer):
            actor.PickableOn()
        for actor in self._Mark2.GetActors(renderer):
            actor.PickableOn()

        renderer.AddObserver('StartEvent', self.OnRenderEvent)

    def OnRenderEvent(self, renderer, event):
        """Update scale for sphere marks"""
        p1 = self.GetFirstPoint()
        p2 = self.GetSecondPoint()
        x, y, z = (0.5 * (p1[0] + p2[0]),
                   0.5 * (p1[1] + p2[1]),
                   0.5 * (p1[2] + p2[2]))
        camera = renderer.GetActiveCamera()
        if camera.GetParallelProjection():
            worldsize = camera.GetParallelScale()
        else:
            cx, cy, cz = camera.GetPosition()
            d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2)
            worldsize = 2 * d * math.tan(0.5 * camera.GetViewAngle() / 57.296)
        windowWidth, windowHeight = renderer.GetSize()
        if windowWidth > 0 and windowHeight > 0:
            pitch = worldsize / windowHeight
            for mark in (self._Mark1, self._Mark2):
                for actor in mark.GetActors(renderer):
                    actor.SetScale(pitch)

    def GetAnnotateText(self):

        if self._LineProperty.GetOpacity() < 1e-5:
            return ''

        xAngle, yAngle, zAngle = self.GetAngles()
        # A problem exists with VTK font rendering - force windows encoding
        # here
        # locale.getpreferredencoding())
        deg = u'\N{DEGREE SIGN}'.encode('cp1252')
        dims = self._ImageData.GetDimensions()
        ndims = 0
        for i in dims:
            if i > 1:
                ndims += 1

        if ndims == 2:
            angle_label = 'Angle (x,y)'
        else:
            angle_label = 'Angle (x,y,z)'

        if self._sMeasurementUnit == "mm":
            unit_label = '(mm)'
        else:
            unit_label = '(pixels)'

        text = 'Line Length: %1.2f %s' % (self.GetLength(), unit_label)

        if (xAngle == -1) and (yAngle == -1) and (zAngle == -1):
            pass
        else:
            text = text + '\n' + angle_label + ': '
            if ndims == 2:
                text += '%1.1f%s, %1.1f%s' % (xAngle, deg, yAngle, deg)
            else:
                text += '%1.1f%s, %1.1f%s, %1.1f%s' % (
                    xAngle, deg, yAngle, deg, zAngle, deg)

        return text
