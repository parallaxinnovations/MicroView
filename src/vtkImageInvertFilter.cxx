#include "vtkImageInvertFilter.h"

#include "vtkImageData.h"
#include "vtkInformation.h"
#include "vtkInformationVector.h"
#include "vtkObjectFactory.h"
#include "vtkStreamingDemandDrivenPipeline.h"

vtkCxxRevisionMacro(vtkImageInvertFilter, "$Revision: 1.4 $");
vtkStandardNewMacro(vtkImageInvertFilter);

//----------------------------------------------------------------------------
void vtkImageInvertFilter::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os,indent);
}

//----------------------------------------------------------------------------
vtkImageInvertFilter::vtkImageInvertFilter()
{
}

template <class T>
void vtkImageInvertFilterExecute(vtkImageInvertFilter *self,
                             vtkImageData *outData, T *ptr)
{
  int min0, max0, min1, max1, min2, max2;
  int x, y, z, numC, j;
  float range[2];
  T tempdata;
  
  outData->GetExtent(min0, max0, min1, max1, min2, max2);
  numC = outData->GetNumberOfScalarComponents();
  
  range[0] = outData->GetScalarRange()[0];
  range[1] = outData->GetScalarRange()[1];

  self->UpdateProgress(0.0);

  for (z = min2; z <= max2; z++)
  {
  /* update progress */
  if (min2 != max2)
    self->UpdateProgress(z / (float)(max2-min2));
  for (y = min1; y <= max1; y++)
    {
    ptr = static_cast<T *>(outData->GetScalarPointer(min0, y, z));
    for (x = min0; x <= max0; x++)
      {
      for (j = 0; j < numC; j++)
        {
        tempdata = *ptr;
        /* modify data */
        tempdata = range[1] - (tempdata - range[0]);
        *ptr++ = tempdata;
        }
      }
    }
  }
  self->UpdateProgress(1.0);
}

//----------------------------------------------------------------------------
// Split up into finished and border datas.  Fill the border datas.
int vtkImageInvertFilter::RequestData(
  vtkInformation* request,
  vtkInformationVector** inputVector,
  vtkInformationVector* outputVector)
{
  void *ptr = NULL;

  // let superclass allocate data
  this->vtkImageInPlaceFilter::RequestData(request, inputVector, outputVector);

  // get the data object
  vtkInformation *outInfo = outputVector->GetInformationObject(0);
  vtkImageData *output = 
    vtkImageData::SafeDownCast(outInfo->Get(vtkDataObject::DATA_OBJECT()));
  
  switch (output->GetScalarType())
    {
    vtkTemplateMacro(
        vtkImageInvertFilterExecute(this, output, static_cast<VTK_TT *>(ptr)));
    default:
      vtkErrorMacro(<< "Execute: Unknown ScalarType");
      return 1;
    }

  return 1;
}




