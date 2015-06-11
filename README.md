Microview
==========

`MicroView` is a 3D image viewer and analysis tool.  It is written in Python and C++ and leverages a variety of open source tools
including `VTK <http://www.vtk.org>`_, and `wxPython <http://www.wxpython.org>`_.

Build Instructions
------------------

1. Download and install `python <http://www.python.org>`_

2. Install `pip <http://www.pip-installer.org/en/latest/>`_

3. Install `virtualenv <http://www.virtualenv.org/>`_::

   $ pip install virtualenv

4. Create a virtualenv environment::

   $ virtualenv MV

5. Activate the newly created virtualenv environment.  On Windows::

   > MV\Scripts\activate.bat

   while on Linux or OSX::

   $ source bin/activate

6. On Windows, set needed environment variables:

   - if compiling with VS2010 or higher, read and follow `this <http://stackoverflow.com/questions/2817869/error-unable-to-find-vcvarsall-bat>`_ link
   - set language variable::

     $ export LANG='eng_US.UTF-8'

   
6. Download `MicroView` dependencies that aren't easily installed with pip.  For each of the following packages,
   download the installer and place in an accessible folder:

   - `numpy <http://www.numpy.org>`_
   - `scipy <http://www.scipy.org/>`_
   - `matplotlib <http://www.matplotlib.org>`_
   - `scikit-image <http://scikit-image.org/>`_
   - `pywin32 <http://sourceforge.net/projects/pywin32/>`_
   - `M2Crypto <http://chandlerproject.org/Projects/MeTooCrypto>`_
   - `Pillow <https://github.com/python-imaging/Pillow>`_
   - `wxPython <http://www.wxpython.org>`_

   .. note::
   
       Christoph Gohlke's `repository <http://www.lfd.uci.edu/~gohlke/pythonlibs>`_ is an excellent resource
       for Windows installers, especially for 64-bit architectures
   
7. Next, for each downloaded installer, run::

   $ easy_install PACKAGE

    .. note::

        `Pillow` may not install correctly unless an environment variable is set.  Under `cygwin <http://www.cygwin.com>`_, for instance,
        the following command must be executed before attempting to install::
        
            $ export LANG='eng_US.UTF-8'

8. Install `MicroView` dependencies::

   $ pip install -r microview.git/MicroView/requirements.txt



