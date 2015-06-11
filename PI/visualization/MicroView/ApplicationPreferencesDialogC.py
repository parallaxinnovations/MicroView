import wx
import ApplicationPreferencesDialog


class ApplicationPreferencesDialogC(ApplicationPreferencesDialog.ApplicationPreferencesDialog):

    def __init__(self, parent):

        # call base class
        ApplicationPreferencesDialog.ApplicationPreferencesDialog.__init__(
            self, parent)

        # add default settings
        self._treeList = [
            ('Display', [
             'Display option 1', 'Display option 2', 'Display option 3']),
            ('Miscellaneous', [
             'Misc. option 1', 'Misc. option 2', 'Misc. option 3']),
        ]
        self.treeMap = {}

        # Connect Events
        self.m_searchCtrl2.Bind(wx.EVT_TEXT, self.RecreateTree)
        self.m_searchCtrl2.Bind(
            wx.EVT_SEARCHCTRL_CANCEL_BTN, lambda e: self.m_searchCtrl2.SetValue(''))
        self.m_searchCtrl2.Bind(wx.EVT_TEXT_ENTER, self.OnSearch)

        self.RecreateTree()

        self.m_treeCtrl1.ExpandAll()

    def GetValue(self):
        return None

    def AddEntry(self, entry):
        pass

    def OnSearch(self, evt=None):
        pass

    def RecreateTree(self, evt=None):
        # Catch the search type (name or content)

        fullSearch = False

        if evt:
            if fullSearch:
                # Do not`scan all the demo files for every char
                # the user input, use wx.EVT_TEXT_ENTER instead
                return

        ##expansionState = self.m_treeCtrl1.GetExpansionState()

        current = None
        item = self.m_treeCtrl1.GetSelection()
        if item:
            prnt = self.m_treeCtrl1.GetItemParent(item)
            if prnt:
                current = (self.m_treeCtrl1.GetItemText(item),
                           self.m_treeCtrl1.GetItemText(prnt))

        self.m_treeCtrl1.Freeze()
        self.m_treeCtrl1.DeleteAllItems()
        self.root = self.m_treeCtrl1.AddRoot("Preferences")
        self.m_treeCtrl1.SetItemImage(self.root, 0)
        self.m_treeCtrl1.SetItemPyData(self.root, 0)

        treeFont = self.m_treeCtrl1.GetFont()
        catFont = self.m_treeCtrl1.GetFont()

        treeFont.SetWeight(wx.BOLD)
        catFont.SetWeight(wx.BOLD)
        self.m_treeCtrl1.SetItemFont(self.root, treeFont)

        firstChild = None
        selectItem = None
        filter = self.m_searchCtrl2.GetValue()
        count = 0

        for category, items in self._treeList:
            count += 1
            if filter:
                if fullSearch:
                    items = self.searchItems[category]
                else:
                    items = [
                        item for item in items if filter.lower() in item.lower()]
            if items:
                child = self.m_treeCtrl1.AppendItem(
                    self.root, category, image=count)
                self.m_treeCtrl1.SetItemFont(child, catFont)
                self.m_treeCtrl1.SetItemPyData(child, count)
                if not firstChild:
                    firstChild = child
                for childItem in items:
                    image = count
                    theDemo = self.m_treeCtrl1.AppendItem(
                        child, childItem, image=image)
                    self.m_treeCtrl1.SetItemPyData(theDemo, count)
                    self.treeMap[childItem] = theDemo
                    if current and (childItem, category) == current:
                        selectItem = theDemo

        self.m_treeCtrl1.Expand(self.root)
        self.m_treeCtrl1.ExpandAll()
        if selectItem:
            self.skipLoad = True
            self.m_treeCtrl1.SelectItem(selectItem)
            self.skipLoad = False

        self.m_treeCtrl1.Thaw()
        self.searchItems = {}
