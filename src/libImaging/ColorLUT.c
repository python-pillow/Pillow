#include "Imaging.h"
#include <math.h>


/* 8 bits for result. Table can overflow [0, 1.0] range,
   so we need extra bits for overflow and negative values.
   NOTE: This value should be the same as in _imaging/_prepare_lut_table() */
#define PRECISION_BITS (16 - 8 - 2)
#define PRECISION_ROUNDING (1<<(PRECISION_BITS-1))


UINT8 _lookups2[1024] = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
    32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
    48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
    64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
    80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95,
    96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111,
    112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127,
    128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143,
    144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,
    160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175,
    176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191,
    192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207,
    208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223,
    224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239,
    240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
};

UINT8 *lookups2 = &_lookups2[512];


static inline UINT8 clip8(int in)
{
    return lookups2[(in + PRECISION_ROUNDING) >> PRECISION_BITS];
}


static inline void
interpolate3(INT16 out[3], const INT16 a[3], const INT16 b[3], INT16 shift)
{
    out[0] = (a[0] * (0x1000-shift) + b[0] * shift + (1<<11)) >> 12;
    out[1] = (a[1] * (0x1000-shift) + b[1] * shift + (1<<11)) >> 12;
    out[2] = (a[2] * (0x1000-shift) + b[2] * shift + (1<<11)) >> 12;
}

static inline void
interpolate4(INT16 out[4], const INT16 a[4], const INT16 b[4], INT16 shift)
{
    out[0] = (a[0] * (0x1000-shift) + b[0] * shift + (1<<11)) >> 12;
    out[1] = (a[1] * (0x1000-shift) + b[1] * shift + (1<<11)) >> 12;
    out[2] = (a[2] * (0x1000-shift) + b[2] * shift + (1<<11)) >> 12;
    out[3] = (a[3] * (0x1000-shift) + b[3] * shift + (1<<11)) >> 12;
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
    /* The fractions are a way to avoid overflow.
       For every pixel, we interpolate 8 elements from the table:
       current and +1 for every dimension and they combinations.
       If we hit the upper cells from the table,
       +1 cells will be outside of the table.
       With this compensation we never hit the upper cells
       but this also doesn't introduce any noticable difference. */
    float scale1D = (size1D - 1) / (255.0002);
    float scale2D = (size2D - 1) / (255.0002);
    float scale3D = (size3D - 1) / (255.0002);
    int size1D_2D = size1D * size2D;
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
        UINT8* rowIn = (UINT8 *)imIn->image[y];
        UINT8* rowOut = (UINT8 *)imOut->image[y];
        for (x = 0; x < imOut->xsize; x++) {
            float scaled1D = rowIn[x*4 + 0] * scale1D;
            float scaled2D = rowIn[x*4 + 1] * scale2D;
            float scaled3D = rowIn[x*4 + 2] * scale3D;
            int index1D = (int) scaled1D;
            int index2D = (int) scaled2D;
            int index3D = (int) scaled3D;
            INT16 shift1D = (scaled1D - index1D) * 0x1000 + 0.5;
            INT16 shift2D = (scaled2D - index2D) * 0x1000 + 0.5;
            INT16 shift3D = (scaled3D - index3D) * 0x1000 + 0.5;
            int idx = table3D_index3(index1D, index2D, index3D, size1D, size1D_2D);
            INT16 result[4], left[4], right[4];
            INT16 leftleft[4], leftright[4], rightleft[4], rightright[4];

            if (table_channels == 3) {
                interpolate3(leftleft, &table[idx + 0], &table[idx + 3], shift1D);
                interpolate3(leftright, &table[idx + size1D*3],
                             &table[idx + size1D*3 + 3], shift1D);
                interpolate3(left, leftleft, leftright, shift2D);

                interpolate3(rightleft, &table[idx + size1D_2D*3],
                             &table[idx + size1D_2D*3 + 3], shift1D);
                interpolate3(rightright, &table[idx + size1D_2D*3 + size1D*3],
                             &table[idx + size1D_2D*3 + size1D*3 + 3], shift1D);
                interpolate3(right, rightleft, rightright, shift2D);

                interpolate3(result, left, right, shift3D);

                rowOut[x*4 + 0] = clip8(result[0]);
                rowOut[x*4 + 1] = clip8(result[1]);
                rowOut[x*4 + 2] = clip8(result[2]);
                rowOut[x*4 + 3] = rowIn[x*4 + 3];
            }

            if (table_channels == 4) {
                interpolate4(leftleft, &table[idx + 0], &table[idx + 4], shift1D);
                interpolate4(leftright, &table[idx + size1D*4],
                             &table[idx + size1D*4 + 4], shift1D);
                interpolate4(left, leftleft, leftright, shift2D);

                interpolate4(rightleft, &table[idx + size1D_2D*4],
                             &table[idx + size1D_2D*4 + 4], shift1D);
                interpolate4(rightright, &table[idx + size1D_2D*4 + size1D*4],
                             &table[idx + size1D_2D*4 + size1D*4 + 4], shift1D);
                interpolate4(right, rightleft, rightright, shift2D);

                interpolate4(result, left, right, shift3D);

                rowOut[x*4 + 0] = clip8(result[0]);
                rowOut[x*4 + 1] = clip8(result[1]);
                rowOut[x*4 + 2] = clip8(result[2]);
                rowOut[x*4 + 3] = clip8(result[3]);
            }
        }
    }

    return imOut;
}
