Microview
==========

MicroView is a 3D image viewer and analysis tool.  It is written in Python and C++ and leverages a variety of open source tools
including [VTK](http://www.vtk.org), and [wxPython](http://www.wxpython.org).

Build Instructions
------------------

1. Download and install [python](http://www.python.org)

2. Install [pip](http://www.pip-installer.org/en/latest/)

3. Install [virtualenv](http://www.virtualenv.org/)

4. Create a virtualenv environment:
```bash
virtualenv MV
```
5. Activate the newly created virtualenv environment.

6. On Windows, set needed environment variables:

   - if compiling with VS2010 or higher, read and follow [this](http://stackoverflow.com/questions/2817869/error-unable-to-find-vcvarsall-bat) link
   - set language variable:
```bash
export LANG='eng_US.UTF-8'
```
   
6. Download MicroView dependencies that aren't easily installed with pip.  For each of the following packages,
   download the installer and place in an accessible folder:

   - [numpy](http://www.numpy.org)
   - [scipy](http://www.scipy.org)
   - [matplotlib](http://www.matplotlib.org)
   - [scikit-image](http://scikit-image.org)
   - [pywin32](http://sourceforge.net/projects/pywin32)
   - [Pillow](https://github.com/python-imaging/Pillow)
   - [wxPython](http://www.wxpython.org)

 Christoph Gohlke's [repository](http://www.lfd.uci.edu/~gohlke/pythonlibs) is an excellent resource
 for Windows installers, especially for 64-bit architectures
   
7. Next, for each downloaded installer, run:
```bash
easy_install PACKAGE
```

[Pillow](pillow.readthedocs.io) may not install correctly unless an environment variable is set.  Under [cygwin](http://www.cygwin.com>), for instance, the following command must be executed before attempting to install::
```bash        
export LANG='eng_US.UTF-8'
```
8. Install MicroView dependencies:
```bash
pip install -r microview.git/MicroView/requirements.txt
```
