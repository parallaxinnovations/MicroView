from zope import interface
from PI.visualization.MicroView.interfaces import IViewerState
import PageState
import cStringIO


class ViewerState(PageState.PageState):

    interface.implements(IViewerState)

    def __init__(self):

        PageState.PageState.__init__(self)

        self.layout = 'All'
        self.DisplayAllViews = True
        self.table_range = (-249.0, 250.0)
        self.lut_index = 0
        self._type = 'image'

    def __str__(self):
        s = cStringIO.StringIO()
        s.write(PageState.PageState.__str__(self))
        s.write('\tLayout: {0}\n'.format(self.layout))
        s.write('\tDisplayAllViews: {0}\n'.format(self.DisplayAllViews))
        s.write('\tTable range: {0}\n'.format(self.table_range))
        return s.getvalue()
