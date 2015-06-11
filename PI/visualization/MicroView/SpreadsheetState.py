from zope import interface
from PI.visualization.MicroView.interfaces import ISpreadsheetState
import PageState


class SpreadsheetState(PageState.PageState):

    interface.implements(ISpreadsheetState)

    def __init__(self):

        PageState.PageState.__init__(self)
        self._type = 'spreadsheet'
