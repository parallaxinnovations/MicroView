import logging
import DICOMDIRBrowseDialog
from PI.visualization.common.wxDICOMPropertyPage import populate_dicom_properties
from PI.visualization.MicroView.interfaces import IMicroViewOutput
import numpy as np
from scipy.misc import bytescale
import wx
import wx.gizmos as gizmos
import dicom
import os
from zope import component


class DICOMDIR_DisplayPanel(wx.Panel):

    def __init__(self, parent, path=None, main=None):

        wx.Panel.__init__(self, parent, -1)
        self.main = main
        self._last_filename = None
        self._ds = None
        self._search_filter = None

        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.tree = gizmos.TreeListCtrl(self, -1, style=wx.TR_DEFAULT_STYLE
                                        #| wx.TR_HAS_BUTTONS
                                        #| wx.TR_TWIST_BUTTONS
                                        #| wx.TR_ROW_LINES
                                        # | wx.TR_COLUMN_LINES
                                        #| wx.TR_NO_LINES
                                        | wx.TR_FULL_ROW_HIGHLIGHT
                                        )

        self._column_widths = [0, 0, 0, 0, 0]

        # list of files to load
        self.filenames = []
        # filename/title to give current selection
        self.filename = None
        self.canonical_series_name = 'DICOMDIR'

        isz = (16, 16)
        il = wx.ImageList(isz[0], isz[1])
        fldridx = il.Add(
            wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, isz))
        fldropenidx = il.Add(
            wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, isz))
        fileidx = il.Add(
            wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))

        self.tree.SetImageList(il)
        self.il = il

        # create some columns
        self.tree.AddColumn("Series ID")
        self.tree.AddColumn("Modality")
        self.tree.AddColumn("Description")
        self.tree.AddColumn("Acquisition")
        self.tree.AddColumn("Image Count")
        self.tree.SetMainColumn(0)  # the one with the tree in it...

        self.tree.SetColumnWidth(1, wx.COL_WIDTH_AUTOSIZE)
        self.tree.SetColumnWidth(3, wx.COL_WIDTH_AUTOSIZE)
        self.tree.SetColumnWidth(4, wx.COL_WIDTH_AUTOSIZE)

        self.root = self.tree.AddRoot("Patient List")

        self.tree.SetItemImage(
            self.root, fldridx, which=wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(
            self.root, fldropenidx, which=wx.TreeItemIcon_Expanded)

        if path is None:
            path = '/mnt/Users/jerem_000/Desktop/DICOM/DICOM/DICOMDIR'

        path = os.path.abspath(path)

        # Why is this path manipulation needed?
        if os.path.isdir(path):
            self.base_dir = os.path.abspath(os.path.join(path, '..'))
        else:
            self.base_dir = os.path.abspath(os.path.dirname(path))

        with wx.BusyCursor():

            try:
                self._full_ds = ds = dicom.read_dicomdir(path)
            except:
                logging.error("Unable to read '{}'".format(path))
                return

            self.filename = path

            # copied from ImageInfo.py ++
            encoding = ds.get('SpecificCharacterSet', 'utf-8')

            python_encoding = {
                '': 'iso8859',           # default character set for DICOM
                'ISO_IR 6': 'iso8859',   # alias for latin_1 too
                'ISO_IR 100': 'latin_1',
                'ISO 2022 IR 87': 'iso2022_jp',
                # XXX this mapping does not work on chrH32.dcm test files (but
                # no others do either)
                'ISO 2022 IR 13': 'iso2022_jp',
                # XXX chrI2.dcm -- does not quite work -- some chrs wrong. Need
                # iso_ir_149 python encoding
                'ISO 2022 IR 149': 'euc_kr',
                # from Chinese example, 2008 PS3.5 Annex J p1-4
                'ISO_IR 192': 'UTF8',
                'GB18030': 'GB18030',
                'ISO_IR 126': 'iso_ir_126',  # Greek
                'ISO_IR 127': 'iso_ir_127',  # Arab
                'ISO_IR 138': 'iso_ir_138',  # Hebrew
                'ISO_IR 144': 'iso_ir_144',  # Russian
            }
            # copied from ImageInfo.py --

            for patient in ds.patient_records:
                txt = patient.PatientName or '* No Patient Name *'
                self._column_widths[0] = max(
                    self._column_widths[0], self.tree.GetTextExtent(txt)[0])
                data = wx.TreeItemData()
                data.SetData((patient, -1))
                child = self.tree.AppendItem(self.root, txt, data=data)
                self.tree.SetItemText(child, patient.PatientID, 1)

                studies = patient.children
                for study in studies:

                    encoding = study.get('SpecificCharacterSet', 'utf-8')
                    if encoding in python_encoding:
                        encoding = python_encoding[encoding]

                    txt = study.StudyID or '* No Study ID *'
                    self._column_widths[1] = max(
                        self._column_widths[1], self.tree.GetTextExtent(txt)[0])
                    data = wx.TreeItemData()
                    data.SetData((study, -1))
                    child2 = self.tree.AppendItem(child, txt, data=data)
                    self.tree.SetItemText(
                        child2, study.get('StudyDate', '--'), 1)

                    try:
                        s = study.get(
                            'StudyDescription', '--').decode(encoding)
                    except:
                        s = '* Unprintable Study Description *'

                    self.tree.SetItemText(child2, s, 2)

                    all_series = study.children
                    for series in all_series:

                        image_records = series.children
                        acquisitions = {}

                        for rec in series.children:
                            if rec.DirectoryRecordType == 'IMAGE':
                                acq = rec.get('AcquisitionNumber', -1)
                                if acq not in acquisitions:
                                    acquisitions[acq] = 0
                                acquisitions[acq] += 1

                        txt = str(series.SeriesNumber)

                        series_desc = series.get(
                            'SeriesDescription', '* No Series Description *')

                        # support multiple acquisitions
                        if len(acquisitions) == 1 and -1 in acquisitions:
                            data = wx.TreeItemData()
                            data.SetData((series, -1))
                            child3 = self.tree.AppendItem(
                                child2, series_desc.decode(encoding), data=data)
                            modality = series.get('Modality', '--')
                            self.tree.SetItemText(child3, modality, 1)
                            self.tree.SetItemText(
                                child3, series_desc.decode(encoding), 2)
                            self.tree.SetItemText(
                                child3, str(acquisitions[-1]), 4)
                        else:
                            for acq in acquisitions:
                                data = wx.TreeItemData()
                                data.SetData((series, acq))
                                child3 = self.tree.AppendItem(
                                    child2, txt, data=data)
                                modality = series.get('Modality', '--')
                                self.tree.SetItemText(child3, modality, 1)
                                self.tree.SetItemText(
                                    child3, series_desc.decode(encoding), 2)
                                self.tree.SetItemText(child3, str(acq), 3)
                                self.tree.SetItemText(
                                    child3, str(acquisitions[acq]), 4)

            self.tree.Expand(self.root)

        self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectionChanged)

        self.tree.Bind(wx.EVT_SIZE, self._onResize)
        self.tree.Bind(wx.EVT_LIST_COL_END_DRAG, self._onResize, self)

    def _onResize(self, evt):

        evt.Skip()

        width = self.GetSize()[0]

        self.tree.SetColumnWidth(0, self._column_widths[0] + 40)
        self.tree.SetColumnWidth(1, self._column_widths[1] + 40)

        column_widths = [self.tree.GetColumnWidth(i) for i in range(5)]
        _sum = 0
        for i in [0, 1, 3, 4]:
            _sum += column_widths[i]

        # subtract 4 to accommodate for lines
        self.tree.SetColumnWidth(2, width - _sum - 8)

        column_widths = [self.tree.GetColumnWidth(i) for i in range(5)]

    def OnRightUp(self, evt):
        pos = evt.GetPosition()
        item, flags, col = self.tree.HitTest(pos)

        # display a popup menu
        menu = wx.Menu()

        _id = wx.NewId()
        menu.Append(_id, "Delete Series", "Delete series from disk")
        self.Bind(wx.EVT_MENU, self.OnDeleteSeries, id=_id)
        self.PopupMenu(menu)
        menu.Destroy()

    def OnDeleteSeries(self, evt):
        """User has requested a series of images be deleted.  Manage this."""

        item = self.tree.GetSelection()
        data = self.tree.GetItemData(item)

        if data:
            series, acqnum = data.GetData()
            image_filenames = self.GetSelectedSeriesFilenames(series, acqnum)

        # do you really want to delete?
        dlg = wx.MessageDialog(
            None, u"%d files selected for deletion.  Are you sure you want to do this?" % len(
                image_filenames), 'Are you sure?',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        try:
            bAreYouSure = (dlg.ShowModal() == wx.ID_YES)
        finally:
            dlg.Destroy()
        if not bAreYouSure:
            return

        # go ahead and delete files
        err_count = 0
        with wx.BusyCursor():
            try:
                for filename in image_filenames:
                    os.unlink(filename)
            except:
                if err_count == 0:
                    err_count += 1
                    logging.exception("DICOMBrowseDialogC")

        # Perform DICOMDIR reindex
        # TODO: this is overly aggressive - let's do it smarter later
        mviewout = component.getUtility(IMicroViewOutput)
        mviewout.DICOMDIRRegenerate(directory=os.path.dirname(self.filename))

    def OnSize(self, evt):
        self.tree.SetSize(self.GetSize())

    def OnSelectionChanged(self, evt):
        evt.Skip()
        self.UpdateSelection(evt)

    def OnActivate(self, evt):
        self.UpdateSelection(evt, activate=True)

    def process_ids(self, base_dir, ids, folder_bug_workaround=False):

        if not isinstance(ids, str):
            if folder_bug_workaround:
                ids = os.path.join(*ids[1:])
            else:
                ids = os.path.join(*ids)

        # Handle ISO9660 name mangling on linux
        filename = os.path.join(base_dir, ids)
        if os.path.exists(filename):
            return filename

        filename = os.path.join(base_dir, ids.lower())
        if os.path.exists(filename):
            return filename

        filename = os.path.join(base_dir, ids.upper())
        if os.path.exists(filename):
            return filename

        return os.path.join(base_dir, ids)

    def UpdateSelection(self, evt, activate=False):
        item = evt.GetItem()
        data = self.tree.GetItemData(item)
        ds = num = dir_type = None

        if data:
            ds, num = data.GetData()
            dir_type = ds.DirectoryRecordType

        if data is None:
            if activate:
                # optionally try to expand this object
                if self.tree.IsExpanded(item):
                    self.tree.Collapse(item)
                else:
                    self.tree.Expand(item)
            if dir_type is None:
                self.UpdateDICOMDetails(None)
                return

        # abort early if this is a non-terminal node
        if dir_type not in ('SERIES'):
            self.UpdateDICOMDetails(ds)
            self._last_filename = None
            return

        series, acqnum = ds, num
        image_records = series.children

        image_filenames = self.GetSelectedSeriesFilenames(series, acqnum)

        ds = None
        if len(image_filenames) > 0:
            filename = image_filenames[len(image_filenames) / 2]
            if filename != self._last_filename:
                self._last_filename = filename
                with wx.BusyCursor():
                    self._ds = ds = self.UpdateDICOMDetailsFromFile(filename)

        self.filenames = image_filenames

        # create a canonical series name
        name = ''
        if ds:
            if 'StudyID' in ds:
                name += '{}_'.format(ds.StudyID)
            if 'SeriesDescription' in ds:
                name += '{}_'.format(ds.SeriesDescription.strip()
                                     ).replace(' ', '_')
            if 'PatientName' in ds:
                name += '{}'.format(ds.PatientName.strip()).replace(' ', '_')
            self.canonical_series_name = name

    def GetSelectedSeriesFilenames(self, series, acqnum):

        image_records = series.children

        image_filenames = []
        for image_rec in image_records:

            # sanity check - is this an image?
            if image_rec.DirectoryRecordType != 'IMAGE':
                continue

            # sanity check - does this image match acquisition number?
            if acqnum != -1:
                if image_rec.AcquisitionNumber != acqnum:
                    continue

            filename = self.process_ids(
                self.base_dir, image_rec.ReferencedFileID, folder_bug_workaround=False)

            # sanity check
            if not os.path.exists(filename):
                filename = self.process_ids(
                    self.base_dir, image_rec.ReferencedFileID, folder_bug_workaround=True)

            # sanity check - some bad DICOMDIR files reference folder name
            image_filenames.append(filename)

        return image_filenames

    def GetFilenames(self):
        return self.filenames

    def GetDICOMDIRFileName(self):
        return self.filename

    def GetCanonicalSeriesName(self):
        return self.canonical_series_name

    def UpdateDICOMDetailsFromFile(self, filename):
        """load DICOM image a prepare a thumbnail bitmap. Also update dicom details."""

        try:
            ds = dicom.read_file(filename)
        except Exception, e:
            logging.exception("DICOMDIRBrowseDialogC")
            msg = "Unable to read file '{}'".format(filename)
            logging.error(msg)
            dlg = wx.MessageDialog(
               self, msg, 'Error', wx.OK | wx.ICON_ERROR)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
            return

        arr = ds.pixel_array
        if len(arr.shape) == 3:
            _, _h, _w = arr.shape
        else:
            _h, _w = arr.shape
            try:
                arr = bytescale(arr)
            except ValueError:
                # problems exist in scipy.misc.bytescale...
                arr = arr.astype('float32')
                arr = (arr - arr.min()) / (arr.max() - arr.min()) * 255.0
                arr = arr.astype('uint8')
            new_arr = np.zeros([_h, _w, 3], dtype='uint8')
            new_arr[:, :, 0] = arr
            new_arr[:, :, 1] = arr
            new_arr[:, :, 2] = arr
            arr = new_arr

        # create original bitmap
        wx_image = wx.EmptyImage(_w, _h)
        wx_image.SetData(arr.tostring())

        # now downsample
        w, h = self.main.m_bitmapPreview.GetSize()
        wx_image = wx_image.Scale(w, h, wx.IMAGE_QUALITY_HIGH)

        # convert to bitmap
        wxBitmap = wx_image.ConvertToBitmap()

        self.UpdateDICOMDetails(ds, bitmap=wxBitmap)
        return ds

    def UpdateDICOMDetails(self, ds=None, bitmap=None):
        if bitmap is None:
            bitmap = wx.NullBitmap
        self.main.m_bitmapPreview.SetBitmap(bitmap)
        self.update_displayed_tags(ds)

    def update_displayed_tags(self, ds=None):

        # now deal with property list
        if ds is None:
            ds = self._ds
        self.main.m_propertyGrid.Clear()
        if ds is None:
            return
        populate_dicom_properties(ds, self.main.m_propertyGrid, display_tag_numbers=False,
                                  search_filter=self._search_filter)

    def set_search_filter(self, s):
        self._search_filter = s


class DICOMDIRBrowseDialogC(DICOMDIRBrowseDialog.DICOMDIRBrowseDialog):

    def __init__(self, parent, path=None):

        # Start by calling base class constructor
        DICOMDIRBrowseDialog.DICOMDIRBrowseDialog.__init__(self, parent)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.m_panelMainArea.SetSizer(sizer)

        # add an addition panel to the widget
        self.dicom_browser = DICOMDIR_DisplayPanel(
            self.m_panelMainArea, path=path, main=self)
        self._search_filter = None
        sizer.Add(self.dicom_browser, 1, wx.EXPAND | wx.ALL, 0)

        # listen to double-click events
        self.dicom_browser.tree.Bind(
            wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)

        self.Layout()

    def OnActivate(self, evt):

        evt.Skip()

        # pass event to our widget
        self.dicom_browser.OnActivate(evt)

        # did something get selected?
        if len(self.GetFilenames()) > 0:
            # force a close because we're done
            self.EndModal(wx.ID_OK)

    def GetFilenames(self):
        return self.dicom_browser.GetFilenames()

    def GetDICOMDIRFileName(self):
        return self.dicom_browser.GetDICOMDIRFileName()

    def GetCanonicalSeriesName(self):
        return self.dicom_browser.GetCanonicalSeriesName()

    def onSearchCancel(self, evt):
        self._search_filter = None
        self.update_display()

    def onSearch(self, evt):
        self._search_filter = evt.GetString()
        self.update_display()

    def update_display(self):
        """update displayed tags"""
        self.dicom_browser.set_search_filter(self._search_filter)
        self.dicom_browser.update_displayed_tags()
