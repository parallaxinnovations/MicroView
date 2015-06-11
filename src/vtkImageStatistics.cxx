#include "vtkImageStatistics.h"

#include "vtkImageData.h"
#include "vtkImageStencilData.h"
#include "vtkObjectFactory.h"
#include "vtkInformation.h"
#include "vtkInformationVector.h"
#include "vtkStreamingDemandDrivenPipeline.h"

#include <math.h>

vtkCxxRevisionMacro(vtkImageStatistics, "$Revision: 1.8 $");
vtkStandardNewMacro(vtkImageStatistics);

#define SB3_DENSITY 1850.0
#define BMC_FRACTION 0.58

//----------------------------------------------------------------------------
// Constructor sets default values
vtkImageStatistics::vtkImageStatistics()
{
  int idx;
  
  for (idx = 0; idx < 3; ++idx)
    {
    this->ComponentSpacing[idx] = 1.0;
    this->ComponentOrigin[idx] = 0.0;
    this->ComponentExtent[idx*2] = 0;
    this->ComponentExtent[idx*2+1] = 0;
    }
  this->ComponentExtent[1] = 255;
  
  this->ReverseStencil = 0;
  this->BVFThreshold = 1e37;
  this->BoneMineralMass = 0.0;
  this->ThresholdedBoneMineralMass = 0.0;
  
  for (idx = 0; idx < 4; idx++) {
        this->Min[idx] = 0.0;
        this->Max[idx] = 0.0;
        this->Mean[idx] = 0.0;
        this->StandardDeviation[idx] = 0.0;
        this->Total[idx] = 0.0;
  }

  this->VoxelCount = 0;
  this->BoneVoxelCount = 0;
  this->BoneValue = 0;
  this->WaterValue = 0;
  this->LowerExclusionValue = -65534.0;
  this->UpperExclusionValue = 65535.0;
  this->BoneMineralConst = SB3_DENSITY * BMC_FRACTION;

  this->SetNumberOfInputPorts(2);
}


//----------------------------------------------------------------------------
vtkImageStatistics::~vtkImageStatistics()
{
}

//----------------------------------------------------------------------------
// Get volume of selected region
double vtkImageStatistics::GetVolume()
{
  vtkImageData *inData = vtkImageData::SafeDownCast(this->GetInput());
  double *inspacing = inData->GetSpacing();
  double dVoxelVolume = inspacing[0] * inspacing[1] * inspacing[2] / 1000.0;  // measured in cm cubed
 
  return (double) this->VoxelCount * dVoxelVolume;
}

//----------------------------------------------------------------------------
// Get volume of selected thresholded region
double vtkImageStatistics::GetThresholdedVolume()
{
  vtkImageData *inData = vtkImageData::SafeDownCast(this->GetInput());
  double *inspacing = inData->GetSpacing();
  double dVoxelVolume = inspacing[0] * inspacing[1] * inspacing[2] / 1000.0;  // measured in cm cubed
 
  return (double) this->BoneVoxelCount * dVoxelVolume;
}



//----------------------------------------------------------------------------
// This templated function executes the filter for any type of data.
template <class T>
void vtkImageStatisticsExecute(vtkImageStatistics *self,
                               vtkImageData *inData, T *inPtr,
                               vtkImageData *outData, int *outPtr,
                               double Min[4], double Max[4], double Mean[4], double StandardDeviation[4],
                               vtkIdType *VoxelCount, int outExt[6])
{
  int idX, idY, idZ, idxC;
  int iter, pmin0, pmax0;
  vtkIdType inInc0, inInc1, inInc2;
  T *tempPtr;
  int *outPtrC;
  int numC, outIdx, *outExtent;
  vtkIdType *outIncs;
  
  double *origin, *spacing, *inspacing;
  unsigned long count = 0;
  unsigned long target;
  double sumSqr[4], variance;
  // max value index
  int imax[4];

  // variables used to compute statistics (filter handles max 4 components)
  double sum[4];
  for (int i=0; i<4; i++) {
      sum[i] = 0.0;
      Min[i] = VTK_DOUBLE_MAX;
      Max[i] = VTK_DOUBLE_MIN;
      imax[i] = VTK_INT_MIN;
      sumSqr[i] = 0.0;
      StandardDeviation[i] = 0.0;
  }
  *VoxelCount = 0;
  
  vtkImageStencilData *stencil = self->GetStencil();

  // Get information to march through data 
  numC = inData->GetNumberOfScalarComponents();

  // Zero count in every bin
  // TODO: next two lines should be moved elsewhere to allow memory streaming to operate correctly
  memset((void *)outPtr, 0, (outExt[1]-outExt[0] + 1)*(outExt[3] - outExt[2] + 1)*(outExt[5] - outExt[4] + 1)*sizeof(int)*numC);

  inData->GetIncrements(inInc0, inInc1, inInc2);
  outExtent = outData->GetExtent();
  outIncs = outData->GetIncrements();
  origin = outData->GetOrigin();
  spacing = outData->GetSpacing();
  inspacing = inData->GetSpacing();
  target = (unsigned long)((outExt[3] - outExt[2] + 1)*(outExt[1] - outExt[0] +1)/50.0);
  target++;

  // Initialize bone density variables
  double BoneValue = self->GetBoneValue();
  double WaterValue = self->GetWaterValue();
  double LowerExclusionValue = self->GetLowerExclusionValue();
  double UpperExclusionValue = self->GetUpperExclusionValue();
  self->BoneMineralMass = 0.0;
  self->ThresholdedBoneMineralMass = 0.0;
  double dVoxelVolume = inspacing[0] * inspacing[1] * inspacing[2] / 1000.0;  // measured in cm cubed
  double dMultiplier;

  if (BoneValue != 0)
    dMultiplier = self->GetBoneMineralConst() * dVoxelVolume / (BoneValue - WaterValue);
  else
    dMultiplier = 0.0;


  // Loop through input pixels
  for (idZ = outExt[4]; !self->GetAbortExecute() && idZ <= outExt[5]; idZ++)
    {
    for (idY = outExt[2]; idY <= outExt[3]; idY++)
      {
      if (!(count%target)) 
        {
        self->UpdateProgress((double)count/(50.0*target));
        }
      count++;

      // loop over stencil sub-extents
      iter = 0;
      if (self->GetReverseStencil())
        { // flag that we want the complementary extents
        iter = -1;
        }

      pmin0 = outExt[0];
      pmax0 = outExt[1];
      while ((stencil != 0 && 
              stencil->GetNextExtent(pmin0,pmax0,outExt[0],outExt[1],idY,idZ,iter)) ||
             (stencil == 0 && iter++ == 0))
        {
        // set up pointer for sub extent
        tempPtr = inPtr + (inInc2*(idZ - outExt[4]) +
                           inInc1*(idY - outExt[2]) +
                           numC*(pmin0 - outExt[0]));

        // accumulate over the sub extent
        for (idX = pmin0; idX <= pmax0; idX++)
          {
          // find the bin for this pixel.
          outPtrC = outPtr;
          (*VoxelCount)++;
          for (idxC = 0; idxC < numC; ++idxC)
            {
            // Gather statistics
            sum[idxC]+= *tempPtr;
            sumSqr[idxC]+= (*tempPtr * *tempPtr);
            if (*tempPtr > Max[idxC])
              {
              Max[idxC] = *tempPtr;
              imax[0] = idX;    // save the location of max value...
              imax[1] = idY;    // hack, will not work if numC > 1
              imax[2] = idZ;
              }
            else if (*tempPtr < Min[idxC])
              {
              Min[idxC] = *tempPtr;
              }
            if (*tempPtr >= (self->GetBVFThreshold()))
              (self->BoneVoxelCount)++;
            if ((*tempPtr >= (LowerExclusionValue)) && (*tempPtr <= (UpperExclusionValue))) {
              self->BoneMineralMass +=
                (*tempPtr - WaterValue) * dMultiplier;
	    }
	// Next if bracket added for TM...
            if ((*tempPtr >= (self->GetBVFThreshold())) && (*tempPtr >= (LowerExclusionValue)) && (*tempPtr <= (UpperExclusionValue))) {
              self->ThresholdedBoneMineralMass +=
                (*tempPtr - WaterValue) * dMultiplier;
             }
            // compute the index
            outIdx = (int) floor((((double)*tempPtr++ - origin[idxC]) 
                                  / spacing[idxC]));
            if (!idxC && (outIdx < outExtent[idxC*2] || outIdx > outExtent[idxC*2+1]))
              {
              // Out of bin range
              outPtrC = NULL;
              break;
              }
            outPtrC += (outIdx - outExtent[idxC*2]) * outIncs[idxC];
            }
          if (outPtrC)
            {
            ++(*outPtrC);
            }
          }
        }
      }
    }
 
  // user aborted?
  if (self->GetAbortExecute()) {
    printf("Aborted!");
    return;
  }
  
  if (*VoxelCount) // avoid the div0
    {
    Mean[0] = sum[0] / (double)*VoxelCount;    
    Mean[1] = sum[1] / (double)*VoxelCount;    
    Mean[2] = sum[2] / (double)*VoxelCount;    

    variance = sumSqr[0] / (double)(*VoxelCount-1) - ((double) *VoxelCount * Mean[0] * Mean[0] / (double) (*VoxelCount - 1));
    StandardDeviation[0] = sqrt(variance);
    variance = sumSqr[1] / (double)(*VoxelCount-1) - ((double) *VoxelCount * Mean[1] * Mean[1] / (double) (*VoxelCount - 1));
    StandardDeviation[1] = sqrt(variance);
    variance = sumSqr[2] / (double)(*VoxelCount-1) - ((double) *VoxelCount * Mean[2] * Mean[2] / (double) (*VoxelCount - 1));
    StandardDeviation[2] = sqrt(variance);
    }
  else
    {
    Mean[0] = Mean[1] = Mean[2] = 0.0;
    StandardDeviation[0] = StandardDeviation[1] = StandardDeviation[2] = 0.0;
    }

  self->SetMaxValuePosition(imax);

}

        

//----------------------------------------------------------------------------
// This method is passed a input and output Data, and executes the filter
// algorithm to fill the output from the input.
// It just executes a switch statement to call the correct function for
// the Datas data types.


int vtkImageStatistics::RequestData(
 vtkInformation* vtkNotUsed( request ),
  vtkInformationVector** inputVector,
  vtkInformationVector* outputVector)
{
  void *inPtr;
  void *outPtr;

  // get the input
  vtkInformation* inInfo = inputVector[0]->GetInformationObject(0);
  vtkImageData *inData = vtkImageData::SafeDownCast(inInfo->Get(vtkDataObject::DATA_OBJECT()));

  int inExt[6];
  inInfo->Get(vtkStreamingDemandDrivenPipeline::UPDATE_EXTENT(), inExt);

  // get the output
  vtkInformation *outInfo = outputVector->GetInformationObject(0);
  vtkImageData *outData = vtkImageData::SafeDownCast(outInfo->Get(vtkDataObject::DATA_OBJECT()));

  int outExt[6];
  outInfo->Get(vtkStreamingDemandDrivenPipeline::UPDATE_EXTENT(), outExt);
  
  vtkDebugMacro(<<"Executing image statistics");

  inPtr = inData->GetScalarPointerForExtent(inExt);
  outPtr = outData->GetScalarPointer();
  
  // Components turned into x, y and z
  if (inData->GetNumberOfScalarComponents() > 4)
    {
    vtkErrorMacro("This filter can handle upto 4 components");
    return 1;
    }
  
  // this filter expects that output is type int.
  if (outData->GetScalarType() != VTK_INT)
    {
    vtkErrorMacro(<< "Execute: out ScalarType " << outData->GetScalarType()
                  << " must be int\n");
    return 1;
    }
  
  switch (inData->GetScalarType())
    {
    vtkTemplateMacro(vtkImageStatisticsExecute(this, 
                       inData, static_cast<VTK_TT *>(inPtr), 
                       outData, static_cast<int *>(outPtr),
                       this->Min, this->Max,
                       this->Mean,
                       this->StandardDeviation, 
                       &this->VoxelCount, outExt));
    default:
      vtkErrorMacro(<< "Execute: Unknown ScalarType");
      return 1;
    }
  if (this->VoxelCount)
  {
    this->Total[0] = this->Mean[0]*this->VoxelCount;
    this->Total[1] = this->Mean[1]*this->VoxelCount;
    this->Total[2] = this->Mean[2]*this->VoxelCount;
  }
  return 1;
}

//----------------------------------------------------------------------------
int vtkImageStatistics::FillInputPortInformation(int port, vtkInformation* info)
{
  if (port == 1)
    {
    info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkImageStencilData");
    info->Set(vtkAlgorithm::INPUT_IS_OPTIONAL(), 1);
    }
  else
    {
    info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkImageData");
    }
  return 1;
}

//----------------------------------------------------------------------------
void vtkImageStatistics::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os,indent);

  os << indent << "Mean: " << this->Mean[0] << ", "
	                   << this->Mean[1] << ", "
			   << this->Mean[2] << "\n";
  os << indent << "Min: " << this->Min[0] << ", "
	                  << this->Min[1] << ", "
			  << this->Min[2] << "\n";
  os << indent << "Max: " << this->Max[0] << ", "
	                  << this->Max[1] << ", "
			  << this->Max[2] << "\n";
  os << indent << "StandardDeviation: " << this->StandardDeviation << "\n";
  os << indent << "VoxelCount: " << this->VoxelCount << "\n";
  os << indent << "Bone Voxel Count: " << this->BoneVoxelCount << "\n";
  os << indent << "Bone Threshold: " << this->BVFThreshold << "\n";
  if (this->VoxelCount > 0)
    os << indent << "Bone Volume Fraction: " <<  ((double) this->BoneVoxelCount / (double)this->VoxelCount) << "\n";
  os << indent << "BoneValue: " << this->BoneValue << "\n";
  os << indent << "WaterValue: " << this->WaterValue << "\n";
  os << indent << "LowerExclusionValue: " << this->LowerExclusionValue << "\n";
  os << indent << "UpperExclusionValue: " << this->UpperExclusionValue << "\n";
  os << indent << "Stencil: " << this->GetStencil() << "\n";
  os << indent << "ReverseStencil: " << (this->ReverseStencil ?
                                         "On\n" : "Off\n");

  os << indent << "ComponentOrigin: ( "
     << this->ComponentOrigin[0] << ", "
     << this->ComponentOrigin[1] << ", "
     << this->ComponentOrigin[2] << " )\n";

  os << indent << "ComponentSpacing: ( "
     << this->ComponentSpacing[0] << ", "
     << this->ComponentSpacing[1] << ", "
     << this->ComponentSpacing[2] << " )\n";

  os << indent << "ComponentExtent: ( "
     << this->ComponentExtent[0] << "," << this->ComponentExtent[1] << " "
     << this->ComponentExtent[2] << "," << this->ComponentExtent[3] << " "
     << this->ComponentExtent[4] << "," << this->ComponentExtent[5] << " }\n";
}

