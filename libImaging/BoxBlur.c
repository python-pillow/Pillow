#include "Python.h"
#include "Imaging.h"


Imaging
HorizontalBoxBlur32(Imaging im, Imaging imOut, int radius)
{
    ImagingSectionCookie cookie;

    int x, y, pix, offset;
    int acc[4];

    typedef UINT8 pixel[4];
    pixel *line;

    int window = radius * 2 + 1;

    ImagingSectionEnter(&cookie);

    for (y = 0; y < im->ysize; y++) {
        line = (pixel *) im->image32[y];
        for (x = 0; x < im->xsize; x++) {
            acc[0] = acc[1] = acc[2] = acc[3] = 0;
            for (pix = x - radius; pix <= x + radius; pix++) {
                offset = pix;
                if (pix < 0) {
                    offset = 0;
                } else if (pix >= im->xsize) {
                    offset = im->xsize - 1;
                }
                acc[0] += line[offset][0];
                acc[1] += line[offset][1];
                acc[2] += line[offset][2];
                acc[3] += line[offset][3];
            }

            imOut->image32[y][x] =
                (UINT8)(acc[0] / window) | (UINT8)(acc[1] / window) << 8 |
                (UINT8)(acc[2] / window) << 16 | (UINT8)(acc[3] / window) << 24;
        }
    }

    ImagingSectionLeave(&cookie);

    return imOut;
}


Imaging
ImagingBoxBlur(Imaging im, Imaging imOut, int radius)
{
    HorizontalBoxBlur32(im, imOut, radius);
    return imOut;
}
