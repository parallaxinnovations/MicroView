import logging
import math
import numpy
import vtk
from zope import event
from PI.visualization.MicroView.events import ROIModelTypeChangeEvent, ROIModelOrientationChangeEvent, \
    ROIModelModifiedEvent, ROIModelLinkingChangeEvent, ROIModelControlPointChangeEvent


class ROIModel(object):

    """Contains logic and data for management of cube, spherical and cylindrical ROIs"""

    def __init__(self):

        self.__ROIExtent = None
        self.__ROIBounds = None
        self.__bUseLinking = False
        self.__ImageSpacing = None
        self.__ImageOrigin = None
        self.__ImageExtent = None
        self.__ROIType = None
        self.__ROIOrientation = None
        self.__ROIControlPoints = (None, None)
        self._StencilGenerator = None
        self.__Transform = vtk.vtkTransform()

    def setTransform(self, t):
        # copy transform
        self.__Transform.SetMatrix(t.GetMatrix())
        event.notify(ROIModelModifiedEvent())

    def getModelROITypes(self):
        return 'box', 'cylinder', 'ellipsoid', 'custom'

    def setModelROIType(self, _type):
        assert(isinstance(_type, str))
        assert(_type in self.getModelROITypes())

        dirty = False

        if self.__ROIType != _type:
            self.__ROIType = _type
            dirty = True

        self._StencilGenerator = None

        if dirty:
            event.notify(ROIModelTypeChangeEvent())

    def getModelROIType(self):
        return self.__ROIType

    def setModelROIOrientation(self, o):

        dirty = False

        if self.__ROIOrientation != o:
            self.__ROIOrientation = o
            dirty = True

        self._StencilGenerator = None

        if dirty:
            event.notify(ROIModelOrientationChangeEvent())

    def getModelROIOrientation(self):
        return self.__ROIOrientation

    def setModelROIExtent(self, extent):
        assert(isinstance(extent, tuple))

        # convert extent -> bounds
        bounds = self._ExtentToBounds(extent)

        dirty = False

        if self.__ROIExtent != extent:
            self.__ROIExtent = extent
            self.__ROIBounds = bounds
            dirty = True

        self._StencilGenerator = None

        if dirty:
            event.notify(ROIModelModifiedEvent())

    def getModelROIExtent(self):
        return self.__ROIExtent

    def setModelROIBounds(self, bounds, clear_control_points=True):
        assert(isinstance(bounds, tuple))
        # clear existing control points
        if clear_control_points:
            self.clearROIControlPoints()

        # convert bounds -> extent
        extent = self._BoundsToExtent(bounds)

        # validate the extent
        extent = self._checkExtentInternal(extent)

        # convert extent back to bounds
        bounds = self._ExtentToBounds(extent)

        dirty = False

        if self.__ROIExtent != extent:
            self.__ROIBounds = bounds
            self.__ROIExtent = extent
            dirty = True

        self._StencilGenerator = None

        if dirty:
            event.notify(ROIModelModifiedEvent())

    def getModelROIBounds(self):
        return self.__ROIBounds

    def setModelROILinkingOn(self):
        self.setModelROILinking(True)

    def setModelROILinkingOff(self):
        self.setModelROILinking(False)

    def setModelROILinking(self, linking):
        assert(isinstance(linking, bool))

        dirty = False

        if self.__bUseLinking != linking:
            self.__bUseLinking = linking
            dirty = True

        if dirty:
            event.notify(ROIModelLinkingChangeEvent())

    def getModelROILinking(self):
        return self.__bUseLinking

    def SetInput(self, _input):

        self.__ImageSpacing = _input.GetSpacing()
        self.__ImageOrigin = _input.GetOrigin()
        self.__ImageExtent = _input.GetExtent()

    def getImageSpacing(self):
        return self.__ImageSpacing

    def getImageOrigin(self):
        return self.__ImageOrigin

    def getImageExtent(self):
        return self.__ImageExtent

    def _VoxelToWorld(self, v):
        """Convert point in voxel coordinate
        to world coordinate
        """
        w = list(v)
        for i in range(3):
            w[i] = v[i] * self.__ImageSpacing[i] + self.__ImageOrigin[i]
        return tuple(w)

    def _ExtentToBounds(self, evt):
        """Convert extent to bounds.

        Note that the bounds start at -0.5 and end at 0.5 of the boundary
        voxel centers, i.e. cover all the voxels.
        """

        assert(isinstance(evt, tuple))
        b = [0, 0, 0, 0, 0, 0]
        s = self.getImageSpacing()
        o = self.getImageOrigin()

        for i in range(3):
            b[2 * i] = o[i] + s[i] * (evt[2 * i] - 0.5)
            b[2 * i + 1] = o[i] + s[i] * (evt[2 * i + 1] + 0.5)

        return tuple(b)

    def _BoundsToExtent(self, b):
        """Convert bounds to extent.

        Note that the bounds are shown at -0.5 and +0.5 of
        the centers of boundary voxels.
        """

        assert(isinstance(b, tuple))

        e = [0, 0, 0, 0, 0, 0]
        s = self.getImageSpacing()
        o = self.getImageOrigin()

        for i in range(3):
            # if the span of bounds < 1 pixel this this dimension
            # we have equal extent for this dimension.
            if b[2 * i + 1] - b[2 * i] < s[i]:
                e[2 * i] = int(numpy.round((b[2 * i] - o[i]) / s[i]))
                e[2 * i + 1] = e[2 * i]
            else:
                e[2 * i] = ((b[2 * i] - o[i]) / s[i] + 0.5)
                e[2 * i + 1] = ((b[2 * i + 1] - o[i]) / s[i] - 0.5)

        return tuple(e)

    def _PointsToBounds(self, p1, p2):
        """return bounds defined by two points"""

        assert(isinstance(p1, tuple))
        assert(isinstance(p2, tuple))

        x1, y1, z1 = p1
        x2, y2, z2 = p2

        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        if z1 > z2:
            z1, z2 = z2, z1

        return x1, x2, y1, y2, z1, z2

    def _RoundToNearestVoxelBoundary(self, pos):

        assert(isinstance(pos, tuple))

        s = self.getImageSpacing()
        o = self.getImageOrigin()

        v = [0, 0, 0]
        for i in range(3):
            v[i] = numpy.round((pos[i] - o[i]) / s[i] + 0.5) - 0.5
            v[i] = v[i] * s[i] + o[i]

        return tuple(v)

    def getModelROICenterInPixels(self):

        e = self.getModelROIExtent()
        return (e[0] + e[1]) / 2.0, (e[2] + e[3]) / 2.0, (e[4] + e[5]) / 2.0

    def getModelROICenterInMillimeters(self):

        c = list(self.getModelROICenterInPixels())
        o = self.getImageOrigin()
        s = self.getImageSpacing()

        for i in range(3):
            c[i] = o[i] + (c[i]) * s[i]

        return tuple(c)

    def setModelROISizeInMillimeters(self, size):
        """set the ROI size in millimeters"""

        assert(isinstance(size, tuple))

        size2 = []
        for i in range(3):
            size2.append(size[i] / self.getImageSpacing()[i])
        size2 = tuple(size2)

        return self.setModelROISizeInPixels(size2)

    def setModelROISizeInPixels(self, s):
        """set the ROI size in pixels"""

        assert(isinstance(s, tuple))

        s = list(s)

        # check for linking here
        if self.__bUseLinking:
            old_size = self.getModelROISizeInPixels()
            if s[0] != old_size[0]:
                s = (s[0], s[0], s[2])
            else:
                s = (s[1], s[1], s[2])

        # The size argument here, is really a pixel-based bounds.  Need to subtract
        # one from each component to convert to an extent.
        s = (s[0] - 1, s[1] - 1, s[2] - 1)

        c = self.getModelROICenterInPixels()
        e = [c[0] - s[0] / 2.0, c[0] + s[0] / 2.0, c[1] - s[
            1] / 2.0, c[1] + s[1] / 2.0, c[2] - s[2] / 2.0, c[2] + s[2] / 2.0]

        self.setModelROIExtent(tuple(e))

    def getModelROISizeInPixels(self, e=None):

        if e is None:
            e = self.getModelROIExtent()

        return e[1] - e[0] + 1, e[3] - e[2] + 1, e[5] - e[4] + 1

    def getModelROISizeInMillimeters(self):

        sz = self.getModelROISizeInPixels()
        s = self.getImageSpacing()
        return sz[0] * s[0], sz[1] * s[1], sz[2] * s[2]

    def setModelROICenterInPixels(self, p):
        """
        setModelROICenterInPixels - move the ROI so that it is centered about the given pixel
        """

        assert(isinstance(p, tuple))

        e = self.getModelROIExtent()
        if e is None:
            return
        else:
            e = list(e)

        c = self.getModelROICenterInPixels()
        for i in range(3):
            delta_c = p[i] - c[i]
            e[2 * i] = e[2 * i] + delta_c
            e[2 * i + 1] = e[2 * i + 1] + delta_c

        self.setModelROIExtent(tuple(e))

    def setModelROICenterInMillimeters(self, p):

        assert(isinstance(p, tuple))

        o = self.getImageOrigin()
        s = self.getImageSpacing()
        p = ((p[0] - o[0]) / s[0], (p[1] - o[1]) / s[1], (p[2] - o[2]) / s[2])

        self.setModelROICenterInPixels(p)

    def checkExtentPreserveSize(self):

        e = self._checkExtentInternal(self.getModelROIExtent(), hint='size')
        self.clearROIControlPoints()
        self.setModelROIExtent(tuple(e))

    def checkExtentPreserveCenter(self):

        e = self._checkExtentInternal(self.getModelROIExtent(), hint='center')
        if e is None:
            return
        self.clearROIControlPoints()
        self.setModelROIExtent(tuple(e))

    def _checkExtentInternal(self, e, hint=None):
        """
        Perform integer check on extent
        Perform boundary check on extent
        """

        if e is None:
            return None

        assert(isinstance(e, tuple))

        ei = self.getImageExtent()
        si = (ei[1] - ei[0] + 1, ei[3] - ei[2] + 1, ei[5] - ei[4] + 1)
        sizes = list(self.getModelROISizeInPixels(e))
        e = list(e)

        if hint == 'size':
            # first, sizes _must_ be integral values, so round to nearest int
            # second, sizes must be constrained to be non-zero and smaller than
            # the image itself
            for i in range(3):
                sizes[i] = min(max(numpy.round(sizes[i]), 1), si[i])

            for i in range(3):
                if ((e[2 * i] + 0.5) % 1) == 0:
                    if (sizes[i] % 2) != 0:
                        e[i * 2] = math.floor(e[i * 2])
                    else:
                        e[i * 2] = math.ceil(e[i * 2])
                else:
                    e[i * 2] = numpy.round(e[i * 2])
                e[i * 2 + 1] = e[i * 2] + (sizes[i] - 1)
                if e[i * 2] < ei[i * 2]:
                    e[i * 2] = ei[i * 2]
                    e[i * 2 + 1] = ei[i * 2] + (sizes[i] - 1)
                elif e[i * 2 + 1] > ei[i * 2 + 1]:
                    e[i * 2 + 1] = ei[i * 2 + 1]
                    e[i * 2] = ei[i * 2 + 1] - (sizes[i] - 1)
        elif hint == 'center':
            # TODO: this next line probably does nothing in most situations --
            # are there corner cases?
            e = [numpy.round(i) for i in e]
        else:
            e = [numpy.round(i) for i in e]

        # check bounds against image extent - perform brute force clamping here
        for i in range(3):
            if e[2 * i] < ei[2 * i]:
                e[2 * i] = ei[2 * i]
                e[2 * i + 1] = math.floor(e[2 * i + 1])
            if e[2 * i + 1] > ei[2 * i + 1]:
                e[2 * i + 1] = ei[2 * i + 1]
                e[2 * i] = math.ceil(e[2 * i])

        return tuple(e)

    def setModelDefaultROI(self):
        """Set the extent of the default ROI.

        The default ROI will occupy 1/8th of the image extent in each dimension."""

        e = self.getImageExtent()

        if e is None:
            logging.error('SetModelDefaultROI: Image extent is not valid!')
            return

        xc = (e[1] + e[0]) * 0.5
        yc = (e[3] + e[2]) * 0.5
        zc = (e[5] + e[4]) * 0.5

        xs = (e[1] - e[0]) / 8.0
        ys = (e[3] - e[2]) / 8.0
        zs = (e[5] - e[4]) / 8.0

        # extent of the ROI
        roi_extent = tuple(
            map(int, [xc - xs, xc + xs, yc - ys, yc + ys, zc - zs, zc + zs]))
        self.setModelROIExtent(roi_extent)

    def clearROIControlPoints(self):
        """
        Resets control points
        """
        if self.__ROIControlPoints != (None, None):
            self.__ROIControlPoints = (None, None)
            event.notify(ROIModelControlPointChangeEvent())

    def setModelROIControlPoint(self, index, position):
        """
        Sets a control point for defining the ROI
        """

        assert(index == 0 or index == 1)
        assert(isinstance(position, tuple))

        position = self._RoundToNearestVoxelBoundary(position)

        points = list(self.__ROIControlPoints)
        points[index] = position
        self.__ROIControlPoints = tuple(points)

        # if both point are set, adjust ROI
        if (points[0] is not None) and (points[1] is not None):
            bounds = self._PointsToBounds(points[0], points[1])
            extent = self._BoundsToExtent(bounds)
            extent = self._checkExtentInternal(extent)
            bounds = self._ExtentToBounds(extent)
            self.__ROIBounds = bounds
            self.__ROIExtent = extent
            self._StencilGenerator = None
            event.notify(ROIModelModifiedEvent())

        event.notify(ROIModelControlPointChangeEvent())

    def getModelROIControlPoints(self):
        return self.__ROIControlPoints

    def getModelROIStencil(self):

        import time
        _t0 = time.time()

        t1 = self.__Transform.GetInverse()
        roi_type = self.getModelROIType()
        roi_orientation = self.getModelROIOrientation()

        # bounds, extent and center
        b = self.getModelROIBounds()
        
        # abort early if we haven't been fully set up yet
        if b is None:
            return None

        # determine transformed boundary
        _index = [
            [0, 2, 4], [0, 2, 5], [0, 3, 4], [0, 3, 5],
            [1, 2, 4], [1, 2, 5], [1, 3, 4], [1, 3, 5],
        ]

        b_t = [1e38, -1e38, 1e38, -1e38, 1e38, -1e38]
        is_identity = True

        # is transform identity?
        is_identity = self.__Transform.GetMatrix().Determinant() == 1.0
        #is_identity = False

        for i in range(8):
            i2 = _index[i]
            pt = [b[i2[0]], b[i2[1]], b[i2[2]]]
            _temp = self.__Transform.TransformPoint(pt[0], pt[1], pt[2])
            b_t[0] = min(_temp[0], b_t[0])
            b_t[1] = max(_temp[0], b_t[1])
            b_t[2] = min(_temp[1], b_t[2])
            b_t[3] = max(_temp[1], b_t[3])
            b_t[4] = min(_temp[2], b_t[4])
            b_t[5] = max(_temp[2], b_t[5])

        e_t = self._BoundsToExtent(b_t)

        # sanity check - check for inversion (caused by negative spacing)
        e_t = list(e_t)
        for i in range(3):
            if e_t[i * 2] > e_t[i * 2 + 1]:
                v = e_t[i * 2]
                e_t[i * 2] = e_t[i * 2 + 1]
                e_t[i * 2 + 1] = v

        # expand stencil extent by one pixel on all sides
        e_t = (e_t[0] - 1, e_t[1] + 1, e_t[2] - 1,
               e_t[3] + 1, e_t[4] - 1, e_t[5] + 1)

        # make sure we're dealing with ints
        e_t = map(int, e_t)

        if is_identity:
            # fast, but limited to canonical objects
            self._StencilGenerator = vtk.vtkROIStencilSource()
        else:
            # slow, but more generic
            self._StencilGenerator = vtk.vtkImplicitFunctionToImageStencil()

        self._StencilGenerator.SetOutputOrigin(self.getImageOrigin())
        self._StencilGenerator.SetOutputSpacing(self.getImageSpacing())

        # set extent of stencil - taking into account transformation
        self._StencilGenerator.SetOutputWholeExtent(e_t)

        if is_identity:
            # use DG's fast routines
            if roi_type == 'box':
                self._StencilGenerator.SetShapeToBox()
            elif roi_type == 'cylinder':
                if roi_orientation == 'X':
                    self._StencilGenerator.SetShapeToCylinderX()
                elif roi_orientation == 'Y':
                    self._StencilGenerator.SetShapeToCylinderY()
                elif roi_orientation == 'Z':
                    self._StencilGenerator.SetShapeToCylinderZ()
            elif roi_type == 'ellipsoid':
                self._StencilGenerator.SetShapeToEllipsoid()
            self._StencilGenerator.SetBounds(b)
        else:
            # use JG's slow routines
            if roi_type == 'box':
                obj = vtk.vtkBox()
                obj.SetTransform(t1)
                obj.SetBounds(b)
            elif roi_type == 'cylinder':
                cyl = vtk.vtkCylinder()
                cyl.SetRadius(1.0)

                xc, yc, zc = (b[1] + b[0]) * \
                    0.5, (b[3] + b[2]) * 0.5, (b[5] + b[4]) * 0.5
                diam_a, diam_b, diam_c = (
                    b[1] - b[0]), (b[3] - b[2]), (b[5] - b[4])

                # The cylinder is infinite in extent, so needs to be cropped by using the intersection
                # of three implicit functions -- the cylinder, and two cropping
                # planes
                obj = vtk.vtkImplicitBoolean()
                obj.SetOperationTypeToIntersection()
                obj.AddFunction(cyl)

                clip1 = vtk.vtkPlane()
                clip1.SetNormal(0, 1, 0)
                obj.AddFunction(clip1)

                clip2 = vtk.vtkPlane()
                clip2.SetNormal(0, -1, 0)
                obj.AddFunction(clip2)

                t2 = vtk.vtkTransform()
                t2.Translate(xc, yc, zc)

                if roi_orientation == 'X':
                    # cylinder is infinite in extent in the y-axis
                    t2.Scale(1, diam_b / 2.0, diam_c / 2.0)
                    t2.RotateZ(90)
                    r = diam_a / 2.0
                elif roi_orientation == 'Y':
                    # cylinder is infinite in extent in the y-axis
                    t2.Scale(diam_a / 2.0, 1, diam_c / 2.0)
                    r = diam_b / 2.0
                elif roi_orientation == 'Z':
                    # cylinder is infinite in extent in the y-axis
                    t2.Scale(diam_a / 2.0, diam_b / 2.0, 1)
                    t2.RotateX(90)
                    r = diam_c / 2.0

                clip1.SetOrigin(0, r, 0)
                clip2.SetOrigin(0, -r, 0)

                # combine transforms
                t2.SetInput(self.__Transform)

                obj.SetTransform(t2.GetInverse())

            elif roi_type == 'ellipsoid':
                obj = vtk.vtkSphere()
                obj.SetRadius(1.0)

                xc, yc, zc = (b[1] + b[0]) * \
                    0.5, (b[3] + b[2]) * 0.5, (b[5] + b[4]) * 0.5
                diam_a, diam_b, diam_c = (
                    b[1] - b[0]), (b[3] - b[2]), (b[5] - b[4])

                t2 = vtk.vtkTransform()
                t2.Translate(xc, yc, zc)
                t2.Scale(diam_a / 2.0, diam_b / 2.0, diam_c / 2.0)

                # combine transforms
                t2.SetInput(self.__Transform)

                obj.SetTransform(t2.GetInverse())

            self._StencilGenerator.SetInput(obj)

        _t1 = time.time()
        self._StencilGenerator.Update()
        _t2 = time.time()
        return self._StencilGenerator.GetOutput()
