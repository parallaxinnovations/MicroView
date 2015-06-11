#ifndef __vtkImageStereology_h
#define __vtkImageStereology_h

#include <stdio.h>
#include "MicroViewConfigure.h"
#include "vtkImageInPlaceFilter.h"
#include "vtkImageData.h"

class VTK_MicroView_EXPORT vtkImageStereology : public vtkImageInPlaceFilter
{
public:
  static vtkImageStereology *New();
  vtkTypeMacro(vtkImageStereology,vtkImageInPlaceFilter);
  void PrintSelf(ostream& os, vtkIndent indent);

  // Get/Set macros
  vtkSetMacro(Threshold, double);
  vtkGetMacro(Threshold, double);
  vtkSetMacro(Euler3D, double);
  vtkGetMacro(Euler3D, double);
  vtkSetMacro(Pp, double);
  vtkGetMacro(Pp, double);
  vtkSetMacro(Pl, double);
  vtkGetMacro(Pl, double);

  vtkSetMacro(IntX, long);
  vtkGetMacro(IntX, long);
  vtkSetMacro(IntY, long);
  vtkGetMacro(IntY, long);
  vtkSetMacro(IntZ, long);
  vtkGetMacro(IntZ, long);

  vtkSetMacro(IntXO, long);
  vtkGetMacro(IntXO, long);
  vtkSetMacro(IntYO, long);
  vtkGetMacro(IntYO, long);
  vtkSetMacro(IntZO, long);
  vtkGetMacro(IntZO, long);


  vtkSetMacro(PlX, double);
  vtkGetMacro(PlX, double);
  vtkSetMacro(PlY, double);
  vtkGetMacro(PlY, double);
  vtkSetMacro(PlZ, double);
  vtkGetMacro(PlZ, double);

  vtkSetMacro(numVoxels, long);
  vtkGetMacro(numVoxels, long);

  double GetBVTV() { return Pp; }

  double GetxTbN() { return PlX; }
  double GetyTbN() { return PlY; }
  double GetzTbN() { return PlZ; }
  double GetTbN() { return Pl; }

  double GetxTbTh() { return Pp/PlX; }
  double GetyTbTh() { return Pp/PlY; }
  double GetzTbTh() { return Pp/PlZ; }
  double GetTbTh() { return Pp/Pl; }

  double GetxTbSp() { return (1.0 - Pp) / PlX; }
  double GetyTbSp() { return (1.0 - Pp) / PlY; }
  double GetzTbSp() { return (1.0 - Pp) / PlZ; }
  double GetTbSp() { return (1.0 - Pp) / Pl; }

  double GetxBSBV() { return 2.0 * (PlX / Pp); }
  double GetyBSBV() { return 2.0 * (PlY / Pp); }
  double GetzBSBV() { return 2.0 * (PlZ / Pp); }
  double GetBSBV() { return 2.0 * (Pl / Pp); }

  void SetImageMask(vtkImageData *mask) { this->mask = mask; }
  vtkImageData *GetImageMask() { return this->mask; }

protected:
  double Threshold;
  double Pp;
  double Pl;
  double PlX;
  double PlY;
  double PlZ;
  double Euler3D;
  long IntX;
  long IntY;
  long IntZ;
  long IntXO;
  long IntYO;
  long IntZO;
  long numVoxels;
  vtkImageData *mask;

  vtkImageStereology();
  ~vtkImageStereology();
  vtkImageStereology(const vtkImageStereology&) {};
  void operator=(const vtkImageStereology&) {};

  void ExecuteData (vtkDataObject *);
};

#endif
