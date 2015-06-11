import os
import logging
import sys
import weakref
import appdirs
import wx
import wx.lib.buttons
import wx.lib.scrolledpanel
import wx.lib.stattext
import wx.lib.agw.aui as aui

from zope import component, interface, event

from PI.egg.pkg_resources import iter_entry_points

from PI.visualization.MicroView import _MicroView
from PI.visualization.MicroView.interfaces import IMicroViewMainFrame, IPluginManager, IPlugin, IROIProvider, \
    IStandardROIProvider, IFileDropHandler
from PI.visualization.MicroView.events import ROIDisabledEvent, ActionEvent, \
    PluginActivatedEvent
from PI.visualization.common import PluginHelper

import StockItems


class PluginManager(wx.Panel):

    interface.implements(IPluginManager)

    def __init__(self, parent=None, **kw):

        wx.Panel.__init__(self, parent, id=-1)

        # determine directory of installed software
        self._installdir = os.path.abspath(sys.path[0])

        # get an icon factory
        self._stockicons = StockItems.StockIconFactory()

        # determine default plugin directory
        self._plugindir = os.path.join(self._installdir, "Plugins")

        directories = [os.path.abspath(
            self._plugindir), os.path.join(appdirs.user_data_dir("MicroView", "Parallax Innovations"), "Plugins")]
        logging.info("System plugin directory: {0}".format(directories[0]))
        logging.info("User plugin directory: {0}".format(directories[1]))
        PluginHelper.SetupPlugins(directories)

        # some plugins need to be passed ROI key events
        self._standard_roi_plugins = []

        # we'll modify the splash screen
        splashlogger = logging.getLogger("splash")
        splashlogger.info("Loading plugins...")

        # create a list that holds the registered plugins
        self._pluginWeakReferenceList = []

        self._activeROIPluginWeakRef = {}
        self._activeROIManager = None
        self._TabName2PluginName = {"Tools & Apps": "Tools & Apps"}
        self._pluginCount = 0
        self._menubar = None

        # create a notebook and pack it into the default frame widget
        self.CreateNoteBook()

        # listen to certain zope events
        component.provideHandler(self.onActionEvent)

    def __del__(self):
        # unregister our zope handlers
        gsm = component.getGlobalSiteManager()
        gsm.unregisterHandler(self.onActionEvent)

    def importPluginClass(self, pluginName):
        """Import a plugin module by its name

        Args:
            pluginName (str): The name of the plugin

        Returns:
            obj:  An instance of the plubin
        """

        # If plugin is already loaded, return reference
        if pluginName in sys.modules:
            return sys.modules[pluginName]

        # Next, try to load plugin from an egg
        for module in iter_entry_points(group='PI.MicroView.MicroViewPlugIn.v1', name=pluginName):

            # Load module
            try:
                _class = module.load()
                return _class
            except:
                logging.exception("PluginManager")
                return None

        logging.error("Can't find plugin %s" % pluginName)

        return None

    def createPluginInstance(self, pluginName, bShouldSelect=True):
        """make an instance of the plugin, return it as a weak reference"""

        with wx.BusyCursor():

            # load the module
            _class = None
            try:
                _class = self.importPluginClass(pluginName)
            except:  # ImportError:
                logging.exception("createPluginInstance")
            finally:
                if _class is None:
                    logging.warning(
                        "The plug-in {0} could not be loaded.".format(pluginName))
                    return None

            # determine what this plugin will be called
            tabname = _class.GetTabName()

            # some plugins don't require a gui - check first
            panel = None
            if tabname:

                # create panel for the plugin immediately after loading the module
                # this should occur before the plugin is actually instantiated
                # create a new notebook page
                page = wx.Panel(self._notebook, -1, size=(500, 500))
                sizer = wx.BoxSizer(wx.VERTICAL)
                page.SetSizer(sizer)

                # TODO: fix this
                # JDG        helpCommand = lambda : self.ShowPluginHelp(plugin.GetShortName())
                #        closeCommand = lambda : self.DeactivatePlugin(plugin.GetShortName())

                # This is the root of the plugin widget -- the parent above will be used for
                # splash image etc.
                panel = wx.Panel(page, -1)

                # create a temporary titlebar - must be done after instantiating the
                # plugin
                tw = wx.lib.stattext.GenStaticText(page, -1, '')
                tw.SetBackgroundColour(wx.BLACK)
                tw.SetForegroundColour(wx.WHITE)
                sizer.Add(tw, 0, wx.EXPAND)
                sizer.Add(panel, 1, wx.EXPAND)

            try:
                plugin = _class(panel)
            except:
                logging.exception("PluginManager")
                if tabname:
                    text = "Error: Failed initializing " + \
                        pluginName + " plugin."
                    wx.StaticText(panel, -1, text)
                    tw.SetLabel("Unknown plugin Name")
                return None

            if tabname:
                icon = plugin.GetIcon(16) or wx.NullBitmap
                self._notebook.AddPage(page, tabname, bShouldSelect, icon)

                idx = self._notebook.GetPageCount()

                # Set page bitmap
                icon = plugin.GetIcon()
                if icon:
                    self._notebook.SetPageBitmap(idx, icon)
                else:
                    logging.debug("TODO: create an icon for %s" %
                                  plugin.GetClassName())

                tw.SetLabel(plugin.GetClassName())

                # This next line exists to ensure page is drawn correctly - it forces a
                # layout check
                page.SendSizeEvent()

                page.SetAutoLayout(True)

        return weakref.ref(plugin)

    def CloseManager(self):
        logging.error('CloseManager - warning, this shouldn\'t happen!')
        self.quit()

    def CreateNoteBook(self):

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        self._notebook = aui.AuiNotebook(self)

        style = self._notebook.GetWindowStyleFlag()
        style ^= aui.AUI_NB_WINDOWLIST_BUTTON
        style ^= aui.AUI_NB_CLOSE_BUTTON
        style ^= aui.AUI_NB_USE_IMAGES_DROPDOWN
        self._notebook.SetAGWWindowStyleFlag(style)
        self._notebook.Refresh()
        self._notebook.Update()

        self._notebook.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPluginClose)

        sizer.Add(self._notebook, 1, wx.EXPAND)

        # Add the "Tools & Applications" page to the notebook.
        self.ToolsAndAppsPage = wx.lib.scrolledpanel.ScrolledPanel(
            self._notebook, -1)

        sizer2 = wx.BoxSizer(wx.VERTICAL)
        self.ToolsAndAppsPage.SetSizer(sizer2)

        alignmentPanel = wx.Panel(self.ToolsAndAppsPage, -1)
        sizer2.Add(alignmentPanel)

        sizer3 = wx.BoxSizer(wx.VERTICAL)
        alignmentPanel.SetSizer(sizer3)

        self._notebook.AddPage(self.ToolsAndAppsPage, 'Tools & Apps')

        self.ToolsGroup = wx.Panel(alignmentPanel, -1)
        sizer3.Add(self.ToolsGroup, 0, wx.EXPAND | wx.ALL, 5)

        g = wx.StaticBox(self.ToolsGroup, label='Tools')
        self.ToolsSizer = wx.StaticBoxSizer(g, wx.VERTICAL)
        self.ToolsGroup.SetSizer(self.ToolsSizer)

        self.ApplicationsGroup = wx.Panel(alignmentPanel, -1)
        sizer3.Add(self.ApplicationsGroup, 0, wx.EXPAND | wx.ALL, 5)

        g = wx.StaticBox(self.ApplicationsGroup, label='Applications')
        self.ApplicationsSizer = wx.StaticBoxSizer(g, wx.VERTICAL)
        self.ApplicationsGroup.SetSizer(self.ApplicationsSizer)

        # set up scrolling
        self.ToolsAndAppsPage.SetAutoLayout(True)
        self.ToolsAndAppsPage.SetupScrolling()

        # this is where we should put our logo
        bmp = self._stockicons.getBitmap("parallax-logo")
        company_logo = wx.StaticBitmap(self, -1, bmp)
        sizer.Add(company_logo)

    def OnPluginClose(self, evt):

        page_index = self._notebook.GetSelection()
        page_text = self._notebook.GetPageText(page_index)
        pluginName = self._TabName2PluginName[page_text]

        if pluginName in ('Tools & Apps',):
            evt.Veto()
        else:
            self.DeactivatePlugin(pluginName)

    def RegisterPlugin(self, pluginweakref):
        """Registers an instance of a plugin with the system"""

        plugin = pluginweakref()
        _ref = weakref.ref(plugin)

        # register the plugin with zope
        gsm = component.getGlobalSiteManager()
        gsm.registerUtility(plugin, IPlugin, name=plugin.GetShortName())

        self._pluginWeakReferenceList.append(pluginweakref)

        self._TabName2PluginName[plugin.GetTabName()] = plugin.GetShortName()

        if IFileDropHandler.providedBy(plugin):
            # register the plugin with zope as an file drop handler (only if activated)
            gsm.registerUtility(
                plugin, IFileDropHandler, name=plugin.GetShortName())

    def GetPluginReferenceByName(self, pluginName, *args, **kw):
        """return a weakref reference to a plugin instance with the given pluginName"""

        # Search to see if plugin already exists
        gsm = component.getGlobalSiteManager()

        try:
            plugin = gsm.getUtility(IPlugin, name=pluginName)
            return weakref.ref(plugin)
        except interface.interfaces.ComponentLookupError:
            # plugin isn't currently in the registry
            pass

        # Go create plugin, and get weak reference to it
        pluginweakref = self.createPluginInstance(pluginName, *args, **kw)
        if pluginweakref:
            self.RegisterPlugin(pluginweakref)

        return pluginweakref

    def GetActivePluginName(self):

        page = self._notebook.GetCurrentPage()
        for plugin in self._pluginWeakReferenceList:
            p = plugin()
            if p._Dialog.GetParent() is page:
                # we've found the page
                return p.GetShortName()

    def ActivateStandardROIPlugins(self, **kw):
        """Activate any plugins that implement the IStandardROIProvider interface"""
        for plugin in self._standard_roi_plugins:
            self.ActivatePlugin(plugin.GetShortName(), **kw)

    def ActivatePlugin(self, pluginName, **kw):
        """Activates a registered plugin referenced by name"""

        pluginweakref = self.GetPluginReferenceByName(pluginName, **kw)

        if not pluginweakref:
            logging.error(pluginName + " not found.")
            return -1

        if kw.get('bShouldSelect', True):
            current_page = self._notebook.GetSelection()
            for page in range(self._notebook.GetPageCount()):
                page_text = self._notebook.GetPageText(page)
                pn = self._TabName2PluginName[page_text]
                if pn == pluginName:
                    # only select tab if it isn't current - otherwise a focus shift
                    # occurs
                    if page != current_page:
                        self._notebook.SetSelection(page)
                    break

        pluginweakref().OnPluginOpen()
        pluginweakref().ActivatePlugin()

        # send out a message indicating that a plugin has been instantiated
        event.notify(PluginActivatedEvent(pluginName))

        return 0

    @component.adapter(ActionEvent)
    def onActionEvent(self, evt):
        """
        Called whenever an ActionEvent has been received - usually generated by pressing the
        spacebar
        """
        page_index = self._notebook.GetSelection()
        page_text = self._notebook.GetPageText(page_index)

        # sanity check - make sure a plugin is selected
        if page_text == 'Tools & Apps':
            return

        pluginName = self._TabName2PluginName[page_text]
        pluginweakref = self.GetPluginReferenceByName(pluginName)

        if pluginweakref:
            pluginweakref().ActionEvent(evt.GetEvent())

    def HandleEventFromPlugins(self, obj, evt):
        """Mainly used for communication between plugins.
        """
        pass

    def GetROIType(self, image_index=None):

        roitype = None
        roi_plugin = self.GetActiveROIPlugin(image_index)
        if roi_plugin:
            roi_plugin = roi_plugin()
            if roi_plugin:
                roitype = roi_plugin.GetROIType(image_index)

        return roitype

    def GetROIStencilData(self, image_index):

        stencil = None
        roi_plugin = self.GetActiveROIPlugin(image_index)
        if roi_plugin:
            roi_plugin = roi_plugin()
            if roi_plugin:
                stencil = roi_plugin.GetROIStencilData(image_index)

        return stencil

    def GetROIBounds(self, image_index):

        bounds = None
        roi_plugin = self.GetActiveROIPlugin(image_index)
        if roi_plugin:
            roi_plugin = roi_plugin()
            if roi_plugin:
                bounds = roi_plugin.GetROIBounds(image_index)

        return bounds

    def GetROIExtent(self, image_index):

        extent = None
        roi_plugin = self.GetActiveROIPlugin(image_index)
        if roi_plugin:
            roi_plugin = roi_plugin()
            if roi_plugin:
                extent = roi_plugin.GetROIExtent(image_index)

        return extent

    def GetROIStats(self):
        return component.getUtility(IMicroViewMainFrame).GetROIStats()

    def DeactivatePlugin(self, pluginName):
        """Deactivates a registered plugin"""

        pluginweakref = self.GetPluginReferenceByName(pluginName)

        if pluginweakref:

            plugin = pluginweakref()

            # first let the plugin handle moving away from the plugin
            try:
                plugin.DeactivatePlugin()
            except:
                logging.exception("DeactivatePlugin")

            # next handle closure of the plugin
            try:
                plugin.OnPluginClose()
            except:
                logging.exception("DeactivatePlugin")

            # Destroy references to plugin
            gsm = component.getGlobalSiteManager()
            gsm.unregisterUtility(plugin, IPlugin, name=plugin.GetShortName())

            try:
                gsm.unregisterUtility(
                    plugin, IFileDropHandler, name=plugin.GetShortName())
            except Exception, e:
                pass

            del(self._TabName2PluginName[plugin.GetTabName()])
            self._pluginWeakReferenceList.remove(pluginweakref)

            return

    def ShowPluginHelp(self, pluginName):
        """Shows help section for this plugin"""
        plugin = self.GetPluginReferenceByName(pluginName)
        if plugin:
            component.getUtility(
                IMicroViewMainFrame).showHelp(plugin._helpLink)

    def SetMenu(self, m):
        self._menubar = m

    def Quit(self):
        """Shutdown routine for plugin manager.  Returns True if all okay, False if any plugin
           tries to abort the shutdown."""

        # deactivate all plugins.

        ret = True

        gsm = component.getGlobalSiteManager()

        # give each plugin a chance to abort shutdown
        for (name, plugin) in gsm.getUtilitiesFor(IPlugin):
            try:
                if not plugin.OnApplicationClose():
                    ret = False
                    logging.info(
                        "quit aborted by plugin {0}".format(plugin.GetShortName()))
                    return ret
            except:
                # make sure plugin errors don't cause MicroView shutdown to stop
                logging.exception('PluginManager')

        # deregister all ROI plugins
        for (name, plugin_class) in gsm.getUtilitiesFor(IROIProvider):
            gsm.unregisterUtility(
                plugin_class, IROIProvider, name=plugin_class.GetShortName())

        # deactivate/close each plugin
        for (name, plugin) in gsm.getUtilitiesFor(IPlugin):
            try:
                self.DeactivatePlugin(name)
            except:
                logging.exception("PluginManager")

#        # deactivate/close each plugin
#        for (name, plugin) in gsm.getUtilitiesFor(IPlugin):
#            self.DeactivatePlugin(name)

        return ret

    def CallPluginMethod(self, pluginName, methodName, *args, **kw):
        """call an arbitrary method of a plugin with arbitrary arguments"""
        plugin = self.GetPluginReferenceByName(pluginName)
        if not plugin:
            logging.error('Unknown plugin')
            return
        if not hasattr(plugin, methodName):
            logging.error('plugin %s has no method %s' % (
                pluginName, methodName))
            return
        return apply(getattr(plugin, methodName), args, kw)

    def LoadPlugins(self):
        """Load all available plugins"""

        # some plugins may request keybindings that should be mapped to them - we'll instantiate plugins
        # and reroute keyboard events there as needed

        self._keybindings = {}
        gsm = component.getGlobalSiteManager()

        # iterate over all plugins
        for module in iter_entry_points(group='PI.MicroView.MicroViewPlugIn.v1'):

            # Load module
            try:
                plugin_class = module.load()
            except:
                logging.exception("PluginManager")
                continue

            # does this class provide a standard ROI interface?
            if IStandardROIProvider.implementedBy(plugin_class):
                self._standard_roi_plugins.append(plugin_class)

            # does this class provide a generic ROI interface?
            if IROIProvider.implementedBy(plugin_class):
                # register the plugin with zope as an ROI provider too (prior to loading plugin)
                gsm.registerUtility(
                    plugin_class, IROIProvider, name=plugin_class.GetShortName())

            # bind a menu entry to this plugin
            menu = []

            m = plugin_class.GetMenuEntry()
            if m:
                menu = m.split('|')
            else:
                menu.append('Plugins')
                menu.append(plugin_class.GetClassName().replace('...', ''))

            sep_front = sep_back = 0
            if menu[0] == '':
                sep_front = 1
                menu = menu[1:]
            if menu[-1] == '':
                sep_back = 1
                menu = menu[:-1]
            if sep_front == 1:
                m = self._menubar.GetMenu(self._menubar.FindMenu(menu[0]))
                m.AppendSeparator()
            if len(menu) > 2:
                try:
                    self._menubar.addcascademenu(menu[0], menu[1], '')
                except ValueError:
                    pass
                menu = menu[1:]

            try:
                button_image = plugin_class.GetToolbarBitmap()
                menu_image = plugin_class.GetMenuBitmap()
            except:
                logging.exception("PluginManager")

            # Find menu, create ID, create menu item, add optional icon
            m = self._menubar.GetMenu(self._menubar.FindMenu(menu[0]))
            _id = wx.NewId()
            item = wx.MenuItem(m, _id, menu[
                               1] + '...', plugin_class.GetDescription())
            if menu_image:
                item.SetBitmap(menu_image)
            m.AppendItem(item)

            # Wire up callback for this menu item
            self.GetTopLevelParent().Bind(
                wx.EVT_MENU, lambda event, i=plugin_class.GetShortName(), s=self: s.ActivatePlugin(i), id=_id)

            if sep_back == 1:
                m = self._menubar.GetMenu(self._menubar.FindMenu(menu[0]))
                m.AppendSeparator()

            managergroup = plugin_class.GetManagerGroup()

            if managergroup:
                group = getattr(self, managergroup + 'Group')
                sizer = getattr(self, managergroup + 'Sizer')

                # create Button
                # TODO: convert to a bitmap button
                _id = wx.NewId()
                if button_image is None:
                    button_image = wx.EmptyBitmap(16, 16)

                button = wx.Button(
                    group, id=_id, label=menu[1], style=wx.BU_LEFT)
                button.SetBitmap(button_image)

                sizer.Add(button, 0, wx.EXPAND)
                self.Bind(wx.EVT_BUTTON, lambda event, s=self,
                          i=plugin_class.GetShortName(): s.ActivatePlugin(i), button)
