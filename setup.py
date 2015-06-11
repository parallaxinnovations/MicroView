# =========================================================================
#
# Copyright (c) 2000-2002 Enhanced Vision Systems
# Copyright (c) 2002-2008 GE Healthcare
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


"""
To use this setup script to install MicroView:

        cd MicroView
        python setup.py install

Contributed by:  Jeremy Gill <jgill@parallax-innovations.com>
"""

import sys
import os
import shutil
import base64
import re

# sanity check
from vtk.util import vtkImageExportToArray, vtkImageImportFromArray

from distutils.core import setup

from distutils.command.build_ext import build_ext as _build_ext
from distutils.core import Extension
import glob
import tempfile
from distutils import sysconfig

#
# We need to kludge a cmake-build dynamic library into a python distutils build process.
# This is done by hooking into distutils directly
#


class build_ext(_build_ext):

    def __init__(self, dist):
        _build_ext.__init__(self, dist)
        if sys.platform == 'win32':
            self._extension = 'MicroViewPython.pyd'
        else:
            self._extension = 'libMicroViewPython.so'

    def find_binary(self):
        """
        search folder for the python extension
        """
        ret = ''
        for _dirpath, _dirnames, filenames in os.walk('.'):
            for file in filenames:
                if file.lower().endswith('.so') or file.lower().endswith('.dll') or file.lower().endswith('.pyd'):
                    # weed out spurious hits
                    if 'MicroView' in file:
                        ret = os.path.join(_dirpath, file)
                        break
        return ret

    def build_extensions(self):
        src = self.find_binary()
        dest = os.path.join(
            self.build_lib, 'PI', 'visualization', 'MicroView', self._extension)
        if os.path.abspath(src) != os.path.abspath(dest):
            print "Copying cmake-built extension into build output directory (%s => %s)" % (src, dest)
            shutil.copy(src, dest)


init_name = os.path.join(
    os.path.dirname(sys.argv[0]), 'PI', 'visualization', 'MicroView', '__init__.py')
__init__py = """
try:
  __import__('pkg_resources').declare_namespace(__name__)
except:
  __path__ = __import__('pkgutil').extend_path(__path__, __name__)
PACKAGE_VERSION = "2.5.0"
PACKAGE_SHA1 = "NA"
"""
with open(init_name, 'wt') as _file:
    _file.write(__init__py.strip() + '\n')

base = os.path.dirname(sys.argv[0])

# Add Icons
icondir = os.path.join(
    os.path.dirname(sys.argv[0]), 'PI', 'visualization', 'MicroView', 'Icons')
if os.path.exists(icondir):
    init_name = os.path.join(icondir, '__init__.py')
    with open(init_name, 'wt') as _file:
        _file.write(__init__py.strip() + '\n')
        _file.write('\n')
        icon_glob = glob.glob(os.path.join(icondir, '*.png'))
        for g in icon_glob:
            bn = os.path.splitext(os.path.basename(g))[0].replace('-', '_')
            s = open(g, 'rb').read()
            _file.write("%s = \"%s\"\n" % (bn, base64.b64encode(s)))

requires_list = ['reportlab', 'pi_microview_common', 'xlwt', 'openpyxl',
                 'twisted', 'pybonjour', 'xlrd', 'appdirs', 'pyfits',
                 'matplotlib', 'numpy', 'scipy', 'pynetdicom', 'pydicom', 'PyYAML', 'nibabel',
                 'zope.component', 'zope.interface', 'zope.event', 'unicodecsv',
                 'PI_auth', 'PI_utils', 'PI_build']

setup(name='MicroView',
      version="2.5.0",
      license="Hybrid",
      description="2D/3D Image Viewer",
      author="Jeremy D. Gill",
      author_email="jgill@parallax-innovations.com",
      maintainer="Jeremy D. Gill",
      maintainer_email="jgill@parallax-innovations.com",
      requires=requires_list,
      url="http://www.parallax-innovations.com/microview",
      packages=['PI', 'PI.visualization', 'PI.visualization.MicroView',
                'PI.visualization.MicroView.Cursors', 'PI.visualization.MicroView.Icons'],
      package_data={'': ['*.gif', '*.png', '*.ico']},
      long_description="MicroView is an open source 3D volume viewer.\n"
      "MicroView includes numerous free and commercial image analysis tools and plug-ins.",
      cmdclass={'build_ext': build_ext},    # override some built commands
      ext_modules=[Extension('libvtkMultiIOPython', [''])],
      )
