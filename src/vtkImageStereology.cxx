#include "vtkImageStereology.h"
#include "vtkObjectFactory.h"


#include "vtkInformation.h"
#include "vtkInformationExecutivePortKey.h"
#include "vtkInformationVector.h"
#include "vtkStreamingDemandDrivenPipeline.h"

inline double deter_euler3d_rec3_3(double q27[3][3][3]);
/*
 *  Original notes from Tim Morgan
 * 
 *  Pl = number of test line intersections divided by total testline Length
 *  Pp = Bone volume fraction
 *  
 *  Pl = Pl / nSlices
 *  Pp = Pp / nSlices
 *  
 *  fBV_TV = BV/TV
 *  fTb_N = Pl
 *  fTb_Th = Pp/Pl
 *  fTb_Sp = (1-Pp)/Pl
 *  fBS_BV = 2*Pl/Pp
 */

vtkStandardNewMacro(vtkImageStereology);


//------------------------------------------------------------------------------
/* Repleaced with vtkStandardNewMacro (see above)
vtkImageStereology* vtkImageStereology::New()
{
  // First try to create the object from the vtkObjectFactory
  vtkObject* ret = vtkObjectFactory::CreateInstance("vtkImageStereology");
  if(ret)
    {
    return (vtkImageStereology*)ret;
    }
  // If the factory was unable to create the object, then create it here.
  return new vtkImageStereology;
}
*/

//----------------------------------------------------------------------------
vtkImageStereology::vtkImageStereology()
{
  this->Pp = this->Pl = this->PlX = this->PlY =
             this->PlZ = this->Euler3D = 0.0;
  this->Threshold = 0.0;
  this->mask = NULL;
}

//----------------------------------------------------------------------------
vtkImageStereology::~vtkImageStereology()
{
}

//----------------------------------------------------------------------------
// This templated function executes the filter for any type of data.
template <class T>
void vtkImageStereologyExecute(vtkImageStereology *self,
        vtkImageData *outData, T *ptr)
{
  int min0, max0, min1, max1, min2, max2;
  int x, y, z;
  int i, j, k;
  unsigned char *maskPtr;
  vtkImageData *mask = self->GetImageMask();
  double threshold = self->GetThreshold();  
  long numVoxels = 0;
  long numBoneVoxels = 0;
  long numX = 0, numY = 0, numZ = 0;
  long numXO = 0, numYO = 0, numZO = 0;
  double euler = 0.0;

  double *inSpacing = ((vtkImageData *)self->GetInput())->GetSpacing();
  int increments[3];
  double q27[3][3][3];

  
  outData->GetExtent(min0, max0, min1, max1, min2, max2);

  increments[0] = 1;
  increments[1] = max0 - min0 + 1;
  increments[2] = increments[1] * (max1 - min1 + 1);

  min0++; max0--; min1++; max1--; min2++; max2--;

  self->UpdateProgress(0.0);

  for (z = min2; z <= max2; z++)
  {
  /* update progress */
  if (min2 != max2)
    self->UpdateProgress((z-min2) / (float)(max2-min2));
  for (y = min1; y <= max1; y++)
    {
    ptr = (T *) (outData->GetScalarPointer(min0, y, z));
    if (mask)
      maskPtr = (unsigned char *) (mask->GetScalarPointer(min0, y, z));
    else
      maskPtr = NULL;

    for (x = min0; x <= max0; x++)
      {
        if ((maskPtr == NULL) || (maskPtr[x - min0])) { // is voxel within the masked portion of image?
          numVoxels++;

          if (ptr[x - min0] >= threshold) {
            numBoneVoxels++;
            
            if ((ptr[x - min0 - increments[0]] < threshold))
              numX++;
            if ((ptr[x - min0 + increments[1]] < threshold))
              numY++;
            if ((ptr[x - min0 - increments[2]] < threshold))
              numZ++;
            if ((ptr[x - min0 + increments[0]] < threshold))
              numXO++;
            if ((ptr[x - min0 - increments[1]] < threshold))
              numYO++;
            if ((ptr[x - min0 + increments[2]] < threshold))
              numZO++;

            // compute Euler index
            for (k=-1;k<=1;k++)
              for (j=-1;j<=1;j++)
                for (i=-1;i<=1;i++)
                  q27[i+1][j+1][k+1] = (ptr[x - min0 + increments[0]*i + increments[1]*j + increments[2]*k] >= threshold); 
            euler += deter_euler3d_rec3_3(q27);
          }
        }
      }
    }
  }
  self->SetPp((double)numBoneVoxels/(double)numVoxels);

  self->SetIntX(numX);
  self->SetIntY(numY);
  self->SetIntZ(numZ);
  self->SetIntXO(numXO);
  self->SetIntYO(numYO);
  self->SetIntZO(numZO);

  self->SetPlX((double) ((numX+numXO)/2.0) / (double) (numVoxels * inSpacing[0]) * 2);
  self->SetPlY((double) ((numY+numYO)/2.0) / (double) (numVoxels * inSpacing[1]) * 2);
  self->SetPlZ((double) ((numZ+numZO)/2.0) / (double) (numVoxels * inSpacing[2]) * 2);
  self->SetPl((self->GetPlX() + self->GetPlY() + self->GetPlZ()) / 3.0);
  self->SetEuler3D(euler);
  self->SetnumVoxels(numVoxels);
  self->UpdateProgress(1.0);
}


//----------------------------------------------------------------------------
// This method is passed a input and output region, and executes the filter
// algorithm to fill the output from the input.
// It just executes a switch statement to call the correct function for
// the regions data types.
void vtkImageStereology::ExecuteData(vtkDataObject *out)
{ 
  void *ptr = NULL;
  
  // let superclass allocate data
  this->vtkImageInPlaceFilter::ExecuteData(out);

  vtkImageData *outData = this->GetOutput();
  
  switch (outData->GetScalarType())
    {
    vtkTemplateMacro(vtkImageStereologyExecute(this,
                      outData, static_cast<VTK_TT *>(ptr)));
    default:
      vtkErrorMacro(<< "Execute: Unknown ScalarType");
      return;
    }
}


//----------------------------------------------------------------------------
inline double calc_eul1d3_3(double as[3])
{
  return as[1] - 0.5 * (as[0]*as[1] + as[1]*as[2]);
}

//----------------------------------------------------------------------------
inline double calc_euler2d3_3(double aa[3][3])
{
  double as[3], eul2dl, eul2de, eul1di;
  int i;
  // copy values
  for (i=0;i<3;i++) as[i] = aa[1][i];
  eul2dl = calc_eul1d3_3(as);

  // copy values
  for (i=0;i<3;i++) as[i] = aa[1][i] * aa[0][i];  
  eul2de = calc_eul1d3_3(as);
  
  // copy values
  for (i=0;i<3;i++) as[i] = aa[1][i] * aa[2][i];  
  eul1di = calc_eul1d3_3(as);
  return eul2dl - 0.5 * (eul2de + eul1di);
}

//----------------------------------------------------------------------------
inline double deter_euler3d_rec3_3(double q27[3][3][3])
{
  double aa[3][3], eul3dp, eul3de, eul2di;
  int i, j;

  // copy values
  for (j=0;j<3;j++)
    for (i=0;i<3;i++)
      aa[i][j] = q27[1][i][j];
  eul3dp = calc_euler2d3_3(aa);

  // copy values
  for (j=0;j<3;j++)
    for (i=0;i<3;i++)
      aa[i][j] = q27[1][i][j] * q27[0][i][j];
  eul3de = calc_euler2d3_3(aa);

  // copy values
  for (j=0;j<3;j++)
    for (i=0;i<3;i++)
      aa[i][j] = q27[1][i][j] * q27[2][i][j];
  eul2di = calc_euler2d3_3(aa);
  return eul3dp - 0.5*(eul3de + eul2di);
}


//----------------------------------------------------------------------------
// Description:
// PrintSelf function ...
void vtkImageStereology::PrintSelf(ostream& os, vtkIndent indent)
{
    
    double voxel_volume = 0.0;
    double *inSpacing;
    
    if (this->GetInput()) {
      inSpacing = vtkImageData::SafeDownCast(this->GetInput())->GetSpacing();
      voxel_volume = inSpacing[0] * inSpacing[1] * inSpacing[2];
    }

  vtkImageInPlaceFilter::PrintSelf(os,indent);
  os << indent << "Threshold: " << this->Threshold << "\n";
  os << indent << "Number of voxels used: " << this->numVoxels << "\n";
  os << indent << "Volume used (mm^3): " << (double) this->numVoxels * voxel_volume << "\n";
  os << indent << "Number of Intersections (x,y,z): " << this->GetIntX() << " : " << this->GetIntXO() << ", "
     << this->GetIntY() << " : " << this->GetIntYO() << ", " << this->GetIntZ() << " : " << this->GetIntZO() << "\n";
  os << indent << "Pp: " << this->Pp << "\n";
  os << indent << "PlX: " << this->PlX << "\n";
  os << indent << "PlY: " << this->PlY << "\n";
  os << indent << "PlZ: " << this->PlZ << "\n";
  os << indent << "Pl: " << this->Pl << "\n";
  os << indent << "Euler index (27 neighbours): " << this->Euler3D << "\n";
  os << indent << "-Euler/volume (27 neighbours): " << -1.0 * this->Euler3D / voxel_volume / this->numVoxels << "\n";
  os << indent << "BVTV: " << this->GetBVTV() << "\n";
  os << indent << "Tb.N (x,y,z,avg.): " << this->GetxTbN() << ", "
                                        << this->GetyTbN() << ", "
                                        << this->GetzTbN() << ", "
                                        << this->GetTbN() << "\n";

  os << indent << "Tb.Th (x,y,z,avg.): " << this->GetxTbTh() << ", "
                                        << this->GetyTbTh() << ", "
                                        << this->GetzTbTh() << ", "
                                        << this->GetTbTh() << "\n";

  os << indent << "Tb.Sp (x,y,z,avg.): " << this->GetxTbSp() << ", "
                                        << this->GetyTbSp() << ", "
                                        << this->GetzTbSp() << ", "
                                        << this->GetTbSp() << "\n";

  os << indent << "BSBV (x,y,z,avg.): " << this->GetxBSBV() << ", "
                                        << this->GetyBSBV() << ", "
                                        << this->GetzBSBV() << ", "
                                        << this->GetBSBV() << "\n";

}
