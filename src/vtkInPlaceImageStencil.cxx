#include "vtkInPlaceImageStencil.h"

#include "vtkImageData.h"
#include "vtkInformation.h"
#include "vtkInformationVector.h"
#include "vtkObjectFactory.h"
#include "vtkImageStencilData.h"
#include "vtkPointData.h"
#include "vtkStreamingDemandDrivenPipeline.h"

vtkStandardNewMacro(vtkInPlaceImageStencil);

//----------------------------------------------------------------------------
void vtkInPlaceImageStencil::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os,indent);
}

//----------------------------------------------------------------------------
vtkInPlaceImageStencil::vtkInPlaceImageStencil()
{
	this->ReverseStencil = 0;
	this->MaskValue = 0.0;
        this->Stencil = NULL;
        this->SetNumberOfInputPorts(1);
}



template <class T>
void vtkInPlaceImageStencilExecute(vtkInPlaceImageStencil *self,
                             vtkImageData *outData, T *ptr)
{
  int min0, max0, min1, max1, min2, max2;
  int pmin0, pmax0;
  int x, y, z, iter, numC, idxC;
  vtkIdType inInc0, inInc1, inInc2;
  T *tempPtr;
  double outVal;

  vtkImageStencilData *stencil = self->GetStencil();
 
  outData->GetExtent(min0, max0, min1, max1, min2, max2);

  outData->GetIncrements(inInc0, inInc1, inInc2);
  numC = outData->GetNumberOfScalarComponents();
  outVal = self->GetMaskValue();

  self->UpdateProgress(0.0);

  for (z = min2; z <= max2; z++)
  {
  /* update progress */
  if (min2 != max2)
    self->UpdateProgress((z-min2) / (float)(max2-min2));
  for (y = min1; y <= max1; y++)
    {

      // loop over stencil sub-extents
      iter = 0;
      if (self->GetReverseStencil())
        { // flag that we want the complementary extents
        iter = -1;
        }
      pmin0 = min0;
      pmax0 = max0;

      ptr = static_cast<T *>(outData->GetScalarPointer(min0, y, z));
     
      while ((stencil != 0 && 
              stencil->GetNextExtent(pmin0,pmax0,min0,max0,y,z,iter)) ||
             (stencil == 0 && iter++ == 0))
        {
        tempPtr = ptr + (numC*(pmin0 - min0));
        for (x = pmin0; x <= pmax0; x++)
          for (idxC = 0; idxC < numC; ++idxC)
            *tempPtr++ = static_cast<T>(outVal);
	}
      // ugly hack -- remove this once Hua has his class completed
      if (self->GetReverseStencil() && (stencil != 0)) {
      pmin0 = min0;
      pmax0 = max0;
      iter = -1;
      if (!stencil->GetNextExtent(pmin0,pmax0,min0,max0,y,z,iter))
        {
        pmin0 = min0;
        pmax0 = max0;
        // set up pointer for sub extent
        tempPtr = ptr + (inInc2*(z - min2) +
                           inInc1*(y - min1) +
                           numC*(pmin0 - min0));
        for (x = pmin0; x <= pmax0; x++)
          for (idxC = 0; idxC < numC; ++idxC)
            *tempPtr++ = static_cast<T>(outVal);
	}
      }
      // end of ugly hack
    }
  }
  self->UpdateProgress(1.0);
}

//----------------------------------------------------------------------------
// Split up into finished and border datas.  Fill the border datas.
int vtkInPlaceImageStencil::RequestData(
  vtkInformation* request,
  vtkInformationVector** inputVector,
  vtkInformationVector* outputVector)
{
  void *ptr = NULL;

  // get the data object
  vtkInformation *outInfo = outputVector->GetInformationObject(0);
  vtkImageData *output = 
    vtkImageData::SafeDownCast(outInfo->Get(vtkDataObject::DATA_OBJECT()));
  int *outExt = outInfo->Get(vtkStreamingDemandDrivenPipeline::UPDATE_EXTENT());

  vtkInformation *inInfo = inputVector[0]->GetInformationObject(0);
  vtkImageData *input = 
    vtkImageData::SafeDownCast(inInfo->Get(vtkDataObject::DATA_OBJECT()));

 
  // always pass input straight through to output
  output->GetPointData()->PassData(input->GetPointData());
  output->SetExtent(outExt);
   
  switch (output->GetScalarType())
    {
    vtkTemplateMacro(
      vtkInPlaceImageStencilExecute(this, output, static_cast<VTK_TT *>(ptr)));
    default:
      vtkErrorMacro(<< "Execute: Unknown ScalarType");
      return 1;
    }

  return 1;
}




