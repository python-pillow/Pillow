#include "Imaging.h"
#include <math.h>


#define ROUND_UP(f) ((int) ((f) >= 0.0 ? (f) + 0.5F : (f) - 0.5F))


/* 8 bits for result. Table can overflow [0, 1.0] range,
   so we need extra bits for overflow and negative values. */
#define PRECISION_BITS (16 - 8 - 2)


static inline void
interpolate3(INT16 out[3], const INT16 a[3], const INT16 b[3], float shift)
{
    out[0] = a[0] * (1-shift) + b[0] * shift;
    out[1] = a[1] * (1-shift) + b[1] * shift;
    out[2] = a[2] * (1-shift) + b[2] * shift;
}

static inline void
interpolate4(INT16 out[3], const INT16 a[3], const INT16 b[3], float shift)
{
    out[0] = a[0] * (1-shift) + b[0] * shift;
    out[1] = a[1] * (1-shift) + b[1] * shift;
    out[2] = a[2] * (1-shift) + b[2] * shift;
    out[3] = a[3] * (1-shift) + b[3] * shift;
}

static inline int
table3D_index3(int index1D, int index2D, int index3D,
               int size1D, int size1D_2D)
{
    return (index1D + index2D * size1D + index3D * size1D_2D) * 3;
}

static inline int
table3D_index4(int index1D, int index2D, int index3D,
               int size1D, int size1D_2D)
{
    return (index1D + index2D * size1D + index3D * size1D_2D) * 4;
}

/*
 Transforms colors of imIn using provided 3D look-up table
 and puts the result in imOut. Returns imOut on sucess or 0 on error.
 
 imOut, imIn — images, should be the same size and may be the same image.
    Should have 3 or 4 channels.
 table_channels — number of channels in the look-up table, 3 or 4.
    Should be less or equal than number of channels in imOut image;
 size1D, size_2D and size3D — dimensions of provided table;
 table — flatten table,
    array with table_channels × size1D × size2D × size3D elements,
    where channels are changed first, then 1D, then​ 2D, then 3D.
    Each element is signed 16-bit int where 0 is lowest output value
    and 255 << PRECISION_BITS (16320) is highest value.
*/ 
Imaging
ImagingColorLUT3D_linear(Imaging imOut, Imaging imIn, int table_channels,
                         int size1D, int size2D, int size3D,
                         INT16* table)
{
    int size1D_2D = size1D * size2D;
    float scale1D = (size1D - 1) / 255.0;
    float scale2D = (size2D - 1) / 255.0;
    float scale3D = (size3D - 1) / 255.0;
    int x, y;

    if (table_channels < 3 || table_channels > 4) {
        PyErr_SetString(PyExc_ValueError, "table_channels could be 3 or 4");
        return NULL;
    }

    if (imIn->type != IMAGING_TYPE_UINT8 ||
        imOut->type != IMAGING_TYPE_UINT8 ||
        imIn->bands < 3 ||
        imOut->bands < table_channels
    ) {
        return (Imaging) ImagingError_ModeError();
    }

    /* In case we have one extra band in imOut and don't have in imIn.*/
    if (imOut->bands > table_channels && imOut->bands > imIn->bands) {
        return (Imaging) ImagingError_ModeError();
    }

    for (y = 0; y < imOut->ysize; y++) {
        UINT8 *rowIn = (UINT8 *)imIn->image[y];
        UINT8 *rowOut = (UINT8 *)imIn->image[y];
        for (x = 0; x < imOut->xsize; x++) {
            float scaled1D = rowIn[x*4 + 0] * scale1D;
            float scaled2D = rowIn[x*4 + 1] * scale2D;
            float scaled3D = rowIn[x*4 + 2] * scale3D;
            int index1D = (int) scaled1D;
            int index2D = (int) scaled2D;
            int index3D = (int) scaled3D;
            float shift1D = scaled1D - index1D;
            float shift2D = scaled2D - index2D;
            float shift3D = scaled3D - index3D;
            
        }
    }

    return imOut;
}
