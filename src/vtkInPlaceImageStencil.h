#ifndef __vtkInPlaceImageStencil_h
#define __vtkInPlaceImageStencil_h

#include "vtkImageInPlaceFilter.h"
#include "MicroViewConfigure.h"

class vtkImageStencilData;

class VTK_MicroView_EXPORT vtkInPlaceImageStencil : public vtkImageInPlaceFilter
{
public:
  static vtkInPlaceImageStencil *New();
  vtkTypeMacro(vtkInPlaceImageStencil,vtkImageInPlaceFilter);
  void PrintSelf(ostream& os, vtkIndent indent);


  // Description:
  void SetStencil(vtkImageStencilData *stencil) { this->Stencil = stencil; };
  vtkImageStencilData *GetStencil() { return this->Stencil; };
  vtkSetMacro(ReverseStencil, int);
  vtkBooleanMacro(ReverseStencil, int);
  vtkGetMacro(ReverseStencil, int);
  vtkSetMacro(MaskValue, double);
  vtkGetMacro(MaskValue, double);
  
  
protected:

  int ReverseStencil;
  double MaskValue;
  vtkImageStencilData *Stencil;

  vtkInPlaceImageStencil();
  ~vtkInPlaceImageStencil() {};

  virtual int RequestData(vtkInformation *request,
                          vtkInformationVector** inputVector,
                          vtkInformationVector* outputVector);

private:
  vtkInPlaceImageStencil(const vtkInPlaceImageStencil&);  // Not implemented.
  void operator=(const vtkInPlaceImageStencil&);  // Not implemented.
};



#endif



