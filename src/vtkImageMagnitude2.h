/*=========================================================================

  Program:   Visualization Toolkit
  Module:    vtkImageMagnitude2.h

  Copyright (c) Ken Martin, Will Schroeder, Bill Lorensen
  All rights reserved.
  See Copyright.txt or http://www.kitware.com/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notice for more information.

=========================================================================*/
// .NAME vtkImageMagnitude2 - Colapses components with magnitude function..
// .SECTION Description
// vtkImageMagnitude2 takes the magnitude of the components.


#ifndef __vtkImageMagnitude2_h
#define __vtkImageMagnitude2_h


#include "vtkThreadedImageAlgorithm.h"
#include "MicroViewConfigure.h"

class VTK_MicroView_EXPORT vtkImageMagnitude2 : public vtkThreadedImageAlgorithm
{
public:
  static vtkImageMagnitude2 *New();
  vtkTypeMacro(vtkImageMagnitude2,vtkThreadedImageAlgorithm);

protected:
  vtkImageMagnitude2();
  ~vtkImageMagnitude2() {};

  virtual int RequestInformation (vtkInformation *, vtkInformationVector**,
                                  vtkInformationVector *);

  void ThreadedExecute (vtkImageData *inData, vtkImageData *outData,
                        int outExt[6], int id);

private:
  vtkImageMagnitude2(const vtkImageMagnitude2&);  // Not implemented.
  void operator=(const vtkImageMagnitude2&);  // Not implemented.
};

#endif










