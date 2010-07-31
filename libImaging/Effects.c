/* 
 * The Python Imaging Library
 * $Id$
 *
 * various special effects and image generators
 *
 * history:
 * 1997-05-21 fl   Just for fun
 * 1997-06-05 fl   Added mandelbrot generator
 * 2003-05-24 fl   Added perlin_turbulence generator (in progress)
 *
 * Copyright (c) 1997-2003 by Fredrik Lundh.
 * Copyright (c) 1997 by Secret Labs AB.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Imaging.h"

#include <math.h>

Imaging
ImagingEffectMandelbrot(int xsize, int ysize, double extent[4], int quality)
{
    /* Generate a Mandelbrot set covering the given extent */

    Imaging im;
    int x, y, k;
    double width, height;
    double x1, y1, xi2, yi2, cr, ci, radius;
    double dr, di;

    /* Check arguments */
    width  = extent[2] - extent[0];
    height = extent[3] - extent[1];
    if (width < 0.0 || height < 0.0 || quality < 2)
        return (Imaging) ImagingError_ValueError(NULL);

    im = ImagingNew("L", xsize, ysize);
    if (!im)
        return NULL;

    dr = width/(xsize-1);
    di = height/(ysize-1);

    radius = 100.0;

    for (y = 0; y < ysize; y++) {
        UINT8* buf = im->image8[y];
	for (x = 0; x < xsize; x++) {
	    x1 = y1 = xi2 = yi2 = 0.0;
	    cr = x*dr + extent[0];
	    ci = y*di + extent[1];
	    for (k = 1;; k++) {
		y1 = 2*x1*y1 + ci;
		x1 = xi2 - yi2 + cr;
		xi2 = x1*x1;
		yi2 = y1*y1;
		if ((xi2 + yi2) > radius) {
		    buf[x] = k*255/quality;
		    break;
		}
		if (k > quality) {
		    buf[x] = 0;
		    break;
		}
	    }
	}
    }
    return im;
}

Imaging
ImagingEffectNoise(int xsize, int ysize, float sigma)
{
    /* Generate gaussian noise centered around 128 */

    Imaging imOut;
    int x, y;
    int nextok;
    double this, next;

    imOut = ImagingNew("L", xsize, ysize);
    if (!imOut)
	return NULL;

    next = 0.0;
    nextok = 0;

    for (y = 0; y < imOut->ysize; y++) {
        UINT8* out = imOut->image8[y];
	for (x = 0; x < imOut->xsize; x++) {
            if (nextok) {
                this = next;
                nextok = 0;
            } else {
                /* after numerical recepies */
                double v1, v2, radius, factor;
                do {
                    v1 = rand()*(2.0/32767.0) - 1.0;
                    v2 = rand()*(2.0/32767.0) - 1.0;
                    radius= v1*v1 + v2*v2;
                } while (radius >= 1.0);
                factor = sqrt(-2.0*log(radius)/radius);
                this = factor * v1;
                next = factor * v2;
            }
            out[x] = (unsigned char) (128 + sigma * this);
        }
    }

    return imOut;
}

Imaging
ImagingEffectPerlinTurbulence(int xsize, int ysize)
{
    /* Perlin turbulence (In progress) */

    return NULL;
}

Imaging
ImagingEffectSpread(Imaging imIn, int distance)
{
    /* Randomly spread pixels in an image */

    Imaging imOut;
    int x, y;

    imOut = ImagingNew(imIn->mode, imIn->xsize, imIn->ysize);

    if (!imOut)
	return NULL;

#define	SPREAD(type, image)\
    for (y = 0; y < imIn->ysize; y++)\
	for (x = 0; x < imIn->xsize; x++) {\
            int xx = x + (rand() % distance) - distance/2;\
            int yy = y + (rand() % distance) - distance/2;\
            if (xx >= 0 && xx < imIn->xsize && yy >= 0 && yy < imIn->ysize) {\
                imOut->image[yy][xx] = imIn->image[y][x];\
                imOut->image[y][x]   = imIn->image[yy][xx];\
            } else\
                imOut->image[y][x]   = imIn->image[y][x];\
        }

    if (imIn->image8) {
	SPREAD(UINT8, image8);
    } else {
	SPREAD(INT32, image32);
    }

    ImagingCopyInfo(imOut, imIn);

    return imOut;
}

/* -------------------------------------------------------------------- */
/* Taken from the "C" code in the W3C SVG specification.  Translated
   to C89 by Fredrik Lundh */

#if 0

/* Produces results in the range [1, 2**31 - 2].
Algorithm is: r = (a * r) mod m
where a = 16807 and m = 2**31 - 1 = 2147483647
See [Park & Miller], CACM vol. 31 no. 10 p. 1195, Oct. 1988
To test: the algorithm should produce the result 1043618065
as the 10,000th generated number if the original seed is 1.
*/
#define RAND_m 2147483647 /* 2**31 - 1 */
#define RAND_a 16807 /* 7**5; primitive root of m */
#define RAND_q 127773 /* m / a */
#define RAND_r 2836 /* m % a */

static long
perlin_setup_seed(long lSeed)
{
  if (lSeed <= 0) lSeed = -(lSeed % (RAND_m - 1)) + 1;
  if (lSeed > RAND_m - 1) lSeed = RAND_m - 1;
  return lSeed;
}

static long
perlin_random(long lSeed)
{
  long result;
  result = RAND_a * (lSeed % RAND_q) - RAND_r * (lSeed / RAND_q);
  if (result <= 0) result += RAND_m;
  return result;
}

#define BSize 0x100
#define BM 0xff
#define PerlinN 0x1000
#define NP 12 /* 2^PerlinN */
#define NM 0xfff
static int perlin_uLatticeSelector[BSize + BSize + 2];
static double perlin_fGradient[4][BSize + BSize + 2][2];
typedef struct
{
  int nWidth; /* How much to subtract to wrap for stitching. */
  int nHeight;
  int nWrapX; /* Minimum value to wrap. */
  int nWrapY;
} StitchInfo;

static void
perlin_init(long lSeed)
{
  double s;
  int i, j, k;
  lSeed = perlin_setup_seed(lSeed);
  for(k = 0; k < 4; k++)
  {
    for(i = 0; i < BSize; i++)
    {
      perlin_uLatticeSelector[i] = i;
      for (j = 0; j < 2; j++)
        perlin_fGradient[k][i][j] = (double)(((lSeed = perlin_random(lSeed)) % (BSize + BSize)) - BSize) / BSize;
      s = (double) (sqrt(perlin_fGradient[k][i][0] * perlin_fGradient[k][i][0] + perlin_fGradient[k][i][1] * perlin_fGradient[k][i][1]));
      perlin_fGradient[k][i][0] /= s;
      perlin_fGradient[k][i][1] /= s;
    }
  }
  while(--i)
  {
    k = perlin_uLatticeSelector[i];
    perlin_uLatticeSelector[i] = perlin_uLatticeSelector[j = (lSeed = perlin_random(lSeed)) % BSize];
    perlin_uLatticeSelector[j] = k;
  }
  for(i = 0; i < BSize + 2; i++)
  {
    perlin_uLatticeSelector[BSize + i] = perlin_uLatticeSelector[i];
    for(k = 0; k < 4; k++)
      for(j = 0; j < 2; j++)
        perlin_fGradient[k][BSize + i][j] = perlin_fGradient[k][i][j];
  }
}

#define s_curve(t) ( t * t * (3. - 2. * t) )
#define lerp(t, a, b) ( a + t * (b - a) )
static double
perlin_noise2(int nColorChannel, double vec[2], StitchInfo *pStitchInfo)
{
  int bx0, bx1, by0, by1, b00, b10, b01, b11;
  double rx0, rx1, ry0, ry1, *q, sx, sy, a, b, t, u, v;
  register int i, j;

  t = vec[0] + (double) PerlinN;
  bx0 = (int)t;
  bx1 = bx0+1;
  rx0 = t - (int)t;
  rx1 = rx0 - 1.0f;
  t = vec[1] + (double) PerlinN;
  by0 = (int)t;
  by1 = by0+1;
  ry0 = t - (int)t;
  ry1 = ry0 - 1.0f;

  /* If stitching, adjust lattice points accordingly. */
  if(pStitchInfo != NULL)
  {
    if(bx0 >= pStitchInfo->nWrapX)
      bx0 -= pStitchInfo->nWidth;
    if(bx1 >= pStitchInfo->nWrapX)
      bx1 -= pStitchInfo->nWidth;
    if(by0 >= pStitchInfo->nWrapY)
      by0 -= pStitchInfo->nHeight;
    if(by1 >= pStitchInfo->nWrapY)
      by1 -= pStitchInfo->nHeight;
  }

  bx0 &= BM;
  bx1 &= BM;
  by0 &= BM;
  by1 &= BM;

  i = perlin_uLatticeSelector[bx0];
  j = perlin_uLatticeSelector[bx1];
  b00 = perlin_uLatticeSelector[i + by0];
  b10 = perlin_uLatticeSelector[j + by0];
  b01 = perlin_uLatticeSelector[i + by1];
  b11 = perlin_uLatticeSelector[j + by1];
  sx = (double) (s_curve(rx0));
  sy = (double) (s_curve(ry0));
  q = perlin_fGradient[nColorChannel][b00]; u = rx0 * q[0] + ry0 * q[1];
  q = perlin_fGradient[nColorChannel][b10]; v = rx1 * q[0] + ry0 * q[1];
  a = lerp(sx, u, v);
  q = perlin_fGradient[nColorChannel][b01]; u = rx0 * q[0] + ry1 * q[1];
  q = perlin_fGradient[nColorChannel][b11]; v = rx1 * q[0] + ry1 * q[1];
  b = lerp(sx, u, v);
  return lerp(sy, a, b);
}

double
perlin_turbulence(
    int nColorChannel, double *point, double fBaseFreqX, double fBaseFreqY,
    int nNumOctaves, int bFractalSum, int bDoStitching,
    double fTileX, double fTileY, double fTileWidth, double fTileHeight)
{
  StitchInfo stitch;
  StitchInfo *pStitchInfo = NULL; /* Not stitching when NULL. */

  double fSum = 0.0f;
  double vec[2];
  double ratio = 1;

  int nOctave;

  vec[0] = point[0] * fBaseFreqX;
  vec[1] = point[1] * fBaseFreqY;

  /* Adjust the base frequencies if necessary for stitching. */
  if(bDoStitching)
  {
    /* When stitching tiled turbulence, the frequencies must be adjusted */
    /* so that the tile borders will be continuous. */
    if(fBaseFreqX != 0.0)
    {
      double fLoFreq = (double) (floor(fTileWidth * fBaseFreqX)) / fTileWidth;
      double fHiFreq = (double) (ceil(fTileWidth * fBaseFreqX)) / fTileWidth;
      if(fBaseFreqX / fLoFreq < fHiFreq / fBaseFreqX)
        fBaseFreqX = fLoFreq;
      else
        fBaseFreqX = fHiFreq;
    }

    if(fBaseFreqY != 0.0)
    {
      double fLoFreq = (double) (floor(fTileHeight * fBaseFreqY)) / fTileHeight;
      double fHiFreq = (double) (ceil(fTileHeight * fBaseFreqY)) / fTileHeight;
      if(fBaseFreqY / fLoFreq < fHiFreq / fBaseFreqY)
        fBaseFreqY = fLoFreq;
      else
        fBaseFreqY = fHiFreq;
    }

    /* Set up initial stitch values. */
    pStitchInfo = &stitch;
    stitch.nWidth = (int) (fTileWidth * fBaseFreqX + 0.5f);
    stitch.nWrapX = (int) (fTileX * fBaseFreqX + PerlinN + stitch.nWidth);
    stitch.nHeight = (int) (fTileHeight * fBaseFreqY + 0.5f);
    stitch.nWrapY = (int) (fTileY * fBaseFreqY + PerlinN + stitch.nHeight);
  }

  for(nOctave = 0; nOctave < nNumOctaves; nOctave++)
  {
    if(bFractalSum)
      fSum += (double) (perlin_noise2(nColorChannel, vec, pStitchInfo) / ratio);
    else
      fSum += (double) (fabs(perlin_noise2(nColorChannel, vec, pStitchInfo)) / ratio);

    vec[0] *= 2;
    vec[1] *= 2;
    ratio *= 2;

    if(pStitchInfo != NULL)
    {
        /* Update stitch values. Subtracting PerlinN before the multiplication and */
        /* adding it afterward simplifies to subtracting it once. */
      stitch.nWidth *= 2;
      stitch.nWrapX = 2 * stitch.nWrapX - PerlinN;
      stitch.nHeight *= 2;
      stitch.nWrapY = 2 * stitch.nWrapY - PerlinN;
    }
  }
  return fSum;
}

#endif
