from PI.visualization.MicroView._MicroView import *
from zope import interface, event
# don't change this
from PI.visualization.MicroView.interfaces import IImageProcessor
from PI.visualization.common.events import ProgressEvent
from PI.visualization.vtkMultiIO import MVImage

import vtk
import logging
import scipy.ndimage
import skimage.filters
import numpy as np


class MicroViewImageProcessor(object):

    interface.implements(IImageProcessor)

    def ConvertToGrayScale(self, image):
        """Convert Image to grayscale representation"""

        image.SetReleaseDataFlag(1)
        _filter = vtkImageMagnitude2()
        _filter.SetInput(image.GetRealImage())
        _filter.AddObserver('ProgressEvent', self.HandleVTKProgressEvent)
        _filter.SetProgressText("Converting to grayscale...")
        logging.info("Image converted to grayscale")
        _filter.Update()

        return MVImage.MVImage(_filter.GetOutputPort(), input=image)

    def MedianFilter(self, image, kernel_size=3, image3d=True):
        """Returns a median-filtered version of image"""

        image.SetReleaseDataFlag(1)

        ks = int(kernel_size)
        ksx, ksy, ksz = ks, ks, ks

        dims = image.GetDimensions()
        if dims[2] == 1 or image3d == False:
            ksz = 1

        _filter = vtk.vtkImageMedian3D()

        _filter.SetKernelSize(ksx, ksy, ksz)
        _filter.SetInput(image.GetRealImage())
        _filter.SetProgressText("Median filtering image...")
        _filter.AddObserver('ProgressEvent', self.HandleVTKProgressEvent)
        logging.info(
            "Median filter applied with radius={0}".format(kernel_size))
        _filter.Update()

        return MVImage.MVImage(_filter.GetOutputPort(), input=image)

    def UniformFilter(self, image, radius=3, image3d=True):
        """Performs an in-place uniform filter on an image"""

        n = image.get_array()
        dims = n.shape

        if image3d or len(dims) == 2 or dims[0] == 1:
            event.notify(ProgressEvent("Applying uniform filter...", 0.5))
            n[:] = scipy.ndimage.filters.uniform_filter(n, size=radius)
            event.notify(ProgressEvent("Applying uniform filter...", 1.0))
        else:
            # apply slice-by-slice filter
            for z in range(dims[0]):
                event.notify(
                    ProgressEvent("Applying uniform filter...", float(z) / dims[0]))
                n[z, :] = scipy.ndimage.filters.uniform_filter(
                    n[z, :], size=radius)

        # image.GetPointData().GetScalars().Modified()
        image.ScalarsModified()
        event.notify(ProgressEvent("Applying uniform filter...", 1.0))

        logging.info("Uniform filter applied with radius={0}".format(radius))

    def MaximumFilter(self, image, radius=3, image3d=True):
        """Performs an in-place maximum filter on an image"""

        n = image.get_array()
        dims = n.shape

        if image3d or len(dims) == 2 or dims[0] == 1:
            event.notify(ProgressEvent("Applying maximum filter...", 0.5))
            n[:] = scipy.ndimage.filters.maximum_filter(n, size=radius)
            event.notify(ProgressEvent("Applying maximum filter...", 1.0))
        else:
            # apply slice-by-slice filter
            for z in range(dims[0]):
                event.notify(
                    ProgressEvent("Applying maximum filter...", float(z) / dims[0]))
                n[z, :] = scipy.ndimage.filters.maximum_filter(
                    n[z, :], size=radius)

        # image.GetPointData().GetScalars().Modified()
        image.ScalarsModified()
        event.notify(ProgressEvent("Applying maximum filter...", 1.0))

        logging.info("Maximum filter applied with radius={0}".format(radius))

    def MinimumFilter(self, image, radius=3, image3d=True):
        """Performs an in-place minimum filter on an image"""

        n = image.get_array()
        dims = n.shape

        if image3d or len(dims) == 2 or dims[0] == 1:
            event.notify(ProgressEvent("Applying minimum filter...", 0.5))
            n[:] = scipy.ndimage.filters.minimum_filter(n, size=radius)
            event.notify(ProgressEvent("Applying minimum filter...", 0.5))
        else:
            # apply slice-by-slice filter
            for z in range(dims[0]):
                event.notify(
                    ProgressEvent("Applying minimum filter...", float(z) / dims[0]))
                n[z, :] = scipy.ndimage.filters.minimum_filter(
                    n[z, :], size=radius)

        # image.GetPointData().GetScalars().Modified()
        image.ScalarsModified()
        event.notify(ProgressEvent("Applying minimum filter...", 1.0))

        logging.info("Minimum filter applied with radius={0}".format(radius))

    def GaussianFilter(self, image, radius=3, image3d=True):
        """Returns a Gaussian-smoothed version of image"""

        n = image.get_array()
        dims = n.shape

        if image3d or len(dims) == 2 or dims[0] == 1:

            # use VTK here - multithreaded performance
            image.SetReleaseDataFlag(1)

            _filter = vtk.vtkImageGaussianSmooth()
            _filter.SetDimensionality(3)
            _filter.SetRadiusFactor(radius)
            _filter.SetInput(image.GetRealImage())
            _filter.SetProgressText("Applying Gaussian filter...")
            _filter.AddObserver('ProgressEvent', self.HandleVTKProgressEvent)
            _filter.Update()

            image = MVImage.MVImage(_filter.GetOutputPort(), input=image)

        else:
            # apply slice-by-slice filter
            for z in range(dims[0]):
                event.notify(
                    ProgressEvent("Applying slice-by-slice Gaussian filter...", float(z) / dims[0]))
                n[z, :] = scipy.ndimage.filters.gaussian_filter(
                    n[z, :], sigma=radius)
            # image.GetPointData().GetScalars().Modified()
            image.ScalarsModified()
            event.notify(
                ProgressEvent("Applying slice-by-slice Gaussian filter...", 1.0))

        logging.info("Gaussian filter applied with radius={0}".format(radius))

        return image

    def AnisotropicFilter(self, image, num_iterations, diffusion_threshold, diffusion_factor, faces_on=True,
                          edges_on=True, corners_on=True):
        """Returns a edge-preserving smoothed version of image"""
        image.SetReleaseDataFlag(1)

        _filter = vtk.vtkImageAnisotropicDiffusion3D()
        _filter.SetNumberOfIterations(int(num_iterations))
        _filter.SetDiffusionThreshold(float(diffusion_threshold))
        _filter.SetDiffusionFactor(float(diffusion_factor))

        _filter.SetFaces(int(faces_on))
        _filter.SetEdges(int(edges_on))
        _filter.SetCorners(int(corners_on))

        # we need this here because there are two paths into this routine
        if isinstance(image, MVImage.MVImage):
            real_image = image.GetRealImage()
        else:
            real_image = image

        _filter.SetInput(real_image)
        _filter.SetProgressText("Smoothing image...")
        _filter.AddObserver('ProgressEvent', self.HandleVTKProgressEvent)
        logging.info("Anisotropic filter applied")
        _filter.Update()

        return MVImage.MVImage(_filter.GetOutputPort(), input=image)

    def ImageGradientMagnitudeFilter(self, image):
        """Returns the image gradient magnitude of image"""
        image.SetReleaseDataFlag(1)

        _filter = vtk.vtkImageGradientMagnitude()

        # we need this here because there are two paths into this routine
        if isinstance(image, MVImage.MVImage):
            real_image = image.GetRealImage()
        else:
            real_image = image

        _filter.SetInput(real_image)
        _filter.SetProgressText("Calculating Image gradient magnitude...")
        _filter.AddObserver('ProgressEvent', self.HandleVTKProgressEvent)
        logging.info("Image gradient magnitude applied")
        _filter.Update()

        return MVImage.MVImage(_filter.GetOutputPort(), input=image)

    def ImageLaplacianFilter(self, image):
        """Returns the image Laplacian"""
        image.SetReleaseDataFlag(1)

        _filter = vtk.vtkImageLaplacian()

        # we need this here because there are two paths into this routine
        if isinstance(image, MVImage.MVImage):
            real_image = image.GetRealImage()
        else:
            real_image = image

        _filter.SetInput(real_image)
        _filter.SetProgressText("Calculating Image Laplacian...")
        _filter.AddObserver('ProgressEvent', self.HandleVTKProgressEvent)
        logging.info("Image Laplacian applied")

        _filter.Update()

        return MVImage.MVImage(_filter.GetOutputPort(), input=image)

    def DownsampleImage(self, image, nbits=8):
        """Downsamples an image"""

        image.SetReleaseDataFlag(1)

        # get the min and max values from the image
        (minval, maxval) = image.GetScalarRange()

        # create an 8-bit version of this image
        _filter = vtk.vtkImageShiftScale()
        _filter.SetInput(image.GetRealImage())
        _filter.SetShift(-minval)
        try:
            if nbits == 8:
                _filter.SetScale(255.0 / (maxval - minval))
            elif nbits == 16:
                _filter.SetScale(65535.0 / (maxval - minval))
        except ZeroDivisionError:
            logging.exception("DownsampleImage")
            _filter.SetScale(1.0)
        if nbits == 8:
            _filter.SetOutputScalarTypeToUnsignedChar()
        elif nbits == 16:
            _filter.SetOutputScalarTypeToShort()
        elif nbits == 32:
            _filter.SetOutputScalarTypeToFloat()
        elif nbits == 64:
            _filter.SetOutputScalarTypeToDouble()

        _filter.AddObserver('ProgressEvent', self.HandleVTKProgressEvent)
        _filter.SetProgressText("Downsampling to %d-bit..." % nbits)
        logging.info("Image downsampled to {0}-bit".format(nbits))
        _filter.Update()

        return MVImage.MVImage(_filter.GetOutputPort(), input=image)

    def ImageFlip(self, image, axis):
        """Flips image about a given axis, without doubling memory"""

        # image.SetReleaseDataFlag(1)
        _filter = vtkImageInPlaceMirrorFilter()
        _filter.SetAxis(axis)
        _filter.SetInputConnection(image.GetOutputPort())
        _filter.SetProgressText("Flipping image...")
        _filter.AddObserver('ProgressEvent', self.HandleVTKProgressEvent)
        logging.info("Image flipped")
        _filter.Update()

        return MVImage.MVImage(_filter.GetOutputPort(), input=image)

    def AdaptiveThresholdFilter(self, image, radius=20):
        """Apply an adaptive bilateral-mean threshold"""

        from skimage.morphology import disk

        n = image.get_array()
        for z in range(n.shape[0]):
            event.notify(ProgressEvent(
                "Applying bilateral-mean adaptive threshold...", float(z) / n.shape[0]))
            n[z, :, :] = skimage.filters.rank.mean_bilateral(
                n[z, :, :], disk(radius), s0=10, s1=10)
        image.ScalarsModified()
        # image.GetPointData().GetScalars().Modified()

        event.notify(
            ProgressEvent("Applying bilateral-mean adaptive threshold...", 1.0))
        logging.info(
            "Adaptive threshold applied with radius={0}".format(radius))

    def OtsuThresholdFilter(self, image):
        """Apply Otsu threshold"""

        logging.info("Computing Otsu threshold...")
        n = image.get_array()
        threshold = skimage.filters.threshold_otsu(n)
        logging.info("Otsu threshold: {0}".format(threshold))
        n[:] = (n > threshold)
        image.ScalarsModified()

        logging.info("Otsu threshold applied")

    def AdaptiveOtsuThresholdFilter(self, image, min_level=1000.0, max_level=1e34, chunk_size=32):
        """Break image into chunks; threshold each chunk individually

        One notable limitation here - the same threshold is applied for each pixel within each chunk so discontinuities
        likely occur at the boundary between chunks.  A smarter approach would be to perform trilinear interpolation
        across the entire image to find an optimal threshold and use this rather than the chunk-level Otsu value.

        Args:
            arr (np.ndarray): 3D numpy array representing the image
            min_level (float): Optional level to clamp thresholding - this is useful if we land on an image region
                with no signal
            max_level (float): Unused
            chunk_size (int): Size of image region to examine

        """

        # Image is broken into `chunk_size` chunks along each axis
        # min_level applies a cutoff to avoid boosting noise
        # max_level - not sure if this is useful or not

        # access underlying image
        logging.info("Performing Adaptive Otsu thresholding...")
        arr = image.get_array()

        zs, ys, xs = arr.shape
        xn = int(np.ceil(xs / float(chunk_size)))
        yn = int(np.ceil(ys / float(chunk_size)))
        zn = int(np.ceil(zs / float(chunk_size)))

        #thresholds = np.zeros([zn, yn, xn], dtype='float32')

        for z in range(zn):
            for y in range(yn):
                for x in range(xn):
                    arr2 = arr[z * chunk_size:(z + 1) * chunk_size,
                               y * chunk_size:(y + 1) * chunk_size,
                               x * chunk_size:(x + 1) * chunk_size]
                    try:
                        otsu = skimage.filters.threshold_otsu(arr2)
                        # don't let otsu threshold fall below min_level
                        otsu = max(otsu, min_level)
                        # don't let otsu threshold rise above max_level
                        otsu = min(otsu, max_level)
                        #thresholds[z, y, x] = otsu
                        arr2[:] = arr2 > otsu
                    except ValueError:
                        pass

        # reinterpolate threshold image
        #thresholds2 = zoom(thresholds, [float(zs)/zn, float(ys)/yn, float(xs)/xn])

        # finally, threshold image
        #arr[:] = arr > thresholds2

        # image.GetPointData().GetScalars().Modified()
        image.ScalarsModified()

        logging.info("Adaptive Otsu threshold applied")

    def BinaryErodeFilter(self, image, niter):
        """Erode image"""

        logging.info("Eroding image...")
        n = image.get_array()
        n[:] = scipy.ndimage.morphology.binary_erosion(n, iterations=niter)
        # image.GetPointData().GetScalars().Modified()
        image.ScalarsModified()

        logging.info("Binary erosion applied")

    def BinaryDilateFilter(self, image, niter):
        """Dilate image"""

        logging.info("Dilating image...")
        n = image.get_array()
        n[:] = scipy.ndimage.morphology.binary_dilation(n, iterations=niter)
        # image.GetPointData().GetScalars().Modified()
        image.ScalarsModified()

        logging.info("Binary dilation applied")

    def ImageThreshold(self, image, threshold_value):
        """Threshold an image"""

        image.SetReleaseDataFlag(1)
        _filter = vtk.vtkImageThreshold()
        _filter.ReplaceInOn()
        _filter.ReplaceOutOn()
        _filter.SetInValue(1)
        _filter.SetOutValue(0)
        _filter.SetOutputScalarType(3)
        _filter.SetInput(image.GetRealImage())
        _filter.ThresholdByUpper(threshold_value)
        _filter.AddObserver('ProgressEvent', self.HandleVTKProgressEvent)
        _filter.SetProgressText("Thresholding...")
        logging.info("Image thresholded")
        return MVImage.MVImage(_filter.GetOutputPort(), input=image)

    def LabelImageInPlace(self, image):
        """Label a binary image.  Returns number of labels"""

        logging.info("Labelling image...")
        n = image.get_array()
        _label, _n = scipy.ndimage.measurements.label(n)
        n[:] = _label
        # image.GetPointData().GetScalars().Modified()
        image.ScalarsModified()

        logging.info("Image labelled - {0} labels found".format(_n))

        return _n

    def CalculateRegionProps(self, image):
        """Calculate region properties"""

        props = skimage.measure.regionprops(image)

    def ImageInvert(self, image):
        """Inverts an image greylevel values"""

        # image.SetReleaseDataFlag(1)
        _filter = vtkImageInvertFilter()
        _filter.SetInput(image.GetRealImage())
        _filter.AddObserver('ProgressEvent', self.HandleVTKProgressEvent)
        _filter.SetProgressText("Inverting...")
        logging.info("Image inverted")
        return MVImage.MVImage(_filter.GetOutputPort(), input=image)

    def OpenCloseImageFilter(self, image, settings):
        """Open or close an image"""

        image.SetReleaseDataFlag(1)
        _filter = vtk.vtkImageOpenClose3D()
        _filter.SetInput(image.GetRealImage())
        _filter.AddObserver('ProgressEvent', self.HandleVTKProgressEvent)
        _filter.SetProgressText("Opening/Closing...")
        _filter.SetKernelSize(
            settings['KernelSizeX'], settings['KernelSizeY'], settings['KernelSizeZ'])
        _filter.SetOpenValue(settings['OpenValue'])
        _filter.SetCloseValue(settings['CloseValue'])
        logging.info("Open/close filter applied")
        return MVImage.MVImage(_filter.GetOutputPort(), input=image)

    def ComputeDistanceMap(self, image):
        """Compute the Euclidean distance transform of an image"""

        # experimental, in-place scipy work
        logging.info("Computing Euclidean distance transform...")
        n = image.get_array()
        n[:] = scipy.ndimage.morphology.distance_transform_edt(
            n).astype(n.dtype)
        # image.GetPointData().GetScalars().Modified()
        image.ScalarsModified()
        logging.info("Distance transform applied")

        return image

#        _filter = vtk.vtkImageEuclideanDistance()
#        _filter.SetInput(image.GetRealImage())
#        _filter.AddObserver('ProgressEvent', self.HandleVTKProgressEvent)
#        _filter.SetProgressText("Computing distance transform...")
        logging.info("Distance transform applied")

#        _cast = vtk.vtkImageCast()
#        _cast.SetInput(_filter.GetOutput())
#        _cast.SetOutputScalarType(image.GetScalarType())
#        _cast.Update()

        return MVImage.MVImage(_cast.GetOutputPort(), input=image)

    def HandleVTKProgressEvent(self, obj, evt):
        """A VTK object generated a progress event - convert it to a zope-style event"""
        event.notify(ProgressEvent(
            obj.GetProgressText(), obj.GetProgress()))
