/*=========================================================================
This source has no copyright.  It is intended to be copied by users
wishing to create their own VTK classes locally.
=========================================================================*/
#ifndef __Configure_h
#define __Configure_h

#if 1
# define MicroView_SHARED
#endif

#if defined(_MSC_VER) && defined(MicroView_SHARED)
# pragma warning ( disable : 4275 )
#endif

#if defined(_WIN32) && defined(MicroView_SHARED)
# define VTK_MicroView_EXPORT __declspec( dllexport ) 
#else
# define VTK_MicroView_EXPORT
#endif

#endif // __MicroViewConfigure_h
