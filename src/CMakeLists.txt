PROJECT(MicroView)

cmake_minimum_required(VERSION 2.8)

# # Mac needs hand holding
LINK_DIRECTORIES(/usr/local/lib)
INCLUDE_DIRECTORIES(/usr/local/include/vtk-6.1)

FIND_PACKAGE(PythonInterp)
FIND_PACKAGE(PythonLibs)
FIND_PACKAGE(VTK)
FIND_PACKAGE(OpenGL REQUIRED)

MESSAGE("VTK_LIBRARIES=${VTK_LIBRARIES}")

IF(VTK_FOUND)
  INCLUDE(${VTK_USE_FILE})
ENDIF(VTK_FOUND)

######################################################################################

INCLUDE(${VTK_CMAKE_DIR}/vtkWrapPython.cmake)

SET(VISUALIZATION_ROOT ${Visualization_SOURCE_DIR})


# Your c++ class files. They must be accompanied by
# a header file of the same name in order for the
# VTK Python wrapper to work.
SET(srcs
  vtkImageInPlaceMirrorFilter.cxx
  vtkImageInvertFilter.cxx
  vtkImagePurify.cxx
  vtkImageStatistics.cxx
  vtkImageStereology.cxx
  vtkInPlaceImageStencil.cxx
  vtkStderrOutputWindow.cxx
  vtkImageMagnitude2.cxx
  )

# The libraries that your classes use. If you need
# libraries that aren't VTK kits (e.g., zlib or netcdf),
# then use CMake's FIND_LIBRARY command and add the result
# to this list.
SET(libs
  ${VTK_LIBRARIES}
)

# The VTK Python libraries that the automatically-generated
# Python wrappers for your classes will use. This should only
# be vtkCommonPython, but some VTK installations require each
# vtk(some VTK kit)Python to be listed.

IF("${VTK_MAJOR_VERSION}" EQUAL 5)
SET(py_libs
  vtkCommonPythonD
  vtkImagingPythonD
  vtkIOPythonD
  vtkFilteringPythonD
  vtkGraphicsPythonD
  vtkHybridPythonD
  vtkImagingPythonD
  vtkVolumeRenderingPythonD
  vtkWidgetsPythonD
)
ELSE("${VTK_MAJOR_VERSION}" EQUAL 5)
SET(py_libs
  vtkWrappingPython27Core-6.1
  vtkInteractionWidgetsPython27D-6.1
  vtkCommonCorePython27D-6.1
  vtkImagingGeneralPython27D-6.1
  vtkImagingStatisticsPython27D-6.1
  vtkCommonExecutionModelPython27D-6.1
  vtkIOImagePython27D-6.1
  vtkCommonDataModelPython27D-6.1
)
ENDIF("${VTK_MAJOR_VERSION}" EQUAL 5)

######################################################
# You do not need to change anything beyond this point.
######################################################

INCLUDE_DIRECTORIES(${PROJECT_SOURCE_DIR})
INCLUDE_DIRECTORIES(${PROJECT_BINARY_DIR})
INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_DIRS})

OPTION(BUILD_SHARED_LIBS "Build with shared libraries."
       ${VTK_BUILD_SHARED_LIBS})

IF(BUILD_SHARED_LIBS)
  SET(VTKLOCAL_BUILD_SHARED_LIBS_CONFIG 1)
ELSE(BUILD_SHARED_LIBS)
  SET(VTKLOCAL_BUILD_SHARED_LIBS_CONFIG 0)
ENDIF(BUILD_SHARED_LIBS)

VTK_WRAP_PYTHON3("${PROJECT_NAME}Python" python_srcs "${srcs}")
ADD_LIBRARY("${PROJECT_NAME}Python" MODULE ${python_srcs} ${srcs} ${POISSON_SURFACE_RECONSTRUCTION_SOURCES} "${PROJECT_NAME}PythonInit.cxx")
TARGET_LINK_LIBRARIES("${PROJECT_NAME}Python" ${py_libs} ${libs} ${OPENGL_LIBRARIES} ${OPENGL_glu_LIBRARY} ${GLEW_LIBRARY})
