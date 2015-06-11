"""
Defines zope interfaces
"""


from zope import interface
from PI.visualization.common.interfaces import IProgress


class IImageProcessor(IProgress):

    """
    Provides classes that work on VTK images - it is expected that each method takes
    an image, and returns a modified version of the image using VTK's pipeline methodology.
    """


class IMicroViewMainFrame(interface.Interface):

    """
    Implements the main MicroView application class
    """


class IFileDropHandler(interface.Interface):

    """
    Object accepts file drops
    """

    def OnDropFilesEvent(self, filenames):
        """
        Handle a file drop
        """


class IROIProvider(interface.Interface):

    """
    Interface for ROI providers
    """

    def GetROIBounds(image_index):
        """
        Return ROI bounds
        """

    def GetROIExtent(image_index):
        """
        Return ROI extent
        """

    def GetROIStencil(image_index):
        """
        Returns ROI stencil
        """

    def GetROIPolyData(image_index):
        """
        Returns ROI polydata
        """


class IStandardROIProvider(IROIProvider):

    """
    Interface for so-called 'Standard' ROI providers.  In addition to the capabilities of
    an IROIProvider, these classes should also respond to certain ROI keybindings:  e.g.
    3, 7, and 8 keys.
    """


class IMicroViewInput(IProgress):

    """
    Interface for objects that load data from disk
    """


class ICurrentMicroViewInput(IProgress):

    """
    Interface for the currently-selected object that loads data from disk
    """


class IMicroViewOutput(IProgress):

    """
    Interface for objects that save data to disk
    """


class ICurrentMicroViewOutput(IProgress):

    """
    Interface for the currently-selected object that saves data to disk
    """


class IConfigFile(interface.Interface):

    """
    Represents the interface to a config file reader/writer
    """
    def set(section, option, value):
        """
        Set the value of a given option in a given section
        """

    def get(section, option):
        """
        Get the value of an option in a given section
        """


class IStockIconProvider(interface.Interface):

    """
    Interface for providing bitmaps and icons
    """
    def getBitmap(name, size):
        """
        Returns a resource as a wx bitmap
        """

    def getMenuBitmap(name):
        """
        Returns a resource as a wx bitmap, scaled for use in menus
        """


class IImage(interface.Interface):

    """
    Represents a VTK image
    """


class ICurrentImage(IImage):

    """
    Represents the currently selected VTK image
    """


class IPageState(interface.Interface):

    """
    Represents the generic state of one of MicroView`s notepad pages

    This interface will keep stuff common to all pages
    """

    def GetPageState(self):
        """Returns the page state"""


class ISpreadsheetState(IPageState):

    """
    Represents the state of a spreadsheet page - a specific instance of a
    MicroView notepad page
    """


class ICurrentSpreadsheetState(ISpreadsheetState):

    """
    Represents the state of a spreadsheet page - a specific instance of a
    MicroView notepad page
    """


class IViewerState(IPageState):

    """
    Represents the state of a viewer - a specific instance of a
    MicroView notepad page
    """


class ICurrentViewerState(IViewerState):

    """
    Represents the currently selected viewer state
    """


class IViewer(interface.Interface):

    """
    TODO: figure out what this interface does
    """

    def GetPageState(self):
        """Returns the page state"""


class ISpreadsheet(IViewer):

    """
    Represents a spreadsheet widget
    """

    def GetSpreadsheetIndex(self):
        """Returns the spread-sheet index"""


class ICurrentSpreadsheet(ISpreadsheet):

    """
    TODO: figure out what this interface does
    """


class IViewportManager(IViewer):

    """
    TODO: figure out what this interface does
    """

    def GetImageIndex(self):
        """Returns the image index"""


class ICurrentViewportManager(IViewportManager):

    """
    TODO: figure out what this interface does
    """


class IOrthoView(interface.Interface):

    """
    TODO: figure out what this interface does
    """


class ICurrentOrthoView(IOrthoView):

    """
    TODO: figure out what this interface does
    """


class IPluginManager(interface.Interface):

    """
    TODO: figure out what this interface does
    """


class IApplicationPreferencesManager(interface.Interface):

    """Application Preferences dialog"""


class IPlugin(IProgress):

    """
    Interface describing MicroView plugins
    """
    def GetClassName(cls):
        """Returns the classname for the given plugin"""

    def GetShortName(cls):
        """Returns shortname for plugin"""

    def GetDescription(cls):
        """Returns a description for this plugin"""

    def GetMenuBitmap(cls):
        """Returns a wx bitmap for this plugin suitable for use in a menu"""

    def GetToolbarBitmap(cls):
        """Returns a wx bitmap for this plugin suitable for use in a toolbar"""

    def GetMenuEntry(cls):
        """Return menu description"""

    def GetManagerGroup(cls):
        """Return manager group for this plugin (used in Apps&Tools page)"""

    def GetTabName(cls):
        """Returns the name used in tabbed labels"""

    def GetObjectState():
        """Returns a pickleable representation of this plugin"""

    def SetObjectState(o):
        """Sets up the plugin based on a pickleable class rep. object"""

    def Serialize():
        """Serialize the state of a plugin to a string"""

    def DeSerialize(s):
        """Deserialize the state of the plugin from a file"""

    def GetIcon(size):
        """Returns the wx bitmap resource defined for this plugin"""

    def GetMenuIcon():
        """Returns the wx menu icon resource defined for this plugin"""

    def GetCurrentDirectory():
        """Get working directory for this plugin"""

    def SaveCurrentDirectory(curr):
        """Save current directory for this plugin"""

    def ActionEvent(evt):
        """Place holder - override in a plugin to perform special functionality
            whenever user action occurs (generally, when spacebar is pressed)"""

    def GetUserAction():
        """Returns method invoked on user Action"""

    def InvokeProgressEvent(progress, progressText):
        """Post a zope progress event"""

    def OnPluginClose():
        """Override this method to permit the plugin to close itself cleanly"""

    def OnPluginOpen():
        """Override this method to permit the plugin to perform tasks
        when the plugin is _first_ activated"""

    def OnApplicationClose():
        """Override this method to permit the plugin to perform tasks
        when the application is closed.  Routine must return True if all
        is okay; False if the plugin requests an app shutdown abort."""

    def ActivatePlugin():
        """Plugin has been activated by the plugin manager"""

    def DeactivatePlugin():
        """Plugin has been deactivated by the plugin manager"""

    def HandleVTKProgressEvent(obj, evt):
        """
        A VTK object generated a progress event - convert it to a zope-style
        event
        """

    def isManaged():
        """Returns True if this plugin is embedded"""

    def GetPluginManager():
        """Convenience method: return a pointer to the plugin manager"""

    def GetMicroView():
        """Convenience method: returns a pointer to the main frame (deprecated)"""

    def showHelp():
        """Show help for this plugin"""

    def CreatePluginDialogFrame(parent):
        """Create dialog frame for this plugin.

        Optional arg: managed=False makes the dialog appear in it's own top window.
        """

    def InvokeImageLoadedEvent():
        """Utility method - force an 'image change' event

        Useful on startup of the plugin"""

    def OnImageChangeEvent(evt):
        """Default method to call when an image change has occurred"""

    def UpdateROIValues(evt):
        """A hook to allow plugins to get hold of the currently selected region
        of interest"""

    def UpdateROIListConsumerControls():
        """Override method for ROI list consumers"""


class IResultWindow(interface.Interface):

    """
    An interface for writing text to something like a window
    """
    def WriteText(text):
        """
        Append text to window
        """


class IMicroViewSplashScreen(interface.Interface):

    """
    An interface for managing a application's splashscreen
    """


class IOrthoPlanes(interface.Interface):

    """
    A collection of Orthoplanes
    """


class ICurrentOrthoPlanes(IOrthoPlanes):

    """
    The currently selected ortho plane collection
    """
