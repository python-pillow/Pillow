#include "Imaging.h"

#include <math.h>

#define ROUND_UP(f) ((int) ((f) >= 0.0 ? (f) + 0.5F : (f) - 0.5F))


Imaging
ImagingReduce(Imaging imIn, int xscale, int yscale)
{
    Imaging imOut = NULL;

    imOut = ImagingNewDirty(imIn->mode, imIn->xsize, imIn->ysize);

    return imOut;
}
