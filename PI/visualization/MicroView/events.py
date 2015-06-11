from PI.visualization.common.events import BaseEvent
import cStringIO

##########################################################################
# Line plotting and histogram related events
##########################################################################


class PlotWindowCursorPosition(BaseEvent):

    """
    The mouse cursor position has changed
    """

    def __init__(self, x, y):

        self._x = x
        self._y = y


class HistogramSelectionModifiedEvent(BaseEvent):

    """
    A range of values has been selected on a histogram image
    """

    def __init__(self, x0, x1, visible):
        self._x0 = x0
        self._x1 = x1
        self._visible = visible

    def GetRange(self):
        return self._x0, self._x1

    def GetVisibility(self):
        return self._visible


class BinSizeModifiedEvent(BaseEvent):

    """
    Document me
    """

    def __init__(self, binsize):
        self._binsize = binsize

    def GetBinSize(self):
        return self._binsize


class HistogramClosedEvent(BaseEvent):

    """
    Document me
    """


class GlobalHistogramChangedEvent(BaseEvent):

    """
    Document me
    """

    def __init__(self, histogram):
        self._histogram = histogram

    def GetHistogram(self):
        return self._histogram


##########################################################################
# Plugin-related events
##########################################################################

class PluginActivatedEvent(BaseEvent):

    """
    A plugin has been created
    """

    def __init__(self, pluginname):
        self._pluginname = pluginname

    def GetPluginName(self):
        return self._pluginname

##########################################################################
# General GUI events
##########################################################################


class ActionEvent(BaseEvent):

    """
    A space-key event has occurred
    """

    def __init__(self, evt):
        self._event = evt

    def GetEvent(self):
        return self._event


class OrthoCenterChangeEvent(BaseEvent):

    """
    An orthoview has had it's center point changed
    """

    def __init__(self, pos):
        self._position = pos

    def GetPosition(self):
        return self._position


class AutoThresholdCommandEvent(BaseEvent):

    """
    Command event: request an updated Otsu threshold for the current image
    """


class BackgroundColourChangeEvent(BaseEvent):

    """
    Command event to change a window's background colour and gradient settings
    """


class ShowWindowLevelDialogEvent(BaseEvent):

    """
    Command event generated when a request has been made to show the window/level
    edit dialog
    """


class SetWindowLevelCommand(BaseEvent):

    """
    Command event generated when window/level values should be adjusted
    """

    def __init__(self, _min, _max):
        self._min = _min
        self._max = _max

    def getTableRange(self):
        return self._min, self._max


class NoImagesLoadedEvent(BaseEvent):

    """
    Event generated when all images in MicroView have been closed
    """


class OrthoPlanesRemoveInputEvent(BaseEvent):

    """
    Document me
    """

    def __init__(self, name):
        self._input_name = name

    def GetInputName(self):
        return self._input_name


class XSliceValueChangeEvent(BaseEvent):

    """
    Event for updating the x-slice slider on the main toolbar
    """

    def __init__(self, xslice, xpos):
        self._xslice = xslice
        self._xpos = xpos

    def GetSliceValue(self):
        return self._xslice

    def GetSlicePosition(self):
        return self._xpos


class YSliceValueChangeEvent(BaseEvent):

    """
    Event for updating the y-slice slider on the main toolbar
    """

    def __init__(self, yslice, ypos):
        self._yslice = yslice
        self._ypos = ypos

    def GetSliceValue(self):
        return self._yslice

    def GetSlicePosition(self):
        return self._ypos


class ZSliceValueChangeEvent(BaseEvent):

    """
    Event for updating the z-slice slider on the main toolbar
    """

    def __init__(self, zslice, zpos):
        self._zslice = zslice
        self._zpos = zpos

    def GetSliceValue(self):
        return self._zslice

    def GetSlicePosition(self):
        return self._zpos


class TrackedSliceIndexChangeEvent(BaseEvent):

    """
    Event for updating z-slice scrollbar on the main toolbar
    """

    def __init__(self, slice_idx):
        self._slice_idx = slice_idx

    def GetTrackedSliceIndex(self):
        return self._slice_idx


class ViewportMouseDown(BaseEvent):

    """Mouse button down event in a viewport"""

    def __init__(self, viewport):

        self._viewport = viewport

    def GetViewport(self):
        return self._viewport


class ViewportModifiedEvent(BaseEvent):

    def __init__(self, image_index, panes, pane_indices, layout):

        self._image_index = image_index
        self._panes = panes
        self._pane_indices = pane_indices
        self._layout = layout

    def GetPanes(self):
        return self._panes

    def GetPaneIndices(self):
        return self._pane_indices

    def GetLayout(self):
        return self._layout

    def GetImageIndex(self):
        return self._image_index


class ViewportModified2Event(BaseEvent):

    def __init__(self, image_index, pane):

        self._image_index = image_index
        self._pane = pane


class SynchronizeEvent(BaseEvent):

    """Event to indicate binding of a collection of viewports"""

    def __init__(self, old_sync_list, new_sync_list):

        self._old_sync_list = old_sync_list
        self._new_sync_list = new_sync_list

    def GetOldSyncList(self):
        return self._old_sync_list

    def GetNewSyncList(self):
        return self._new_sync_list


class HelpEvent(BaseEvent):

    def __init__(self, helplink):

        self._helplink = helplink

    def GetHelpTopic(self):

        return self._helplink


class ModePaletteEvent(BaseEvent):

    def __init__(self, mode):
        self._mode = mode

    def GetMode(self):
        return self._mode


class ScalesVisibilityChangeEvent(BaseEvent):

    """
    A change in the visibility of 2D viewport scale actors has been requested
    """

    def __init__(self, visibility):
        self._visibility = visibility

    def GetVisibility(self):
        return self._visibility


class ColourBarVisibilityChangeEvent(BaseEvent):

    """
    A change in the visibility of 3D viewport colourbar actor has been requested
    """

    def __init__(self, visibility):
        self._visibility = visibility

    def GetVisibility(self):
        return self._visibility


class NotebookChangeBaseEvent(BaseEvent):

    """
    A notebook or image change has occurred
    """

    def __init__(self, index, num_images_loaded, page_title):
        self._current_image = index
        self._numberOfCurrentImagesDisplayed = num_images_loaded
        self._page_title = page_title

    def GetCurrentImageIndex(self):
        return self._current_image

    def GetNumberOfImagesCurrentlyLoaded(self):
        return self._numberOfCurrentImagesDisplayed

    def GetTitle(self):
        return self._page_title

    def __str__(self):
        s = cStringIO.StringIO()
        s.write("{0}:\n".format(self.__class__))
        s.write("\tCurrent image index: {0}\n".format(self._current_image))
        s.write("\tNumber of images displayed: {0}\n".format(
            self._numberOfCurrentImagesDisplayed))
        s.write("\tPage title: {0}\n".format(self._page_title))
        return s.getvalue()


class NotebookPageChangingEvent(NotebookChangeBaseEvent):

    """
    This event is fired when a EVT_NOTEBOOK_PAGE_CHANGING has been invoked by the main viewer notebook control
    """


class NotebookPageChangedEvent(NotebookChangeBaseEvent):

    """
    This event is fired when a EVT_NOTEBOOK_PAGE_CHANGED has been invoked by the main viewer notebook control
    """


class CurrentImageClosingEvent(NotebookChangeBaseEvent):

    """
    The current image is being closed - take whatever actions are necessary
    """


class CurrentImageChangeEvent(NotebookChangeBaseEvent):

    """
    A change in the current image has occurred
    """


##########################################################################
# Statusbar events
##########################################################################

class StatusbarTextEvent(BaseEvent):

    """
    Event for updating text on the statusbar - override me
    """

    def __init__(self, text=''):
        self._text = text

    def GetText(self):
        return self._text


class StatusbarCursorXYPosition(StatusbarTextEvent):

    """
    Event for updating the x,y cursor position text on the statusbar
    """


class StatusbarCursorSlicePosition(StatusbarTextEvent):

    """
    Event for updating the z cursor position text on the statusbar
    """


class StatusbarVoxelValue(StatusbarTextEvent):

    """
    Event for updating the greylevel value text on the statusbar
    """


##########################################################################
# Bonjour/Zeroconf/Rendezvous events
##########################################################################

class BaseBonjourEvent(BaseEvent):

    """Base class for bonjour events"""

    def __init__(self, **kw):
        self._name = kw.get('name', '')
        self._stype = kw.get('stype', '')
        self._domain = kw.get('domain', '')
        self._host = kw.get('host', '')
        self._port = kw.get('port', '')
        self._txt = kw.get('txt', '')
        self._address = kw.get('address', '')

    def __str__(self):
        s = ''
        s += 'Bonjour Event:\n'
        s += ('\tName: %s\n' % self._name)
        s += ('\tType: %s\n' % self._stype)
        s += ('\tDomain: %s\n' % self._domain)
        s += ('\tHost: %s\n' % self._host)
        s += ('\tAddress: %s\n' % self._address)
        s += ('\tPort: %d\n' % self._port)
        s += ('\tTxt: %s\n' % self._txt)
        return s

    @property
    def name(self):
        return self._name

    @property
    def stype(self):
        return self._stype

    @property
    def domain(self):
        return self._domain

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def txt(self):
        return self._txt

    @property
    def address(self):
        return self._address


class BonjourServiceAddedEvent(BaseBonjourEvent):

    """
    Event generated when a bonjour service appears
    """


class BonjourServiceRemovedEvent(BaseBonjourEvent):

    """
    Event generated when a bonjour service disappears
    """


class DICOMServiceAddedEvent(BonjourServiceAddedEvent):

    """
    Event generated when a DICOM service appears
    """


class DICOMServiceRemovedEvent(BonjourServiceRemovedEvent):

    """
    Event generated when a DICOM service disappears
    """


class ReconServiceAddedEvent(BonjourServiceAddedEvent):

    """
    Event generated when a Reconstruction service appears
    """


class ReconServiceRemovedEvent(BonjourServiceRemovedEvent):

    """
    Event generated when a Reconstruction service disappears
    """


##########################################################################
# Window/Level events
##########################################################################

class WindowLevelPresetEvent(BaseEvent):

    """A preset window/level setting has been requested"""

    def __init__(self, text):
        self._text = text

    def GetPreset(self):
        return self._text


class WindowLevelTextChangeEvent(BaseEvent):

    """
    Event that indicates w/l text has changed
    """

    def __init__(self, text):
        self._text = text

    def GetText(self):
        return self._text


##########################################################################
# ROI & Stencil events
##########################################################################

class HistogramIsActiveROIEvent(BaseEvent):

    """
    The Histogram tool has become the active ROI owner for the
    current image
    """


class GetROIStencilEvent(BaseEvent):

    """
    Document me
    """


class StandardROIChangeExtentCommandEvent(BaseEvent):

    """Command event indicating that the current standard ROI should be adjusted"""

    def __init__(self, extent=(0, 1, 0, 1, 0, 1)):
        self._extent = extent

    def GetExtent(self):
        return self._extent


class StandardROIChangeBoundsCommandEvent(BaseEvent):

    """Command event indicating that the current standard ROI should be adjusted"""

    def __init__(self, bounds=(0, 1, 0, 1, 0, 1)):
        self._bounds = bounds

    def GetBounds(self):
        return self._bounds


class ROIEnabledEvent(BaseEvent):

    def __init__(self, pluginname, image_index):
        self._pluginname = pluginname
        self._image_index = image_index

    def GetPluginName(self):
        return self._pluginname

    def GetImageIndex(self):
        return self._image_index


class ROIModifiedEvent(BaseEvent):

    def __init__(self, pluginname, image_index):
        self._pluginname = pluginname
        self._image_index = image_index

    def GetPluginName(self):
        return self._pluginname

    def GetImageIndex(self):
        return self._image_index


class ROIDisabledEvent(BaseEvent):

    def __init__(self, pluginname, image_index):
        self._pluginname = pluginname
        self._image_index = image_index

    def GetPluginName(self):
        return self._pluginname

    def GetImageIndex(self):
        return self._image_index


class ROIListChangedEvent(BaseEvent):

    """
    Document me
    """


class ROIKeyEvent(BaseEvent):

    """
    a 3-, 7- or 8-key, with or without the control key has occurred
    """

    def __init__(self, evt):
        self._event = evt

    def GetEvent(self):
        return self._event


class DisableEvent(BaseEvent):

    """
    Document me
    """


class EnableEvent(BaseEvent):

    """
    Document me
    """

##########################################################################
# Standard ROI model events
##########################################################################


class ROIModelModifiedEvent(BaseEvent):

    """
    a model has been modified
    """


class ROIModelLinkingChangeEvent(BaseEvent):

    """
    Event that indicates a change in the behaviour when resizing an ROI model.
    """


class ROIModelTypeChangeEvent(BaseEvent):

    """
    Event indicating that the model type has been changed
    """


class ROIModelOrientationChangeEvent(BaseEvent):

    """
    The ROI model orientation has been changed
    """


class ROIModelControlPointChangeEvent(BaseEvent):

    """
    A control point (used to determine outline of model) has changed
    """

##########################################################################
# Monitoring events
##########################################################################


class MotionMonitoringDisableRequestedEvent(BaseEvent):

    """
    Document me
    """


class MotionMonitoringEnableRequestedEvent(BaseEvent):

    """
    Document me
    """


class EnableMotionMonitoring(BaseEvent):

    """
    Event sent by volume rendering code - is this still used?
    """


class DisableMotionMonitoring(BaseEvent):

    """
    Event sent by volume rendering code - is this still used?
    """


##########################################################################
# Image Lookup table events
##########################################################################

class ChangeImageLUT(BaseEvent):

    """
    Command requesting an image LUT change
    """

    def __init__(self, orthoView, image, pageState, lut_index):
        self.orthoView = orthoView
        self.image = image
        self.pageState = pageState
        self.lut_index = lut_index


class ImageLUTChanged(BaseEvent):

    """
    Event generated when image LUT changes
    """
