#include "vtkStderrOutputWindow.h"
#include "vtkObjectFactory.h"

#include <iostream>

vtkCxxRevisionMacro(vtkStderrOutputWindow, "$Revision: 1.3 $");
vtkStandardNewMacro(vtkStderrOutputWindow);

void vtkStderrOutputWindow::Initialize() 
{
}


void vtkStderrOutputWindow::DisplayText(const char* text)
{
  std::cerr << "Text: " << text << "\n";
}

void vtkStderrOutputWindow::DisplayErrorText(const char* text)
{
  std::cerr << "Error: " << text << "\n";
}

void vtkStderrOutputWindow::DisplayWarningText(const char* text)
{
  std::cerr << "Warning: " << text << "\n";
}

void vtkStderrOutputWindow::DisplayGenericWarningText(const char* text)
{
  std::cerr << "GenericWarning: " << text << "\n";
}

void vtkStderrOutputWindow::DisplayDebugText(const char* text)
{
  std::cerr << "Debug: " << text << "\n";
}
