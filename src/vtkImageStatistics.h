// .NAME vtkImageStatistics - Generalized histograms up to 4 dimensions.
// .SECTION Description
// vtkImageStatistics - This filter divides component space into
// discrete bins.  It then counts the number of pixels associated
// with each bin.  The output is this "scatter plot" (histogram values for 1D).
// The dimensionality of the output depends on how many components the 
// input pixels have.  Input pixels with one component generate a 1D histogram.
// This filter can only handle images with 1 to 3 scalar components.
// The input can be any type, but the output is always int.
// Some statistics are computed on the pixel values at the same time.
// The SetStencilFunction, SetClippingExtents and ReverseStencil
// functions allow the statistics to be computed on an arbitrary
// portion of the input data.
// See the documentation for vtkImageStencil for more information.


#ifndef __vtkImageStatistics_h
#define __vtkImageStatistics_h


#include "vtkImageAccumulate.h"
#include "MicroViewConfigure.h"

class vtkImageStencilData;

class VTK_MicroView_EXPORT vtkImageStatistics : public vtkImageAccumulate
{
public:
  static vtkImageStatistics *New();
  vtkTypeRevisionMacro(vtkImageStatistics,vtkImageAccumulate);
  void PrintSelf(ostream& os, vtkIndent indent);

  // Description:
  // Get the statistics information for the data.
  vtkGetVector3Macro(Total, double);
  vtkSetMacro(BVFThreshold, double);
  vtkGetMacro(BVFThreshold, double);
  vtkSetMacro(BoneValue, double);
  vtkGetMacro(BoneValue, double);
  vtkSetMacro(WaterValue, double);
  vtkGetMacro(WaterValue, double);
  vtkSetMacro(LowerExclusionValue, double);
  vtkGetMacro(LowerExclusionValue, double);
  vtkSetMacro(UpperExclusionValue, double);
  vtkGetMacro(UpperExclusionValue, double);
  vtkSetMacro(BoneMineralConst, double);
  vtkGetMacro(BoneMineralConst, double);

  vtkSetVector3Macro(MaxValuePosition, int);
  vtkGetVector3Macro(MaxValuePosition, int);

  long int BoneVoxelCount;
  long int GetBoneVoxelCount() { return BoneVoxelCount; }
  double BoneMineralMass;
  double ThresholdedBoneMineralMass;
  double GetBMD() { if (GetVolume() != 0.0) return BoneMineralMass / GetVolume(); else return 0.0;}
  double GetThresholdedBMD() { if (GetVolume() != 0.0) return ThresholdedBoneMineralMass / GetThresholdedVolume(); else return 0.0;}
  double GetBoneMass() { return BoneMineralMass; }
  double GetThresholdedBoneMass() { return ThresholdedBoneMineralMass; }
  double GetVolume();
  double GetThresholdedVolume();
  
protected:
  vtkImageStatistics();
  ~vtkImageStatistics();

  int RequestData(vtkInformation* request,
                          vtkInformationVector** inputVector,
                          vtkInformationVector* outputVector);

  virtual int FillInputPortInformation(int, vtkInformation*);

  double Total[3];
  int MaxValuePosition[3];
  double BVFThreshold;
  double BoneValue;
  double WaterValue;
  double LowerExclusionValue;
  double UpperExclusionValue;
  double BoneMineralConst;

private:
  vtkImageStatistics(const vtkImageStatistics&);  // Not implemented.
  void operator=(const vtkImageStatistics&);  // Not implemented.
};

#endif



