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
ObjectManager is a base class to develop management plugins in MicroView
"""

import collections
from PI.visualization.MicroView import MicroViewPlugIn


class ObjectManager(MicroViewPlugIn.MicroViewPlugIn):

    __classname__ = "ObjectManager"
    __label__ = "Object Manager"
    __shortname__ = "ObjectManager"
    __description__ = "Maintains objects in memory"
    __menuentry__ = None
    __iconname__ = None
    __icon__ = None
    __managergroup__ = None

    def __init__(self, parent):

        MicroViewPlugIn.MicroViewPlugIn.__init__(self, parent)

        self._helpLink = 'ObjectManager'

        self._ObjectList = {}
        self._counter = 1
        self._parent = parent
        self._cursel = None

        # Create a file filter
        self._wft = collections.OrderedDict()

        # Save a file filter
        self._rft = collections.OrderedDict()

        self._filename = None

    #
    # basic commands, many to be overridden by derived classes
    #
    #
    def selectionCommand(self, evt):
        pass

    def ClearCurrentSelection(self):
        self._cursel = None

    def SaveObject(self, evt):
        pass

    def LoadObject(self, evt):
        pass

    def DeleteObject(self, evt):
        pass

    def RenameObject(self, evt):
        pass

    def DeleteAllObjects(self, evt):
        pass

    #
    # MicroView application settings, callbacks, accessors
    #

    def OnPluginClose(self):
        pass

    def OnApplicationClose(self):
        try:
            self.DeleteAllObjects(0)
            return True
        except:
            return False
