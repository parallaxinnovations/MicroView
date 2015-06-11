/*=========================================================================

  Program:   Visualization Toolkit
  Module:    $RCSfile: vtkStderrOutputWindow.h,v $

  Copyright (c) Ken Martin, Will Schroeder, Bill Lorensen
  All rights reserved.
  See Copyright.txt or http://www.kitware.com/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
     PURPOSE.  See the above copyright notice for more information.

=========================================================================*/
// .NAME vtkStderrOutputWindow - pipe warnings to stderr
// .SECTION Description
// Writes debug/warning/error output to stderr.
// 

#ifndef __vtkStderrOutputWindow_h
#define __vtkStderrOutputWindow_h

#include "vtkFileOutputWindow.h"


class VTK_EXPORT vtkStderrOutputWindow : public vtkFileOutputWindow
{
public:
  vtkTypeRevisionMacro(vtkStderrOutputWindow, vtkFileOutputWindow);

  static vtkStderrOutputWindow* New();

  virtual void DisplayText(const char*);
  virtual void DisplayErrorText(const char*);
  virtual void DisplayWarningText(const char*);
  virtual void DisplayGenericWarningText(const char*);
  virtual void DisplayDebugText(const char*);

 protected:
  vtkStderrOutputWindow() {}; 
  virtual ~vtkStderrOutputWindow() {}; 

  void Initialize();
private:
  vtkStderrOutputWindow(const vtkStderrOutputWindow&);  // Not implemented.
  void operator=(const vtkStderrOutputWindow&);  // Not implemented.
};



#endif
