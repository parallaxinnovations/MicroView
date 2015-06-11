#ifndef __vtkImagePurify_h
#define __vtkImagePurify_h

#include "vtkSimpleImageToImageFilter.h"
#include "MicroViewConfigure.h"

class VTK_MicroView_EXPORT vtkImagePurify : public vtkSimpleImageToImageFilter
{
public:
  static vtkImagePurify *New();
  vtkTypeRevisionMacro(vtkImagePurify,vtkSimpleImageToImageFilter);
  vtkSetMacro(Threshold, float);
  vtkGetMacro(Threshold, float);
  void PrintSelf(ostream& os, vtkIndent indent);
  vtkGetMacro(PurifyError, int);
  vtkSetMacro(PurifyError, int);

protected:
  float Threshold;

  vtkImagePurify() {};
  ~vtkImagePurify() {};

  int PurifyError;
  
  virtual void SimpleExecute(vtkImageData* input, vtkImageData* output);
private:
  vtkImagePurify(const vtkImagePurify&);  // Not implemented.
  void operator=(const vtkImagePurify&);  // Not implemented.
};

#endif







