//
//  A class to dump a stenciled image to a text file
// 

#ifndef __vtkImageTextExport_h
#define __vtkImageTextExport_h


#include "vtkImageToImageFilter.h"
#include "MicroViewConfigure.h"

class vtkImageStencilData;

class VTK_MicroView_EXPORT vtkImageTextExport : public vtkImageToImageFilter
{
public:
  static vtkImageTextExport *New();
  vtkTypeRevisionMacro(vtkImageTextExport,vtkImageToImageFilter);
  void PrintSelf(ostream& os, vtkIndent indent);

  // Description:
  // Use a stencil to specify which voxels to accumulate.
  void SetStencil(vtkImageStencilData *stencil);
  vtkImageStencilData *GetStencil();

  // Rewrite this filter as an image output class at some point...
  vtkSetStringMacro(FileName);
  vtkGetStringMacro(FileName);
  
protected:
  vtkImageTextExport();
  ~vtkImageTextExport();
  char *FileName;
  
  void ExecuteInformation(vtkImageData *input, vtkImageData *output);
  void ComputeInputUpdateExtent(int inExt[6], int outExt[6]);
  void ExecuteInformation(){this->vtkImageToImageFilter::ExecuteInformation();};
  void ExecuteData(vtkDataObject *out);

private:
  vtkImageTextExport(const vtkImageTextExport&);  // Not implemented.
  void operator=(const vtkImageTextExport&);  // Not implemented.
};

#endif



