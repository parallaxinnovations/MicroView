import appdirs
import logging
import numpy as np
import os
import dicom
import re
import sys
import vtk
import wx
from vtk.util import vtkImageExportToArray

from PI.visualization.vtkMultiIO import vtkLoadReaders
from PI.dicom import dicomdir
import MicroViewIO
from PI.visualization.common import MicroViewSettings, MicroViewObjectShelve
import ImageImportDialog


class InvalidParameter(Exception):
    pass


class ImageImportDialogSettings(object):

    """Encapsulates settings for the image import dialog"""

    def __init__(self):

        self.file_template = 'image###.png'
        self.first_number = 0
        self.last_number = 0
        self.x_spacing = 1.0
        self.y_spacing = 1.0
        self.z_spacing = 1.0
        self.bIsRawImage = True
        self.bShouldIConvertToGreyscale = False
        self.bIs3DImage = False
        self.header_size = 0
        self.data_type = 'short'
        self.data_endian = 'little endian'
        self.number_channels = 1
        self.x_size = 512
        self.y_size = 512
        self.z_size = 1


class ImageImportDialogC(ImageImportDialog.ImageImportDialog):

    """
    A customized image input dialog.
    """

    def __init__(self, parent):

        # Start by calling base class constructor
        ImageImportDialog.ImageImportDialog.__init__(self, parent)

        self._imageData = None
        self._savedFileName = None
        self.bIsDICOM = None
        self._dicomdir = None
        self._file_list = []
        self._showHelp = None
        self._installdir = os.path.abspath(sys.path[0])
        plugindir = os.path.join(self._installdir, "Plugins")
        self._reader, formats = vtkLoadReaders.LoadImageReaders(
            directories=[plugindir, os.path.join(appdirs.user_data_dir("MicroView", "Parallax Innovations"), "Plugins")])
        self.SetSize(self.GetBestSize())

        # Load settings
        self.LoadSettings()

        # disable most of the dialog
        self.m_panelMainDialog.Enable(False)
        self.m_buttonOK.Enable(False)

    def LoadSettings(self):

        root = MicroViewObjectShelve.MicroViewObjectShelve.getObject(
        ).getRoot()

        if 'options.ImageImportDialog' not in root or not isinstance(root['options.ImageImportDialog'], ImageImportDialogSettings):
            root['options.ImageImportDialog'] = ImageImportDialogSettings()
        state = root['options.ImageImportDialog']

        self.m_filePicker.SetPath(state.file_template)
        self.m_spinCtrlFirstNum.SetValue(int(state.first_number))
        self.m_spinCtrlLastNum.SetValue(int(state.last_number))
        self.m_textCtrlXSpacing.ChangeValue(str(state.x_spacing))
        self.m_textCtrlYSpacing.ChangeValue(str(state.y_spacing))
        self.m_textCtrlZSpacing.ChangeValue(str(state.z_spacing))
        self.m_checkRawImage.SetValue(state.bIsRawImage)
        self.m_panelRawParameters.Enable(state.bIsRawImage)
        self.m_checkConvertToGrayscale.SetValue(
            state.bShouldIConvertToGreyscale)
        self.m_check3DImage.SetValue(state.bIs3DImage)
        self.m_textCtrlHeaderSize.ChangeValue(str(state.header_size))
        self.m_choiceDataType.SetStringSelection(state.data_type)
        self.m_choiceDataEndian.SetStringSelection(state.data_endian)
        self.m_textCtrlNumberChannels.ChangeValue(str(state.number_channels))
        self.m_textCtrlXSize.ChangeValue(str(state.x_size))
        self.m_textCtrlYSize.ChangeValue(str(state.y_size))
        self.m_textCtrlZSize.SetValue(str(state.z_size))

        # set button states
        self.m_panelRawParameters.Enable(state.bIsRawImage)
        self.m_checkBoxFlipImage.Enable(state.bIsRawImage)
        if not state.bIsRawImage:
            self.m_checkBoxFlipImage.SetValue(False)

        self.m_textCtrlZSize.Enable(state.bIs3DImage)

    def SaveSettings(self):

        root = MicroViewObjectShelve.MicroViewObjectShelve.getObject(
        ).getRoot()

        if 'options.ImageImportDialog' not in root or not isinstance(root['options.ImageImportDialog'], ImageImportDialogSettings):
            root['options.ImageImportDialog'] = ImageImportDialogSettings()
        state = root['options.ImageImportDialog']

        state.file_template = self.m_filePicker.GetPath()
        state.first_number = int(self.m_spinCtrlFirstNum.GetValue() or 0)
        state.last_number = int(self.m_spinCtrlLastNum.GetValue() or 0)
        state.x_spacing = self.m_textCtrlXSpacing.GetValue()
        state.y_spacing = self.m_textCtrlYSpacing.GetValue()
        state.z_spacing = self.m_textCtrlZSpacing.GetValue()
        state.bIsRawImage = self.m_checkRawImage.GetValue()
        state.bShouldIConvertToGreyscale = self.m_checkConvertToGrayscale.GetValue(
        )
        state.bIs3DImage = self.m_check3DImage.GetValue()
        state.header_size = self.m_textCtrlHeaderSize.GetValue()
        state.data_type = self.m_choiceDataType.GetStringSelection()
        state.data_endian = self.m_choiceDataEndian.GetStringSelection()
        state.number_channels = self.m_textCtrlNumberChannels.GetValue()
        state.x_size = self.m_textCtrlXSize.GetValue()
        state.y_size = self.m_textCtrlYSize.GetValue()
        state.z_size = self.m_textCtrlZSize.GetValue()

        root['options.ImageImportDialog'] = state
        root.sync()

    def isGrayScaleRequested(self):
        return self.m_checkConvertToGrayscale.IsChecked()

    def ImageSizeOk(self, szInBytes):
        """Check the size of imported image to see
        if it will fit into memory. This seems only an issue for
        windows only.
        """

        if szInBytes <= 0:
            return False

        if sys.platform != 'win32':
            # assume we're okay
            return True

        # 64 bit check - this should cause x64 to ignore code after this check
        if sys.maxsize > (2 ** 31 - 1):
            return True

        max_volume_size = 840 * 1024 * 1024

        return szInBytes <= max_volume_size

    def updateGUIState(self):

        self.m_textCtrlXSpacing.Enable(not self.bIsDICOM)
        self.m_textCtrlYSpacing.Enable(not self.bIsDICOM)
        self.m_textCtrlZSpacing.Enable(not self.bIsDICOM)
        self.m_spinCtrlFirstNum.Enable(not self.bIsDICOM)
        self.m_spinCtrlLastNum.Enable(not self.bIsDICOM)
        self.m_staticText2.Enable(not self.bIsDICOM)
        self.m_staticText3.Enable(not self.bIsDICOM)
        self.m_staticText4.Enable(not self.bIsDICOM)
        self.m_staticText5.Enable(not self.bIsDICOM)
        self.m_staticText6.Enable(not self.bIsDICOM)
        self.m_checkRawImage.Enable(not self.bIsDICOM)
        self.m_check3DImage.Enable(not self.bIsDICOM)

        if self.bIsDICOM:
            self.m_spinCtrlFirstNum.SetValue(0)
            self.m_spinCtrlLastNum.SetValue(0)
        else:
            if len(self._num_list) > 0:
                self.m_spinCtrlFirstNum.SetValue(int(self._num_list[0]))
                last_val = int(self._num_list[-1])
                self.m_spinCtrlLastNum.SetValue(last_val)
                self.m_textCtrlZSize.SetValue(str(last_val))
            else:
                self.m_spinCtrlFirstNum.SetValue(0)
                self.m_spinCtrlLastNum.SetValue(0)
                if self.m_check3DImage.GetValue() == 0:
                    self.m_textCtrlZSize.SetValue('1')

    def updateButtonState(self, evt=None):

        # first, update memory usage
        bShouldEnable = self.updateMemoryUsage()

        if bShouldEnable:

            # check additional fields
            try:
                if not (float(self.m_textCtrlXSpacing.GetValue()) != 0):
                    raise Exception("X value is invalid")
                if not (float(self.m_textCtrlYSpacing.GetValue()) != 0):
                    raise Exception("Y value is invalid")
                if not (float(self.m_textCtrlZSpacing.GetValue()) != 0):
                    raise Exception("Z value is invalid")
            except:
                bShouldEnable = False

        self.m_buttonOK.Enable(bShouldEnable)
        self.m_buttonUpdate.Enable(bShouldEnable)

    def updateMemoryUsage(self, evt=None):

        colour = (0, 255, 0)

        # determine memory requirements if the user is to load image
        dt = self.m_choiceDataType.GetStringSelection()
        if dt in ('char', 'unsigned char'):
            element_size = 8
        elif dt in ('short', 'unsigned short'):
            element_size = 16
        elif dt in ('int', 'unsigned int', 'float'):
            element_size = 32
        elif dt == 'double':
            element_size = 64
        else:
            raise InvalidParameter("Unsupported image data type")

        sz_label = 'unknown'
        sz = -1

        try:
            numberOfChannels = int(self.m_textCtrlNumberChannels.GetValue())
            convert_to_grayscale = self.m_checkConvertToGrayscale
            if numberOfChannels == 1:
                convert_to_grayscale.SetValue(False)
                convert_to_grayscale.Enable(False)
            else:
                convert_to_grayscale.Enable(True)
            if convert_to_grayscale.IsChecked():
                numberOfChannels = 1

            bFormatError = False
            xsize = ysize = 0

            try:
                xsize = int(self.m_textCtrlXSize.GetValue())
                ysize = int(self.m_textCtrlYSize.GetValue())
            except:
                bFormatError = True

            if self.m_check3DImage.GetValue() is True:
                try:
                    zsize = int(self.m_textCtrlZSize.GetValue())
                except:
                    zsize = 1
                    bFormatError = True
            else:
                try:
                    firstnum = int(self.m_spinCtrlFirstNum.GetValue())
                    lastnum = int(self.m_spinCtrlLastNum.GetValue())
                    zsize = max(firstnum, lastnum) - min(firstnum, lastnum) + 1
                except:
                    zsize = 1

            if self.bIsDICOM:
                zsize = len(self._slice_locations)

            if bFormatError:
                sz_label = '* Error *'
            else:
                sz = xsize * ysize * zsize * \
                    element_size * numberOfChannels / 8
                sz_gb = sz / 1024 / 1024 / 1024.
                if sz_gb > 1.0:
                    sz_label = '%0.4g GiB' % (sz / 1024 / 1024 / 1024.)
                else:
                    sz_label = '%0.4g MiB' % (sz / 1024 / 1024.)

            # sanity check
            try:
                header_size = int(self.m_textCtrlHeaderSize.GetValue())
            except:
                header_size = -1
                logging.warning(
                    "header size parse error: {0}".format(header_size))

            if ((xsize <= 0) or (ysize <= 0) or (zsize <= 0) or
                    (numberOfChannels <= 0) or (header_size < 0)):
                sz_label = 'invalid parameter'
                raise InvalidParameter("Invalid parameter")

        except:
            logging.exception("ImageImportDialog")
            colour = (255, 0, 0)

        self.m_staticTextMemoryLabel.SetLabel(sz_label)
        if sz_label != 'unknown':
            if not self.ImageSizeOk(sz):
                colour = (255, 0, 0)
        self.m_staticTextMemoryLabel.SetForegroundColour(colour)

        return colour != (255, 0, 0)

    def SetHelpCommand(self, helpCommand):
        self._showHelp = helpCommand

    def GetFileList(self):
        return self._file_list

    def guess_image_pixel_size(self, full_name):
        # try to guess what the pixel size is
        try:
            self._reader.SetFileName(full_name)

            # if we can identify the file, reader._reader will be something
            # other than None

            if self._reader._reader is not None:
                o = self._reader.GetOutput()

                if vtk.vtkVersion().GetVTKMajorVersion() > 5:
                    o.Update()
                else:
                    # this is undesirable...
                    o.Update()

                # if we got this far, the images are known to us
                self.m_textCtrlNumberChannels.ChangeValue(
                    str(o.GetNumberOfScalarComponents()))

                spacing = list(o.GetSpacing())

                if self.bIsDICOM:
                    indices = [0]
                    if len(self._slice_locations) > 1:
                        # get sorted indices
                        indices = np.argsort(
                            np.array([float(f) for f in self._slice_locations]))
                        spacing[-1] = self._slice_locations[indices[1]] - \
                            self._slice_locations[indices[0]]

                self.SetSpacing(spacing)
                # update dimensions without reading image
                x0, x1, y0, y1, z0, z1 = o.GetWholeExtent()
                x = x1 - x0 + 1
                y = y1 - y0 + 1
                z = z1 - z0 + 1
                self.m_textCtrlXSize.ChangeValue(str(x))
                self.m_textCtrlYSize.ChangeValue(str(y))

                num_slices = z
                if self.bIsDICOM:
                    num_slices = len(indices)

                if num_slices > 1:
                    self.m_textCtrlZSize.ChangeValue(str(num_slices))
                    self.m_spinCtrlFirstNum.SetValue(0)
                    self.m_spinCtrlLastNum.SetValue(0)
                    if not self.bIsDICOM:
                        self.m_check3DImage.SetValue(True)

                # we know about this file type, so it isn't raw
                self.m_checkRawImage.SetValue(False)
                self.m_checkBoxFlipImage.Enable(False)

                # dicom images need flipping?
                #if self.bIsDICOM:
                #    self.m_checkBoxFlipImage.SetValue(True)
                #else:
                #    self.m_checkBoxFlipImage.SetValue(False)

                self.m_panelRawParameters.Enable(False)

                # update scalar type
                scalar_type = o.GetScalarType()

                obj = self.m_choiceDataType

                if scalar_type == 3:
                    obj.SetStringSelection('unsigned char')
                elif scalar_type == 5:
                    obj.SetStringSelection('unsigned short')
                elif scalar_type == 4:
                    obj.SetStringSelection('short')
                elif scalar_type == 6:
                    obj.SetStringSelection('int')
                elif scalar_type == 10:
                    obj.SetStringSelection('float')
                elif scalar_type == 11:
                    obj.SetStringSelection('double')

                # determine byte order
                order = self._reader.GetDataByteOrder()
                self.m_choiceDataEndian.SetSelection(1 - order)

            else:
                # We've failed to identify file type - must be raw
                self.m_checkRawImage.SetValue(True)
                self.m_panelRawParameters.Enable(True)
                self.m_checkBoxFlipImage.Enable(True)
                self.m_textCtrlImageTitle.ChangeValue("Raw Data Import")
        except:
            logging.exception("ImageImportDialog")

    def update_file_list(self, full_name, ds, examiner):

        _dir, fname = os.path.split(full_name)

        if self.bIsDICOM:
            examiner.ExamineDirectory(self.match_tags)
            self._dicomdir = examiner.GetDICOMDIR()
            series = examiner.GetSeriesInfo()
            series_number = ds.get('SeriesNumber')
            acq_number = ds.get('AcquisitionNumber')
            label = '{0}.{1}'.format(series_number, acq_number)
            if series_number is not None:
                self._file_list = series[label]
                self._slice_locations = examiner.GetSeriesSliceLocations()[
                    label]

                # sanity check
                bad_slice_thickness = False
                s = map(float, self._slice_locations[:])
                s.sort()
                if len(s) < 2:
                    diff = s[1] - s[0]
                    for i in range(len(s) - 1):
                        epsilon = (s[i + 1] - s[i]) - diff
                        if abs(epsilon) > 1e-3:
                            bad_slice_thickness = True
                            break
                if bad_slice_thickness:
                    dlg = wx.MessageDialog(wx.GetApp().GetTopWindow(),
                                           "Slice thickness is not fixed!  Image will be distorted.", 'Warning', wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()

            else:
                self._file_list = examiner.GetDICOMFilenames()
                self._slice_locations = []
            self._num_list = [0, 0]
        else:
            patt = re.compile('(\d+)\D*$')
            matchobj = patt.search(fname)
            self._num_list = []
            self._file_list = []
            if matchobj:
                start = matchobj.start()
                theNumbers = matchobj.group(1)
                n = len(theNumbers)

                # tack directory back onto basename
                start += (len(_dir) + 1)

                template = full_name[:start] + '#' * n + full_name[start + n:]
                self.m_filePicker.SetPath(template)

                # find the numbers
                patt = os.path.basename(full_name[
                                        :start]) + '(' + '\d' * n + ')' + full_name[start + n:]
                patt = re.compile(patt)
                for f in os.listdir(os.path.dirname(full_name)):
                    mobj = patt.search(f)
                    if mobj:
                        self._num_list.append(int(mobj.group(1)))
                        self._file_list.append(f)
                self._num_list.sort()
            else:
                self.m_filePicker.SetPath(full_name)

    def BrowseFile(self, fname):
        """Allows the user to select a filename"""

        self._savedFileName = fname
        self._reader._reader = None
        full_name = os.path.abspath(fname)
        _dir, fname = os.path.split(full_name)

        self._num_list = []

        self._file_list = [full_name]
        self._slice_locations = []

        # is file a DICOM file?
        ds = {}
        examiner = MicroViewIO.wxMicroViewDICOMExaminer(_dir)
        self.bIsDICOM = examiner.IsDICOMFile(full_name)

        self.match_tags = {}

        if self.bIsDICOM:

            try:
                ds = dicom.read_file(
                    full_name, stop_before_pixels=True, force=True)
                if 'PhotometricInterpretation' not in ds:
                    self.bIsDICOM = False
                if 'AcquisitionNumber' in ds:
                    self.bHasAcquisitionNumber = True

                tags = ['StudyID', 'SeriesNumber', 'AcquisitionNumber']
                if ds.Modality == 'MR':
                    tags.append('EchoNumbers')

                for tag in tags:
                    if tag in ds:
                        self.match_tags[tag] = ds.get(tag)
            except:
                pass

        with wx.BusyCursor():
            self.update_file_list(full_name, ds, examiner)

            # update DICOMDIR file
            if self.bIsDICOM:
                dicomdir_filename = os.path.join(_dir, 'DICOMDIR')
                dicomdir = examiner.GetDICOMDIR().get_dicomdir()
                if dicomdir:
                    try:
                        dicom.write_file(dicomdir_filename, dicomdir)
                        logging.info(
                            "Successfully wrote {}.".format(dicomdir_filename))
                    except:
                        pass

        self.guess_image_pixel_size(full_name)

        self.updateGUIState()
        self.updateButtonState()

        # if files are DICOM-format, fill in a reasonable guess at a name
        if self.bIsDICOM:
            name = ''
            if 'StudyID' in ds:
                name += '{}_'.format(ds.StudyID)
            if 'SeriesDescription' in ds:
                name += '{}_'.format(ds.SeriesDescription.strip()
                                     ).replace(' ', '_')
            if 'PatientName' in ds:
                name += '{}'.format(ds.PatientName.strip()).replace(' ', '_')
            if not name:
                name = "DICOM Import"

            self.m_textCtrlImageTitle.SetValue(name)

    def ToggleRawImageReader(self, evt):

        # get a handle on part of the GUI - we'd like to enable or disable all the children
        # contained within the 'Raw Params' static box sizer
        self.m_panelRawParameters.Enable(evt.IsChecked())
        self.m_checkBoxFlipImage.Enable(evt.IsChecked())
        if not evt.IsChecked():
            self.m_checkBoxFlipImage.SetValue(False)

    def ToggleGrayScale(self, evt):
        self.updateButtonState()

    def ToggleRaw3D(self, evt):

        if evt.IsChecked():
            # don't use file template, use filename
            if self._savedFileName:
                self.m_filePicker.SetPath(self._savedFileName)
            self.m_textCtrlZSize.Enable(True)
            self.m_spinCtrlFirstNum.Enable(False)
            self.m_spinCtrlLastNum.Enable(False)
        else:
            self.m_textCtrlZSize.Enable(False)
            self.m_spinCtrlFirstNum.Enable(True)
            self.m_spinCtrlLastNum.Enable(True)

        self.updateButtonState()

    def SetSpacing(self, spacing):
        self.m_textCtrlXSpacing.ChangeValue('%0.5f' % spacing[0])
        self.m_textCtrlYSpacing.ChangeValue('%0.5f' % spacing[1])
        self.m_textCtrlZSpacing.ChangeValue('%0.5f' % spacing[2])

    def GetImageTitle(self):
        """Return the image title given by user"""
        return self.m_textCtrlImageTitle.GetValue()

    def GetCurrentDirectory(self):
            # determine working directory
        curr_dir = os.getcwd()

        config = MicroViewSettings.MicroViewSettings.getObject()

        # over-ride with system-wide directory
        try:
            curr_dir = config.GlobalCurrentDirectory or curr_dir
        except:
            config.GlobalCurrentDirectory = curr_dir

        return curr_dir

    def onButtonExamine(self, evt):

        # enable dialog components
        self.m_buttonOK.Enable(True)
        self.m_panelMainDialog.Enable(True)

        # start by assuming image isn't 3D
        self.m_check3DImage.SetValue(False)

        # go handle file browse
        with wx.BusyCursor():
            self.BrowseFile(self.m_filePicker.GetPath())

    def OnFilePickerChanged(self, evt):
        # disable main panel until you hit 'examine'
        self.m_panelMainDialog.Enable(False)
        self.m_buttonOK.Enable(False)

    def onButtonUpdate(self, evt):

        try:
            first = int(self.m_spinCtrlFirstNum.GetValue())
            last = int(self.m_spinCtrlLastNum.GetValue())
        except:
            first = last = 0

        fspec = self.m_filePicker.GetPath()

        if self.m_check3DImage.IsChecked():
            l = 0
            fileName = fspec
        else:
            p0 = fspec.find('#')
            p1 = fspec.rfind('#')

            if p0 != -1:
                l = p1 - p0 + 1
                filePrefix = fspec[0:p0]
                filePattern = '%%s%%0%dd' % (l) + fspec[p1 + 1:]
                # This is the slice that we'll try to read
                middle = int((first + last) / 2.0)
                z0 = z1 = (middle - first)
                fileName = (filePrefix + filePattern) % ('', middle)
            else:
                l = 0
                fileName = fspec

        if self.bIsDICOM:
            # TODO: we're sorting this data in more than one place it seems...
            indices = np.argsort(
                np.array([float(f) for f in self._slice_locations]))
            # choose a card from the middle of the deck
            fileName = self._file_list[indices[len(indices) / 2]]

        xspacing = float(self.m_textCtrlXSpacing.GetValue())
        yspacing = float(self.m_textCtrlYSpacing.GetValue())
        zspacing = float(self.m_textCtrlZSpacing.GetValue())
        xsize = int(self.m_textCtrlXSize.GetValue())
        ysize = int(self.m_textCtrlYSize.GetValue())
        zsize = int(self.m_textCtrlZSize.GetValue())
        header_size = int(self.m_textCtrlHeaderSize.GetValue())
        numC = int(self.m_textCtrlNumberChannels.GetValue())

        # this isn't quite correct, but will do for now...
        swap_bytes = (
            self.m_choiceDataEndian.GetStringSelection() == 'big endian')

        if self.m_checkRawImage.IsChecked():
            reader = vtk.vtkImageReader2()
            reader.FileLowerLeftOn()
            reader.SetSwapBytes(swap_bytes)
            reader.SetHeaderSize(header_size)
            reader.SetDataSpacing(xspacing, yspacing, zspacing)
            reader.SetNumberOfScalarComponents(numC)
            dt = self.m_choiceDataType.GetStringSelection()
            if dt == 'unsigned char':
                reader.SetDataScalarTypeToUnsignedChar()
            elif dt == 'unsigned short':
                reader.SetDataScalarTypeToUnsignedShort()
            elif dt == 'short':
                reader.SetDataScalarTypeToShort()
            elif dt == 'int':
                reader.SetDataScalarTypeToInt()
            elif dt == 'float':
                reader.SetDataScalarTypeToFloat()
            elif dt == 'double':
                reader.SetDataScalarTypeToDouble()
        else:
            reader = self._reader

        reader.SetFileName(fileName)

        if self.m_check3DImage.IsChecked():
            z0 = z1 = int(zsize / 2)
            reader.SetFileDimensionality(3)
        else:
            reader.SetFileDimensionality(2)
            z0 = z1 = 0

        # if image is either a 3D image or using raw importer, we need to explicitly set
        # data extent
        if self.m_check3DImage.IsChecked() or self.m_checkRawImage.IsChecked():
            reader.SetDataExtent(0, xsize - 1, 0, ysize - 1, z0, z1)

        w, h = self.m_bitmapPreview.GetSize()
        try:

            # update reader rather than image (for VTK-6 compatibility)
            if vtk.vtkVersion().GetVTKMajorVersion() > 5:
                reader.Update()
            else:
                reader.GetOutput().Update()

            image = reader.GetOutput()

            flip = self.m_checkBoxFlipImage.GetValue()
            wxBitmap = MicroViewIO.VTKImageToBitmap(image, w, h, flip=flip)

        except:
            w, h = self.m_bitmapPreview.GetSize()
            wxBitmap = wx.EmptyBitmap(w, h)
            logging.error("ImageImportDialog")

        # paste into GUI
        self.m_bitmapPreview.SetBitmap(wxBitmap)
