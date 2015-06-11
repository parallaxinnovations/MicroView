/************************************************************************/
/* vtkImagePurify.cxx                                                   */
/*                                                                      */
/* vtk class mimicking the original contributed by Mike Westmore.       */
/* Class exists to purify a binary volume, removing isolated bony       */
/* spicules and encapsulated marrow spaces.                             */
/*                                                                      */
/************************************************************************/

#include "vtkImagePurify.h"

#include "vtkImageData.h"
#include "vtkObjectFactory.h"

#define max(a,b) ((a) > (b) ? (a) : (b))
#define min(a,b) ((a) < (b) ? (a) : (b))


vtkCxxRevisionMacro(vtkImagePurify, "$Revision: 1.3 $");  // this is needed to prevent vtable problems
vtkStandardNewMacro(vtkImagePurify);

// The switch statement in Execute will call this method with
// the appropriate input type (IT). Note that this example assumes
// that the output data type is the same as the input data type.
// This is not always the case.
template <class IT>
void vtkImagePurifyExecute(vtkImagePurify* self, vtkImageData* input,
                                        vtkImageData* output,
                                        IT* inPtr, IT* outPtr)
{
  int x, y, z;
  float Threshold;
  unsigned char *scrap, *pure;
  int *xbound, *ybound, *zbound;
  vtkIdType outInc0, outInc1, outInc2;
  long index, numbounds;
  int dims[3]; 

  input->GetDimensions(dims);
  output->GetIncrements(outInc0, outInc1, outInc2);
  int size = dims[0]*dims[1]*dims[2];
  
  Threshold = self->GetThreshold();

  self->SetPurifyError(0);
  
  if (input->GetScalarType() != output->GetScalarType())
    {
    vtkGenericWarningMacro(<< "Execute: input ScalarType, " << input->GetScalarType()
    << ", must match out ScalarType " << output->GetScalarType());
    self->SetPurifyError(-1);
    return;
    }
 
  // allocate space for various arrays
  scrap = new unsigned char[size];
  pure = new unsigned char[size];
  xbound = new int[size]; 
  ybound = new int[size]; 
  zbound = new int[size]; 

  // create two binarized copies of image
  for (index = 0; index < size; index++)
  {
    if (inPtr[index] >= Threshold)
      scrap[index] = outPtr[index] = static_cast<IT>(255);
    else
      scrap[index] = outPtr[index] = 0;
  }
  
  // search for first non-zero value on first edge of cube
  numbounds = 0;
  x = y = z = 0;
  while ( ( y < dims[1] ) && ( numbounds == 0 ) )
    {
    while ( ( x < dims[0] ) && ( numbounds == 0 ) )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == static_cast<IT>(255) )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = static_cast<IT>(254);
        xbound[0] = x; ybound[0] = y; zbound[0] = z;
        numbounds = 1;
        }
      x++;
      }
    x = 0;
    y++;
    }
 
  // search for first non-zero value on second edge of cube
  x = y = 0; z = dims[2] - 1;
  while ( ( y < dims[1] ) && ( numbounds == 0 ) )
    {
    while ( ( x < dims[0] ) && ( numbounds == 0 ) )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == static_cast<IT>(255) )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = static_cast<IT>(254);
        xbound[0] = x; ybound[0] = y; zbound[0] = z;
        numbounds = 1;
        }
      x++;
      }
    x = 0;
    y++;
    }

  // search for first non-zero value on third edge of cube
  x = z = y = 0; 
  while ( ( z < dims[2] ) && ( numbounds == 0 ) )
    {
    while ( ( x < dims[0] ) && ( numbounds == 0 ) )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == static_cast<IT>(255) )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = static_cast<IT>(254);
        xbound[0] = x; ybound[0] = y; zbound[0] = z;
        numbounds = 1;
        }
      x++;
      }
    x = 0;
    z++;
    }

  // search for first non-zero value on fourth edge of cube
  x = z = 0; y = dims[1] - 1; 
  while ( ( z < dims[2] ) && ( numbounds == 0 ) )
    {
    while ( ( x < dims[0] ) && ( numbounds == 0 ) )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == static_cast<IT>(255) )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = static_cast<IT>(254);
        xbound[0] = x; ybound[0] = y; zbound[0] = z;
        numbounds = 1;
        }
      x++;
      }
    x = 0;
    z++;
    }

  // search for first non-zero value on fifth edge of cube
  x = z = y = 0; 
  while ( ( z < dims[2] ) && ( numbounds == 0 ) )
    {
    while ( ( y < dims[1] ) && ( numbounds == 0 ) )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == static_cast<IT>(255) )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = static_cast<IT>(254);
        xbound[0] = x; ybound[0] = y; zbound[0] = z;
        numbounds = 1;
        }
      y++;
      }
    y = 0;
    z++;
    }

  // search for first non-zero value on sixth edge of cube
  z = y = 0; x = dims[0] - 1; 
  while ( ( z < dims[2] ) && ( numbounds == 0 ) )
    {
    while ( ( y < dims[1] ) && ( numbounds == 0 ) )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == static_cast<IT>(255) )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = static_cast<IT>(254);
        xbound[0] = x; ybound[0] = y; zbound[0] = z;
        numbounds = 1;
        }
      y++;
      }
    y = 0;
    z++;
    }

//////////////////////////////////////////////////////////////////////////
  if ( numbounds == 0 ) {
    vtkGenericWarningMacro(<< "Execute: no bounding edge voxel detected!");
    self->SetPurifyError(-1);
  }
  
//////////////////////////////////////////////////////////////////////////
  long xstart, ystart, zstart, xend, yend, zend, numvox, numvox_max = 0;
  long xi, yi, zi;

  while ( numbounds > 0 )
    {
    while ( numbounds > 0 )
      {
      numbounds--;
      x = xbound[numbounds];
      y = ybound[numbounds];
      z = zbound[numbounds];
      
      outPtr[z*outInc2 + y*outInc1 + x*outInc0] = static_cast<IT>(253);
      xstart = max(x - 1, 0);
      xend   = min(x + 1, dims[0] - 1);
      ystart = max(y - 1, 0);
      yend   = min(y + 1, dims[1] - 1);
      zstart = max(z - 1, 0);
      zend   = min(z + 1, dims[2] - 1);
  
      for ( zi = zstart; zi <= zend; zi++ )
        {
        for ( yi = ystart; yi <= yend; yi++ )
          {
          for ( xi = xstart; xi <= xend; xi++ )
            {
            if ( outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] == static_cast<IT>(255) )
              {
              outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] = static_cast<IT>(254);
              xbound[numbounds] = xi;
              ybound[numbounds] = yi;
              zbound[numbounds] = zi;
              numbounds++;
              }
            }
          }
        }
      }
    numvox = 0;
    for (zi = 0; zi < dims[2]; zi++) 
      for (yi = 0; yi < dims[1]; yi++)
        for (xi = 0; xi < dims[0]; xi++)
        {
        if ( outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] == static_cast<IT>(255) )
          outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] = 0;
        if ( outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] == static_cast<IT>(253) )
          {
          outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] = static_cast<IT>(255);
          numvox++;
          }
        }
    
    if ( numvox > numvox_max )
      {
      numvox_max = numvox;
      index = 0;
      for (zi = 0; zi < dims[2]; zi++) 
        for (yi = 0; yi < dims[1]; yi++)
          for (xi = 0; xi < dims[0]; xi++)
            pure[index++] = outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0];
      }

    index = 0;
    for (zi = 0; zi < dims[2]; zi++) 
      for (yi = 0; yi < dims[1]; yi++)
        for (xi = 0; xi < dims[0]; xi++)
	{
          if (outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] == static_cast<IT>(255))
          {
            outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] = 0;
            scrap[index] = 0;
          }
	  if (outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] == 0)
            outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] = scrap[index];
	  index++;
	}

////////////////////////////////////////////////////////////////////////

  // search for first non-zero value on first edge of cube
  numbounds = 0;
  x = y = z = 0;
  while ( ( y < dims[1] ) && ( numbounds == 0 ) )
    {
    while ( ( x < dims[0] ) && ( numbounds == 0 ) )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == static_cast<IT>(255) )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = static_cast<IT>(254);
        xbound[0] = x; ybound[0] = y; zbound[0] = z;
        numbounds = 1;
        }
      x++;
      }
    x = 0;
    y++;
    }
  
  // search for first non-zero value on second edge of cube
  x = y = 0; z = dims[2] - 1;
  while ( ( y < dims[1] ) && ( numbounds == 0 ) )
    {
    while ( ( x < dims[0] ) && ( numbounds == 0 ) )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == static_cast<IT>(255) )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = static_cast<IT>(254);
        xbound[0] = x; ybound[0] = y; zbound[0] = z;
        numbounds = 1;
        }
      x++;
      }
    x = 0;
    y++;
    }

  // search for first non-zero value on third edge of cube
  x = z = y = 0; 
  while ( ( z < dims[2] ) && ( numbounds == 0 ) )
    {
    while ( ( x < dims[0] ) && ( numbounds == 0 ) )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == static_cast<IT>(255) )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = static_cast<IT>(254);
        xbound[0] = x; ybound[0] = y; zbound[0] = z;
        numbounds = 1;
        }
      x++;
      }
    x = 0;
    z++;
    }

  // search for first non-zero value on fourth edge of cube
  x = z = 0; y = dims[1] - 1; 
  while ( ( z < dims[2] ) && ( numbounds == 0 ) )
    {
    while ( ( x < dims[0] ) && ( numbounds == 0 ) )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == static_cast<IT>(255) )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = static_cast<IT>(254);
        xbound[0] = x; ybound[0] = y; zbound[0] = z;
        numbounds = 1;
        }
      x++;
      }
    x = 0;
    z++;
    }

  // search for first non-zero value on fifth edge of cube
  x = z = y = 0; 
  while ( ( z < dims[2] ) && ( numbounds == 0 ) )
    {
    while ( ( y < dims[1] ) && ( numbounds == 0 ) )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == static_cast<IT>(255) )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = static_cast<IT>(254);
        xbound[0] = x; ybound[0] = y; zbound[0] = z;
        numbounds = 1;
        }
      y++;
      }
    y = 0;
    z++;
    }

  // search for first non-zero value on sixth edge of cube
  z = y = 0; x = dims[0] - 1; 
  while ( ( z < dims[2] ) && ( numbounds == 0 ) )
    {
    while ( ( y < dims[1] ) && ( numbounds == 0 ) )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == static_cast<IT>(255) )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = static_cast<IT>(254);
        xbound[0] = x; ybound[0] = y; zbound[0] = z;
        numbounds = 1;
        }
      y++;
      }
    y = 0;
    z++;
    }
    }   
////////////////////////////////////////////////////////////////////////

  index = 0;
  for (zi = 0; zi < dims[2]; zi++) 
    for (yi = 0; yi < dims[1]; yi++)
      for (xi = 0; xi < dims[0]; xi++)
        outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] = pure[index++];
  
  numbounds = 0;
  z = 0;
  for ( y = 0; y < dims[1]; y++ )
    {
    for ( x = 0; x < dims[0]; x++ )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == 0 )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = 1;
        xbound[numbounds] = x;
        ybound[numbounds] = y;
        zbound[numbounds] = z;
        numbounds++;
        }
      }
    }

  z = dims[2] - 1;
  for ( y = 0; y < dims[1]; y++ )
    {
    for ( x = 0; x < dims[0]; x++ )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == 0 )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = 1;
        xbound[numbounds] = x;
        ybound[numbounds] = y;
        zbound[numbounds] = z;
        numbounds++;
        }
      }
    }

  y = 0;
  for ( z = 0; z < dims[2]; z++ )
    {
    for ( x = 0; x < dims[0]; x++ )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == 0 )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = 1;
        xbound[numbounds] = x;
        ybound[numbounds] = y;
        zbound[numbounds] = z;
        numbounds++;
        }
      }
    }


  y = dims[1] - 1;
  for ( z = 0; z < dims[2]; z++ )
    {
    for ( x = 0; x < dims[0]; x++ )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == 0 )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = 1;
        xbound[numbounds] = x;
        ybound[numbounds] = y;
        zbound[numbounds] = z;
        numbounds++;
        }
      }
    }

  x = 0;
  for ( z = 0; z < dims[2]; z++ )
    {
    for ( y = 0; y < dims[1]; y++ )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == 0 )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = 1;
        xbound[numbounds] = x;
        ybound[numbounds] = y;
        zbound[numbounds] = z;
        numbounds++;
        }
      }
    }

  x = dims[0] - 1;
  for ( z = 0; z < dims[2]; z++ )
    {
    for ( y = 0; y < dims[1]; y++ )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + x*outInc0] == 0 )
        {
        outPtr[z*outInc2 + y*outInc1 + x*outInc0] = 1;
        xbound[numbounds] = x;
        ybound[numbounds] = y;
        zbound[numbounds] = z;
        numbounds++;
        }
      }
    }

  while ( numbounds > 0 )
    {
    numbounds--;
    x = xbound[numbounds];
    y = ybound[numbounds];
    z = zbound[numbounds];
    outPtr[z*outInc2 + y*outInc1 + x*outInc0] = 2;
    if ( x > 0 )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + (x-1)*outInc0] == 0 )
        {
        outPtr[z*outInc2 + y*outInc1 + (x-1)*outInc0] = 1;
        xbound[numbounds] = x - 1;
        ybound[numbounds] = y;
        zbound[numbounds] = z;
        numbounds++;
        }
      }
    if ( x < dims[0] - 1 )
      {
      if ( outPtr[z*outInc2 + y*outInc1 + (x+1)*outInc0] == 0 )
        {
        outPtr[z*outInc2 + y*outInc1 + (x+1)*outInc0] = 1;
        xbound[numbounds] = x + 1;
        ybound[numbounds] = y;
        zbound[numbounds] = z;
        numbounds++;
        }
      }
    if ( y > 0 )
      {
      if ( outPtr[z*outInc2 + (y-1)*outInc1 + x*outInc0] == 0 )
        {
        outPtr[z*outInc2 + (y-1)*outInc1 + x*outInc0] = 1;
        xbound[numbounds] = x;
        ybound[numbounds] = y - 1;
        zbound[numbounds] = z;
        numbounds++;
        }
      }
    if ( y < dims[1] - 1 )
      {
      if ( outPtr[z*outInc2 + (y+1)*outInc1 + x*outInc0] == 0 )
        {
        outPtr[z*outInc2 + (y+1)*outInc1 + x*outInc0] = 1;
        xbound[numbounds] = x;
        ybound[numbounds] = y + 1;
        zbound[numbounds] = z;
        numbounds++;
        }
      }
    if ( z > 0 )
      {
      if ( outPtr[(z-1)*outInc2 + y*outInc1 + x*outInc0] == 0 )
        {
        outPtr[(z-1)*outInc2 + y*outInc1 + x*outInc0] = 1;
        xbound[numbounds] = x;
        ybound[numbounds] = y;
        zbound[numbounds] = z - 1;
        numbounds++;
        }
      }
    if ( z < dims[2] - 1 )
      {
      if ( outPtr[(z+1)*outInc2 + y*outInc1 + x*outInc0] == 0 )
        {
        outPtr[(z+1)*outInc2 + y*outInc1 + x*outInc0] = 1;
        xbound[numbounds] = x;
        ybound[numbounds] = y;
        zbound[numbounds] = z + 1;
        numbounds++;
        }
      }
    }

  for (zi = 0; zi < dims[2]; zi++) 
    for (yi = 0; yi < dims[1]; yi++)
      for (xi = 0; xi < dims[0]; xi++)
      {
        if ((outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] == 0) || (outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] == static_cast<IT>(255)))
	  outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] = 1;
        if (outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] == 2)
	  outPtr[zi*outInc2 + yi*outInc1 + xi*outInc0] = 0;
      }

//////////////////////////////////////////////////////////////////////////
  // free arrays
  delete [] scrap;
  delete [] pure;
  delete [] xbound;
  delete [] ybound;
  delete [] zbound;
}

void vtkImagePurify::SimpleExecute(vtkImageData* input,
                                                vtkImageData* output)
{

  void* inPtr = input->GetScalarPointer();
  void* outPtr = output->GetScalarPointer();

  switch(output->GetScalarType())
    {
    // This is simple a #define for a big case list. It handles
    // all data types vtk can handle.
    vtkTemplateMacro(vtkImagePurifyExecute(this, input, output,
                      static_cast<VTK_TT *>(inPtr), static_cast<VTK_TT *>(outPtr)));
    default:
      vtkGenericWarningMacro("Execute: Unknown input ScalarType");
      return;
    }
}

//----------------------------------------------------------------------------
// Description:
// PrintSelf function ...
void vtkImagePurify::PrintSelf(ostream& os, vtkIndent indent)
{
  vtkSimpleImageToImageFilter::PrintSelf(os,indent);
  os << indent << "Threshold: " << this->Threshold << "\n";
  os << indent << "Error value: " << this->PurifyError << "\n";
}
