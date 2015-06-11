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
Info - this plugin displays information about the image.

Some fields are editable.  Click on the 'value' portion
"""

import datetime
import dicom
import collections
import logging
import wx
from zope import component, event, interface
import wx.propgrid as wxpg

from PI.visualization.common import MicroViewSettings, MicroViewObjectShelve
from PI.visualization.common.wxDICOMPropertyPage import populate_dicom_properties
from PI.visualization.common.events import MicroViewSettingsModifiedEvent
from PI.visualization.vtkMultiIO.events import HeaderValueModifiedEvent
from PI.visualization.MicroView import MicroViewPlugIn, data
from PI.visualization.MicroView.interfaces import ICurrentMicroViewInput, ICurrentImage, IPlugin,\
    ICurrentViewportManager, ICurrentOrthoView
from PI.visualization.MicroView.events import CurrentImageChangeEvent, NoImagesLoadedEvent,\
    ChangeImageLUT, ImageLUTChanged, BackgroundColourChangeEvent


class CustomColourProperty(wxpg.PyColourProperty):

    def __init__(self, *args, **kw):
        wxpg.PyColourProperty.__init__(self, *args, **kw)

    def GetEditor(self):
        return "TextCtrlWithButton"


class BackgroundColourEditor(wxpg.PyTextCtrlEditor):

    def __init__(self, *args, **kw):
        wxpg.PyTextCtrlEditor.__init__(self, *args, **kw)

    def OnEvent(self, propGrid, prop, ctrl, event):

        if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
            buttons = self.buttons
            evtId = event.GetId()

            if evtId == buttons.GetButtonId(0):
                # Do something when the first button is pressed
                wx.LogDebug("First button pressed")
                return False  # Return false since value did not change
            if evtId == buttons.GetButtonId(1):
                # Do something when the second button is pressed
                wx.MessageBox("Second button pressed")
                return False  # Return false since value did not change
            if evtId == buttons.GetButtonId(2):
                # Do something when the third button is pressed
                wx.MessageBox("Third button pressed")
                return False  # Return false since value did not change

        return self.CallSuperMethod("OnEvent", propGrid, prop, ctrl, event)


class Property(object):

    def __init__(self, category, name, value, value_type, read_only=False, disabled=False):
        self.category = category
        self.name = name
        self.value = value
        self.value_type = value_type
        self.read_only = read_only
        self.disabled = disabled


class ImageInfo(MicroViewPlugIn.MicroViewPlugIn):

    initialized = False

    interface.implements(IPlugin)

    __classname__ = "Image Information..."
    __shortname__ = "ImageInfo"
    __label__ = "Image Info"
    __description__ = "Displays image information"
    __iconname__ = "info"
    __menuentry__ = "|Tools|Image Information"
    __managergroup__ = "Tools"
    __tabname__ = "Image Info"

    def __init__(self, parent):

        MicroViewPlugIn.MicroViewPlugIn.__init__(self, parent)

        self._helpLink = 'image-info-image-information'

        # create a gui container
        MicroViewPlugIn.MicroViewPlugIn.CreatePluginDialogFrame(self, parent)
        self.CreateGUI()

        self.modtostring = {
            'BI': 'Biomagnetic Imaging', 'CD': 'Color flow Doppler', 'DD': 'Duplex Dopler', 'DG': 'Diaphanography',
            'CR': 'Computed Radiography', 'CT': 'Computed Tomography', 'ES': 'Endoscopy', 'LS': 'Laser Surface Scan',
            'PT': 'Positron emission tomography (PET)', 'ST': 'SPECT', 'MR': 'Magnetic Resonance NM', 'NM': 'Nuclear Medicine',
            'XA': 'X-Ray Angiography', 'US': 'Ultrasound', 'RG': 'Radiographic Imaging', 'TG': 'Thermography',
            'RF': 'Radio Fluoroscopy', 'DX': 'Digital Radiography', 'MG': 'Mammography', 'IO': 'Itra-oral Radiography',
            'PX': 'Panoramic X-Ray', 'GM': 'General Microscopy', 'SM': 'Slide Microscopy',
            'OP': 'Ophthalmic Photography', 'OT': 'Other', 'IVUS': 'Itravascular Ultrasound',
            'PA': 'Photo-accoustic Ultrasound', 'RTIMAGE': 'Radiotherapy Image',
            'RTDOSE': 'Radiotherapy Dose', 'RTSTRUCT': 'Radiotherapy Structure Set', 'RTPLAN': 'Radiotherapy Plan',
            'RTRECORD': 'RT Treatment Record',
        }

        self.patient_positions = {'': 'Unknown',
                                  'HFP': 'Head first-prone',
                                  'HFS': 'Head first-supine',
                                  'FFP': 'Feet first-prone',
                                  'FFS': 'Feet first-supine',
                                  'HFDR': 'Head first-decibitus right',
                                  'HFDL': 'Head first-decibitus left',
                                  'FFDR': 'Feet first-decibitus right',
                                  'FFDL': 'Feet first-decibitus left'
                                  }

        self.modtostring = collections.OrderedDict(sorted(
            self.modtostring.items(), key=lambda t: t[0]))

        # get a reference to the app settings
        self._config = MicroViewSettings.MicroViewSettings.getObject()

        self._search_filter = None

        # listen to certain zope events
        component.provideHandler(self.OnConfigModified)
        component.provideHandler(self.onHeaderValueModifiedEvent)
        component.provideHandler(self.OnImageChangeEvent)
        component.provideHandler(self.OnNoImagesLoadedEvent)
        component.provideHandler(self.onImageLUTChanged)

        # Update entries
        self.UpdateHeaderValues()
        self.UpdateDICOMHeaderValues()

    def OnPluginClose(self):
        # unregister our zope handlers
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.OnConfigModified)
        gsm.unregisterHandler(self.onHeaderValueModifiedEvent)
        gsm.unregisterHandler(self.OnImageChangeEvent)
        gsm.unregisterHandler(self.OnNoImagesLoadedEvent)
        gsm.unregisterHandler(self.onImageLUTChanged)

    @component.adapter(CurrentImageChangeEvent)
    def OnImageChangeEvent(self, evt):
        self.UpdateHeaderValues()
        self.UpdateDICOMHeaderValues()

    @component.adapter(NoImagesLoadedEvent)
    def OnNoImagesLoadedEvent(self, evt):
        self._general_page.Clear()
        self._dicom_page.Clear()

    @component.adapter(ImageLUTChanged)
    def onImageLUTChanged(self, evt):
        self.UpdateHeaderValues()

    @component.adapter(MicroViewSettingsModifiedEvent)
    def OnConfigModified(self, evt):
        self.UpdateHeaderValues()
        self.UpdateDICOMHeaderValues()

    @component.adapter(HeaderValueModifiedEvent)
    def onHeaderValueModifiedEvent(self, evt):
        """
        Respond to changes in image header
        """
        self.UpdateHeaderValues()
        self.UpdateDICOMHeaderValues()

    def CreateGUI(self):

        # use this object for lookup table info
        self.LD = data.LutData()

        # propgrid
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self._Dialog.SetSizer(self.sizer)
        self._pg = wxpg.PropertyGridManager(self._Dialog, style=wxpg.PG_SPLITTER_AUTO_CENTER |
                                            wxpg.PG_AUTO_SORT |
                                            wxpg.PG_TOOLBAR)
        self._pg.RegisterAdditionalEditors()
        if ImageInfo.initialized == 0:
            self._pg.RegisterEditor(BackgroundColourEditor)
            ImageInfo.initialized = True

        self._general_page = self._pg.AddPage("General Properties")
        self._dicom_page = self._pg.AddPage(
            "DICOM Tag Info", bmp=self._stockicons.getToolbarBitmap("dicom_button"))

        # add an anonymize button
        toolbar = self._pg.GetToolBar()
        toolbar.AddSeparator()
        toolId = wx.NewId()
        anon_bitmap = self._stockicons.getToolbarBitmap("anonymize")
        anon_tool = toolbar.AddLabelTool(
            toolId, "Anonymize", anon_bitmap, shortHelp="Anonymize Image", longHelp="Anonymize Image")
        toolbar.Realize()

        self.sizer.Add(self._pg, 1, wx.EXPAND)
        self._pg.Bind(wxpg.EVT_PG_CHANGED, self.OnPropertyChange)
        self._pg.Bind(wx.EVT_TOOL, self.onAnonymizeButton, anon_tool)

        # search button
        self.m_searchCtrl = wx.SearchCtrl(self._Dialog, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER)
        self.m_searchCtrl.ShowSearchButton(True)
        self.m_searchCtrl.ShowCancelButton(True)
        self.sizer.Add(self.m_searchCtrl, 0, wx.BOTTOM | wx.EXPAND, 5)

        # Connect Events
        self.m_searchCtrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.onSearchCancel)
        self.m_searchCtrl.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.onSearch)
        self.m_searchCtrl.Bind(wx.EVT_TEXT_ENTER, self.onSearch)

    def onSearch(self, evt):
        self._search_filter = evt.GetString()
        self.update_display()

    def onSearchCancel(self, evt):
        self._search_filter = None
        self.update_display()

    def update_display(self):
        """update displayed tags"""
        self.set_search_filter(self._search_filter)
        self.UpdateHeaderValues()
        self.UpdateDICOMHeaderValues()

    def set_search_filter(self, s):
        self._search_filter = s

    def UpdateDICOMHeaderValues(self):

        self._dicom_page.Clear()

        # get main frame widget - abort if something goes wrong
        # for instance - handle case where all tabs are closed
        try:
            image = component.getUtility(ICurrentImage)
            dicom_header = image.GetDICOMHeader()
        except:
            return

        # DICOM Info
        self._dicom_page.Append(wxpg.PropertyCategory("DICOM Tags"))

        populate_dicom_properties(dicom_header, self._dicom_page, search_filter=self._search_filter)

    def sizeof_fmt(self, num):
        for x in ['bytes', 'KiB', 'MiB', 'GiB']:
            if num < 1024.0:
                return "%3.2f %s" % (num, x)
            num /= 1024.0
        return "%3.1f%s" % (num, 'TiB')

    def UpdateHeaderValues(self):

        # clear the existing general page
        self._general_page.Clear()

        # get main frame widget - abort if something goes wrong
        # for instance - handle case where all tabs are closed
        try:

            try:
                image = component.getUtility(ICurrentImage)
            except component.ComponentLookupError:
                # no image is loaded
                return

            header = image.GetHeader().copy()
            dicom_header = image.GetDICOMHeader()
            pageState = component.getUtility(
                ICurrentViewportManager).GetPageState()
        except:
            logging.exception("ImageInfo")
            return

        # if page isn't an image, get out of here early
        if pageState.GetPageType() != "image":
            return

        # remove hidden properties

        # Update all text fields in the dialog box
        # Title
        val = dicom_header.PatientsName
        if isinstance(val, list):
            val = '\\'.join(val)

        properties = {'Image Properties': [], 'Patient/Subject Info': [], 'Scan Properties': [],
                      'Reconstruction Properties': [], "Display Properties": [],
                      'Additional Properties': []}

        prop = Property("Image Properties",
                        "Number of Channels",
                        image.GetNumberOfScalarComponents(),
                        int, True)
        properties[prop.category].append(prop)

        spacing = image.GetSpacing()
        origin = image.GetOrigin()
        (SizeX, SizeY, SizeZ) = image.GetDimensions()
        _range = image.GetScalarRange()
        _size = SizeX * SizeY * SizeZ * image.GetScalarSize() * image.GetNumberOfScalarComponents()


        prop = Property("Image Properties", "Minimum Value", float(_range[0]), float, True)
        properties[prop.category].append(prop)

        prop = Property("Image Properties", "Maximum Value", float(_range[1]), float, True)
        properties[prop.category].append(prop)

        prop = Property("Image Properties", "Voxel Size (mm)",
                        "%.4F %.4F %.4F" % (spacing[0], spacing[1], spacing[2]), str, True)
        properties[prop.category].append(prop)

        prop = Property("Image Properties", "Image Origin (mm)",
                        "%.4F %.4F %.4F" % (origin[0], origin[1], origin[2]), str, True)
        properties[prop.category].append(prop)

        prop = Property("Image Properties", "Image Bit-depth",
                        int(image.GetScalarSize() * 8), int, True)
        properties[prop.category].append(prop)

        prop = Property("Image Properties", "Image Data Type",
                        image.GetScalarTypeAsString(), str, True)
        properties[prop.category].append(prop)

        prop = Property("Image Properties", "Dimensions",
                        "%d %d %d" % (SizeX, SizeY, SizeZ), str, True)
        properties[prop.category].append(prop)

        prop = Property("Image Properties", "Memory Required",
                        self.sizeof_fmt(_size), str, True)
        properties[prop.category].append(prop)

        prop = Property("Patient/Subject Info", "Title",
                        str(val).encode('utf-8'), str, False)
        properties[prop.category].append(prop)

        val = dicom_header.SeriesDescription
        prop = Property("Patient/Subject Info", "Subject",
                        str(val).encode('utf-8'), str, False)
        properties[prop.category].append(prop)

        if 'PatientPosition' in dicom_header:
            pos = dicom_header.PatientPosition
        else:
            pos = ''

        if pos in self.patient_positions:
            index = self.patient_positions.keys().index(pos)
        else:
            index = 0

        prop = Property("Patient/Subject Info", "Patient Position",
                        index, self.patient_positions.values(), False)
        properties[prop.category].append(prop)

        # Modality
        modality = dicom_header.Modality

        if modality in self.modtostring:
            index = self.modtostring.keys().index(modality)
        else:
            index = 0

        prop = Property("Scan Properties", "Modality",
                        index, self.modtostring.values(), False)
        properties[prop.category].append(prop)

        try:
            _d = image.GetDate()  # DICOM-style date
            dmy = None
            try:
                year, month, day = int(_d[0:4]), int(_d[4:6]), int(_d[6:8])
            except:
                logging.error("Unable to parse DICOM date: {0}".format(_d))
            _t = image.GetTime()  # DICOM_style time
            try:
                hour, minute, second, microsecond = int(
                    _t[0:2]), int(_t[2:4]), int(_t[4:6]), _t[6:]
                dmy = (day, month - 1, year)
            except:
                logging.error("Unable to parse DICOM time: {0}".format(_t))

            if dmy:
                prop = Property("Scan Properties", "Date",
                                wx.DateTimeFromDMY(*dmy), wx.DateTime, False)
                properties[prop.category].append(prop)
        except:
            logging.exception("UpdateHeaderValues")

        # Scan-related fields (deprecated)
        scan_mapping = {'spacingunit': (str, 'Measurement Unit'), }

        # handle old-style keywords (deprecated)
        for key in header:
            if key.startswith('scan_') or key.startswith('scanner_'):
                if key in scan_mapping:
                    dtype, label = scan_mapping[key]
                else:
                    dtype, label = (str, key)

                if dtype == float or isinstance(header[key], float):
                    prop = Property("Scan Properties", label, float(header[key]), float, False)
                elif dtype == int or isinstance(header[key], int):
                    prop = Property("Scan Properties", label, int(header[key]), int, False)
                else:
                    prop = Property("Scan Properties", label, str(header[key]), str, False)

                properties[prop.category].append(prop)

        # scan-related DICOM fields
        dicom_scan_fields = {'ExposureTime': (float, 'Exposure Time (ms)'),
                             'KVP': (float, 'X-Ray Voltage (kVp)'),
                             'XRayTubeCurrent': (float, 'X-Ray Tube Current (mA)'),
                             'XRayTubeCurrentInmA': (float, u'X-Ray Tube Current (mA)'),
                             'XRayTubeCurrentInuA': (float, u'X-Ray Tube Current (\u00b5A)'),
                             'DistanceSourceToPatient': (float, 'Object Position (mm)'),
                             'DistanceSourceToDetector': (float, 'Detector Position (mm)'),
                             'Manufacturer': (str, 'Scanner Manufacturer'),
                             'ManufacturerModelName': (str, 'Scanner Model'),
                             'ProtocolName': (str, 'Protocol Name'),
                             }

        # handle DICOM keywords
        for key in dicom_scan_fields:
            if key in dicom_header:
                dtype, label = dicom_scan_fields[key]
                value = dicom_header.get(key)
                if dtype == float:
                    try:
                        value = float(value)
                        prop = Property("Scan Properties", label, value, float, False)
                        properties[prop.category].append(prop)
                        continue
                    except:
                        dtype = str
                elif dtype == int:
                    try:
                        value = int(value)
                        prop = Property("Scan Properties", label, value, int, False)
                        properties[prop.category].append(prop)
                        continue
                    except:
                        dtype = str

                prop = Property("Scan Properties", label, str(dicom_header.get(key)), str, False)
                properties[prop.category].append(prop)

        # Reconstruction-related fields
        recon_property_created = False
        recon_mapping = {'recon_sw_version': (str, 'Software Version'),
                         'recon_git_sha1': (str, 'Software SHA1'),
                         'recon_date': (str, 'Reconstruction Date'),
                         'recon_center_of_rotation': (float, 'Center of Rotation'),
                         'recon_central_slice': (float, 'Central Slice'),
                         'recon_filter_type': (str, 'Filter Type'),
                         'recon_auth': (int, 'Reconstruction Authorized'),
                         'recon_cmdLine': (str, 'Commandline'),
                         'recon_gate_delay_us': (float, u'Gating delay (\u00b5s)'),
                         'recon_gate_window_us': (float, u'Gating window (\u00b5s)'),
                         'ct_recon_macaddr': (str, 'Ethernet Address'),
                         'ct_recon_every_nth_proj': (int, 'View Skip'),
                         'ct_cone_angle': (float, 'Cone Angle (deg)')}

        for key in header.keys():
            if key.startswith('recon_') or key.startswith('ct_recon_') or key in ('y_bin', 'z_bin'):
                if key in recon_mapping:
                    dtype, label = recon_mapping[key]
                else:
                    dtype, label = (str, key)

                if dtype == float:
                    prop = Property("Reconstruction Properties", label, float(header[key]), float, False)
                    properties[prop.category].append(prop)
                else:
                    prop = Property("Reconstruction Properties", label, str(header[key]), str, False)
                    properties[prop.category].append(prop)

                del(header[key])

        try:
            if modality == 'CT':
                prop = Property("Reconstruction Properties", "Air Value", float(header.get('air', 0.0)), float, False)
                properties[prop.category].append(prop)
                prop = Property("Reconstruction Properties", "Water Value", float(header.get('water', 0.0)), float, False)
                properties[prop.category].append(prop)
                prop = Property("Reconstruction Properties", "Bone Value (HU", int(header.get('boneHU', 0)), int, False)
                properties[prop.category].append(prop)
        except:
            pass

        self._general_page.Append(wxpg.PropertyCategory("Display Properties"))
        prop = Property("Display Properties", "Texture Interpolation",
                        bool(self._config.bInterpolateTextures), bool, False)
        properties[prop.category].append(prop)

        numC = image.GetNumberOfScalarComponents()
        prop = Property("Display Properties", "Colour Table", pageState.lut_index, self.LD.get_names(), False,
                        disabled=(numC > 1))
        properties[prop.category].append(prop)

        # grab configuration object, see if there's any colour info in there
        try:
            root = MicroViewObjectShelve.MicroViewObjectShelve.getObject(
            ).getRoot()
            state = root['options.pane3D.background']
            bg1 = state.GetTopColour()
            bg2 = state.GetBottomColour()
            use_gradient = state.GetGradientState()
        except:
            bg1 = bg2 = (0, 0, 0)
            use_gradient = True

        # for the moment, colour editing shall be disabled
        prop = Property("Display Properties", "Background Colour #1", bg1, tuple, False)
        properties[prop.category].append(prop)
        prop = Property("Display Properties", "Background Colour #2", bg2, tuple, False)
        properties[prop.category].append(prop)
        prop = Property("Display Properties", "Enable Background Gradient", use_gradient, bool, False)
        properties[prop.category].append(prop)

        # everything else
        for key in header:
            _k = key.lower()
            if not (_k.startswith('recon_') or _k.startswith('scan_') or _k.startswith('scanner_') or
                    _k.startswith('hidden')):
                if key.lower() not in ('size', 'air', 'water', 'bonehu', 'y_bin', 'z_bin'):
                    try:
                        prop = Property("Additional Properties", key, str(header[key]), str, False)
                        properties[prop.category].append(prop)
                    except:
                        logging.warning("duplicate tag: {0}".format(key))


        _filter = None
        if self._search_filter:
            _filter = self._search_filter.lower()
            _filter = _filter.split()

        added_categories = []

        for category in properties:
                for property in properties[category]:

                    name = property.name
                    value = property.value

                    # apply filter
                    should_display = False
                    if _filter:
                        for _f in _filter:
                            if _f in unicode(name).lower() or _f in unicode(repr(value)).lower():
                                should_display = True
                                break
                        if not should_display:
                            continue

                    if category not in added_categories:
                        added_categories.append(category)
                        self._general_page.Append(wxpg.PropertyCategory(category))

                    if property.value_type is int:
                        _id = wxpg.IntProperty(property.name, value=property.value)
                    elif property.value_type is float:
                        _id = wxpg.FloatProperty(property.name, value=property.value)
                    elif property.value_type is str:
                        _id = wxpg.StringProperty(property.name, value=property.value)
                    elif isinstance(property.value_type, list):
                        # enum
                        _id = wxpg.EnumProperty(property.name, property.name, property.value_type,
                                                range(len(property.value_type)), property.value)
                    elif property.value_type is wx.DateTime:
                        # date
                        _id = wxpg.DateProperty(property.name, value=property.value)
                        _id.SetAttribute(wxpg.PG_DATE_PICKER_STYLE, wx.DP_DROPDOWN | wx.DP_SHOWCENTURY)
                    elif property.value_type is bool:
                        _id = wxpg.BoolProperty(property.name, value=property.value)
                    elif property.value_type is tuple:
                        _id = wxpg.ColourProperty(property.name, value=property.value)

                    self._general_page.Append(_id)
                    if property.read_only:
                        _id.ChangeFlag(wxpg.PG_PROP_READONLY, True)
                    if property.disabled:
                        self._general_page.DisableProperty(_id)

    def onAnonymizeButton(self, evt):

        dlg = wx.MessageDialog(
            wx.GetApp().GetTopWindow(), "This function will attempt to replace patient-specific details\nfrom the " +
                "header of this image and replace them with generic values.\n\nWould you like to anonimize " +
                "this image?", 'Anonymize', wx.YES_NO)
        ret = dlg.ShowModal()
        dlg.Destroy()
        if ret == wx.ID_YES:
            # go anonymize the image
            image = component.getUtility(ICurrentImage)
            dicom_header = image.GetDICOMHeader()
            dicom_header.walk(self.PN_callback)

            # Change Patient ID
            dicom_header.PatientID = "MICROVIEW^USER^000"

            # Remove data elements (should only do so if DICOM type 3 optional)
            # Use general loop so easy to add more later
            # Could also have done: del ds.OtherPatientIDs, etc.
            for name in ['OtherPatientIDs', 'OtherPatientIDsSequence', 'PatientsSex', 'PatientsAge',
                         'PatientsWeight', 'PatientsAddress', 'PatientComments', 'PatientSize']:
                if name in dicom_header:
                    delattr(dicom_header, name)

            # Same as above but for blanking data elements that are type 2.
            for name in ['PatientBirthDate']:
                if name in dicom_header:
                    dicom_header.data_element(name).value = ''

            # Set Accession number to a time stamp
            if 'AccessionNumber' in dicom_header:
                d = datetime.datetime.now()
                dicom_header.AccessionNumber = int(
                    '%04d%02d%02d' % (d.year, d.month, d.day))

            # Remove private tags if function argument says to do so. Same for
            # curves
            dicom_header.remove_private_tags()
            dicom_header.walk(self.curves_callback)

            # Update GUI
            self.UpdateDICOMHeaderValues()
            self.UpdateHeaderValues()

    def PN_callback(self, ds, data_element):
        """Called from the dataset "walk" recursive function for all data elements."""
        if data_element.VR == "PN":
            data_element.value = "* anonymized *"

    def curves_callback(self, ds, data_element):
        """Called from the dataset "walk" recursive function for all data elements."""
        if data_element.tag.group & 0xFF00 == 0x5000:
            del ds[data_element.tag]

    def OnPropertyChange(self, evt):

        # get the name of the property that has been modified
        name = evt.GetPropertyName()

        # get a reference to the current image header
        io_object = component.getUtility(ICurrentMicroViewInput)
        image = component.getUtility(ICurrentImage)
        header = image.GetHeader()
        dicom_header = image.GetDICOMHeader()

        sendModificationMessage = False

        if name == "Texture Interpolation":
            # Toggle texture interpolation
            logging.info("Turning texture interpolation %s" % {
                         True: 'On', False: 'Off'}[evt.GetPropertyValue()])
            self._config.bInterpolateTextures = evt.GetPropertyValue()
            event.notify(MicroViewSettingsModifiedEvent(self._config))
        elif name == "Image Origin (mm)":
            try:
                origin = map(float, evt.GetPropertyValue().split())
                io_object.GetOutput().SetOrigin(origin)
            except:
                logging.error(
                    "Unable to parse image origin value: " + evt.GetPropertyValue())
        elif name == "Modality":
            value = self.modtostring.keys()[
                evt.GetPropertyValue()]
            dicom_header.Modality = value
            sendModificationMessage = True
            key = 'modality'
        elif name == "Patient Position":
            value = self.patient_positions.keys()[
                evt.GetPropertyValue()]
            dicom_header.PatientPosition = value
            sendModificationMessage = True
            key = 'patient pos'
        elif name == "Colour Table":
            # send out a command to change this image's colour table
            orthoView = component.getUtility(ICurrentOrthoView)
            pageState = component.getUtility(
                ICurrentViewportManager).GetPageState()
            lut_index = evt.GetPropertyValue()
            image = component.getUtility(ICurrentImage)
            event.notify(ChangeImageLUT(
                orthoView, image, pageState, lut_index))
        elif name == 'Background Colour #1':
            root = MicroViewObjectShelve.MicroViewObjectShelve.getObject(
            ).getRoot()
            state = root['options.pane3D.background']
            state.SetTopColour(evt.GetPropertyValue()[0:3])
            root['options.pane3D.background'] = state
            event.notify(BackgroundColourChangeEvent())
        elif name == 'Background Colour #2':
            root = MicroViewObjectShelve.MicroViewObjectShelve.getObject(
            ).getRoot()
            state = root['options.pane3D.background']
            state.SetBottomColour(evt.GetPropertyValue()[0:3])
            root['options.pane3D.background'] = state
            event.notify(BackgroundColourChangeEvent())
        elif name == 'Enable Background Gradient':
            root = MicroViewObjectShelve.MicroViewObjectShelve.getObject(
            ).getRoot()
            state = root['options.pane3D.background']
            state.SetGradientState(evt.GetPropertyValue())
            root['options.pane3D.background'] = state
            event.notify(BackgroundColourChangeEvent())

        if sendModificationMessage is True:
            event.notify(HeaderValueModifiedEvent(key, value))

        # Update GUI
        self.UpdateDICOMHeaderValues()

##########################################################################


def createPlugin(panel):
    return ImageInfo(panel)
