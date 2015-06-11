import math
from vtkAtamai import ActorFactory, VolumeFactory
import vtk


class VolumeFactory2(VolumeFactory.VolumeFactory):

    def __init__(self):
        VolumeFactory.VolumeFactory.__init__(self)

        #
        # Dabble with GPU
        #
        self._GPUVolumeRayCastMapper = vtk.vtkGPUVolumeRayCastMapper()

    def SetInput(self, image):
        VolumeFactory.VolumeFactory.SetInput(self, image)
        spacing = map(abs, image.GetSpacing())
        dim = image.GetDimensions()

        # determine memory used by this reslice object
        s = image.GetScalarSize() * dim[0] * dim[1] * dim[2]
        factor = max(1.0, float(s) / (150 * 1024 * 1024))
        factor = 1.0

        self._RayCastReslice.SetOutputSpacing(spacing[
                                              0] * factor, spacing[1] * factor, spacing[2] * factor)
        self.SetLowQuality()
        self._RayCastReslice.UpdateWholeExtent()

        #
        # Dabble with GPU
        #
        # JDG
        # self._GPUVolumeRayCastMapper.SetVolumeRayCastFunction(self.GetRayCastFunction())
        self._GPUVolumeRayCastMapper.SetClippingPlanes(
            self._ClippingCube.GetClippingPlanes())
        self._GPUVolumeRayCastMapper.AutoAdjustSampleDistancesOn()
        self._GPUVolumeRayCastMapper.SetInput(image)

    def SetHighQuality(self):
        image = self._VolumeRayCastMapper.GetInput()

        # update image information (VTK-6 compatible)
        image.GetProducerPort().GetProducer().UpdateInformation()

        spacing = image.GetSpacing()
        self._VolumeRayCastMapper.SetSampleDistance(max(spacing) * 0.5)
        self._VolumeProperty.SetInterpolationTypeToLinear()
        self.Modified()

    def SetLowQuality(self):
        image = self._VolumeRayCastMapper.GetInput()

        # update image information (VTK-6 compatible)
        image.GetProducerPort().GetProducer().UpdateInformation()

        spacing = image.GetSpacing()
        self._VolumeRayCastMapper.SetSampleDistance(max(spacing) * 2.0)
        self._VolumeProperty.SetInterpolationTypeToNearest()
        self.Modified()

    def SetRayCastFunction(self, f):
        self._rayCastFunction = f
        self._VolumeRayCastMapper.SetVolumeRayCastFunction(
            self._rayCastFunction)

    def GetRayCastFunction(self):
        return self._VolumeRayCastMapper.GetVolumeRayCastFunction()

    def GetVolumeRayCastMapper(self):
        return self._VolumeRayCastMapper

    def GetGPUVolumeRayCastMapper(self):
        return self._GPUVolumeRayCastMapper

    def GetLODProp3D(self):
        return self._Volume

    def AddRayCasting(self):
        # over-ride some functionality here
        lods = self.GetLODIds()

        # delete high quality texture mapping
        self.GetLODProp3D().RemoveLOD(lods[1])
        lods = lods[0:]
        idRC = self.GetLODProp3D().AddLOD(self.GetGPUVolumeRayCastMapper(),
                                          self.GetVolumeProperty(),
                                          0.5)
        self.GetLODProp3D().SetLODLevel(idRC, 0.0)

    def GetPickList(self, event):
        # get a list of PickInformation objects, one for each picked actor

        # first query the clipping cube
        picklist = self._ClippingCube.GetPickList(event)

        # using isosurface?
        isiso = self.GetRayCastFunction().IsA(
            'vtkVolumeRayCastIsosurfaceFunction')
        threshold = 0
        if isiso:
            threshold = self.GetRayCastFunction().GetIsoValue()

        if len(picklist) == 1:
            info = ActorFactory.PickInformation()
            event.renderer.SetDisplayPoint(event.x, event.y, 0.0)
            event.renderer.DisplayToWorld()
            info.position = event.renderer.GetWorldPoint()[0:3]
            info.normal = event.renderer.GetActiveCamera().GetViewPlaneNormal()
            info.vector = event.renderer.GetActiveCamera().GetViewUp()
            picklist.append(info)

        # if we have entrance and exit points,
        if len(picklist) == 2:
            discardedinfo = None

            point1 = picklist[0].position
            point2 = picklist[1].position
            vec = (point2[0] - point1[0],
                   point2[1] - point1[1],
                   point2[2] - point1[2])
            pathlength = math.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)

            # determine scalefactor - use 5% of minimum dimension as threshold,
            # rather than 1 mm (this was the old setting)
            ex = self.GetInput().GetWholeExtent()
            sp = self.GetInput().GetSpacing()
            v = min((ex[1] - ex[0] + 1) * sp[0], (ex[3] - ex[
                    2] + 1) * sp[1], (ex[5] - ex[4] + 1) * sp[2])
            if pathlength < 0.05 * v:
                hitVolume = 1
            else:
                hitVolume = 0

            # set up an implicit function that we can query
            vol = self._ImplicitVolume
            if self._OpacityTransferFunction:
                vol.SetOutValue(0.0)
            else:
                vol.SetOutValue(self._LookupTable.GetTableRange()[0])
                table = self._LookupTable
                _range = table.GetTableRange()
                maxidx = table.GetNumberOfColors() - 1

            if self._PickThreshold > 0.0 and not hitVolume:
                # cast a ray into the volume from one side

                # get mininum voxel spacing
                spacing = min(map(abs, self._Input.GetSpacing()))

                # get the number of steps required along the length
                N = int(math.ceil(abs(pathlength / spacing)))
                dx, dy, dz = (vec[0] / N, vec[1] / N, vec[2] / N)
                dr = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)

                transparency = 1.0
                x0, y0, z0 = point1
                for i in range(N):
                    x = x0 + i * dx
                    y = y0 + i * dy
                    z = z0 + i * dz
                    value = vol.FunctionValue(
                        x + dx / 2, y + dy / 2, z + dz / 2)
                    if self._OpacityTransferFunction:
                        alpha = self._OpacityTransferFunction.GetValue(value)
                    else:
                        idx = int(round((value - _range[0]) /
                                        (_range[1] - _range[0]) * maxidx))
                        if idx < 0:
                            idx = 0
                        elif idx > maxidx:
                            idx = maxidx
                        alpha = table.GetTableValue(idx)[3]
                    transparency = transparency * math.pow(1.0 - alpha, dr)
                    # check if opacity is greater than threshold
                    if ((not isiso) and ((1.0 - transparency) > self._PickThreshold)) or (isiso and (value > threshold)):
                        if i != 0:
                            picklist[0].position = (x, y, z)
                            gx, gy, gz = vol.FunctionGradient(x, y, z)
                            picklist[0].normal = (-gx, -gy, -gz)
                        hitVolume = 1
                        break
                    table = self._LookupTable
                    if discardedinfo:
                        picklist[0] = discardedinfo

                if hitVolume:
                    # cast a ray into the volume from the other side
                    x1, y1, z1 = point2
                    transparency = 1.0
                    for i in range(N):
                        x = x1 - i * dx
                        y = y1 - i * dy
                        z = z1 - i * dz
                        value = vol.FunctionValue(
                            x - dx / 2, y - dy / 2, z - dz / 2)
                        if self._OpacityTransferFunction:
                            alpha = \
                                self._OpacityTransferFunction.GetValue(value)
                        else:
                            idx = int(round((value - range[0]) /
                                            (range[1] - range[0]) * maxidx))
                            if idx < 0:
                                idx = 0
                            elif idx > maxidx:
                                idx = maxidx
                            alpha = table.GetTableValue(idx)[3]
                        transparency = transparency * math.pow(1.0 - alpha, dr)
                        if ((not isiso) and ((1.0 - transparency) > self._PickThreshold)) or (isiso and (value > threshold)):
                            if i != 0:
                                picklist[1].position = (x, y, z)
                                gx, gy, gz = vol.FunctionGradient(x, y, z)
                                picklist[1].normal = (-gx, -gy, -gz)
                            break
                else:
                    picklist = []

        for child in self._Children:
            if child != self._ClippingCube:    # already done it
                picklist = picklist + child.GetPickList(event)

        return picklist
