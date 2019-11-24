#include "Imaging.h"

#include <math.h>

#define ROUND_UP(f) ((int) ((f) >= 0.0 ? (f) + 0.5F : (f) - 0.5F))


void
ImagingReduce2x2(Imaging imOut, Imaging imIn)
{
    ImagingSectionCookie cookie;
    int x, y;
    int ss0, ss1, ss2, ss3;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / 2; y++) {
                UINT8 *line0 = (UINT8 *)imIn->image[y*2 + 0];
                UINT8 *line1 = (UINT8 *)imIn->image[y*2 + 1];
                if (imIn->bands == 2) {

                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / 2; x++) {
                        UINT32 v;
                        ss0 = line0[x*2*4 + 0] + line0[x*2*4 + 4] +
                              line1[x*2*4 + 0] + line1[x*2*4 + 4];
                        ss1 = line0[x*2*4 + 1] + line0[x*2*4 + 5] +
                              line1[x*2*4 + 1] + line1[x*2*4 + 5];
                        ss2 = line0[x*2*4 + 2] + line0[x*2*4 + 6] +
                              line1[x*2*4 + 2] + line1[x*2*4 + 6];
                        v = MAKE_UINT32((ss0 + 2) >> 2, (ss1 + 2) >> 2,
                                        (ss2 + 2) >> 2, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4

                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}


void
ImagingReduce4x4(Imaging imOut, Imaging imIn)
{
    ImagingSectionCookie cookie;
    int x, y;
    int ss0, ss1, ss2, ss3;

    ImagingSectionEnter(&cookie);
    if (imIn->image8) {

    } else {
        switch(imIn->type) {
        case IMAGING_TYPE_UINT8:
            for (y = 0; y < imIn->ysize / 4; y++) {
                UINT8 *line0 = (UINT8 *)imIn->image[y*4 + 0];
                UINT8 *line1 = (UINT8 *)imIn->image[y*4 + 1];
                UINT8 *line2 = (UINT8 *)imIn->image[y*4 + 2];
                UINT8 *line3 = (UINT8 *)imIn->image[y*4 + 3];
                if (imIn->bands == 2) {

                } else if (imIn->bands == 3) {
                    for (x = 0; x < imIn->xsize / 4; x++) {
                        UINT32 v;
                        ss0 = line0[x*4*4 + 0] + line0[x*4*4 + 4] + line0[x*4*4 + 8] + line0[x*4*4 + 12] +
                              line1[x*4*4 + 0] + line1[x*4*4 + 4] + line1[x*4*4 + 8] + line1[x*4*4 + 12] +
                              line2[x*4*4 + 0] + line2[x*4*4 + 4] + line2[x*4*4 + 8] + line2[x*4*4 + 12] +
                              line3[x*4*4 + 0] + line3[x*4*4 + 4] + line3[x*4*4 + 8] + line3[x*4*4 + 12];
                        ss1 = line0[x*4*4 + 1] + line0[x*4*4 + 5] + line0[x*4*4 + 9] + line0[x*4*4 + 13] +
                              line1[x*4*4 + 1] + line1[x*4*4 + 5] + line1[x*4*4 + 9] + line1[x*4*4 + 13] +
                              line2[x*4*4 + 1] + line2[x*4*4 + 5] + line2[x*4*4 + 9] + line2[x*4*4 + 13] +
                              line3[x*4*4 + 1] + line3[x*4*4 + 5] + line3[x*4*4 + 9] + line3[x*4*4 + 13];
                        ss2 = line0[x*4*4 + 2] + line0[x*4*4 + 6] + line0[x*4*4 + 10] + line0[x*4*4 + 14] +
                              line1[x*4*4 + 2] + line1[x*4*4 + 6] + line1[x*4*4 + 10] + line1[x*4*4 + 14] +
                              line2[x*4*4 + 2] + line2[x*4*4 + 6] + line2[x*4*4 + 10] + line2[x*4*4 + 14] +
                              line3[x*4*4 + 2] + line3[x*4*4 + 6] + line3[x*4*4 + 10] + line3[x*4*4 + 14];
                        v = MAKE_UINT32((ss0 + 8) >> 4, (ss1 + 8) >> 4,
                                        (ss2 + 8) >> 4, 0);
                        memcpy(imOut->image[y] + x * sizeof(v), &v, sizeof(v));
                    }
                } else {  // bands == 4

                }
            }
            break;

        case IMAGING_TYPE_INT32:
            break;

        case IMAGING_TYPE_FLOAT32:
            break;
        }
    }
    ImagingSectionLeave(&cookie);
}


Imaging
ImagingReduce(Imaging imIn, int xscale, int yscale)
{
    Imaging imOut = NULL;

    imOut = ImagingNewDirty(imIn->mode,
                            (imIn->xsize + xscale - 1) / xscale,
                            (imIn->ysize + yscale - 1) / yscale);

    if (xscale == 2 && yscale == 2) {
        ImagingReduce2x2(imOut, imIn);
    } else if (xscale == 4 && yscale == 4) {
        ImagingReduce4x4(imOut, imIn);
    }


    return imOut;
}
