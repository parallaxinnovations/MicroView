# =========================================================================
#
# Copyright (c) 2005-2008 GE Healthcare.
# Copyright (c) 2011-2015 Parallax Innovations Inc.
#
# Use, modification and redistribution of the software, in source or
# binary forms, are permitted provided that the following terms and
# conditions are met:
#
# 1) Redistribution of the source code, in verbatim or modified
#    form, must retain the above copyright notice, this license,
#    the following disclaimer, and any notices that refer to this
#    license and/or the following disclaimer.
#
# 2) Redistribution in binary form must include the above copyright
#    notice, a copy of this license and the following disclaimer
#    in the documentation or with other materials provided with the
#    distribution.
#
# 3) Modified copies of the source code must be clearly marked as such,
#    and must not be misrepresented as verbatim copies of the source code.
#
# THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE SOFTWARE "AS IS"
# WITHOUT EXPRESSED OR IMPLIED WARRANTY INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE.  IN NO EVENT SHALL ANY COPYRIGHT HOLDER OR OTHER PARTY WHO MAY
# MODIFY AND/OR REDISTRIBUTE THE SOFTWARE UNDER THE TERMS OF THIS LICENSE
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, LOSS OF DATA OR DATA BECOMING INACCURATE
# OR LOSS OF PROFIT OR BUSINESS INTERRUPTION) ARISING IN ANY WAY OUT OF
# THE USE OR INABILITY TO USE THE SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGES.
#
# =========================================================================

#
# This file represents a derivative work by Parallax Innovations Inc.
#

"""
StockItems - Classes for managing system stock resources, like icons.

Classes:

        StockIconFactory - Manages icon resources.  Maintains a cache of
                           icon pixmaps, indexed by name
"""

import sys
import os
import StringIO
import base64
import importlib
import wx
import logging
from zope import interface
# don't change this
from PI.visualization.MicroView.interfaces import IStockIconProvider
import six
from PI.singleton import Singleton


class StockIconFactory(six.with_metaclass(Singleton.Singleton, object)):

    interface.implements(IStockIconProvider)

    _icondictionary = {}
    _install_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    _icon_dir = os.path.join(_install_dir, 'Icons')

    def getBitmap(self, name, size=wx.ART_TOOLBAR, package=None):
        """Returns a wx Bitmap object -- either loads it from disk, or
        returns a cached copy.  Also understands wx art objects"""

        if name is None:
            return None

        # build up a list of packages we should search through for
        # this icon
        package_list = []
        if package is not None:
            if package not in package_list:
                package_list.append(package)

        package_list.append('PI.visualization.MicroView.Icons')

        names = [name]

        if not name.startswith('wxART_'):
            if isinstance(size, int):
                # look for a correct size version first
                names.insert(0, '{0}_{1}x{1}'.format(name, size))

        for name in names:

            if name in self._icondictionary.keys():
                return self._icondictionary[name]
            else:
                if name.startswith('wxART_'):
                    # we assume this is a wx.ArtProvider ID
                    if isinstance(size, unicode):
                        bitmap = wx.ArtProvider.GetBitmap(name, size)
                    else:
                        bitmap = wx.ArtProvider.GetBitmap(
                            name, size=(size, size))
                else:
                    try:
                        basename = name + '.png'

                        # try to load from eggs directly as a resource
                        # if this fails, try to load from __init__ file instead
                        f = None

                        for package in package_list:

                            if f is None:
                                try:
                                    mod = importlib.import_module(package)
                                    f = StringIO.StringIO(base64.b64decode(
                                        eval('mod.' + name.replace('-', '_'))))
                                    break
                                except AttributeError, e:
                                    pass
                                except:
                                    logging.exception("StockItems")
                        if f:
                            bitmap = wx.ImageFromStream(f).ConvertToBitmap()
                        else:
                            bitmap = None
                    except:
                        bitmap = None

                if bitmap:
                    self._icondictionary[name] = bitmap

            if name in self._icondictionary.keys():
                return self._icondictionary[name]

        return None

    def getSizedBitmap(self, name, _size, package=None):
        bm = self.getBitmap(name, size=_size, package=package)
        if (bm is not None) and (bm.GetHeight() > _size):
            factor = bm.GetHeight() / float(_size)
            bm = bm.ConvertToImage().Scale(int(bm.GetWidth() / factor),
                                           _size, quality=wx.IMAGE_QUALITY_HIGH).ConvertToBitmap()
            sized_name = '{0}_{1}x{1}'.format(name, _size)
            if sized_name not in self._icondictionary:
                self._icondictionary[sized_name] = bm
        return bm

    def getMenuBitmap(self, name, package=None):

        if name.startswith('wxART_'):
            size = wx.ART_MENU
        else:
            size = 16

        return self.getSizedBitmap(name, size, package=package)

    def getToolbarBitmap(self, name, package=None):

        if name.startswith('wxART_'):
            size = wx.ART_TOOLBAR
        else:
            size = 24

        return self.getSizedBitmap(name, 24, package=package)
