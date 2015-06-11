#ifndef __vtkImageInvertFilter_h
#define __vtkImageInvertFilter_h

#include "vtkImageInPlaceFilter.h"
#include "MicroViewConfigure.h"

class VTK_MicroView_EXPORT vtkImageInvertFilter : public vtkImageInPlaceFilter
{
public:
  static vtkImageInvertFilter *New();
  vtkTypeRevisionMacro(vtkImageInvertFilter,vtkImageInPlaceFilter);
  void PrintSelf(ostream& os, vtkIndent indent);
 
protected:
  vtkImageInvertFilter();
  ~vtkImageInvertFilter() {};

  virtual int RequestData(vtkInformation *request,
                          vtkInformationVector** inputVector,
                          vtkInformationVector* outputVector);

private:
  vtkImageInvertFilter(const vtkImageInvertFilter&);  // Not implemented.
  void operator=(const vtkImageInvertFilter&);  // Not implemented.
};



#endif



