/*
 * The Python Imaging Library.
 * $Id$
 *
 * a simple drawing package for the Imaging library
 *
 * history:
 * 1996-04-13 fl  Created.
 * 1996-04-30 fl  Added transforms and polygon support.
 * 1996-08-12 fl  Added filled polygons.
 * 1996-11-05 fl  Fixed float/int confusion in polygon filler
 * 1997-07-04 fl  Support 32-bit images (C++ would have been nice)
 * 1998-09-09 fl  Eliminated qsort casts; improved rectangle clipping
 * 1998-09-10 fl  Fixed fill rectangle to include lower edge (!)
 * 1998-12-29 fl  Added arc, chord, and pieslice primitives
 * 1999-01-10 fl  Added some level 2 ("arrow") stuff (experimental)
 * 1999-02-06 fl  Added bitmap primitive
 * 1999-07-26 fl  Eliminated a compiler warning
 * 1999-07-31 fl  Pass ink as void* instead of int
 * 2002-12-10 fl  Added experimental RGBA-on-RGB drawing
 * 2004-09-04 fl  Support simple wide lines (no joins)
 * 2005-05-25 fl  Fixed line width calculation
 *
 * Copyright (c) 1996-2006 by Fredrik Lundh
 * Copyright (c) 1997-2006 by Secret Labs AB.
 *
 * See the README file for information on usage and redistribution.
 */

/* FIXME: support fill/outline attribute for all filled shapes */
/* FIXME: support zero-winding fill */
/* FIXME: add drawing context, support affine transforms */
/* FIXME: support clip window (and mask?) */

#include "Imaging.h"

#include <math.h>

#define CEIL(v)  (int) ceil(v)
#define FLOOR(v) ((v) >= 0.0 ? (int) (v) : (int) floor(v))

#define INK8(ink) (*(UINT8*)ink)
#define INK32(ink) (*(INT32*)ink)

/* like (a * b + 127) / 255), but much faster on most platforms */
#define MULDIV255(a, b, tmp)\
        (tmp = (a) * (b) + 128, ((((tmp) >> 8) + (tmp)) >> 8))

#define BLEND(mask, in1, in2, tmp1, tmp2)\
        (MULDIV255(in1, 255 - mask, tmp1) + MULDIV255(in2, mask, tmp2))

/*
 * Rounds around zero (up=away from zero, down=torwards zero)
 * This guarantees that ROUND_UP|DOWN(f) == -ROUND_UP|DOWN(-f)
 */
#define ROUND_UP(f)    ((int) ((f) >= 0.0 ? floor((f) + 0.5F) : -floor(fabs(f) + 0.5F)))
#define ROUND_DOWN(f)    ((int) ((f) >= 0.0 ? ceil((f) - 0.5F) : -ceil(fabs(f) - 0.5F)))

/* -------------------------------------------------------------------- */
/* Primitives                                                           */
/* -------------------------------------------------------------------- */

typedef struct {
    /* edge descriptor for polygon engine */
    int d;
    int x0, y0;
    int xmin, ymin, xmax, ymax;
    float dx;
} Edge;

/* Type used in "polygon*" functions */
typedef void (*hline_handler)(Imaging, int, int, int, int);

static inline void
point8(Imaging im, int x, int y, int ink)
{
    if (x >= 0 && x < im->xsize && y >= 0 && y < im->ysize)
        im->image8[y][x] = (UINT8) ink;
}

static inline void
point32(Imaging im, int x, int y, int ink)
{
    if (x >= 0 && x < im->xsize && y >= 0 && y < im->ysize)
        im->image32[y][x] = ink;
}

static inline void
point32rgba(Imaging im, int x, int y, int ink)
{
    unsigned int tmp1, tmp2;

    if (x >= 0 && x < im->xsize && y >= 0 && y < im->ysize) {
        UINT8* out = (UINT8*) im->image[y]+x*4;
        UINT8* in = (UINT8*) &ink;
        out[0] = BLEND(in[3], out[0], in[0], tmp1, tmp2);
        out[1] = BLEND(in[3], out[1], in[1], tmp1, tmp2);
        out[2] = BLEND(in[3], out[2], in[2], tmp1, tmp2);
    }
}

static inline void
hline8(Imaging im, int x0, int y0, int x1, int ink)
{
    int tmp;

    if (y0 >= 0 && y0 < im->ysize) {
        if (x0 > x1)
            tmp = x0, x0 = x1, x1 = tmp;
        if (x0 < 0)
            x0 = 0;
        else if (x0 >= im->xsize)
            return;
        if (x1 < 0)
            return;
        else if (x1 >= im->xsize)
            x1 = im->xsize-1;
        if (x0 <= x1)
            memset(im->image8[y0] + x0, (UINT8) ink, x1 - x0 + 1);
    }
}

static inline void
hline32(Imaging im, int x0, int y0, int x1, int ink)
{
    int tmp;
    INT32* p;

    if (y0 >= 0 && y0 < im->ysize) {
        if (x0 > x1)
            tmp = x0, x0 = x1, x1 = tmp;
        if (x0 < 0)
            x0 = 0;
        else if (x0 >= im->xsize)
            return;
        if (x1 < 0)
            return;
        else if (x1 >= im->xsize)
            x1 = im->xsize-1;
        p = im->image32[y0];
        while (x0 <= x1)
            p[x0++] = ink;
    }
}

static inline void
hline32rgba(Imaging im, int x0, int y0, int x1, int ink)
{
    int tmp;
    unsigned int tmp1, tmp2;

    if (y0 >= 0 && y0 < im->ysize) {
        if (x0 > x1)
            tmp = x0, x0 = x1, x1 = tmp;
        if (x0 < 0)
            x0 = 0;
        else if (x0 >= im->xsize)
            return;
        if (x1 < 0)
            return;
        else if (x1 >= im->xsize)
            x1 = im->xsize-1;
        if (x0 <= x1) {
            UINT8* out = (UINT8*) im->image[y0]+x0*4;
            UINT8* in = (UINT8*) &ink;
            while (x0 <= x1) {
                out[0] = BLEND(in[3], out[0], in[0], tmp1, tmp2);
                out[1] = BLEND(in[3], out[1], in[1], tmp1, tmp2);
                out[2] = BLEND(in[3], out[2], in[2], tmp1, tmp2);
                x0++; out += 4;
            }
        }
    }
}

static inline void
line8(Imaging im, int x0, int y0, int x1, int y1, int ink)
{
    int i, n, e;
    int dx, dy;
    int xs, ys;

    /* normalize coordinates */
    dx = x1-x0;
    if (dx < 0)
        dx = -dx, xs = -1;
    else
        xs = 1;
    dy = y1-y0;
    if (dy < 0)
        dy = -dy, ys = -1;
    else
        ys = 1;

    n = (dx > dy) ? dx : dy;

    if (dx == 0)

        /* vertical */
        for (i = 0; i < dy; i++) {
            point8(im, x0, y0, ink);
            y0 += ys;
        }

    else if (dy == 0)

        /* horizontal */
        for (i = 0; i < dx; i++) {
            point8(im, x0, y0, ink);
            x0 += xs;
        }

    else if (dx > dy) {

        /* bresenham, horizontal slope */
        n = dx;
        dy += dy;
        e = dy - dx;
        dx += dx;

        for (i = 0; i < n; i++) {
            point8(im, x0, y0, ink);
            if (e >= 0) {
                y0 += ys;
                e -= dx;
            }
            e += dy;
            x0 += xs;
        }

    } else {

        /* bresenham, vertical slope */
        n = dy;
        dx += dx;
        e = dx - dy;
        dy += dy;

        for (i = 0; i < n; i++) {
            point8(im, x0, y0, ink);
            if (e >= 0) {
                x0 += xs;
                e -= dy;
            }
            e += dx;
            y0 += ys;
        }

    }
}

static inline void
line32(Imaging im, int x0, int y0, int x1, int y1, int ink)
{
    int i, n, e;
    int dx, dy;
    int xs, ys;

    /* normalize coordinates */
    dx = x1-x0;
    if (dx < 0)
        dx = -dx, xs = -1;
    else
        xs = 1;
    dy = y1-y0;
    if (dy < 0)
        dy = -dy, ys = -1;
    else
        ys = 1;

    n = (dx > dy) ? dx : dy;

    if (dx == 0)

        /* vertical */
        for (i = 0; i < dy; i++) {
            point32(im, x0, y0, ink);
            y0 += ys;
        }

    else if (dy == 0)

        /* horizontal */
        for (i = 0; i < dx; i++) {
            point32(im, x0, y0, ink);
            x0 += xs;
        }

    else if (dx > dy) {

        /* bresenham, horizontal slope */
        n = dx;
        dy += dy;
        e = dy - dx;
        dx += dx;

        for (i = 0; i < n; i++) {
            point32(im, x0, y0, ink);
            if (e >= 0) {
                y0 += ys;
                e -= dx;
            }
            e += dy;
            x0 += xs;
        }

    } else {

        /* bresenham, vertical slope */
        n = dy;
        dx += dx;
        e = dx - dy;
        dy += dy;

        for (i = 0; i < n; i++) {
            point32(im, x0, y0, ink);
            if (e >= 0) {
                x0 += xs;
                e -= dy;
            }
            e += dx;
            y0 += ys;
        }

    }
}

static inline void
line32rgba(Imaging im, int x0, int y0, int x1, int y1, int ink)
{
    int i, n, e;
    int dx, dy;
    int xs, ys;

    /* normalize coordinates */
    dx = x1-x0;
    if (dx < 0)
        dx = -dx, xs = -1;
    else
        xs = 1;
    dy = y1-y0;
    if (dy < 0)
        dy = -dy, ys = -1;
    else
        ys = 1;

    n = (dx > dy) ? dx : dy;

    if (dx == 0)

        /* vertical */
        for (i = 0; i < dy; i++) {
            point32rgba(im, x0, y0, ink);
            y0 += ys;
        }

    else if (dy == 0)

        /* horizontal */
        for (i = 0; i < dx; i++) {
            point32rgba(im, x0, y0, ink);
            x0 += xs;
        }

    else if (dx > dy) {

        /* bresenham, horizontal slope */
        n = dx;
        dy += dy;
        e = dy - dx;
        dx += dx;

        for (i = 0; i < n; i++) {
            point32rgba(im, x0, y0, ink);
            if (e >= 0) {
                y0 += ys;
                e -= dx;
            }
            e += dy;
            x0 += xs;
        }

    } else {

        /* bresenham, vertical slope */
        n = dy;
        dx += dx;
        e = dx - dy;
        dy += dy;

        for (i = 0; i < n; i++) {
            point32rgba(im, x0, y0, ink);
            if (e >= 0) {
                x0 += xs;
                e -= dy;
            }
            e += dx;
            y0 += ys;
        }

    }
}

static int
x_cmp(const void *x0, const void *x1)
{
    float diff = *((float*)x0) - *((float*)x1);
    if (diff < 0)
        return -1;
    else if (diff > 0)
        return 1;
    else
        return 0;
}


/*
 * Filled polygon draw function using scan line algorithm.
 */
static inline int
polygon_generic(Imaging im, int n, Edge *e, int ink, int eofill,
        hline_handler hline)
{

    Edge** edge_table;
    float* xx;
    int edge_count = 0;
    int ymin = im->ysize - 1;
    int ymax = 0;
    int i;

    if (n <= 0) {
        return 0;
    }

    /* Initialize the edge table and find polygon boundaries */
    edge_table = malloc(sizeof(Edge*) * n);
    if (!edge_table) {
        return -1;
    }

    for (i = 0; i < n; i++) {
        /* This causes that the pixels of horizontal edges are drawn twice :(
         * but without it there are inconsistencies in ellipses */
        if (e[i].ymin == e[i].ymax) {
            (*hline)(im, e[i].xmin, e[i].ymin, e[i].xmax, ink);
            continue;
        }
        if (ymin > e[i].ymin) {
            ymin = e[i].ymin;
        }
        if (ymax < e[i].ymax) {
            ymax = e[i].ymax;
        }
        edge_table[edge_count++] = (e + i);
    }
    if (ymin < 0) {
        ymin = 0;
    }
    if (ymax >= im->ysize) {
        ymax = im->ysize - 1;
    }

    /* Process the edge table with a scan line searching for intersections */
    xx = malloc(sizeof(float) * edge_count * 2);
    if (!xx) {
        free(edge_table);
        return -1;
    }
    for (; ymin <= ymax; ymin++) {
        int j = 0;
        for (i = 0; i < edge_count; i++) {
            Edge* current = edge_table[i];
            if (ymin >= current->ymin && ymin <= current->ymax) {
                xx[j++] = (ymin - current->y0) * current->dx + current->x0;
            }
            /* Needed to draw consistent polygons */
            if (ymin == current->ymax && ymin < ymax) {
                xx[j] = xx[j - 1];
                j++;
            }
        }
        qsort(xx, j, sizeof(float), x_cmp);
        for (i = 1; i < j; i += 2) {
            (*hline)(im, ROUND_UP(xx[i - 1]), ymin, ROUND_DOWN(xx[i]), ink);
        }
    }

    free(xx);
    free(edge_table);
    return 0;
}

static inline int
polygon8(Imaging im, int n, Edge *e, int ink, int eofill)
{
    return polygon_generic(im, n, e, ink, eofill, hline8);
}

static inline int
polygon32(Imaging im, int n, Edge *e, int ink, int eofill)
{
    return polygon_generic(im, n, e, ink, eofill, hline32);
}

static inline int
polygon32rgba(Imaging im, int n, Edge *e, int ink, int eofill)
{
    return polygon_generic(im, n, e, ink, eofill, hline32rgba);
}

static inline void
add_edge(Edge *e, int x0, int y0, int x1, int y1)
{
    /* printf("edge %d %d %d %d\n", x0, y0, x1, y1); */

    if (x0 <= x1)
        e->xmin = x0, e->xmax = x1;
    else
        e->xmin = x1, e->xmax = x0;

    if (y0 <= y1)
        e->ymin = y0, e->ymax = y1;
    else
        e->ymin = y1, e->ymax = y0;

    if (y0 == y1) {
        e->d = 0;
        e->dx = 0.0;
    } else {
        e->dx = ((float)(x1-x0)) / (y1-y0);
        if (y0 == e->ymin)
            e->d = 1;
        else
            e->d = -1;
    }

    e->x0 = x0;
    e->y0 = y0;
}

typedef struct {
    void (*point)(Imaging im, int x, int y, int ink);
    void (*hline)(Imaging im, int x0, int y0, int x1, int ink);
    void (*line)(Imaging im, int x0, int y0, int x1, int y1, int ink);
    int (*polygon)(Imaging im, int n, Edge *e, int ink, int eofill);
} DRAW;

DRAW draw8 = { point8,  hline8,  line8,  polygon8 };
DRAW draw32 = { point32, hline32, line32, polygon32 };
DRAW draw32rgba = { point32rgba, hline32rgba, line32rgba, polygon32rgba };

/* -------------------------------------------------------------------- */
/* Interface                                                            */
/* -------------------------------------------------------------------- */

#define DRAWINIT()\
    if (im->image8) {\
        draw = &draw8;\
        ink = INK8(ink_);\
    } else {\
        draw = (op) ? &draw32rgba : &draw32;    \
        ink = INK32(ink_);\
    }

int
ImagingDrawPoint(Imaging im, int x0, int y0, const void* ink_, int op)
{
    DRAW* draw;
    INT32 ink;

    DRAWINIT();

    draw->point(im, x0, y0, ink);

    return 0;
}

int
ImagingDrawLine(Imaging im, int x0, int y0, int x1, int y1, const void* ink_,
                int op)
{
    DRAW* draw;
    INT32 ink;

    DRAWINIT();

    draw->line(im, x0, y0, x1, y1, ink);

    return 0;
}

int
ImagingDrawWideLine(Imaging im, int x0, int y0, int x1, int y1,
                    const void* ink_, int width, int op)
{
    DRAW* draw;
    INT32 ink;
    int dx, dy;
    double big_hypotenuse, small_hypotenuse, ratio_max, ratio_min;
    int dxmin, dxmax, dymin, dymax;
    Edge e[4];

    DRAWINIT();

    if (width <= 1) {
        draw->line(im, x0, y0, x1, y1, ink);
        return 0;
    }

    dx = x1-x0;
    dy = y1-y0;
    if (dx == 0 && dy == 0) {
        draw->point(im, x0, y0, ink);
        return 0;
    }

    big_hypotenuse = sqrt((double) (dx*dx + dy*dy));
    small_hypotenuse = (width - 1) / 2.0;
    ratio_max = ROUND_UP(small_hypotenuse) / big_hypotenuse;
    ratio_min = ROUND_DOWN(small_hypotenuse) / big_hypotenuse;

    dxmin = ROUND_DOWN(ratio_min * dy);
    dxmax = ROUND_DOWN(ratio_max * dy);
    dymin = ROUND_DOWN(ratio_min * dx);
    dymax = ROUND_DOWN(ratio_max * dx);
    {
        int vertices[4][2] = {
            {x0 - dxmin, y0 + dymax},
            {x1 - dxmin, y1 + dymax},
            {x1 + dxmax, y1 - dymin},
            {x0 + dxmax, y0 - dymin}
        };

        add_edge(e+0, vertices[0][0], vertices[0][1], vertices[1][0], vertices[1][1]);
        add_edge(e+1, vertices[1][0], vertices[1][1], vertices[2][0], vertices[2][1]);
        add_edge(e+2, vertices[2][0], vertices[2][1], vertices[3][0], vertices[3][1]);
        add_edge(e+3, vertices[3][0], vertices[3][1], vertices[0][0], vertices[0][1]);

        draw->polygon(im, 4, e, ink, 0);
    }
    return 0;
}

int
ImagingDrawRectangle(Imaging im, int x0, int y0, int x1, int y1,
                     const void* ink_, int fill, int op)
{
    int y;
    int tmp;
    DRAW* draw;
    INT32 ink;

    DRAWINIT();

    if (y0 > y1)
        tmp = y0, y0 = y1, y1 = tmp;

    if (fill) {

        if (y0 < 0)
            y0 = 0;
        else if (y0 >= im->ysize)
            return 0;

        if (y1 < 0)
            return 0;
        else if (y1 > im->ysize)
            y1 = im->ysize;

        for (y = y0; y <= y1; y++)
            draw->hline(im, x0, y, x1, ink);

    } else {

        /* outline */
        draw->line(im, x0, y0, x1, y0, ink);
        draw->line(im, x1, y0, x1, y1, ink);
        draw->line(im, x1, y1, x0, y1, ink);
        draw->line(im, x0, y1, x0, y0, ink);

    }

    return 0;
}

int
ImagingDrawPolygon(Imaging im, int count, int* xy, const void* ink_,
                   int fill, int op)
{
    int i, n;
    DRAW* draw;
    INT32 ink;

    if (count <= 0)
        return 0;

    DRAWINIT();

    if (fill) {

        /* Build edge list */
        Edge* e = malloc(count * sizeof(Edge));
        if (!e) {
            (void) ImagingError_MemoryError();
            return -1;
        }
        for (i = n = 0; i < count-1; i++)
            add_edge(&e[n++], xy[i+i], xy[i+i+1], xy[i+i+2], xy[i+i+3]);
        if (xy[i+i] != xy[0] || xy[i+i+1] != xy[1])
            add_edge(&e[n++], xy[i+i], xy[i+i+1], xy[0], xy[1]);
        draw->polygon(im, n, e, ink, 0);
        free(e);

    } else {

        /* Outline */
        for (i = 0; i < count-1; i++)
            draw->line(im, xy[i+i], xy[i+i+1], xy[i+i+2], xy[i+i+3], ink);
        draw->line(im, xy[i+i], xy[i+i+1], xy[0], xy[1], ink);

    }

    return 0;
}

int
ImagingDrawBitmap(Imaging im, int x0, int y0, Imaging bitmap, const void* ink,
                  int op)
{
    return ImagingFill2(
        im, ink, bitmap,
        x0, y0, x0 + bitmap->xsize, y0 + bitmap->ysize
        );
}

/* -------------------------------------------------------------------- */
/* standard shapes */

#define ARC 0
#define CHORD 1
#define PIESLICE 2

static int
ellipse(Imaging im, int x0, int y0, int x1, int y1,
        int start, int end, const void* ink_, int fill,
        int mode, int op)
{
    int i, n;
    int cx, cy;
    int w, h;
    int x = 0, y = 0;
    int lx = 0, ly = 0;
    int sx = 0, sy = 0;
    DRAW* draw;
    INT32 ink;

    w = x1 - x0;
    h = y1 - y0;
    if (w < 0 || h < 0)
        return 0;

    DRAWINIT();

    cx = (x0 + x1) / 2;
    cy = (y0 + y1) / 2;

    while (end < start)
        end += 360;

    if (mode != ARC && fill) {

        /* Build edge list */
        Edge* e = malloc((end - start + 3) * sizeof(Edge));
        if (!e) {
            ImagingError_MemoryError();
            return -1;
        }

        n = 0;

        for (i = start; i <= end; i++) {
            x = FLOOR((cos(i*M_PI/180) * w/2) + cx + 0.5);
            y = FLOOR((sin(i*M_PI/180) * h/2) + cy + 0.5);
            if (i != start)
                add_edge(&e[n++], lx, ly, x, y);
            else
                sx = x, sy = y;
            lx = x, ly = y;
        }

        if (n > 0) {
            /* close and draw polygon */
            if (mode == PIESLICE) {
                if (x != cx || y != cy) {
                    add_edge(&e[n++], x, y, cx, cy);
                    add_edge(&e[n++], cx, cy, sx, sy);
                }
            } else {
                if (x != sx || y != sy)
                    add_edge(&e[n++], x, y, sx, sy);
            }
            draw->polygon(im, n, e, ink, 0);
        }

        free(e);

    } else {

        for (i = start; i <= end; i++) {
            x = FLOOR((cos(i*M_PI/180) * w/2) + cx + 0.5);
            y = FLOOR((sin(i*M_PI/180) * h/2) + cy + 0.5);
            if (i != start)
                draw->line(im, lx, ly, x, y, ink);
            else
                sx = x, sy = y;
            lx = x, ly = y;
        }

        if (i != start) {
            if (mode == PIESLICE) {
                if (x != cx || y != cy) {
                    draw->line(im, x, y, cx, cy, ink);
                    draw->line(im, cx, cy, sx, sy, ink);
                }
            } else if (mode == CHORD) {
                if (x != sx || y != sy)
                    draw->line(im, x, y, sx, sy, ink);
            }
        }
    }

    return 0;
}

int
ImagingDrawArc(Imaging im, int x0, int y0, int x1, int y1,
               int start, int end, const void* ink, int op)
{
    return ellipse(im, x0, y0, x1, y1, start, end, ink, 0, ARC, op);
}

int
ImagingDrawChord(Imaging im, int x0, int y0, int x1, int y1,
               int start, int end, const void* ink, int fill, int op)
{
    return ellipse(im, x0, y0, x1, y1, start, end, ink, fill, CHORD, op);
}

int
ImagingDrawEllipse(Imaging im, int x0, int y0, int x1, int y1,
                   const void* ink, int fill, int op)
{
    return ellipse(im, x0, y0, x1, y1, 0, 360, ink, fill, CHORD, op);
}

int
ImagingDrawPieslice(Imaging im, int x0, int y0, int x1, int y1,
                    int start, int end, const void* ink, int fill, int op)
{
    return ellipse(im, x0, y0, x1, y1, start, end, ink, fill, PIESLICE, op);
}

/* -------------------------------------------------------------------- */

/* experimental level 2 ("arrow") graphics stuff.  this implements
   portions of the arrow api on top of the Edge structure.  the
   semantics are ok, except that "curve" flattens the bezier curves by
   itself */

#if 1 /* ARROW_GRAPHICS */

struct ImagingOutlineInstance {

    float x0, y0;

    float x, y;

    int count;
    Edge *edges;

    int size;

};


ImagingOutline
ImagingOutlineNew(void)
{
    ImagingOutline outline;

    outline = calloc(1, sizeof(struct ImagingOutlineInstance));
    if (!outline)
        return (ImagingOutline) ImagingError_MemoryError();

    outline->edges = NULL;
    outline->count = outline->size = 0;

    ImagingOutlineMove(outline, 0, 0);

    return outline;
}

void
ImagingOutlineDelete(ImagingOutline outline)
{
    if (!outline)
        return;

    if (outline->edges)
        free(outline->edges);

    free(outline);
}


static Edge*
allocate(ImagingOutline outline, int extra)
{
    Edge* e;

    if (outline->count + extra > outline->size) {
        /* expand outline buffer */
        outline->size += extra + 25;
        if (!outline->edges)
            e = malloc(outline->size * sizeof(Edge));
        else
            e = realloc(outline->edges, outline->size * sizeof(Edge));
        if (!e)
            return NULL;
        outline->edges = e;
    }

    e = outline->edges + outline->count;

    outline->count += extra;

    return e;
}

int
ImagingOutlineMove(ImagingOutline outline, float x0, float y0)
{
    outline->x = outline->x0 = x0;
    outline->y = outline->y0 = y0;

    return 0;
}

int
ImagingOutlineLine(ImagingOutline outline, float x1, float y1)
{
    Edge* e;

    e = allocate(outline, 1);
    if (!e)
        return -1; /* out of memory */

    add_edge(e, (int) outline->x, (int) outline->y, (int) x1, (int) y1);

    outline->x = x1;
    outline->y = y1;

    return 0;
}

int
ImagingOutlineCurve(ImagingOutline outline, float x1, float y1,
                    float x2, float y2, float x3, float y3)
{
    Edge* e;
    int i;
    float xo, yo;

#define STEPS 32

    e = allocate(outline, STEPS);
    if (!e)
        return -1; /* out of memory */

    xo = outline->x;
    yo = outline->y;

    /* flatten the bezier segment */

    for (i = 1; i <= STEPS; i++) {

        float t = ((float) i) / STEPS;
        float t2 = t*t;
        float t3 = t2*t;

        float u = 1.0F - t;
        float u2 = u*u;
        float u3 = u2*u;

        float x = outline->x*u3 + 3*(x1*t*u2 + x2*t2*u) + x3*t3 + 0.5;
        float y = outline->y*u3 + 3*(y1*t*u2 + y2*t2*u) + y3*t3 + 0.5;

        add_edge(e++, xo, yo, (int) x, (int) y);

        xo = x, yo = y;

    }

    outline->x = xo;
    outline->y = yo;

    return 0;
}

int
ImagingOutlineCurve2(ImagingOutline outline, float cx, float cy,
                     float x3, float y3)
{
    /* add bezier curve based on three control points (as
       in the Flash file format) */

    return ImagingOutlineCurve(
        outline,
        (outline->x + cx + cx)/3, (outline->y + cy + cy)/3,
        (cx + cx + x3)/3, (cy + cy + y3)/3,
        x3, y3);
}

int
ImagingOutlineClose(ImagingOutline outline)
{
    if (outline->x == outline->x0 && outline->y == outline->y0)
        return 0;
    return ImagingOutlineLine(outline, outline->x0, outline->y0);
}

int
ImagingOutlineTransform(ImagingOutline outline, double a[6])
{
    Edge *eIn;
    Edge *eOut;
    int i, n;
    int x0, y0, x1, y1;
    int X0, Y0, X1, Y1;

    double a0 = a[0]; double a1 = a[1]; double a2 = a[2];
    double a3 = a[3]; double a4 = a[4]; double a5 = a[5];

    eIn = outline->edges;
    n = outline->count;

    /* FIXME: ugly! */
    outline->edges = NULL;
    outline->count = outline->size = 0;

    eOut = allocate(outline, n);
    if (!eOut) {
        outline->edges = eIn;
        outline->count = outline->size = n;
        ImagingError_MemoryError();
        return -1;
    }

    for (i = 0; i < n; i++) {

        x0 = eIn->x0;
        y0 = eIn->y0;

        /* FIXME: ouch! */
        if (eIn->x0 == eIn->xmin)
            x1 = eIn->xmax;
        else
            x1 = eIn->xmin;
        if (eIn->y0 == eIn->ymin)
            y1 = eIn->ymax;
        else
            y1 = eIn->ymin;

        /* full moon tonight!  if this doesn't work, you may need to
           upgrade your compiler (make sure you have the right service
           pack) */

        X0 = (int) (a0*x0 + a1*y0 + a2);
        Y0 = (int) (a3*x0 + a4*y0 + a5);
        X1 = (int) (a0*x1 + a1*y1 + a2);
        Y1 = (int) (a3*x1 + a4*y1 + a5);

        add_edge(eOut, X0, Y0, X1, Y1);

        eIn++;
        eOut++;

    }

    free(eIn);

    return 0;
}

int
ImagingDrawOutline(Imaging im, ImagingOutline outline, const void* ink_,
                   int fill, int op)
{
    DRAW* draw;
    INT32 ink;

    DRAWINIT();

    draw->polygon(im, outline->count, outline->edges, ink, 0);

    return 0;
}

#endif
