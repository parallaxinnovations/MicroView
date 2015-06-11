#!/usr/bin/env python

"""
Look-up tables for image visualisation / image processing applications.

Original data located on http://rsb.info.nih.gov/ij/download/luts/
Rasband, W.S., ImageJ, U. S. National Institutes of Health, Bethesda,
Maryland, USA, http://rsb.info.nih.gov/ij/, 1997-2005.

How does it work?

LUT Data is stored in a PNG image 256 pixel wide, n_lut high.
The PNG image is stored as base64 data inside this file.

The latest version of this file is stored in my google code repository:
    http://code.google.com/p/ezwidgets/

Copyright (c) 2007 Egor Zindy <ezindy@gmail.com>

Released under the MIT licence.
"""
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

__author__ = "Egor Zindy <ezindy@gmail.com>"
__copyright__ = "Copyright (c) 2007 Egor Zindy"
__license__ = "MIT"
__version__ = "1.0"
__date = "2007-10-11"
__status__ = "Production"


import wx
from binascii import a2b_base64
import cStringIO


class LutData(object):

    def __init__(self, table=None):

        stream = cStringIO.StringIO(a2b_base64(_luts))
        _s = wx.ImageFromStream(stream).GetData()
        stream.close()

        if table is not None:
            names = []
            s = ""
            for i in table:
                names.append(_names[i])
                s += _s[i * 768:(i + 1) * 768]

            self._names = names
            self._s = s
        else:
            self._names = _names
            self._s = _s

    def get_count(self):
        return len(self._names)

    def get_lut(self, i):
        if i >= self.get_count():
            i = 0
        s = self._s[i * 768:(i + 1) * 768]
        return s

    def get_rgb(self, i):
        if i >= self.get_count():
            i = 0
        s = self.get_lut(i)
        return s[::3], s[1::3], s[2::3]

    def get_name(self, i):
        if i >= self.get_count():
            i = 0
        return self._names[i]

    def get_names(self):
        return self._names

_names = ['Grey', 'RangeIndicator', 'cells', '6_reserved_colors', 'HiLo',
          'Isocontour', 'sepia', 'Magenta', 'blue_orange', 'GEM-256', 'GEM-16',
          'Blue-Orange', 'Auxctq', 'GE', 'MMC', 'Brain', 'CEqual', 'warm',
          'Hot_Iron', 'Warm_Metal', '001-fire', 'Siemens',
          'Split_BlueRed_WarmMetal', 'Split_BlackBlue_RedWhite',
          'Split_BlackWhite_WarmMetal', 'Thermal-SP', 'Thermal', 'Brown_Body',
          'hot', 'HotRed', 'gold', 'brown', 'cmy-yellow', 'smart', 'Heart',
          'Thallium', 'log_down', 'Edges', 'Green_Table', 'rgb-green', 'cmy-cyan',
          'blue', 'neon-blue', 'neon-magenta', 'haze', 'log_up', 'hsatl1',
          'hsatv1', 'hsatl2', 'Log_Up', 'colder', '003-ice', '004-phase',
          '32_colors', 'S_Pet', 'Blue_Green_Red', 'A_Squared', '20_colors',
          '12_Colors', '10_Percent', '5percent', 'multi', '16_colors', '16_color',
          '16-color', 'Royal', '8color', 'step5', 'step10', 'Thal_256', 'Thal_16',
          '5_ramps', 'Sopha', 'Ceretec', 'unionjack', 'ether',
          'Split_BlackWhite_GE', 'cmy-magneta', 'rgb-red', 'Red', 'neon-red',
          'step4', 'PIXRED', 'PIXEF', 'Blue_Green', 'GreenFire', 'HotGreen',
          'neon-green', 'Green', 'grey', 'Yellow_WFG', 'Blue_Red_Yellow',
          'gyr_centre', 'linear', 'prism', 'Rainbow', 'White_Blue_Green_Red',
          'Invert_Grey', '6_Reserved_Colors', '8_Grays', 'Amber', 'Fire-1',
          'nih-image-fire1', 'Fire-2', 'nih-image-fire2', 'Blue_Red', 'red-blue',
          'rgb-blue', 'Log_Down', 'CTI_RAS', '16_ramps', 'UCLA_NIH', 'iman',
          '16_equal', '6_shades', 'brgbcmyw', 'warhol', 'Bullseye', 'topography',
          'StarsAndStripes', 'step20', 'mixed', 'Ice', 'hotter', '005-random',
          'pastel', 'vivid', 'Cyclic', 'hue', 'Spectrum', 'fire-ncsa',
          'System_LUT', 'hue_ramps_08', 'hue_ramps_16', 'cmy']

_luts = "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\
AASUVORK5CYII="
