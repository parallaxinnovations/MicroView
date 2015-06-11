#ifndef __vtkImageInPlaceMirrorFilter_h
#define __vtkImageInPlaceMirrorFilter_h

#include "vtkImageInPlaceFilter.h"
#include "MicroViewConfigure.h"

class VTK_MicroView_EXPORT vtkImageInPlaceMirrorFilter : public vtkImageInPlaceFilter
{
public:
  static vtkImageInPlaceMirrorFilter *New();
  vtkTypeRevisionMacro(vtkImageInPlaceMirrorFilter,vtkImageInPlaceFilter);
  void PrintSelf(ostream& os, vtkIndent indent);

  // Get/Set macros
  vtkSetMacro(Axis, int);  // 0=x, 1=y, 2=z
  vtkGetMacro(Axis, int);  // 0=x, 1=y, 2=z
  
protected:
  vtkImageInPlaceMirrorFilter();
  ~vtkImageInPlaceMirrorFilter() {};
  int Axis;

  virtual int RequestData(vtkInformation *request,
                          vtkInformationVector** inputVector,
                          vtkInformationVector* outputVector);

private:
  vtkImageInPlaceMirrorFilter(const vtkImageInPlaceMirrorFilter&);  // Not implemented.
  void operator=(const vtkImageInPlaceMirrorFilter&);  // Not implemented.
};



#endif



