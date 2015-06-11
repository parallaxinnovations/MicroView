#include "vtkImageInPlaceMirrorFilter.h"

#include "vtkImageData.h"
#include "vtkInformation.h"
#include "vtkInformationVector.h"
#include "vtkObjectFactory.h"
#include "vtkStreamingDemandDrivenPipeline.h"

vtkCxxRevisionMacro(vtkImageInPlaceMirrorFilter, "$Revision: 1.3 $");
vtkStandardNewMacro(vtkImageInPlaceMirrorFilter);

//----------------------------------------------------------------------------
void vtkImageInPlaceMirrorFilter::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os,indent);
}

//----------------------------------------------------------------------------
vtkImageInPlaceMirrorFilter::vtkImageInPlaceMirrorFilter()
{
  this->Axis = 0; // default is to flip in x axis
}

template <class T>
void vtkImageInPlaceMirrorFilterExecute(vtkImageInPlaceMirrorFilter *self,
                             vtkImageData *outData, T *ptr)
{
  int min0, max0, min1, max1, min2, max2, numC;
  int x0, x1, y0, y1, z0, z1;
  int j;
  vtkIdType outInc0, outInc1, outInc2;
  T *tempdata;
  int axis = self->GetAxis();
  
  outData->GetExtent(min0, max0, min1, max1, min2, max2);
  outData->GetIncrements(outInc0, outInc1, outInc2);
  numC = outData->GetNumberOfScalarComponents();
  
  // allocate space for scratch area
  tempdata = new T[numC];

  self->UpdateProgress(0.0);

  switch (axis) {
  case 0: // flip in x-axis
  
  for (z0 = min2; z0 <= max2; z0++)
  {
  /* update progress */
  if (max2 != min2)	  
    self->UpdateProgress(z0 / (float)(max2-min2));
  #pragma omp parallel
  for (y0 = min1; y0 <= max1; y0++)
    {
    ptr = static_cast<T *>(outData->GetScalarPointer(min0, y0, z0));
    x0 = min0*numC; x1 = max0*numC;
    while (x0 <= x1)
      {
	// copy end point into temp array
	for (j = 0; j < numC; j++)
	  tempdata[j] = ptr[x1+j];

        // over-write end point
	for (j = 0; j < numC; j++)
	  ptr[x1+j] = ptr[x0+j];
	
	//  over-write start point
	for (j = 0; j < numC; j++)
	  ptr[x0+j] = tempdata[j];
	x0 += numC; x1 -= numC;
      }
    }
  }
  break;

  case 1: // flip in y-axis

  for (z0 = min2; z0 <= max2; z0++)
  {
  /* update progress */
  if (max1 != min1)
    self->UpdateProgress(z0 / (float)(max1-min1));
  ptr = (T *) (outData->GetScalarPointer(min0, min1, z0)); // pointer to beginning of z-slice
  for (x0 = min0; x0 <= max0; x0++)
    {
    y0 = min1; y1 = max1;
    while (y0 <= y1)
      {
	for (j = 0; j < numC; j++)
	  tempdata[j] = ptr[x0*outInc0 + y1*outInc1 + j];
	for (j = 0; j < numC; j++)
	  ptr[x0*outInc0 + y1*outInc1 + j] = ptr[x0*outInc0 + y0*outInc1 + j];
	for (j = 0; j < numC; j++)
	  ptr[x0*outInc0 + y0*outInc1 + j] = tempdata[j];
	y0++; y1--;
      }
    }
  }
  break;

  case 2: // flip in z-axis
  ptr = (T *) (outData->GetScalarPointer(min0, min1, min2)); // pointer to entire volume
  for (y0 = min1; y0 <= max1; y0++)
  {
  /* update progress */
  if (max1 != min1)
    self->UpdateProgress(y0 / (float)(max1-min1));
  for (x0 = min0; x0 <= max0; x0++)
    {
    z0 = min2; z1 = max2;
    while (z0 <= z1)
      {
	for (j = 0; j < numC; j++)
	  tempdata[j] = ptr[x0*outInc0 + y0*outInc1 + z1*outInc2 + j];
	for (j = 0; j < numC; j++)
	  ptr[x0*outInc0 + y0*outInc1 + z1*outInc2 + j] = ptr[x0*outInc0 + y0*outInc1 + z0*outInc2 + j];
	for (j = 0; j < numC; j++)
	  ptr[x0*outInc0 + y0*outInc1 + z0*outInc2 + j] = tempdata[j];
	z0++; z1--;
      }
    }
  } 
  break;
  
  default:
  break;
  }
  self->UpdateProgress(1.0); 
  delete [] tempdata;
}

//----------------------------------------------------------------------------
// Split up into finished and border datas.  Fill the border datas.
int vtkImageInPlaceMirrorFilter::RequestData(
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
	  vtkImageInPlaceMirrorFilterExecute(this, output, static_cast<VTK_TT *>(ptr)));
    default:
      vtkErrorMacro(<< "Execute: Unknown ScalarType");
      return 1;
    }

  return 1;
}




