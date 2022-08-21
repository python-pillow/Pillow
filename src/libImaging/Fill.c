/*
 * The Python Imaging Library
 * $Id$
 *
 * fill image with constant pixel value
 *
 * history:
 * 95-11-26 fl moved from Imaging.c
 * 96-05-17 fl added radial fill, renamed wedge to linear
 * 98-06-23 fl changed ImageFill signature
 *
 * Copyright (c) Secret Labs AB 1997-98.  All rights reserved.
 * Copyright (c) Fredrik Lundh 1995-96.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

#include "math.h"

Imaging
ImagingFill(Imaging im, const void *colour) {
    int x, y;
    ImagingSectionCookie cookie;

    // Check if every byte in the given color is the same.
    // If they are, we can use memset.
    int allSame = 1;
    const UINT8 b = *(UINT8 *)colour;
    for (x = 1; x < im->pixelsize; ++x) {
        if (((UINT8 *)colour)[x] != b) {
            allSame = 0;
            break;
        }
    }

    ImagingSectionEnter(&cookie);
    if (allSame) {
        for (y = 0; y < im->ysize; ++y) {
            memset(im->image[y], b, im->linesize);
        }
    } else if (im->type == IMAGING_TYPE_SPECIAL) {
        ImagingAccess access = ImagingAccessNew(im);
        if (access) {
            for (y = 0; y < im->ysize; ++y) {
                for (x = 0; x < im->xsize; ++x) {
                    access->put_pixel(im, x, y, colour);
                }
            }
            ImagingAccessDelete(im, access);
        } else {
            for (y = 0; y < im->ysize; ++y) {
                memset(im->image[y], 0, im->linesize);
            }
        }
    } else {
        for (y = 0; y < im->ysize; ++y) {
            UINT8 *out = (UINT8 *)im->image[y];
            for (x = 0; x < im->xsize; ++x) {
                memcpy(out + x * im->pixelsize, colour, im->pixelsize);
            }
        }
    }
    ImagingSectionLeave(&cookie);

    return im;
}

Imaging
ImagingFillLinearGradient(const char *mode) {
    Imaging im;

    if (strcmp(mode, "P") == 0 || strcmp(mode, "PA") == 0) {
        Imaging imTemp = ImagingFillLinearGradient("L");
        im = ImagingConvert(imTemp, mode, NULL, 0);
        ImagingDelete(imTemp);
        return im;
    }

    const int size = 256;
    im = ImagingNewDirty(mode, size, size);
    if (!im) {
        return NULL;
    }

    int y, x;
    switch (im->type) {
        case IMAGING_TYPE_UINT8:
            if (strcmp(mode, "1") == 0) {
                for (y = 0; y < size; ++y) {
                    memset(im->image[y], y < 128 ? 0 : 255, size);
                }
            } else if (strcmp(mode, "LA") == 0 || strcmp(mode, "La") == 0) {
                for (y = 0; y < size; ++y) {
                    UINT8 *out = (UINT8 *)im->image[y];
                    for (x = 0; x < size; ++x) {
                        *out++ = y;
                        *out++ = 255;
                    }
                }
            } else if (strcmp(mode, "RGBA") == 0 || strcmp(mode, "RGBa") == 0 || strcmp(mode, "RGBX") == 0) {
                for (y = 0; y < size; ++y) {
                    UINT8 *out = (UINT8 *)im->image[y];
                    for (x = 0; x < size; ++x) {
                        memset(out + x * 4, y, 3);
                        out[x * 4 + 3] = 255;
                    }
                }
            } else if (strcmp(mode, "CMYK") == 0) {
                for (y = 0; y < size; ++y) {
                    UINT8 *out = (UINT8 *)im->image[y];
                    for (x = 0; x < size; ++x) {
                        memset(out + x * 4, 0, 3);
                        out[x * 4 + 3] = ~(UINT8)y;
                    }
                }
            } else if (strcmp(mode, "YCbCr") == 0) {
                for (y = 0; y < size; ++y) {
                    UINT8 *out = (UINT8 *)im->image[y];
                    for (x = 0; x < size; ++x) {
                        *out++ = y;
                        *out++ = 128;
                        *out++ = 128;
                        *out++ = 255;
                    }
                }
            } else if (strcmp(mode, "HSV") == 0) {
                for (y = 0; y < size; ++y) {
                    UINT8 *out = (UINT8 *)im->image[y];
                    for (x = 0; x < size; ++x) {
                        *out++ = 0;
                        *out++ = 0;
                        *out++ = y;
                        *out++ = 255;
                    }
                }
            } else {
                for (y = 0; y < size; ++y) {
                    memset(im->image[y], y, im->linesize);
                }
            }
            break;
        case IMAGING_TYPE_INT32:
            for (y = 0; y < size; ++y) {
                for (x = 0; x < size; ++x) {
                    IMAGING_PIXEL_INT32(im, x, y) = y;
                }
            }
            break;
        case IMAGING_TYPE_FLOAT32:
            for (y = 0; y < size; ++y) {
                for (x = 0; x < size; ++x) {
                    IMAGING_PIXEL_FLOAT32(im, x, y) = y;
                }
            }
            break;
        case IMAGING_TYPE_SPECIAL: {
            ImagingAccess access = ImagingAccessNew(im);
            if (access) {
                for (y = 0; y < im->ysize; ++y) {
                    for (x = 0; x < im->xsize; ++x) {
                        access->put_pixel(im, x, y, &y);
                    }
                }
                ImagingAccessDelete(im, access);
            } else {
                ImagingDelete(im);
                return (Imaging)ImagingError_ModeError();
            }
            break;
        }
    }

    return im;
}

#define CALC_RADIAL_COLOUR(c, x, y) c = ((int)sqrt(\
(double)((x - 128) * (x - 128) + (y - 128) * (y - 128)) * 2.0));\
if (c >= 255) {c = 255;}
Imaging
ImagingFillRadialGradient(const char *mode) {
    Imaging im;

    if (strcmp(mode, "P") == 0 || strcmp(mode, "PA") == 0) {
        Imaging imTemp = ImagingFillRadialGradient("L");
        im = ImagingConvert(imTemp, mode, NULL, 0);
        ImagingDelete(imTemp);
        return im;
    }

    const int size = 256;
    im = ImagingNewDirty(mode, size, size);
    if (!im) {
        return NULL;
    }

    int y, x, c;
    switch (im->type) {
        case IMAGING_TYPE_UINT8:
            if (strcmp(mode, "1") == 0) {
                for (y = 0; y < size; ++y) {
                    UINT8 *out = (UINT8 *)im->image[y];
                    for (x = 0; x < size; ++x) {
                        CALC_RADIAL_COLOUR(c, x, y)
                        out[x] = c < 128 ? 0 : 255;
                    }
                }
            } else if (strcmp(mode, "LA") == 0 || strcmp(mode, "La") == 0) {
                for (y = 0; y < size; ++y) {
                    UINT8 *out = (UINT8 *)im->image[y];
                    for (x = 0; x < size; ++x) {
                        CALC_RADIAL_COLOUR(c, x, y)
                        *out++ = c;
                        *out++ = 255;
                    }
                }
            } else if (strcmp(mode, "RGBA") == 0 || strcmp(mode, "RGBa") == 0 || strcmp(mode, "RGBX") == 0) {
                for (y = 0; y < size; ++y) {
                    UINT8 *out = (UINT8 *)im->image[y];
                    for (x = 0; x < size; ++x) {
                        CALC_RADIAL_COLOUR(c, x, y)
                        memset(out + x * 4, c, 3);
                        out[x * 4 + 3] = 255;
                    }
                }
            } else if (strcmp(mode, "CMYK") == 0) {
                for (y = 0; y < size; ++y) {
                    UINT8 *out = (UINT8 *)im->image[y];
                    for (x = 0; x < size; ++x) {
                        CALC_RADIAL_COLOUR(c, x, y)
                        memset(out + x * 4, 0, 3);
                        out[x * 4 + 3] = ~(UINT8)c;
                    }
                }
            } else if (strcmp(mode, "YCbCr") == 0) {
                for (y = 0; y < size; ++y) {
                    UINT8 *out = (UINT8 *)im->image[y];
                    for (x = 0; x < size; ++x) {
                        CALC_RADIAL_COLOUR(c, x, y)
                        *out++ = c;
                        *out++ = 128;
                        *out++ = 128;
                        *out++ = 255;
                    }
                }
            } else if (strcmp(mode, "HSV") == 0) {
                for (y = 0; y < size; ++y) {
                    UINT8 *out = (UINT8 *)im->image[y];
                    for (x = 0; x < size; ++x) {
                        CALC_RADIAL_COLOUR(c, x, y)
                        *out++ = 0;
                        *out++ = 0;
                        *out++ = c;
                        *out++ = 255;
                    }
                }
            } else {
                for (y = 0; y < size; ++y) {
                    UINT8 *out = (UINT8 *)im->image[y];
                    for (x = 0; x < size; ++x) {
                        CALC_RADIAL_COLOUR(c, x, y)
                        memset(out + x * im->pixelsize, c, im->pixelsize);
                    }
                }
            }
            break;
        case IMAGING_TYPE_INT32:
            for (y = 0; y < size; ++y) {
                for (x = 0; x < size; ++x) {
                    CALC_RADIAL_COLOUR(c, x, y)
                    IMAGING_PIXEL_INT32(im, x, y) = c;
                }
            }
            break;
        case IMAGING_TYPE_FLOAT32:
            for (y = 0; y < size; ++y) {
                for (x = 0; x < size; ++x) {
                    CALC_RADIAL_COLOUR(c, x, y)
                    IMAGING_PIXEL_FLOAT32(im, x, y) = c;
                }
            }
            break;
        case IMAGING_TYPE_SPECIAL: {
            ImagingAccess access = ImagingAccessNew(im);
            if (access) {
                for (y = 0; y < im->ysize; ++y) {
                    for (x = 0; x < im->xsize; ++x) {
                        CALC_RADIAL_COLOUR(c, x, y)
                        access->put_pixel(im, x, y, &c);
                    }
                }
                ImagingAccessDelete(im, access);
            } else {
                ImagingDelete(im);
                return (Imaging)ImagingError_ModeError();
            }
            break;
        }
    }

    return im;
}
#undef CALC_RADIAL_COLOUR
