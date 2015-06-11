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
MicroViewIO - a collection of useful I/O-based routines for MicroView

Classes:

    MicroViewIO - base class for all I/O
    MicroViewInput - manages image input
    MicroViewOutput - manages image output
    ImageImportDialog - manages MicroView's image import dialog

Global Functions:

    CreateDefaultImage() -- creates a sinusoidal image of a user-defined size

    SavePlaneAsImage() -- saves a given sliceplane as an image

    SaveViewPortSnapShot() -- captures a snapshot of a given viewport

Public Methods:

    AskOpenFileName()	-- prompts the user for a filename.  Massages the filename a little bit.
"""

import unicodecsv
import logging
import time
import dicom
from dicom.dataset import Dataset, FileDataset
import enum
import gdcm
import os
import glob
import re
import sys
import time
import types
import collections
import appdirs
import xlwt
import wx
import URLManager
import vtk
from xml.etree.ElementTree import fromstring, tostring

from zope import component, interface, event

from PI.visualization.vtkMultiIO import vtkLoadReaders, vtkLoadWriters, vtkImageReaderBase, vtkImageWriterBase,\
    MVImage
from PI.visualization.vtkMultiIO.events import ImageWriteBeginEvent
from PI.visualization.MicroView import PACKAGE_VERSION
from vtkEVS import EVSFileDialog
from PI.visualization.common import MicroViewSettings, MicroViewHistory

import ImageImportDialogC
import ImageExportWizard
import DICOMDIRBrowseDialogC

from PI.visualization.common.events import ProgressEvent
from PI.visualization.MicroView.interfaces import ICurrentMicroViewInput, IMicroViewInput, IMicroViewOutput,\
    IImageProcessor, IMicroViewMainFrame, ICurrentImage, ICurrentViewportManager, ICurrentOrthoView, IPluginManager
from PI.visualization.MicroView.events import HelpEvent, StandardROIChangeExtentCommandEvent
from PI.visualization.MicroView._MicroView import vtkImageMagnitude2
from PI.dicom.dicomdir import dicomdir


class FileType(enum.Enum):
    image = 1
    spreadsheet = 2
    plugin = 3
    license = 4


class MicroViewIO(object):

    """An abstract class for MicroView input and output"""

    def __init__(self):

        self.SetFileName('')
        self.SetTitle('')

        config = MicroViewSettings.MicroViewSettings.getObject()
        bNeedsInit = False
        try:
            val = config.DefaultFileExtension
            if val is None:
                bNeedsInit = True
        except:
            bNeedsInit = True
        finally:
            if bNeedsInit:
                config.DefaultFileExtension = 'vff'

        self._urlmanager = URLManager.URLManager()
        self._installdir = os.path.abspath(sys.path[0])
        self._plugindir = os.path.join(self._installdir, "Plugins")
        self._filetype = None

        self.station_id = '0001'
        self.parallax_base_uid = '1.2.826.0.1.3680043.9.1613'
        self._storage_class_uid = {'CT': '1.2.840.10008.5.1.4.1.1.2',
                                   'DX': '1.2.840.10008.5.1.4.1.1.1.1.1',
                                   'MR': '1.2.840.10008.5.1.4.1.1.4',
                                   'US': '1.2.840.10008.5.1.4.1.1.6.1',
                                   'NM': '1.2.840.10008.5.1.4.1.1.20',
                                   'OP': '1.2.840.10008.5.1.4.1.1.77.1.5.2',
                                   'PT': '1.2.840.10008.5.1.4.1.1.128'}

    def GetFileType(self):
        return self._filetype

    def SetFileType(self, ft):
        self._filetype = ft

    def SetTitle(self, title):
        self.__title = title

    def GetTitle(self):
        return self.__title

    def SetFileName(self, filename):
        self.__filename = filename

    def GetFileName(self):
        return self.__filename

    def HandleVTKProgressEvent(self, obj, evt):
        event.notify(ProgressEvent(
            obj.GetProgressText(), obj.GetProgress()))

    def GetCurrentDirectory(self):

        # determine working directory
        try:
            curr_dir = os.getcwd()
        except:
            curr_dir = ''

        config = MicroViewSettings.MicroViewSettings.getObject()

        # over-ride with system-wide directory
        try:
            curr_dir = config.GlobalCurrentDirectory or curr_dir
        except:
            config.GlobalCurrentDirectory = curr_dir

        return curr_dir

    def SaveCurrentDirectory(self, curr_dir):
        config = MicroViewSettings.MicroViewSettings.getObject()
        config.GlobalCurrentDirectory = curr_dir

    def AskOpenFileName(self, _filter):

        default_extension = None
        if self.GetFileName():
            default_extension = '*' + \
                os.path.splitext(self.GetFileName().lower())[-1]

        wildcard, filter_index = self.convert_to_wx(_filter, default_extension)

        dlg = wx.FileDialog(
            component.getUtility(IMicroViewMainFrame), message="Choose a file",
            defaultDir=self.GetCurrentDirectory(),
            defaultFile=self.GetFileName(),
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR
        )

        dlg.SetFilterIndex(filter_index)

        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()
            filename = paths[0]
        else:
            return None

        # wx file browser seems to have a bug - it tacks on an extension to
        # files if they don't have one
        if not os.path.exists(filename):
            filename = os.path.splitext(filename)[0]

        # save the current working directory
        curr_dir = os.path.dirname(os.path.abspath(filename))
        self.SaveCurrentDirectory(curr_dir)

        # set the default extension
        MicroViewSettings.MicroViewSettings.getObject().DefaultFileExtension = os.path.splitext(
            filename)[1][1:]

        return filename

    def convert_to_wx(self, _filter, default_extension):

        wildcard = ''
        idx = 0
        filter_index = 0

        # Add an "All known filetypes" entry at the beginning if it isn't
        # already there
        if 'All known filetypes' not in _filter:
            all_extensions = []
            for description in _filter:
                if description != 'All files':
                    all_extensions.extend(_filter[description])
            _new_filter = collections.OrderedDict()
            _new_filter['All known filetypes'] = all_extensions
            for entry in _filter:
                _new_filter[entry] = _filter[entry]
            _filter = _new_filter

        if 'All files' not in _filter:
            _filter['All files'] = ['*']

        for e in _filter:
            found = False
            if len(_filter[e]) > 0:
                extensions = _filter[e][0]
                if default_extension == extensions:
                    found = True
                for additional_extension in _filter[e][1:]:
                    extensions += ';%s' % additional_extension
                    if default_extension == additional_extension:
                        found = True
                if e == 'All known filetypes':
                    wildcard += '%s|%s;%s|' % (e,
                                               extensions, extensions.upper())
                else:
                    wildcard += '%s (%s)|%s;%s|' % (e,
                                                    extensions, extensions, extensions.upper())
                    if found:
                        filter_index = idx
            idx += 1

        wildcard = wildcard[:-1]

        return wildcard, filter_index

    def AskSaveAsFileName(self, _filter, message="Save file", defaultfile="", defaultExt=None):

        if defaultExt is None:
            # try to work out default extension from filename
            if defaultfile:
                defaultExt = '*' + os.path.splitext(defaultfile.lower())[-1]

        wildcard, filter_index = self.convert_to_wx(_filter, defaultExt)

        defaultDir = self.GetCurrentDirectory()
        if defaultfile:
            defaultDir, defaultfile = os.path.split(
                os.path.abspath(defaultfile))

        dlg = wx.FileDialog(
            component.getUtility(IMicroViewMainFrame), message=message,
            defaultDir=self.GetCurrentDirectory(),
            defaultFile=defaultfile,
            wildcard=wildcard,
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT | wx.FD_CHANGE_DIR
        )

        dlg.SetFilterIndex(filter_index)

        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
        else:
            return None

        if os.path.splitext(filename)[1] == '':
            dlg = wx.MessageDialog(component.getUtility(
                IMicroViewMainFrame), "Please specify a file extension", 'Info', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return None

        # save the current working directory
        curr_dir = os.path.dirname(os.path.abspath(filename))
        self.SaveCurrentDirectory(curr_dir)

        # set the default extension
        MicroViewSettings.MicroViewSettings.getObject(
        ).DefaultFileExtension = os.path.splitext(filename)[1][1:]

        return filename

#############################################################################


"""
MicroViewInput: handle MicroView file open and import
"""


class MicroViewInput(MicroViewIO):

    """A class for handling reading and writing of files for MicroView."""

    interface.implements(IMicroViewInput)

    def __init__(self):
        MicroViewIO.__init__(self)
        self._importDone = False
        self.convertToGrayScale = False

        # default file format
        self._reader, self.formats = \
            vtkLoadReaders.LoadImageReaders(directories=[
                self._plugindir,
                os.path.join(appdirs.user_data_dir("MicroView", "Parallax Innovations"), "Plugins")])
        self._reader.AddObserver('ProgressEvent', self.HandleVTKProgressEvent)

        # filename filter for input
        self._reader_filter = self._reader.GetMatchingFormatStrings()
        self._reader_filter['CSV file'] = ['*.csv']
        self._reader_filter['Excel spreadsheet file'] = ['*.xls', '*.xlsx']
        self._reader_filter['All files'] = ['*']

        # user help topic: 'import' or 'export'
        # used for UserEvent
        self._helpTopic = None
        self._importDialog = None
        self._image_title = ''
        self._firstImportFileName = ''

    def tearDown(self):
        self._reader.tearDown()
        del(self._reader)
        del(self.formats)
        del(self._reader_filter)

    def GetReader(self):
        return self._reader

    def GetImageOutput(self):
        reader = self.GetReader()
        image = reader.GetOutput()
        # propagate coordinate system info
        image.SetCoordinateSystem(reader.GetCoordinateSystem())
        return image

    def OpenFile(self, filename=None):
        """Opens and reads a file. Return errors status."""

        # Request a filename from the user
        if filename is None:
            filename = self.AskOpenFileName(self._reader_filter)
        else:
            # save the current working directory
            curr_dir = os.path.dirname(os.path.abspath(filename))
            self.SaveCurrentDirectory(curr_dir)
        if not filename:
            return False

        # if file is a URL, handle it here
        # if the file can be read directly, then it isn't a URL
        if (':/' in filename) and (not os.access(filename, os.R_OK)):
            fname = self._urlmanager.getURL(filename)
        else:
            fname = filename

        self.SetFileName(filename)
        self.SetTitle(os.path.split(filename)[-1])

        _dir = os.path.dirname(filename)

        # if filename is DICOMDIR, pull up a patient browser to allow user to
        # select series
        if os.path.split(filename)[-1].lower() == 'dicomdir':

            dlg = DICOMDIRBrowseDialogC.DICOMDIRBrowseDialogC(
                component.getUtility(IMicroViewMainFrame), filename)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    filenames = dlg.GetFilenames()
                    if len(filenames) > 0:
                        # create a VTK string array
                        arr = vtk.vtkStringArray()
                        # pack filenames into an array
                        for name in filenames:

                            lower_name = name

                            # sanity check
                            if os.path.exists(name):
                                arr.InsertNextValue(name)
                            elif os.path.exists(lower_name):
                                arr.InsertNextValue(lower_name)
                            else:
                                logging.warning("File '%s' is missing." % name)

                        # construct useful filename/title here
                        self.SetTitle(dlg.GetCanonicalSeriesName())

                        # go load it -- make sure to sort slices
                        logging.info("Loading DICOMDIR image data from {}...".format(filename))
                        return self.OpenImageFile(arr, check_order=True)
            finally:
                dlg.Destroy()
            return

        # Save the extension as default
        ext = MicroViewSettings.MicroViewSettings.getObject().DefaultFileExtension = os.path.splitext(
            self.GetFileName())[1][1:]

        # Handle spreadsheets, eggs and images separately
        logging.info("Loading {}...".format(filename))

        if ext.lower() in ('egg',):
            return self.OpenPlugin(fname)
        elif ext.lower() in ('csv', 'xls', 'xlsx'):
            return self.OpenSpreadsheetFile(fname)
        elif re.compile('^.*license.*\.conf$').match(filename.lower()):
            return self.OpenLicenseFile(filename)
        else:
            return self.OpenImageFile(fname)

    def OpenPlugin(self, filename):
        self.SetFileType(FileType.plugin)
        return True

    def OpenSpreadsheetFile(self, filename):
        self.SetFileType(FileType.spreadsheet)
        return True

    def OpenLicenseFile(self, filename):
        self.SetFileType(FileType.license)
        return True

    def GetSpreadsheetOutput(self):
        return None

    def OpenImageFile(self, filename, **kw):
        """Opens and reads an image from a file or a list of files. Don`t call this directly.

        Args:
            filename (str,obj): either a single filename or a vtkArray() of filenames

        Returns:
            bool: True if image load was successful
        """

        if isinstance(filename, str) or isinstance(filename, unicode):

            # Open the single file
            try:
                ret = self._reader.SetFileName(filename, **kw)
            except Exception, e:
                logging.exception(e)
                ret = False

            if ret is False:
                dlg = wx.MessageDialog(wx.GetApp().GetTopWindow(), "Unable to load %s" %
                                       filename, 'Error', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        elif isinstance(filename, vtk.vtkStringArray):

            # Open a collection of files
            try:
                ret = self._reader.SetFileNames(filename, **kw)
            except Exception, e:
                logging.exception(e)
                ret = False

            if ret is False:
                dlg = wx.MessageDialog(
                    wx.GetApp().GetTopWindow(), "Unable to load file slices", 'Error', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        self._reader.SetProgressText("Reading image...")

        # Keep a history of recent files
        if isinstance(filename, str) or isinstance(filename, unicode):
            logging.info("Loaded image from file: %s" % filename)
        else:
            logging.info("Loaded image stack")

        MicroViewHistory.MicroViewHistory.getObject().AddFileToHistory(
            self.GetFileName())

        self.SetFileType(FileType.image)

        return True

    def LoadVolumeCoordinatesFromDisk(self, filename):

        image = component.getUtility(ICurrentImage)
        origin = image.GetOrigin()
        spacing = image.GetSpacing()
        pluginManager = component.getUtility(IPluginManager)

        # make sure standard ROI tool is loaded and active
        standard_roi_plugin = pluginManager.GetPluginReferenceByName(
            'StandardROITool', bShouldSelect=False)()
        standard_roi_plugin.ActivatePlugin()            

        standard_roi_plugin.SetROIType('box')    

        if filename.lower().endswith('.xml'):
            # handle new xml format
            try:
                evt = fromstring(open(filename, 'rt').read())
                points = map(float, evt.text.split())
                pos1 = [(points[0] - origin[0]) / spacing[0], 
                        (points[2] - origin[1]) / spacing[1], 
                        (points[4] - origin[2]) / spacing[2]]
                pos2 = [(points[1] - origin[0]) / spacing[0], 
                        (points[3] - origin[1]) / spacing[1], 
                        (points[5] - origin[2]) / spacing[2]]
            except:
                logging.error('unable to parse "%s"' % (filename))
                return -1
            logging.info("Loaded ROI coords from '{}'".format(filename))
        else:
            # fall-back to old crop coordinate file here
            try:
                f = open(filename, "rt")
                XPositionValue, YPositionValue, ZPositionValue = map(
                    float, f.readline().split())
                MajorValue, MinorValue, HeightValue = map(float, f.readline().split())
                f.close()

                pos1 = [int(XPositionValue), int(YPositionValue), int(ZPositionValue)]
                pos2 = [pos1[0] + MajorValue - 1, pos1[
                    1] + MinorValue - 1, pos1[2] + HeightValue - 1]
            except:
                logging.error('unable to parse "%s"' % (filename))
                return -1
            logging.info("Loaded ROI coords from '{}'".format(filename))

        # send it a command to set the ROI
        event.notify(StandardROIChangeExtentCommandEvent(
            extent=(pos1[0], pos2[0], pos1[1], pos2[1], pos1[2], pos2[2])))
            
        return 0

    def GetHelpTopic(self):
        return self._helpTopic

    def GetImportedImage(self):

        if self._importDone:
            if self.convertToGrayScale:
                logging.info('computing image magnitude...')
                f = vtkImageMagnitude2()
                f.SetInputConnection(self._reader.GetOutputPort())
                image = MVImage.MVImage(f.GetOutputPort())
            else:
                # 2013-08-30:  raw images are returned as real images, everything else should already by
                # a MVImage object
                output = self._reader.GetOutputPort()
                image = self._reader.GetOutput()
                if not isinstance(image, MVImage.MVImage):
                    image = MVImage.MVImage(self._reader.GetOutputPort())

            # image should always be in mm since there's an option to set this
            # on the user interface
            image.SetMeasurementUnitToMM()

            return image, self.GetImportedFileName()
        else:
            return None, None

    def GetImportedFileName(self):
        return self._image_title or self._firstImportFileName

    def ShowImportDialog(self):

        if self._importDialog is None:
            self._importDialog = ImageImportDialogC.ImageImportDialogC(
                component.getUtility(IMicroViewMainFrame))

        ret = self._importDialog.ShowModal()

        if ret == wx.ID_OK:
            with wx.BusyCursor():
                _path = self._importDialog.m_filePicker.GetPath()
                # self._importDialog.BrowseFile(os.path.abspath(_path))
                self.convertToGrayScale = self._importDialog.isGrayScaleRequested()
                self.ImageImport()

    def ImageImport(self):

        self._importDone = False

        # save settings
        self._importDialog.SaveSettings()

        xspacing = float(self._importDialog.m_textCtrlXSpacing.GetValue())
        yspacing = float(self._importDialog.m_textCtrlYSpacing.GetValue())
        zspacing = float(self._importDialog.m_textCtrlZSpacing.GetValue())
        self._image_title = self._importDialog.GetImageTitle()

        raw_3D = self._importDialog.m_check3DImage.GetValue()
        flip = self._importDialog.m_checkBoxFlipImage.GetValue()
        fspec = self._importDialog.m_filePicker.GetPath()

        bIsDICOM = False

        if raw_3D:
            l = 0
            file_list = [fspec]
        else:
            bIsDICOM = self._importDialog.bIsDICOM
            if bIsDICOM:
                file_list = self._importDialog.GetFileList()
                l = len(file_list)
                first = last = 0
            else:
                try:
                    first = int(
                        self._importDialog.m_spinCtrlFirstNum.GetValue())
                    last = int(self._importDialog.m_spinCtrlLastNum.GetValue())
                except:
                    first = last = 0

                p0 = fspec.find('#')
                p1 = fspec.rfind('#')

                if p0 != -1:
                    l = p1 - p0 + 1
                    filePrefix = fspec[0:p0]
                    filePattern = '%%s%%0%dd' % (l) + fspec[p1 + 1:]
                    file_list = [
                        filePattern % (filePrefix, num) for num in range(first, last + 1)]
                else:
                    l = 0
                    file_list = [fspec]

            # sanity check - check existence of first/last image
            if l > 0:
                ftemp = file_list[0]
                self._firstImportFileName = ftemp
                if os.access(ftemp, os.R_OK) != 1:
                    dlg = wx.MessageDialog(component.getUtility(
                        IMicroViewMainFrame), 'Unable to access "%s"' % ftemp, 'Error', wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                ftemp = file_list[-1]
                if os.access(ftemp, os.R_OK) != 1:
                    dlg = wx.MessageDialog(component.getUtility(
                        IMicroViewMainFrame), "Unable to access '%s'" % ftemp, 'IOError', wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
            else:
                self._firstImportFileName = file_list[0]

        # check if we need to use our own reader
        if self._reader is None or self._importDialog.m_checkRawImage.GetValue():
            self.useRawReader = 1

            headersize = int(
                self._importDialog.m_textCtrlHeaderSize.GetValue())
            xsize = int(self._importDialog.m_textCtrlXSize.GetValue())
            ysize = int(self._importDialog.m_textCtrlYSize.GetValue())
            if raw_3D:
                zsize = int(self._importDialog.m_textCtrlZSize.GetValue())

            reader = vtk.vtkImageReader2()

            # vtkImageReader2 doesn't like to handle one filename with string
            # arrays
            if len(file_list) == 1:
                reader.SetFileName(file_list[0])
            else:
                fn = vtk.vtkStringArray()
                for _file in file_list:
                    fn.InsertNextValue(_file)
                reader.SetFileNames(fn)

            reader.SetHeaderSize(headersize)
            if raw_3D:
                z0 = 0
                z1 = zsize - 1
                reader.SetFileDimensionality(3)
            else:
                z0 = min(first, last)
                z1 = max(first, last)

            reader.SetDataExtent((0, xsize - 1,
                                  0, ysize - 1,
                                  z0, z1))
            reader.SetDataSpacing(xspacing, yspacing, zspacing)
            reader.SetFileLowerLeft(flip)

            dt = self._importDialog.m_choiceDataType.GetStringSelection()
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
                logging.error("data type '%s' not supported" % dt)

            endian = self._importDialog.m_choiceDataEndian.GetStringSelection(
            )
            if endian == 'big endian':
                reader.SetDataByteOrderToBigEndian()
            else:
                reader.SetDataByteOrderToLittleEndian()

            self._reader._reader = reader
            reader.SetProgressText("Importing images...")
            reader.AddObserver(
                'ProgressEvent', self.HandleVTKProgressEvent)

            del reader

        else:
            if l > 0:
                # create a VTK string array
                arr = vtk.vtkStringArray()
                # pack filenames into the array
                for name in file_list:
                    # sanity check
                    if os.path.exists(name):
                        arr.InsertNextValue(name)
                    else:
                        logging.warning("File '%s' is missing." % name)
                if bIsDICOM:
                    self._reader.SetFileNames(arr, check_order=True)
                else:
                    self._reader.SetFileNames(arr)
            else:
                self._reader.SetFileName(fspec)
            if not bIsDICOM:
                self._reader.SetDataSpacing(xspacing, yspacing, zspacing)
            self._reader.SetProgressText("Importing images...")

        self._importDone = True

    # Return a count of the number of time points in the time series.
    def TimePointCount(self):
        cTimePoints = 1
        try:
            cTimePoints = self._reader.TimePointCount()
        except:
            pass

        return cTimePoints

    # Make the given time point (by index) the current time point.
    def SetCurrentTimePoint(self, index):
        self._importDone = False
        try:
            self._reader.SetCurrentTimePoint(index)
        except:
            pass
        self._importDone = True

    def AutoImageImport(self, aFileNames=None):
        """Automatically import (i.e., no prompting the user) the
        images from ExternalSelection (a class defined below."""
        self._importDone = False

        if not aFileNames:
            selection = ExternalSelection()
            selection.Refresh()
            aFileNames = selection.GetSelectedFiles()

        cFiles = len(aFileNames)
        if (self._reader != None and cFiles > 0):
            self._firstImportFileName = aFileNames[0]
            strExt = os.path.splitext(self._firstImportFileName)[1]
            self._reader.SetExtension(strExt, self._firstImportFileName)
            self._reader.SetDataExtent(0, 0, 0, 0, 0, cFiles)
            self._reader.SetDataSpacing(1.0, 1.0, 1.0)
            self._reader.SetFileList(aFileNames)

        self._importDone = True


class ImageExportWizardC(ImageExportWizard.ImageExportWizard):

    def SetInput(self, image):
        self._image = image

    def SetWriter(self, writer):
        self._writer = writer

    def RunWizard(self):
        self.bShouldDownsample = False
        self.downsampleBitDepth = 8
        self.bWizardFinished = False

        self.FitToPage(self.m_wizPageIntro)

        ImageExportWizard.ImageExportWizard.RunWizard(
            self, self.m_wizPageIntro)

        # Forget about the image and writer
        self._image = None
        self._writer = None

    def GetDirectory(self):
        return self.m_dirPickerForExport.GetPath()

    def SetDirectory(self, path):
        self.m_dirPickerForExport.SetPath(path)

    def GetCompletionStatus(self):
        return self.bWizardFinished

    def GetDownsampleStatus(self):
        return self.bShouldDownsample

    def GetDownsampleBitDepth(self):
        return self.downsampleBitDepth

    def GetFileExtension(self):
        return self._file_pattern[self.m_listBoxFormats.GetStringSelection()][0]

    def onInitDialog(self, event):
        # should downsampling be allowed?
        sz = self._image.GetScalarSize()
        bits = sz * 8
        values = ['8-bit unsigned char', '16-bit signed int',
                  '32-bit float', '64-bit double']

        self.m_choiceDownsample.Enable(sz > 1)
        self.m_choiceDownsample.Clear()

        # populate entries
        self.m_choiceDownsample.Append("Don't downsample")
        for i in range(sz - 1):
            self.m_choiceDownsample.Append(values[i])
        self.m_choiceDownsample.Select(0)

    def onWizardFinished(self, evt):
        self.bWizardFinished = True

    def onListBoxDoubleClick(self, evt):
        # advance dialog if user double clicks
        self.ShowPage(self.GetCurrentPage().GetNext())

    def onWizardPageChanged(self, event):

        page = event.GetPage()

        if page == self.m_wizPageSelectFormat:

            depth = self._image.GetScalarSize() * 8

            if self.m_choiceDownsample.IsEnabled():
                val = self.m_choiceDownsample.GetSelection()
                if val > 0:
                    depth = val * 8
                    self.downsampleBitDepth = depth
                self.bShouldDownsample = (val != 0)
            else:
                self.bShouldDownsample = False
                self.downsampleBitDepth = 8

            # determine list of matching file formats that this image can be
            # exported into
            depth_enum = {8: vtkImageWriterBase.DEPTH_8,
                          16: vtkImageWriterBase.DEPTH_16,
                          32: vtkImageWriterBase.DEPTH_32,
                          64: vtkImageWriterBase.DEPTH_64}[depth]

            self._file_pattern = self._writer.GetMatchingFormatStrings(
                depth_enum | vtkImageWriterBase.IMAGE_2D)
            # update dialog list with file format info
            self.m_listBoxFormats.Clear()
            keys = self._file_pattern.keys()
            if len(keys) > 0:
                self.m_listBoxFormats.InsertItems(keys, 0)


def CreateDefaultImage(size=None):
    """Create MicroView's default sinusoidal input image"""
    if size is None:
        size = (100, 100, 100)

    xs, ys, zs = size
    cos = vtk.vtkImageSinusoidSource()
    cos.SetWholeExtent(0, xs - 1, 0, ys - 1, 0, zs - 1)
    cos.SetAmplitude(250)
    cos.SetDirection(1, 1, 0)
    cos.SetPeriod(60.)
    cos.ReleaseDataFlagOff()
    cast = vtk.vtkImageCast()
    cast.SetInputConnection(cos.GetOutputPort())
    cast.SetOutputScalarTypeToShort()
    with wx.WindowDisabler():
        with wx.BusyCursor():
            cast.Update()
    mv_image = MVImage.MVImage(cast.GetOutputPort())
    mv_image.SetMeasurementUnitToMM()

    return mv_image

##########################################################################

"""
MicroViewOutput: MicroView save and export
"""


class MicroViewOutput(MicroViewIO):

    interface.implements(IMicroViewOutput)

    def __init__(self):

        MicroViewIO.__init__(self)

        self.SetFileName('')
        self._writer = None
        self._parallax_base_uid = '1.2.826.0.1.3680043.9.1613'
        self._exportDialog = None
        self._transform = None

    def create_writer(self):
        if self._writer is None:
            self._writer, self.formats2 = \
                vtkLoadWriters.LoadImageWriters(directories=[
                    self._plugindir,
                    os.path.join(appdirs.user_data_dir("MicroView", "Parallax Innovations"), "Plugins")])
            self._writer_filter = self._writer.GetMatchingFormatStrings()
            self._writer.AddObserver(
                'ProgressEvent', self.HandleVTKProgressEvent)

    def SetupWriterFilter(self, image):

        image.UpdateInformation()
        extent = image.GetWholeExtent()

        bits = image.GetScalarSize() * 8
        props = 0
        if bits == 8:
            props = props | vtkImageWriterBase.DEPTH_8
        elif bits == 16:
            props = props | vtkImageWriterBase.DEPTH_16
        elif bits == 32:
            props = props | vtkImageWriterBase.DEPTH_32
        elif bits == 64:
            props = props | vtkImageWriterBase.DEPTH_64

        if not ((extent[0] == extent[1]) or
                (extent[2] == extent[3]) or
                (extent[4] == extent[5])):
            props = props | vtkImageWriterBase.IMAGE_3D

        if self._writer is None:
            self.create_writer()

        self._writer_filter = self._writer.GetMatchingFormatStrings(props)

    def CreateDefaultDICOMFile(self):

        try:
            image = component.getUtility(ICurrentImage)
        except:
            return

        dicom_header = image.GetDICOMHeader()

        file_meta = Dataset()

        # Secondary Capture by default
        file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.7'
        file_meta.ImplementationClassUID = self._parallax_base_uid
        file_meta.FileMetaInformationVersion = '\x00\x01'
        # Explicit VR Little Endian (for DICOMDIR)
        file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.1'
        file_meta.ImplementationVersionName = PACKAGE_VERSION
        file_meta.SourceApplicationEntityTitle = 'MicroView'

        ds = FileDataset('dummy', {}, file_meta=file_meta, preamble="\0" * 128)

        # default SOPClassUID (Secondary capture)
        ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.7'

        # copy image dicom header values across
        for tag in dicom_header:
            ds[tag.tag] = tag

        if 'SOPClassUID' not in ds:
            if dicom_header.Modality in self._storage_class_uid:
                ds.SOPClassUID = ds.file_meta.MediaStorageSOPClassUID = self._storage_class_uid[
                    ds.Modality]

        return ds

    def is_file_dicom(self, filename, magic=None):
        """
        Manage this ourselves to handle non-conformant DICOM images
        """
        try:
            with open(filename, 'rb') as f:
                header = f.read(132)

            # is this a conforming header?
            if 'DICM' in header:
                return 3

            # is this a non-conformant header?
            count = 0
            for tag in ['PRIMARY', 'SECONDARY', 'ORIGINAL', 'DERIVED']:
                if tag in header:
                    count += 1
            if count >= 2:
                return 3
        except:
            pass

        return 0

    def ExportDICOMDIR(self):

        directory = self.GetCurrentDirectory()

        # select output folder
        dlg = wx.DirDialog(
            None, "Choose DICOMDIR directory", directory, wx.DD_DEFAULT_STYLE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                directory = dlg.GetPath()
            else:
                return
        finally:
            dlg.Destroy()
            
        with wx.BusyCursor():

            # read any existing dicomdir
            logging.info("Reading existing DICOMDIR file...")
            dcmdir = None
            dicomdir_filename = os.path.join(directory, 'DICOMDIR')
            for filename in (os.path.join(directory, 'DICOMDIR'), os.path.join(directory, 'dicomdir')):
                if os.path.exists(filename):
                    dicomdir_filename = filename
                    directory = os.path.abspath(
                        os.path.dirname(dicomdir_filename))
                    try:
                        dcmdir = dicom.read_dicomdir(filename)
                        break
                    except:
                        pass

            if dcmdir is None:
                logging.error(
                    "Unable to read DICOMDIR file - a new one will be generated")

            # get image details and DICOM header
            image = component.getUtility(ICurrentImage)
            dicom_header = self.CreateDefaultDICOMFile()
            zsize = image.GetDimensions()[-1]

            # we need a valid study date otherwise it's difficult to sort

            # for now, we'll use a flat folder structure -- MV0001 style
            num = 0
            done = False
            while not done:
                name = 'MV%04d' % num
                subfolder = os.path.join(directory, name)
                if not os.path.exists(subfolder):
                    try:
                        os.makedirs(subfolder)
                    except:
                        logging.error(
                            "Unable to make directory {}".format(subfolder))
                        return
                    done = True
                else:
                    num += 1

            # set up writer
            if self._writer is None:
                self.create_writer()
            self._writer.SetWriterByFileExtension('.dcm')

            fn = vtk.vtkStringArray()
            template = os.path.join(subfolder, 'I%06d')
            for i in range(zsize):
                fn.InsertNextValue(template % i)
            self._writer.SetFileNames(fn)

            # do export
            # use an MVImage here rather than raw image
            self._writer.SetInput(image)
            self._writer.SetDICOMHeader(dicom_header)

            # give app last-ditch opportunity before writing image
            ortho = component.getUtility(ICurrentOrthoView)
            event.notify(ImageWriteBeginEvent(ortho.GetImageIndex()))

            self._writer.Write()

            # update DICOMDIR
            cwd = os.getcwd()
            os.chdir(directory)

            # walk directory and find all DICOM files contained within
            filenames = []

            t0 = time.time()

            try:
                msg = "Examining existing DICOM records..."
                logging.info(msg)

                dlg = wx.ProgressDialog("DICOMDIR Export",
                                        msg,
                                        maximum=100,
                                        parent=wx.GetApp().GetTopWindow(),
                                        style=0
                                        | wx.PD_CAN_ABORT
                                        | wx.PD_AUTO_HIDE
                                        | wx.PD_APP_MODAL
                                        | wx.PD_ELAPSED_TIME
                                        )
                if not dlg.UpdatePulse(msg):
                    return

                if dcmdir is not None:
                    t0 = time.time()
                    # simply append to existing DICOMDIR file
                    dd = dicomdir(dcmdir)

                    # create/add a patient record
                    patient = Dataset()
                    patient.DirectoryRecordType = 'PATIENT'
                    patient.PatientName = dicom_header.PatientName
                    patient.PatientID = dicom_header.PatientID
                    dd.add_record(patient)

                    # create a study record
                    study = Dataset()
                    study.DirectoryRecordType = 'STUDY'
                    study.StudyDate = dicom_header.StudyDate
                    study.StudyTime = dicom_header.StudyTime
                    study.AccessionNumber = ''
                    study.StudyInstanceUID = dicom_header.StudyInstanceUID
                    study.StudyID = dicom_header.StudyID
                    dd.add_record(study, patient_record=patient)

                    # create a series record
                    series = Dataset()
                    series.DirectoryRecordType = 'SERIES'
                    series.SeriesDate = dicom_header.SeriesDate
                    series.SeriesTime = dicom_header.SeriesTime
                    series.SeriesDescription = dicom_header.get('SeriesDescription', '')
                    series.AccessionNumber = ''
                    series.SeriesInstanceUID = dicom_header.SeriesInstanceUID
                    series.SeriesNumber = dicom_header.SeriesNumber
                    series.Modality = dicom_header.Modality
                    dd.add_record(
                        series, study_record=study, patient_record=patient)

                    # create the image records
                    for i in range(zsize):

                        image = Dataset()
                        image.DirectoryRecordType = 'IMAGE'
                        image.RecordInUseFlag = 65535
                        image.ReferencedFileID = [name, 'I%06d' % i]
                        # CT Image Storage
                        image.ReferencedSOPClassUIDInFile = '1.2.840.10008.5.1.4.1.1.2'
                        image.ReferencedSOPInstanceUIDInFile = '1.2.3.4.5.6'
                        image.ReferencedTransferSyntaxUIDInFile = '1.2.840.10008.1.2.1'
                        image.ImageType = dicom_header.ImageType
                        image.InstanceNumber = '1'
                        dd.add_record(
                            image, series_record=series, study_record=study, patient_record=patient)

                    # update everything
                    if not dlg.UpdatePulse("Updating DICOMDIR file..."):
                        return
                    dd.update()
                    ds = dd.get_dicomdir()
                    dicom.write_file(dicomdir_filename, ds)
                    t1 = time.time()

                    # TODO: implement the rest of this here
                else:
                    for root, dirs, files in os.walk(directory):
                        for _file in files:
                            filename = os.path.join(root, _file)
                            if not 'dicomdir' in filename.lower():
                                try:
                                    code = self.is_file_dicom(filename)
                                    if code == 3:
                                        filename2 = os.path.abspath(filename).replace(
                                            os.path.abspath(directory), '').replace(os.path.sep, '/')[1:]
                                        filenames.append(
                                            filename2.encode('utf-8'))
                                except:
                                    pass

                    gen = gdcm.DICOMDIRGenerator()
                    gen.SetRootDirectory(directory.encode('utf-8'))
                    gen.SetFilenames(tuple(filenames))

                    if not dlg.UpdatePulse("Generating new DICOMDIR file..."):
                        return

                    if not gen.Generate():
                        logging.error("DICOMDIR generation failed!")
                        return

                    if not dlg.UpdatePulse("Writing DICOMDIR file..."):
                        return

                    w = gdcm.Writer()
                    w.SetFile(gen.GetFile())
                    w.SetFileName(dicomdir_filename.encode('utf-8'))

                    if not w.Write():
                        logging.error("DICOMDIR write failed!")
                        return
            finally:
                dlg.Destroy()

            t1 = time.time()
            logging.info("Elapsed time: {}".format(t1 - t0))

            os.chdir(cwd)
            logging.info(
                "Exported data to DICOMDIR folder: {}".format(subfolder))

    def DICOMDIRRegenerate(self, directory=None):

        if directory is None:
            directory = self.GetCurrentDirectory()

            # select output folder
            dlg = wx.DirDialog(
                None, "Choose DICOMDIR directory", directory, wx.DD_DEFAULT_STYLE)
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    directory = dlg.GetPath()
                else:
                    return
            finally:
                dlg.Destroy()

        with wx.BusyCursor():
            try:
                dlg = wx.ProgressDialog("DICOMDIR Generate",
                                        "Scanning...",
                                        maximum=100,
                                        parent=wx.GetApp().GetTopWindow(),
                                        style=0
                                        | wx.PD_CAN_ABORT
                                        | wx.PD_AUTO_HIDE
                                        | wx.PD_APP_MODAL
                                        | wx.PD_ELAPSED_TIME
                                        )

                dicomdir_filename = os.path.join(directory, "DICOMDIR")
                dd = dicomdir(dicomdir_filename)

                class Spinner(object):

                    def __init__(self, dlg):
                        self._dlg = dlg

                    def Yield(self):
                        return dlg.UpdatePulse()

                spinner = Spinner(dlg)
                dd.Yield = spinner.Yield

                # go walk directory
                ret = dd.walk_directory(directory)

                # if we're successful, write DICOMDIR
                if ret:
                    ds = dd.get_dicomdir()
                    dicom.write_file(dicomdir_filename, ds)
            finally:
                dlg.Destroy()

    def ExportImage(self, directory=None, exportSelection=None):

        if directory is None:
            directory = self.GetCurrentDirectory()

        if self._writer is None:
            self.create_writer()

        # create export wizard
        wizard = ImageExportWizardC(component.getUtility(IMicroViewMainFrame))
        wizard.SetInput(component.getUtility(ICurrentImage).GetRealImage())
        wizard.SetWriter(self._writer)
        wizard.SetDirectory(directory)
        wizard.RunWizard()

        exit_status = wizard.GetCompletionStatus()

        if exit_status:
            downsample_depth = wizard.GetDownsampleBitDepth()
            bShouldDownsample = wizard.GetDownsampleStatus()
            directory = wizard.GetDirectory()
            self.SaveCurrentDirectory(directory)
            extension = wizard.GetFileExtension()[1:]

        wizard.Destroy()

        if not exit_status:
            return

        image = component.getUtility(ICurrentImage)

        # downsample image if we need to
        if bShouldDownsample:
            obj = component.getUtility(IImageProcessor)
            with wx.BusyCursor():
                image = obj.DownsampleImage(image, downsample_depth)

                # update image (VTK-6 compatible)
                image.GetProducerPort().GetProducer().Update()

        self._writer.SetWriterByFileExtension(extension)

        # set up filenames
        zsize = image.GetDimensions()[-1]

        if hasattr(self._writer, 'SetFileNames'):
            # use more flexible method, if it exists
            fn = vtk.vtkStringArray()
            template = os.path.join(directory, 'export-%04d' + extension)
            for i in range(zsize):
                fn.InsertNextValue(template % i)
            self._writer.SetFileNames(fn)
        else:
            self._writer.SetFilePrefix(os.path.join(directory, "export-"))
            self._writer.SetFilePattern("%s%04d" + extension)

        self._writer.SetInput(image)

        if hasattr(self._writer, 'SetFileDimensionality'):
            self._writer.SetFileDimensionality(2)

        # setup header values
        _header = image.GetHeader().copy()

        # Convert date
        if 'date' in _header:
            if isinstance(_header['date'], types.ListType):
                _header['date'] = '%d %d %d' % tuple(_header['date'])

        # Convert title
        if 'title' in _header:
            _header['title'] = '%s (Exported)' % (_header['title'])
        else:
            _header['title'] = "Generated by MicroView (Exported)"

        # set dicom and other header values
        ds = image.GetDICOMHeader()
        self._writer.SetDICOMHeader(ds)
        self._writer.SetHeader(_header)

        with wx.BusyCursor():
            self._writer.SetProgressText("Exporting Image...")

            # now actually perform image export
            try:

                # if output directory doesn't exist, create it now
                if not os.path.exists(directory):
                    logging.info(
                        "Creating output directory '{}'".format(directory))
                    os.makedirs(directory)

                # give app last-ditch opportunity before writing image
                ortho = component.getUtility(ICurrentOrthoView)
                event.notify(ImageWriteBeginEvent(ortho.GetImageIndex()))
                self._writer.Write()
            except AttributeError, message:
                dlg = wx.MessageDialog(component.getUtility(
                    IMicroViewMainFrame), message.message, 'Error', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
            except IOError, (errno, strerror):
                dlg = wx.MessageDialog(component.getUtility(IMicroViewMainFrame), "[Errno %d]: %s" % (
                    errno, strerror), 'Error', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
            except Exception, e:
                logging.exception("MicroViewIO")

            self._writer.SetProgress(1.0)
            self._writer.InvokeEvent('ProgressEvent')

    # TODO: is this needed for VTK-6?
    def SetROIStencilData(self, stencil):
        self._ROIStencil = stencil

    def SetImageTransform(self, transform):
        self._transform = transform
        # self._reslice.SetResliceTransform(transform)

    def _SaveImageToFile(self, image, progressText='Exporting Image...', filename=None,
                         defaultfilename='', message='Save image to file...'):
        """ Save input to a output file. Ask for file name if not supplied."""

        # update filters here
        self.SetupWriterFilter(image)

        if not filename:
            filename = self.AskSaveAsFileName(self._writer_filter, message=message,
                                              defaultfile=defaultfilename)

        if not filename:
            return -1

        self.SetFileName(filename)

        if self._writer is None:
            self.create_writer()

        try:
            self._writer.SetFileName(filename)
        except AttributeError, message:
            dlg = wx.MessageDialog(component.getUtility(
                IMicroViewMainFrame), str(message), 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

            return -1
        self._writer.SetInput(image)

        # copy header information from the input file into the output file
        title = None

        header = image.GetHeader()
        if 'title' in header:
            title = header['title']
        self._writer.SetHeader(header)

        if title:  # poor VFFWriter...
            try:
                self._writer.SetTitle(title)
            except:
                pass

        with wx.BusyCursor():
            self._writer.SetProgressText(progressText)

            # MINC output need special attention
            if hasattr(self._writer._writer, 'SetMINCAttribute'):

                # update image (VTK-6 compatible)
                image.GetProducerPort().GetProducer().Update()

                if image.GetActualMemorySize() > 400000:
                    message = "File too large, unable to export to MINC."
                    dlg = wx.MessageDialog(component.getUtility(
                        IMicroViewMainFrame), message, 'Error', wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()

                vmin, vmax = image.GetScalarRange()

                # we want to keep the image in original value
                self._writer.Initialize()
                self._writer.SetMINCAttribute('image', 'valid_min', vmin)
                self._writer.SetMINCAttribute('image', 'valid_max', vmax)

            ret = 0

            try:
                # give app last-ditch opportunity before writing image
                ortho = component.getUtility(ICurrentOrthoView)
                event.notify(ImageWriteBeginEvent(ortho.GetImageIndex()))

                self._writer.Write()
            except IOError, e:
                logging.exception("MicroViewIO")
                dlg = wx.MessageDialog(component.getUtility(
                    IMicroViewMainFrame), "%s" % e.message, 'Error', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

        # check to make sure progressbar has made it to 100%
        if self._writer.GetProgress() < 1.0:
            self._writer.UpdateProgress(1.0)

        # disconnect writer's input
        self._writer.SetInput(None)

        return ret

    def SaveReorientedVolume(self, image, filename=None, defaultfilename=''):
        """Save re-oriented volume as...
        This method is now deprecated - reorientation can be done into memory as well, so the need for a specific
        to disk version isn't there anymore."""

        self._SaveImageToFile(image,
                              progressText='Saving Reoriented Image...',
                              message='Save Reoriented Image to file...',
                              filename=filename,
                              defaultfilename=defaultfilename)

    def SaveVolume(self, AutoCrop=1, filename=None, defaultfilename=''):
        """Save transformed volume as..."""

        image = component.getUtility(ICurrentImage)

        if self._transform:
            # create an image reslice object
            reslice = vtk.vtkImageReslice()
            reslice.SetInterpolationModeToCubic()
            reslice.SetInput(image.GetRealImage())

            if AutoCrop:
                reslice.AutoCropOutputOn()
            else:
                reslice.AutoCropOutputOff()
            reslice.SetResliceTransform(self._transform)
            image = MVImage.MVImage(reslice.GetOutputPort(), input=image)

        return self._SaveImageToFile(image,
                                     progressText='Saving Image...',
                                     filename=filename,
                                     defaultfilename=defaultfilename)

    def SaveSubVolume(self, filename='', stencil_data=None):
        """Save sub volume defined by roi or stencil..."""

        if not stencil_data:
            logging.error("ROI is not set")
            return -1

        # fire a warning if self._transform is on,
        # we'll implement the feature later
        if self._transform:
            logging.error(
                "FIX ME: image transform is not taken into consideration.")

        extent = stencil_data.GetExtent()
        image = component.getUtility(ICurrentImage)
        spacing = image.GetSpacing()
        origin = image.GetOrigin()

        # create an image reslice object
        reslice = vtk.vtkImageReslice()
        reslice.SetInterpolationModeToCubic()
        reslice.SetInput(image.GetRealImage())

        # VTK-6
        if vtk.vtkVersion().GetVTKMajorVersion() > 5:
            reslice.SetStencilData(stencil_data)
        else:
            reslice.SetStencil(stencil_data)

        reslice.SetOutputExtent(extent)
        reslice.SetOutputSpacing(spacing)
        reslice.SetOutputOrigin(origin)

        # set background value in stenciled image to minimum in image
        reslice.SetBackgroundLevel(image.GetScalarRange()[0])

        # Set a new origin to the output image,
        # We could have done this by setting new origin/extent
        # to reslice, but that would conflict with SetStencil.
        newOrigin = (origin[0] + spacing[0] * extent[0],
                     origin[1] + spacing[1] * extent[2],
                     origin[2] + spacing[2] * extent[4])
        changeInfo = vtk.vtkImageChangeInformation()
        changeInfo.SetInput(reslice.GetOutput())
        changeInfo.SetOutputOrigin(newOrigin)
        changeInfo.SetOutputExtentStart(0, 0, 0)

        # save the image
        return self._SaveImageToFile(MVImage.MVImage(changeInfo.GetOutputPort(), input=image),
                                     progressText='Saving sub volume...', filename=filename,
                                     message='Save Crop region to file...')

    def SaveStatisticsToDisk(self, results, filename=None):

        if filename is None:
            dlg = wx.FileDialog(
                component.getUtility(IMicroViewMainFrame), message="Save image statistics",
                defaultDir=self.GetCurrentDirectory(),
                defaultFile="statistics.csv",
                wildcard='CSV file (*.csv)|*.csv|Excel file (*.xls)|*.xls|All files|(*)',
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT | wx.FD_CHANGE_DIR
            )

            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
            else:
                return

        if filename:
            with wx.BusyCursor():
                if filename.lower().endswith('.csv'):
                    with open(filename, 'wb') as _f:
                        writer = unicodecsv.writer(
                            _f, encoding='utf-8', delimiter=',', dialect=unicodecsv.excel)
                        for row in results:
                            writer.writerow(row)
                elif filename.lower().endswith('.xls'):
                    wb = xlwt.Workbook(encoding='utf-8')
                    sheet = wb.add_sheet('Sheet1')
                    for r in range(len(results)):
                        for c in range(len(results[r])):
                            val = results[r][c]
                            try:
                                val = int(val)
                            except:
                                try:
                                    val = float(val)
                                except:
                                    pass
                            sheet.write(r, c, val)
                    wb.save(filename)

        logging.info("Statistical results saved to '%s'" % filename)

    def SaveLogToDisk(self, results, filename=None):

        if filename is None:
            dlg = wx.FileDialog(
                component.getUtility(IMicroViewMainFrame), message="Save log to file",
                defaultDir=self.GetCurrentDirectory(),
                defaultFile="MicroView_log.txt",
                wildcard='Text file|*.txt|All files|(*)',
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT | wx.FD_CHANGE_DIR
            )

            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
            else:
                return

        if filename:
            with open(filename, 'wt') as f:
                f.write(results)

        logging.info("Log results saved to '%s'" % filename)

    def SaveResultsToDisk(self, results, filename=None):

        if filename is None:
            dlg = wx.FileDialog(
                component.getUtility(IMicroViewMainFrame), message="Save results to file",
                defaultDir=self.GetCurrentDirectory(),
                defaultFile="MicroView_results.txt",
                wildcard='Text file|*.txt|All files|(*)',
                style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT | wx.FD_CHANGE_DIR
            )

            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
            else:
                return

        if filename:
            with open(filename, 'wt') as f:
                f.write(results)

        logging.info("Plugin results saved to '%s'" % filename)

    def SaveSubVolumeCoordinatesToDisk(self, filename, stencil=None):
        """Save the ROI coordinates. For backward compatibility.
        The original code is in StatsVolumeSelectionFactory.
        """

        if stencil is None:
            msg = "No stencil defined - cannot save subvolume coordinates"
            logging.error(msg)
            dlg = wx.MessageDialog(component.getUtility(IMicroViewMainFrame), msg,
                                   'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if not filename:
            filename = os.path.join(
                self.GetCurrentDirectory(), 'SubVolumeCoordinates')

        y_bin = 1
        z_bin = 1
        y_bin_read = 0
        z_bin_read = 0
        vol_origin_x = 0
        vol_origin_y = 0
        vol_origin_z = 0
        vol_origin_read = 0
        dims = component.getUtility(ICurrentImage).GetDimensions()

        extent = stencil.GetExtent()

        image = component.getUtility(ICurrentImage)
        header = image.GetHeader()

        # get the data origin
        if 'origin' in header:
            vol_origin_x = header['origin'][0]
            vol_origin_y = header['origin'][1]
            vol_origin_z = header['origin'][2]
            vol_origin_read = 1

        # get binning factors from input file header
        if 'y_bin' in header:
            y_bin = header['y_bin']
            y_bin_read = 1

        if 'z_bin' in header:
            z_bin = header['z_bin']
            z_bin_read = 1

        outOrigin = (extent[0], extent[2], extent[4])

        # HQ: Original code in StatsVolumeSelectionFactory calculates extent
        # from polydata bounds. There was no +1 there. However, there is
        # -1 in the the MinMaxCoordinates function for the clipping so that
        # the clipped image and the save coordinates match.
        outSize = (extent[1] - extent[0] + 1,
                   extent[3] - extent[2] + 1,
                   extent[5] - extent[4] + 1)

        strOutOrigin = "%1.3f %1.3f %1.3f" % outOrigin
        strOutSize = "%1.3f %1.3f %1.3f" % outSize

        if (y_bin_read == 1) and (z_bin_read == 1):
            strOutOriginUnbinned = "%1.3f %1.3f %1.3f" % (outOrigin[0] * y_bin,
                                                          outOrigin[1] * y_bin,
                                                          outOrigin[2] * z_bin)

            strOutSizeUnbinned = "%1.3f %1.3f %1.3f" % (outSize[0] * y_bin,
                                                        outSize[1] * y_bin,
                                                        outSize[2] * z_bin)
        else:
            strOutOriginUnbinned = "?"
            strOutSizeUnbinned = "?"

        if vol_origin_read == 1:
            strOriginUnbinned = "%1.3f %1.3f %1.3f" % (vol_origin_x * y_bin,
                                                       vol_origin_y * y_bin,
                                                       vol_origin_z * z_bin)
        else:
            strOriginUnbinned = "?"

        strWholeVolumeSize = "%0.3f %0.3f %0.3f" % (dims[0] * y_bin,
                                                    dims[1] * y_bin,
                                                    dims[2] * z_bin)

        try:
            file = open(filename, 'wt')

            file.write(strOutOrigin + '\n')
            file.write(strOutSize + '\n')
            file.write(strOutOriginUnbinned + '\n')
            file.write(strOutSizeUnbinned + '\n')
            file.write(strOriginUnbinned + '\n')

            file.write(strWholeVolumeSize + '\n')
            file.write("\n" + '\n')
            file.write("selection origin" + '\n')
            file.write("selection size" + '\n')
            file.write("selection origin (unbinned)" + '\n')
            file.write("selection size (unbinned)" + '\n')
            file.write("volume\'s origin (unbinned)" + '\n')
            file.write("whole volume size (unbinned)" + '\n')
            file.close()
            logging.info("Saved crop info to '%s'" % filename)
        except:
            message = "An error occurred while trying to write to coordinate file"
            dlg = wx.MessageDialog(component.getUtility(IMicroViewMainFrame), "%s '%s'" % (
                message, filename), 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        # Locus II code follows - write out crop region in world coordinates
        # only
        try:
            filename += '.xml'
            _file = open(filename, 'wt')
            _o = stencil.GetOrigin()
            _s = stencil.GetSpacing()
            _e = stencil.GetExtent()
            volname = component.getUtility(
                ICurrentViewportManager).GetPageState().GetFileName()
            volname = os.path.basename(volname)
            _file.write("<CropBoundary name='%s'>%s %s %s %s %s %s</CropBoundary>\n" %
                        (volname,
                         _o[0] + _e[0] * _s[0],
                            _o[0] + _e[1] * _s[0],
                            _o[1] + _e[2] * _s[1],
                            _o[1] + _e[3] * _s[1],
                            _o[2] + _e[4] * _s[2],
                            _o[2] + _e[5] * _s[2]))
            logging.info("Saved crop info to '%s'" % filename)
        except:
            message = "An error occurred while trying to write to coordinate file"
            dlg = wx.MessageDialog(component.getUtility(IMicroViewMainFrame), "%s '%s'" % (
                message, filename), 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        return 0

    def SaveAreaAsImage(self, stencil=None):
        """Write the scene in a ROI to an image file provided the ROI is rectangular and 2D.
        The original code is in StatsVolumeSelectionFactory.
        """

        if stencil is None:
            raise Exception("SaveAreaAsImage: Define an ROI first!!")

        if self._writer is None:
            self.create_writer()

        ext = stencil.GetExtent()

        image = component.getUtility(ICurrentImage)
        spacing = image.GetSpacing()
        origin = image.GetOrigin()

        # set up a permutation matrix
        reslicematrix = vtk.vtkMatrix4x4()

        if ext[2] == ext[3]:  # Y extent is zero, therefore this is XZ plane
            reslicematrix.DeepCopy((1, 0, 0, 0,
                                    0, 0, 1, 0,
                                    0, 1, 0, 0,
                                    0, 0, 0, 1))
            resliceextent = [ext[0], ext[1],
                             ext[4], ext[5],
                             ext[2], ext[3]]
            reslicespacing = [spacing[0], spacing[2], spacing[1]]
            resliceorigin = [origin[0], origin[2], origin[1]]
        elif ext[0] == ext[1]:  # X extent is zero, therefore ZY plane
            reslicematrix.DeepCopy((0, 0, 1, 0,
                                    0, 1, 0, 0,
                                    1, 0, 0, 0,
                                    0, 0, 0, 1))
            resliceextent = [ext[4], ext[5],
                             ext[2], ext[3],
                             ext[0], ext[1]]
            reslicespacing = [spacing[2], spacing[1], spacing[0]]
            resliceorigin = [origin[2], origin[1], origin[0]]
        elif ext[4] == ext[5]:  # no permutation required
            reslicematrix.Identity()
            resliceextent = list(ext)
            reslicespacing = list(spacing)
            resliceorigin = list(origin)
        else:  # this is not a 2D ROI
            raise Exception("SaveAreaAsImage: ROI must be two dimensional!")

        ft = self._writer.GetMatchingFormatStrings(
            vtkImageWriterBase.DEPTH_8 | vtkImageWriterBase.IMAGE_2D)

        filename = self.AskSaveAsFileName(
            ft, message='Save area as image', defaultfile='area.png')

        if filename == '':
            return

        reslice = vtk.vtkImageReslice()
        reslice.SetInput(image)
        reslice.SetResliceAxes(reslicematrix)  # set permutation matrix
        reslice.SetOutputExtent(resliceextent)
        reslice.SetOutputSpacing(reslicespacing)
        reslice.SetOutputOrigin(resliceorigin)
        reslice.InterpolateOn()

        # map image to 8-bit
        colors = vtk.vtkImageMapToColors()
        colors.SetOutputFormatToRGB()
        colors.SetLookupTable(self._wltable)
        colors.SetInput(reslice.GetOutput())

        try:
            self._writer.SetFileName(filename)
        except AttributeError, message:
            dlg = wx.MessageDialog(component.getUtility(
                IMicroViewMainFrame), message, 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

            ret = -1
        self._writer.SetInput(colors.GetOutput())
        try:
            self._writer.Write()
        except IOError:
            dlg = wx.MessageDialog(component.getUtility(
                IMicroViewMainFrame), "An error occurred trying to write file", 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        except AttributeError, message:
            dlg = wx.MessageDialog(component.getUtility(
                IMicroViewMainFrame), message, 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

            ret = -1

    def SetWLTable(self, wltable):
        self._wltable = wltable

    def ShowOutputDialog(self):
        self._outputDialog.Activate()

    def SaveViewPortSnapShot(self, renderer, filename):

        config = MicroViewSettings.MicroViewSettings.getObject()

        with wx.BusyCursor():
            windowToimage = vtk.vtkWindowToImageFilter()
            windowToimage.ReadFrontBufferOff()
            # make sure we've got a quality image
            renderer.GetRenderWindow().SetDesiredUpdateRate(0.0001)
            renderer.Render()
            # make sure backbuffer is up-to-date
            renderer.Render()
            windowToimage.SetInput(renderer.GetVTKWindow())
            windowToimage.Modified()
            output = windowToimage.GetOutput()
            output.Update()

        # create an image writer
        writer, ft = vtkLoadWriters.LoadImageWriters()
        ft = writer.GetMatchingFormatStrings(
            vtkImageWriterBase.DEPTH_8 | vtkImageWriterBase.IMAGE_2D)

        # loop until an image name is selected, or until the user quits
        if filename is None:

            # over-ride with system-wide directory
            curr_dir = os.getcwd()
            try:
                curr_dir = config.GlobalCurrentDirectory or curr_dir
            except:
                config.GlobalCurrentDirectory = curr_dir
            try:
                curr_dir = config.CurrentSnapshotDirectory or curr_dir
            except:
                config.CurrentSnapshotDirectory = curr_dir

            filename = EVSFileDialog.asksaveasfilename(
                defaultfile="snapshot.png",
                message='Save Snapshot',
                filetypes=ft, defaultdir=curr_dir,
                defaultextension='.png')

            if filename:
                config.CurrentSnapshotDirectory = curr_dir = os.path.dirname(
                    os.path.abspath(filename))
            else:
                return

        try:
            writer.SetFileName(filename)
        except AttributeError, message:
            logging.exception("MicroViewIO")
            dlg = wx.MessageDialog(component.getUtility(
                IMicroViewMainFrame), message, 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        writer.SetInput(windowToimage.GetOutput())

        try:
            writer.Write()
        except IOError, (errno, strerror):
            logging.exception("MicroViewIO")
            message = '[Errno %d]: %s' % (errno, strerror)
            dlg = wx.MessageDialog(component.getUtility(
                IMicroViewMainFrame), message, 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def getColourImageFromSlicePlane(self, slicePlane):
        """Given an EVSSlicePlaneFactory() generate a corresponding RGB image"""

        colors = vtk.vtkImageMapToColors()
        colors.SetOutputFormatToRGB()
        colors.SetLookupTable(slicePlane.GetLookupTable())
        colors.SetInput(slicePlane.GetOutput())

        return colors

    def SavePlaneAsImage(self, slicePlane):
        """Save SlicePlane texture image into a 2D image file."""

        colors = self.getColourImageFromSlicePlane(slicePlane)

        # create an image writer
        writer, ft = vtkLoadWriters.LoadImageWriters()
        ft = writer.GetMatchingFormatStrings(
            vtkImageWriterBase.DEPTH_8 | vtkImageWriterBase.IMAGE_2D)

        config = MicroViewSettings.MicroViewSettings.getObject()

        # over-ride with system-wide directory
        curr_dir = os.getcwd()
        try:
            curr_dir = config.GlobalCurrentDirectory or curr_dir
        except:
            config.GlobalCurrentDirectory = curr_dir
        try:
            curr_dir = config.CurrentSnapshotDirectory or curr_dir
        except:
            config.CurrentSnapshotDirectory = curr_dir

        default = '.png'

        try:
            mviewIn = component.getUtility(ICurrentMicroViewInput)
            default = os.path.splitext(mviewIn.GetFileName())[-1] or default
        except:
            pass

        filename = EVSFileDialog.asksaveasfilename(
            message='Save Slice Plane Image',
            defaultfile='slice' +
            default,
            filetypes=ft,
            defaultdir=curr_dir,
            defaultextension=default)
        if filename:
            curr_dir, file = os.path.split(filename)
            config.CurrentSnapshotDirectory = curr_dir
            colors.GetOutput().UpdateInformation()
            try:
                writer.SetFileName(filename)
            except AttributeError, message:
                logging.exception("MicroViewIO")
                dlg = wx.MessageDialog(component.getUtility(
                    IMicroViewMainFrame), message, 'Error', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

            writer.SetInput(colors.GetOutput())
            try:
                writer.Write()
            except IOError, (errno, strerror):
                logging.exception("MicroViewIO")
                message = "[Errno %d]: %s" % (errno, strerror)
                dlg = wx.MessageDialog(component.getUtility(
                    IMicroViewMainFrame), message, 'Error', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

##########################################################################


#=====================================================================
# ExternalSelection
# This class represents image selection by an external source.  It
# acts as the connection between the external source and the MicroView
# application.
#=====================================================================
class ExternalSelection(object):

    m_strSource = ""

    def __init__(self):

        self._strPrimaryFile = ""
        self._aSelectedFiles = []
        self._bSeriesChanged = False

        if ExternalSelection.m_strSource == "":
            # Determine default filename

            strFolder = appdirs.user_data_dir(
                "MicroView", "Parallax Innovations")

            if (sys.platform == 'win32'):
                ExternalSelection.m_strSource = os.path.join(
                    strFolder,
                    'ExternalSelection'
                )
            elif 'linux' in sys.platform:
                ExternalSelection.m_strSource = '/usr/tmp/sdc_selection'

            if not os.access(strFolder, os.R_OK):
                try:
                    os.makedirs(strFolder)
                except:
                    pass

    def SeriesHasChanged(self):
        """Has the collection of files changed since the last refresh?"""
        return self._bSeriesChanged

    def Refresh(self):
        """Update with the latest content described by the external source."""
        try:
            fileSelection = open(ExternalSelection.m_strSource, 'rt')
            strLine = fileSelection.readline()
            self._strPrimaryFile = strLine.split()[0]
            self._bSeriesChanged = self._strPrimaryFile not in self._aSelectedFiles

            self._aSelectedFiles = []
            strLine = fileSelection.readline()
            self._aSelectedFiles = strLine.split()
            fileSelection.close()

        except:
            self._strPrimaryFile = ""
            self._aSelectedFiles = []
            self._bSeriesChanged = True

    def GetPrimaryFile(self):
        """Which is the primary selection, by name?"""
        return self._strPrimaryFile

    def GetSelectedFiles(self):
        """Return the set of selected files, by name."""
        return self._aSelectedFiles

#=====================================================================
# End of ExternalSelection
#=====================================================================


class MicroViewDICOMExaminer(object):

    def __init__(self, _dir):

        self._dir = _dir
        self.dicom_headers = {}
        self._dicomdir = None
        self.series = {}
        self.series_slice_locations = {}
        self._filenames = []
        self.bShouldUpdateDICOMDIR = True

    def GetSeriesInfo(self):
        return self.series

    def GetSeriesHeaders(self):
        return self.dicom_headers

    def GetSeriesSliceLocations(self):
        return self.series_slice_locations

    def GetDICOMFilenames(self):
        return self._filenames

    def GetDICOMDIR(self):
        return self._dicomdir

    def BusyStart(self):

        class BusyObject(object):

            def __enter__(self):
                pass

            def __exit__(self):
                pass

        return BusyObject()

    def Yield(self):
        pass

    def IsDICOMFile(self, filename):
        """Check file to see if it's DICOM"""

        if not os.path.exists(filename):
            return False

        try:
            with open(filename, 'rb') as _f:
                s = _f.read(512)
                if s[128:128 + 4] == 'DICM':
                    return True
                elif '\x08\x00\x08\x60' in s and ('MONOCHROME' in s or 'PALETTE' in s or 'RGB' in s):
                    return True
                else:
                    return False
        except:
            return False

    def ExamineDirectory(self, matching_tags={}):

        self.dicom_headers = {}
        self.series = {}
        self.series_slice_locations = {}
        self._filenames = glob.glob(os.path.join(self._dir, '*'))
        if self.bShouldUpdateDICOMDIR:
            dicomdir_filename = os.path.join(self._dir, 'DICOMDIR')
            self._dicomdir = dicomdir(dicomdir_filename)

        files = self._filenames[:]
        ignored_file_warning = False

        with self.BusyStart():

            for i in range(len(files)):

                # wake up GUI periodically
                if i % 10:
                    self.Yield()

                # update progress
                event.notify(ProgressEvent(
                    "Examining files...", float(i) / len(files)))

                # read DICOM header
                if not self.IsDICOMFile(files[i]):
                    self._filenames.remove(files[i])
                    continue

                # looks good - keep reading
                try:
                    ds = dicom.read_file(
                        files[i], stop_before_pixels=True, force=True)
                except:
                    # something went wrong - oops - our IsDICOMFile() failed
                    # us?!
                    self._filenames.remove(files[i])
                    continue

                # throw out DICOMDIR
                if ds.file_meta.MediaStorageSOPClassUID == '1.2.840.10008.1.3.10':
                    continue

                # update DICOMDIR for this data
                if self.bShouldUpdateDICOMDIR:
                    self._dicomdir.add_file(files[i], self._dir, ds=ds)

                series_number = ds.get('SeriesNumber')
                acq_number = ds.get('AcquisitionNumber')
                label = '{0}.{1}'.format(series_number, acq_number)

                try:
                    slice_loc = float(ds.ImagePositionPatient[2])
                except:
                    slice_loc = ds.get('SliceLocation')

                if series_number is not None:
                    if label not in self.series:
                        self.series[label] = []
                        self.dicom_headers[label] = ds
                        self.series_slice_locations[label] = []

                    # filter out files that don't belong
                    file_matched = True
                    for key in matching_tags:
                        if ds.get(key) != matching_tags[key]:
                            if ignored_file_warning is False:
                                ignored_file_warning = True
                                # we do this like this to avoid too many log
                                # messages
                                logging.debug("Ignoring file {0} because of mismatched tag {1} ({2} != {3})".format(
                                    files[i], key, ds.get(key), matching_tags[key]))
                            file_matched = False
                            break

                    if file_matched:
                        # sort images into sequences
                        self.series[label].append(files[i])

                        # record slice locations
                        if slice_loc is not None:
                            self.series_slice_locations[
                                label].append(slice_loc)

        # finalize DICOMDIR
        if self.bShouldUpdateDICOMDIR:
            self._dicomdir.update()

        # now sort image files according to location
        event.notify(ProgressEvent("Examining files...", 1.0))


class wxMicroViewDICOMExaminer(MicroViewDICOMExaminer):

    def BusyStart(self):
        return wx.BusyCursor()

    def Yield(self):
        pass
        # wx.SafeYield(onlyIfNeeded=True)


def VTKImageToBitmap(image, w, h, flip=False):
    """create a thumbnail of a VTK image"""

    if isinstance(image, vtk.vtkObject):
        real_image = image
    else:
        real_image = image.GetRealImage()

    _min, _max = real_image.GetScalarRange()
    numC = real_image.GetNumberOfScalarComponents()

    # map to 8-bit
    if numC == 3:
        image2 = image
    else:
        colors = vtk.vtkImageMapToColors()
        colors.SetOutputFormatToRGB()
        lut = vtk.vtkLookupTable()
        lut.SetSaturationRange(0, 0)
        lut.SetHueRange(0, 0)
        lut.SetValueRange(0, 1)
        lut.Build()
        lut.SetTableRange(_min, _max)
        colors.SetLookupTable(lut)
        colors.SetInput(real_image)
        image2 = colors.GetOutput()
        image2.Update()

    # wrap image for convenience
    if isinstance(image2, vtk.vtkObject):
        image2 = MVImage.MVImage(image2)
        image2.GetRealImage().Update()

    # export to an RGB array
    arr = image2.get_array().copy()
    _h, _w = arr.shape[0], arr.shape[1]

    # flip?
    if flip:
        arr = arr[::-1, :, :]

    # convert to a wx image
    wx_image = wx.EmptyImage(_w, _h)
    wx_image.SetData(arr.tostring())

    # rescale
    wx_image = wx_image.Scale(w, h, wx.IMAGE_QUALITY_HIGH)

    # convert to bitmap
    wxBitmap = wx_image.ConvertToBitmap()

    return wxBitmap
