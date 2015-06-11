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
Computer statistics of volume of interest using vtkImageStatistics.
   1) mean and standard deviation
   2) histogram
   3) threshold (Otsu method)

Derived From:
   vtkMicroViewEventObject (a concrete implementation of vtkProcessObject)

"""

import math
import numpy
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from zope import component, event
from PI.visualization.common.events import ProgressEvent
from PI.visualization.MicroView import _MicroView

from PI.visualization.MicroView.interfaces import ICurrentImage


class ROIStatistics(object):

    def __init__(self):

        self._imageTransform = None
        self._stencil = None
        self._voiExtent = None
        self._voiPolyData = None

        # create a statistics object
        self._imageStats = _MicroView.vtkImageStatistics()
        self._imageStats.SetProgressText("Calculating image stats...")
        self._imageStats.AddObserver(
            'ProgressEvent', self.HandleVTKProgressEvent)

        # parameters to be calculated
        self._meanValue = None
        self._stdDeviation = None
        self._total = None
        self._voxelCount = None
        self._histogram = None
        self._threshold = None
        self._binSize = 1

    def SetImageTransform(self, transform):
        """Set optionally the transform to the image data."""

        # TODO: this code is broken...

        self._imageTransform = transform
        reslice = vtk.vtkImageReslice()
        reslice.SetInterpolationModeToCubic()
        image = component.getUtility(ICurrentImage)
        reslice.SetInputConnection(image.GetOutputPort())
        reslice.SetResliceTransform(self._imageTransform.GetInverse())
        self._imageStats.SetInputConnection(reslice.GetOutputPort())
        self._imageStats.SetProgressText("Calculating image stats...")

    def SetROIExtent(self, extent):
        """One of the three methods to set the ROI:
        SetROIExtent, SetROIStencilData, SetROIPolyData.
        """
        self._voiExtent = extent

    def SetROIStencilData(self, stencil_data):
        """One of the three methods to set the ROI:
        SetROIExtent, SetROIStencilData, SetROIPolyData.
        """
        self._stencil = stencil_data

        # VTK-6
        if vtk.vtkVersion().GetVTKMajorVersion() > 5:
            self._imageStats.SetStencilData(stencil_data)
        else:
            self._imageStats.SetStencil(stencil_data)

    def SetROIPolyData(self, polydata):
        """One of the three methods to set the xROI:
        SetROIExtent, SetROIStencilData, SetROIPolyData.
        """
        self._voiPolyData = polydata

    def SetBinSize(self, binSize):
        self._binSize = binSize
        # self._imageStats.SetComponentSpacing((binSize, 0.0, 0.0))

    def GetBinSize(self):
        return self._binSize

    def GetMeanValue(self):
        """The mean scalar value of the ROI."""
        self._StatsUpdate1()
        return self._meanValue

    def GetStdDeviation(self):
        """The standard deviation of the ROI."""
        self._StatsUpdate1()
        return self._stdDeviation

    def GetVoxelCount(self):
        """The number of voxels in the ROI."""
        self._StatsUpdate1()
        return self._voxelCount

    def GetTotal(self):
        """The standard deviation of the ROI."""
        self._StatsUpdate1()
        return self._total

    def GetValueRange(self):
        """The range of scalar value of the ROI."""
        self._StatsUpdate1()
        return (self._minValue, self._maxValue)

    def GetHistogram(self):
        """The histogram, a tuples (values, frequencies)"""
        self._CalculateHistogram()
        return self._histogram

    def GetThreshold(self):
        """Otsu threshold of the ROI."""
        self._OtsuThreshold()
        return self._threshold

    def HandleVTKProgressEvent(self, obj, evt):
        """Internal method, observer method to
        the progress event of self._imageStats.
        """
        event.notify(ProgressEvent(
            obj.GetProgressText(), obj.GetProgress()))

    def _StatsUpdate1(self):
        """Calculate mean and standard deviation of volume of interest.
        There are a few ways to define ROI: extent, stencil, and polydata.
        We deal them all here.
        """

        stencil = self._GetStencilData()

        if stencil is None:
            return

        image = component.getUtility(ICurrentImage)

        # since we compute the histogram all the time, ensure that these
        # values are set correctly all the time for multi-component images
        minval, maxval = image.GetScalarRange()
        numOfBins = math.floor((maxval - minval) / self._binSize + 0.5)
        numOfBins = int(numOfBins) + 1
        self._imageStats.SetInputConnection(image.GetOutputPort())
        self._imageStats.SetComponentExtent(0, numOfBins, 0, 0, 0, 0)
        self._imageStats.SetComponentOrigin(
            minval - 0.5 * self._binSize, 0.0, 0.0)
        self._imageStats.SetComponentSpacing(self._binSize, 0.0, 0.0)

        # TODO: figure out why imagestats object isn't updating correctly
        if image.GetMTime() > self._imageStats.GetMTime():
            self._imageStats.Modified()

        self._imageStats.Update()

        self._meanValue = self._imageStats.GetMean()
        self._minValue = self._imageStats.GetMin()
        self._maxValue = self._imageStats.GetMax()
        self._voxelCount = self._imageStats.GetVoxelCount()
        self._stdDeviation = self._imageStats.GetStandardDeviation()
        self._total = self._imageStats.GetTotal()

    def _CalculateHistogram(self):
        """Calculate the histogram of gray scale values
        """

        image = component.getUtility(ICurrentImage)
        stencil_data = self._GetStencilData()
        # stencil_data.Update()  # TODO: VTK-6 figure out what to do here

        image.SetHistogramStencil(stencil_data)
        histo = image.GetHistogramStatistics()
        histo.SetGenerateHistogramImage(False)
        histo.AutomaticBinningOn()
        histo.Update()

        spacing = histo.GetBinSpacing()
        origin = histo.GetBinOrigin()
        arr = histo.GetHistogram()

        n = arr.GetNumberOfTuples()
        x = numpy.linspace(origin, origin + (n - 1) + spacing, num=n)
        y = vtk_to_numpy(arr)

        self._histogram = (x, y)

    def _OtsuThreshold(self):
        """otsu thresholding.
        """

        self._CalculateHistogram()
        xvals, yvals = self._histogram

        if len(xvals) == 0:
            self._threshold = None
            return

        x0 = numpy.array(xvals, 'd')
        h0 = numpy.array(yvals, 'd')

        # ------------ otsu thresholding  ------------------
        h = h0 / numpy.sum(h0)

        # hack for binary image
        if numpy.size(numpy.where(h0 != 0)) == 2:
            self._threshold = (xvals[0] + xvals[-1]) / 2.0
            # print "binary: ", xvals[0], xvals[-1]
            return

        x = numpy.arange(numpy.product(numpy.shape(h)))
        w0 = numpy.cumsum(h)
        w1 = 1 - w0
        eps = 1e-10
        m0 = numpy.cumsum(x * h) / (w0 + eps)
        mt = m0[-1]
        m1 = (mt - m0[0:-1] * w0[0:-1]) / w1[0:-1]
        sB2 = w0[0:-1] * w1[0:-1] * ((m0[0:-1] - m1) ** 2)
        if len(sB2) > 0:
            v = max(sB2)
            t = numpy.nonzero(sB2 == v)[0]
            self._threshold = x0[t[0]]
        else:
            p = numpy.where(h0 > 0)[0][0]
            self._threshold = x0[p]

    def _GetStencilData(self):
        """Internal method to get voi stencil from
        extent, or polydata."""

        if self._stencil:
            return self._stencil

        # either use provided extent or whole image
        if self._voiExtent:
            extent = self._voiExtent
        else:
            extent = component.getUtility(ICurrentImage).GetExtent()

        return self._ExtentToStencilData(extent)

    def _ExtentToStencilData(self, extent):

        image = component.getUtility(ICurrentImage).GetRealImage()

        stencil = vtk.vtkImageStencilData()
        stencil.SetOrigin(image.GetOrigin())
        stencil.SetSpacing(image.GetSpacing())
        stencil.SetExtent(extent)
        stencil.AllocateExtents()
        x0, x1, y0, y1, z0, z1 = extent
        for k in range(z0, z1 + 1):
            for j in range(y0, y1 + 1):
                stencil.InsertNextExtent(x0, x1, j, k)

        return stencil
