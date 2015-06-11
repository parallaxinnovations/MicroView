#include "vtkImageTextExport.h"

#include "vtkImageData.h"
#include "vtkImageStencilData.h"
#include "vtkObjectFactory.h"

vtkCxxRevisionMacro(vtkImageTextExport, "$Revision: 1.3 $");
vtkStandardNewMacro(vtkImageTextExport);


//----------------------------------------------------------------------------
// Constructor sets default values
vtkImageTextExport::vtkImageTextExport()
{
}


//----------------------------------------------------------------------------
vtkImageTextExport::~vtkImageTextExport()
{
}


//----------------------------------------------------------------------------
void vtkImageTextExport::SetStencil(vtkImageStencilData *stencil)
{
  this->vtkProcessObject::SetNthInput(1, stencil); 
}


//----------------------------------------------------------------------------
vtkImageStencilData *vtkImageTextExport::GetStencil()
{
  if (this->NumberOfInputs < 2) 
    { 
    return NULL;
    }
  else
    {
    return (vtkImageStencilData *)(this->Inputs[1]); 
    }
}

//----------------------------------------------------------------------------
// This templated function executes the filter for any type of data.
template <class T>
void vtkImageTextExportExecute(vtkImageTextExport *self,
                               vtkImageData *inData, T *inPtr,
                               vtkImageData *outData, int *outPtr)
{
  int idX, idY, idZ;
  int iter, pmin0, pmax0, min0, max0, min1, max1, min2, max2;
  vtkIdType inInc0, inInc1, inInc2;
  T *tempPtr;
  float val;
  int numC,  *outExtent;
  vtkIdType *outIncs;
  
  unsigned long count = 0;
  unsigned long target;
  int count2 = 0;

  ofstream fout(self->GetFileName());
  vtkImageStencilData *stencil = self->GetStencil();

  // Get information to march through data 
  numC = inData->GetNumberOfScalarComponents();
  inData->GetUpdateExtent(min0, max0, min1, max1, min2, max2);
  inData->GetIncrements(inInc0, inInc1, inInc2);
  outExtent = outData->GetExtent();
  outIncs = outData->GetIncrements();
  target = (unsigned long)((max2 - min2 + 1)*(max1 - min1 +1)/50.0);
  target++;

  // Loop through input pixels
  for (idZ = min2; idZ <= max2; idZ++)
    {
    for (idY = min1; idY <= max1; idY++)
      {
      if (!(count%target)) 
        {
        self->UpdateProgress(count/(50.0*target));
        }
      count++;

      // loop over stencil sub-extents
      iter = 0;
      pmin0 = min0;
      pmax0 = max0;
      while ((stencil != 0 && 
              stencil->GetNextExtent(pmin0,pmax0,min0,max0,idY,idZ,iter)) ||
             (stencil == 0 && iter++ == 0))
        {
        // set up pointer for sub extent
        tempPtr = inPtr + (inInc2*(idZ - min2) +
                           inInc1*(idY - min1) +
                           numC*(pmin0 - min0));

        // accumulate over the sub extent
        for (idX = pmin0; idX <= pmax0; idX++)
          {
		  // write out *tempPtr value here...
		  val = (float) *tempPtr++;
		  if (count2 == 10) {
		    fout << val << "\n";
		    count2 = 0;
		  } else {
		    fout << val << ", ";
		    count2++;
		  }
          }
        }
      }
    }

  fout.close();
}

        

//----------------------------------------------------------------------------
// This method is passed a input and output Data, and executes the filter
// algorithm to fill the output from the input.
// It just executes a switch statement to call the correct function for
// the Datas data types.
void vtkImageTextExport::ExecuteData(vtkDataObject *vtkNotUsed(out))
{
  void *inPtr;
  void *outPtr;
  vtkImageData *inData = this->GetInput();
  vtkImageData *outData = this->GetOutput();
  
  vtkDebugMacro(<<"Executing image accumulate");
  
  // We need to allocate our own scalars since we are overriding
  // the superclasses "Execute()" method.
  outData->SetExtent(outData->GetWholeExtent());
  outData->AllocateScalars();
  
  inPtr = inData->GetScalarPointerForExtent(inData->GetUpdateExtent());
  outPtr = outData->GetScalarPointer();
  
  // Components turned into x, y and z
  if (this->GetInput()->GetNumberOfScalarComponents() > 3)
    {
    vtkErrorMacro("This filter can handle upto 3 components");
    return;
    }
  
  // this filter expects that output is type int.
  if (outData->GetScalarType() != VTK_INT)
    {
    vtkErrorMacro(<< "Execute: out ScalarType " << outData->GetScalarType()
                  << " must be int\n");
    return;
    }
  
  switch (inData->GetScalarType())
    {
    vtkTemplateMacro5(vtkImageTextExportExecute, this, 
                       inData, (VTK_TT *)(inPtr), 
                       outData, (int *)(outPtr));
    default:
      vtkErrorMacro(<< "Execute: Unknown ScalarType");
      return;
    }
}


//----------------------------------------------------------------------------
void vtkImageTextExport::ExecuteInformation(vtkImageData *input, 
                                            vtkImageData *output)
{
  output->SetNumberOfScalarComponents(1);
  output->SetScalarType(VTK_INT);

  // need to set the spacing and origin of the stencil to match the output
  vtkImageStencilData *stencil = this->GetStencil();
  if (stencil)
    {
    stencil->SetSpacing(input->GetSpacing());
    stencil->SetOrigin(input->GetOrigin());
    }
}

//----------------------------------------------------------------------------
// Get ALL of the input.
void vtkImageTextExport::ComputeInputUpdateExtent(int inExt[6], 
                                                  int *vtkNotUsed(outExt))
{
  int *wholeExtent;

  wholeExtent = this->GetInput()->GetWholeExtent();
  memcpy(inExt, wholeExtent, 6*sizeof(int));
}


void vtkImageTextExport::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os,indent);
  os << indent << "Filename: " << this->FileName << "\n";
}

