import logging
import wx
import SynchronizeImageDialog


class SynchronizeImageDialogC(SynchronizeImageDialog.SynchronizeImageDialog):

    def __init__(self, parent):
        SynchronizeImageDialog.SynchronizeImageDialog.__init__(self, parent)

    def SetCurrentSyncList(self, current_index, image_list, current_sync_list):

        image_list.sort()
        idx_map = [il[0] for il in image_list]

        self.m_listBoxImageList.Clear()
        if len(image_list) > 0:
            self.m_listBoxImageList.InsertItems([i[1] for i in image_list], 0)
            for idx in current_sync_list:
                try:
                    idx2 = idx_map.index(idx)
                    self.m_listBoxImageList.SetSelection(idx2)
                except ValueError:
                    logging.warning("Couldn't find index {0}".format(idx))
        else:
            self.m_checkBoxDisableSync.SetValue(1)
            self.m_checkBoxDisableSync.Disable()

    def GetCurrentSyncList(self):
        return self.m_listBoxImageList.GetSelections()

    def onCheckBox(self, evt):
        self.m_listBoxImageList.Enable(not evt.IsChecked())

    def onButtonReset(self, evt):
        """Reset list of synchronized images"""
        self.m_listBoxImageList.SetSelection(wx.NOT_FOUND)

    def onListBoxDoubleClick(self, evt):
        self.EndModal(wx.ID_OK)
