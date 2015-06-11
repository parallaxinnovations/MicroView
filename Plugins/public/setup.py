# =========================================================================
#
# Copyright (c) 2011-2015 Parallax Innovations Inc.
#
# =========================================================================

import sys
import os
import base64
import glob
from setuptools import setup, find_packages

desc = """MicroView base plugins:

ImageInfo          : Displays a property grid for the loaded image
IsoSurfaceDisplay  : Create and save isosurfaces
OptionsDialog      : General applications options
RescaleImage       : Perform linear rescaling of image values
ResampleImage      : Perform spatial resampling of image
StandardROITool    : Standard ROI tool - various basic shapes
"""

fname = os.path.join(os.path.dirname(sys.argv[0]), 'setup.cfg.in')
s = open(fname, 'rt').read().replace(
    '@RELEASE@', "2.5.0")
open(fname[:-3], 'wt').write(s)

__init__py = """
try:
  __import__('pkg_resources').declare_namespace(__name__)
except:
  __path__ = __import__('pkgutil').extend_path(__path__, __name__)

PACKAGE_VERSION = "2.5.0"
PACKAGE_SHA1 = "NA"
"""
print >> open(os.path.join(os.path.dirname(
    sys.argv[0]), 'PIMicroViewBasePlugins', '__init__.py'), 'wt'), __init__py.strip()

# Add Icons
icondir = os.path.join(
    os.path.dirname(sys.argv[0]), 'PIMicroViewBasePlugins', 'Icons')
if os.path.exists(icondir):
    init_name = os.path.join(icondir, '__init__.py')
    _file = open(init_name, 'wt')
    print >> _file, __init__py.strip()
    print >> _file, ''
    icon_glob = glob.glob(os.path.join(icondir, '*.png'))
    icon_glob.sort()
    for g in icon_glob:
        bn = os.path.splitext(os.path.basename(g))[0].replace('-', '_')
        s = open(g, 'rb').read()
        print >> _file, "%s = \"%s\"" % (bn, base64.b64encode(s))
    _file.close()


setup(name='MicroView-base-plugins',
      version="2.5.0",
      description="MicroView base plugins",
      long_description=desc,
      author="Jeremy D. Gill",
      author_email="jgill@parallax-innovations.com",
      maintainer="Jeremy D. Gill",
      maintainer_email="jgill@parallax-innovations.com",
      url="http://parallax-innovations.com/microview",
      packages=find_packages(),
      package_data={'': ['*.gif', '*.png', '*.ico']},
      zip_safe=True,
      entry_points="""
        [PI.MicroView.MicroViewPlugIn.v1]
        BasicBoneAnalysis  = PIMicroViewBasePlugins.BasicBoneAnalysis:BasicBoneAnalysis
        ImageInfo          = PIMicroViewBasePlugins.ImageInfo:ImageInfo
        IsoSurfaceDisplay  = PIMicroViewBasePlugins.IsoSurfaceDisplay:IsoSurfaceDisplay
        OptionsDialog      = PIMicroViewBasePlugins.OptionsDialog:OptionsDialog
        RescaleImage       = PIMicroViewBasePlugins.RescaleImage:RescaleImage
        ResampleImage      = PIMicroViewBasePlugins.ResampleImage:ResampleImage
        StandardROITool    = PIMicroViewBasePlugins.StandardROITool:StandardROITool
        """
      )
