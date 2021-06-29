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
#include <stdint.h>

#define CEIL(v) (int)ceil(v)
#define FLOOR(v) ((v) >= 0.0 ? (int)(v) : (int)floor(v))

#define INK8(ink) (*(UINT8 *)ink)

/*
 * Rounds around zero (up=away from zero, down=towards zero)
 * This guarantees that ROUND_UP|DOWN(f) == -ROUND_UP|DOWN(-f)
 */
#define ROUND_UP(f) ((int)((f) >= 0.0 ? floor((f) + 0.5F) : -floor(fabs(f) + 0.5F)))
#define ROUND_DOWN(f) ((int)((f) >= 0.0 ? ceil((f)-0.5F) : -ceil(fabs(f) - 0.5F)))

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
point8(Imaging im, int x, int y, int ink) {
    if (x >= 0 && x < im->xsize && y >= 0 && y < im->ysize) {
        if (strncmp(im->mode, "I;16", 4) == 0) {
            im->image8[y][x * 2] = (UINT8)ink;
            im->image8[y][x * 2 + 1] = (UINT8)ink;
        } else {
            im->image8[y][x] = (UINT8)ink;
        }
    }
}

static inline void
point32(Imaging im, int x, int y, int ink) {
    if (x >= 0 && x < im->xsize && y >= 0 && y < im->ysize) {
        im->image32[y][x] = ink;
    }
}

static inline void
point32rgba(Imaging im, int x, int y, int ink) {
    unsigned int tmp1;

    if (x >= 0 && x < im->xsize && y >= 0 && y < im->ysize) {
        UINT8 *out = (UINT8 *)im->image[y] + x * 4;
        UINT8 *in = (UINT8 *)&ink;
        out[0] = BLEND(in[3], out[0], in[0], tmp1);
        out[1] = BLEND(in[3], out[1], in[1], tmp1);
        out[2] = BLEND(in[3], out[2], in[2], tmp1);
    }
}

static inline void
hline8(Imaging im, int x0, int y0, int x1, int ink) {
    int tmp, pixelwidth;

    if (y0 >= 0 && y0 < im->ysize) {
        if (x0 > x1) {
            tmp = x0, x0 = x1, x1 = tmp;
        }
        if (x0 < 0) {
            x0 = 0;
        } else if (x0 >= im->xsize) {
            return;
        }
        if (x1 < 0) {
            return;
        } else if (x1 >= im->xsize) {
            x1 = im->xsize - 1;
        }
        if (x0 <= x1) {
            pixelwidth = strncmp(im->mode, "I;16", 4) == 0 ? 2 : 1;
            memset(
                im->image8[y0] + x0 * pixelwidth,
                (UINT8)ink,
                (x1 - x0 + 1) * pixelwidth);
        }
    }
}

static inline void
hline32(Imaging im, int x0, int y0, int x1, int ink) {
    int tmp;
    INT32 *p;

    if (y0 >= 0 && y0 < im->ysize) {
        if (x0 > x1) {
            tmp = x0, x0 = x1, x1 = tmp;
        }
        if (x0 < 0) {
            x0 = 0;
        } else if (x0 >= im->xsize) {
            return;
        }
        if (x1 < 0) {
            return;
        } else if (x1 >= im->xsize) {
            x1 = im->xsize - 1;
        }
        p = im->image32[y0];
        while (x0 <= x1) {
            p[x0++] = ink;
        }
    }
}

static inline void
hline32rgba(Imaging im, int x0, int y0, int x1, int ink) {
    int tmp;
    unsigned int tmp1;

    if (y0 >= 0 && y0 < im->ysize) {
        if (x0 > x1) {
            tmp = x0, x0 = x1, x1 = tmp;
        }
        if (x0 < 0) {
            x0 = 0;
        } else if (x0 >= im->xsize) {
            return;
        }
        if (x1 < 0) {
            return;
        } else if (x1 >= im->xsize) {
            x1 = im->xsize - 1;
        }
        if (x0 <= x1) {
            UINT8 *out = (UINT8 *)im->image[y0] + x0 * 4;
            UINT8 *in = (UINT8 *)&ink;
            while (x0 <= x1) {
                out[0] = BLEND(in[3], out[0], in[0], tmp1);
                out[1] = BLEND(in[3], out[1], in[1], tmp1);
                out[2] = BLEND(in[3], out[2], in[2], tmp1);
                x0++;
                out += 4;
            }
        }
    }
}

static inline void
line8(Imaging im, int x0, int y0, int x1, int y1, int ink) {
    int i, n, e;
    int dx, dy;
    int xs, ys;

    /* normalize coordinates */
    dx = x1 - x0;
    if (dx < 0) {
        dx = -dx, xs = -1;
    } else {
        xs = 1;
    }
    dy = y1 - y0;
    if (dy < 0) {
        dy = -dy, ys = -1;
    } else {
        ys = 1;
    }

    n = (dx > dy) ? dx : dy;

    if (dx == 0) {
        /* vertical */
        for (i = 0; i < dy; i++) {
            point8(im, x0, y0, ink);
            y0 += ys;
        }

    } else if (dy == 0) {
        /* horizontal */
        for (i = 0; i < dx; i++) {
            point8(im, x0, y0, ink);
            x0 += xs;
        }

    } else if (dx > dy) {
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
line32(Imaging im, int x0, int y0, int x1, int y1, int ink) {
    int i, n, e;
    int dx, dy;
    int xs, ys;

    /* normalize coordinates */
    dx = x1 - x0;
    if (dx < 0) {
        dx = -dx, xs = -1;
    } else {
        xs = 1;
    }
    dy = y1 - y0;
    if (dy < 0) {
        dy = -dy, ys = -1;
    } else {
        ys = 1;
    }

    n = (dx > dy) ? dx : dy;

    if (dx == 0) {
        /* vertical */
        for (i = 0; i < dy; i++) {
            point32(im, x0, y0, ink);
            y0 += ys;
        }

    } else if (dy == 0) {
        /* horizontal */
        for (i = 0; i < dx; i++) {
            point32(im, x0, y0, ink);
            x0 += xs;
        }

    } else if (dx > dy) {
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
line32rgba(Imaging im, int x0, int y0, int x1, int y1, int ink) {
    int i, n, e;
    int dx, dy;
    int xs, ys;

    /* normalize coordinates */
    dx = x1 - x0;
    if (dx < 0) {
        dx = -dx, xs = -1;
    } else {
        xs = 1;
    }
    dy = y1 - y0;
    if (dy < 0) {
        dy = -dy, ys = -1;
    } else {
        ys = 1;
    }

    n = (dx > dy) ? dx : dy;

    if (dx == 0) {
        /* vertical */
        for (i = 0; i < dy; i++) {
            point32rgba(im, x0, y0, ink);
            y0 += ys;
        }

    } else if (dy == 0) {
        /* horizontal */
        for (i = 0; i < dx; i++) {
            point32rgba(im, x0, y0, ink);
            x0 += xs;
        }

    } else if (dx > dy) {
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
x_cmp(const void *x0, const void *x1) {
    float diff = *((float *)x0) - *((float *)x1);
    if (diff < 0) {
        return -1;
    } else if (diff > 0) {
        return 1;
    } else {
        return 0;
    }
}

static void
draw_horizontal_lines(
    Imaging im, int n, Edge *e, int ink, int *x_pos, int y, hline_handler hline) {
    int i;
    for (i = 0; i < n; i++) {
        if (e[i].ymin == y && e[i].ymin == e[i].ymax) {
            int xmax;
            int xmin = e[i].xmin;
            if (*x_pos < xmin) {
                // Line would be after the current position
                continue;
            }

            xmax = e[i].xmax;
            if (*x_pos > xmin) {
                // Line would be partway through x_pos, so increase the starting point
                xmin = *x_pos;
                if (xmax < xmin) {
                    // Line would now end before it started
                    continue;
                }
            }

            (*hline)(im, xmin, e[i].ymin, xmax, ink);
            *x_pos = xmax + 1;
        }
    }
}

/*
 * Filled polygon draw function using scan line algorithm.
 */
static inline int
polygon_generic(Imaging im, int n, Edge *e, int ink, int eofill, hline_handler hline) {
    Edge **edge_table;
    float *xx;
    int edge_count = 0;
    int ymin = im->ysize - 1;
    int ymax = 0;
    int i;

    if (n <= 0) {
        return 0;
    }

    /* Initialize the edge table and find polygon boundaries */
    /* malloc check ok, using calloc */
    edge_table = calloc(n, sizeof(Edge *));
    if (!edge_table) {
        return -1;
    }

    for (i = 0; i < n; i++) {
        if (ymin > e[i].ymin) {
            ymin = e[i].ymin;
        }
        if (ymax < e[i].ymax) {
            ymax = e[i].ymax;
        }
        if (e[i].ymin == e[i].ymax) {
            continue;
        }
        edge_table[edge_count++] = (e + i);
    }
    if (ymin < 0) {
        ymin = 0;
    }
    if (ymax > im->ysize) {
        ymax = im->ysize;
    }

    /* Process the edge table with a scan line searching for intersections */
    /* malloc check ok, using calloc */
    xx = calloc(edge_count * 2, sizeof(float));
    if (!xx) {
        free(edge_table);
        return -1;
    }
    for (; ymin <= ymax; ymin++) {
        int j = 0;
        int x_pos = 0;
        for (i = 0; i < edge_count; i++) {
            Edge *current = edge_table[i];
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
            int x_end = ROUND_DOWN(xx[i]);
            if (x_end < x_pos) {
                // Line would be before the current position
                continue;
            }
            draw_horizontal_lines(im, n, e, ink, &x_pos, ymin, hline);
            if (x_end < x_pos) {
                // Line would be before the current position
                continue;
            }

            int x_start = ROUND_UP(xx[i - 1]);
            if (x_pos > x_start) {
                // Line would be partway through x_pos, so increase the starting point
                x_start = x_pos;
                if (x_end < x_start) {
                    // Line would now end before it started
                    continue;
                }
            }
            (*hline)(im, x_start, ymin, x_end, ink);
            x_pos = x_end + 1;
        }
        draw_horizontal_lines(im, n, e, ink, &x_pos, ymin, hline);
    }

    free(xx);
    free(edge_table);
    return 0;
}

static inline int
polygon8(Imaging im, int n, Edge *e, int ink, int eofill) {
    return polygon_generic(im, n, e, ink, eofill, hline8);
}

static inline int
polygon32(Imaging im, int n, Edge *e, int ink, int eofill) {
    return polygon_generic(im, n, e, ink, eofill, hline32);
}

static inline int
polygon32rgba(Imaging im, int n, Edge *e, int ink, int eofill) {
    return polygon_generic(im, n, e, ink, eofill, hline32rgba);
}

static inline void
add_edge(Edge *e, int x0, int y0, int x1, int y1) {
    /* printf("edge %d %d %d %d\n", x0, y0, x1, y1); */

    if (x0 <= x1) {
        e->xmin = x0, e->xmax = x1;
    } else {
        e->xmin = x1, e->xmax = x0;
    }

    if (y0 <= y1) {
        e->ymin = y0, e->ymax = y1;
    } else {
        e->ymin = y1, e->ymax = y0;
    }

    if (y0 == y1) {
        e->d = 0;
        e->dx = 0.0;
    } else {
        e->dx = ((float)(x1 - x0)) / (y1 - y0);
        if (y0 == e->ymin) {
            e->d = 1;
        } else {
            e->d = -1;
        }
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

DRAW draw8 = {point8, hline8, line8, polygon8};
DRAW draw32 = {point32, hline32, line32, polygon32};
DRAW draw32rgba = {point32rgba, hline32rgba, line32rgba, polygon32rgba};

/* -------------------------------------------------------------------- */
/* Interface                                                            */
/* -------------------------------------------------------------------- */

#define DRAWINIT()                           \
    if (im->image8) {                        \
        draw = &draw8;                       \
        ink = INK8(ink_);                    \
    } else {                                 \
        draw = (op) ? &draw32rgba : &draw32; \
        memcpy(&ink, ink_, sizeof(ink));     \
    }

int
ImagingDrawPoint(Imaging im, int x0, int y0, const void *ink_, int op) {
    DRAW *draw;
    INT32 ink;

    DRAWINIT();

    draw->point(im, x0, y0, ink);

    return 0;
}

int
ImagingDrawLine(Imaging im, int x0, int y0, int x1, int y1, const void *ink_, int op) {
    DRAW *draw;
    INT32 ink;

    DRAWINIT();

    draw->line(im, x0, y0, x1, y1, ink);

    return 0;
}

int
ImagingDrawWideLine(
    Imaging im, int x0, int y0, int x1, int y1, const void *ink_, int width, int op) {
    DRAW *draw;
    INT32 ink;
    int dx, dy;
    double big_hypotenuse, small_hypotenuse, ratio_max, ratio_min;
    int dxmin, dxmax, dymin, dymax;
    Edge e[4];

    DRAWINIT();

    dx = x1 - x0;
    dy = y1 - y0;
    if (dx == 0 && dy == 0) {
        draw->point(im, x0, y0, ink);
        return 0;
    }

    big_hypotenuse = hypot(dx, dy);
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
            {x0 + dxmax, y0 - dymin}};

        add_edge(e + 0, vertices[0][0], vertices[0][1], vertices[1][0], vertices[1][1]);
        add_edge(e + 1, vertices[1][0], vertices[1][1], vertices[2][0], vertices[2][1]);
        add_edge(e + 2, vertices[2][0], vertices[2][1], vertices[3][0], vertices[3][1]);
        add_edge(e + 3, vertices[3][0], vertices[3][1], vertices[0][0], vertices[0][1]);

        draw->polygon(im, 4, e, ink, 0);
    }
    return 0;
}

int
ImagingDrawRectangle(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    const void *ink_,
    int fill,
    int width,
    int op) {
    int i;
    int y;
    int tmp;
    DRAW *draw;
    INT32 ink;

    DRAWINIT();

    if (y0 > y1) {
        tmp = y0, y0 = y1, y1 = tmp;
    }

    if (fill) {
        if (y0 < 0) {
            y0 = 0;
        } else if (y0 >= im->ysize) {
            return 0;
        }

        if (y1 < 0) {
            return 0;
        } else if (y1 > im->ysize) {
            y1 = im->ysize;
        }

        for (y = y0; y <= y1; y++) {
            draw->hline(im, x0, y, x1, ink);
        }

    } else {
        /* outline */
        if (width == 0) {
            width = 1;
        }
        for (i = 0; i < width; i++) {
            draw->hline(im, x0, y0 + i, x1, ink);
            draw->hline(im, x0, y1 - i, x1, ink);
            draw->line(im, x1 - i, y0 + width, x1 - i, y1 - width + 1, ink);
            draw->line(im, x0 + i, y0 + width, x0 + i, y1 - width + 1, ink);
        }
    }

    return 0;
}

int
ImagingDrawPolygon(Imaging im, int count, int *xy, const void *ink_, int fill, int op) {
    int i, n, x0, y0, x1, y1;
    DRAW *draw;
    INT32 ink;

    if (count <= 0) {
        return 0;
    }

    DRAWINIT();

    if (fill) {
        /* Build edge list */
        /* malloc check ok, using calloc */
        Edge *e = calloc(count, sizeof(Edge));
        if (!e) {
            (void)ImagingError_MemoryError();
            return -1;
        }
        for (i = n = 0; i < count - 1; i++) {
            x0 = xy[i * 2];
            y0 = xy[i * 2 + 1];
            x1 = xy[i * 2 + 2];
            y1 = xy[i * 2 + 3];
            if (y0 == y1 && i != 0 && y0 == xy[i * 2 - 1]) {
                // This is a horizontal line,
                // that immediately follows another horizontal line
                Edge *last_e = &e[n-1];
                if (x1 > x0 && x0 > xy[i * 2 - 2]) {
                    // They are both increasing in x
                    last_e->xmax = x1;
                    continue;
                } else if (x1 < x0 && x0 < xy[i * 2 - 2]) {
                    // They are both decreasing in x
                    last_e->xmin = x1;
                    continue;
                }
            }
            add_edge(&e[n++], x0, y0, x1, y1);
        }
        if (xy[i * 2] != xy[0] || xy[i * 2 + 1] != xy[1]) {
            add_edge(&e[n++], xy[i * 2], xy[i * 2 + 1], xy[0], xy[1]);
        }
        draw->polygon(im, n, e, ink, 0);
        free(e);

    } else {
        /* Outline */
        for (i = 0; i < count - 1; i++) {
            draw->line(im, xy[i * 2], xy[i * 2 + 1], xy[i * 2 + 2], xy[i * 2 + 3], ink);
        }
        draw->line(im, xy[i * 2], xy[i * 2 + 1], xy[0], xy[1], ink);
    }

    return 0;
}

int
ImagingDrawBitmap(Imaging im, int x0, int y0, Imaging bitmap, const void *ink, int op) {
    return ImagingFill2(
        im, ink, bitmap, x0, y0, x0 + bitmap->xsize, y0 + bitmap->ysize);
}

/* -------------------------------------------------------------------- */
/* standard shapes */

// Imagine 2D plane and ellipse with center in (0, 0) and semi-major axes a and b.
// Then quarter_* stuff approximates its top right quarter (x, y >= 0) with integer
// points from set {(2x+x0, 2y+y0) | x,y in Z} where x0, y0 are from {0, 1} and
// are such that point (a, b) is in the set.

typedef struct {
    int32_t a, b, cx, cy, ex, ey;
    int64_t a2, b2, a2b2;
    int8_t finished;
} quarter_state;

void
quarter_init(quarter_state *s, int32_t a, int32_t b) {
    if (a < 0 || b < 0) {
        s->finished = 1;
    } else {
        s->a = a;
        s->b = b;
        s->cx = a;
        s->cy = b % 2;
        s->ex = a % 2;
        s->ey = b;
        s->a2 = a * a;
        s->b2 = b * b;
        s->a2b2 = s->a2 * s->b2;
        s->finished = 0;
    }
}

// deviation of the point from ellipse curve, basically a substitution
// of the point into the ellipse equation
int64_t
quarter_delta(quarter_state *s, int64_t x, int64_t y) {
    return llabs(s->a2 * y * y + s->b2 * x * x - s->a2b2);
}

int8_t
quarter_next(quarter_state *s, int32_t *ret_x, int32_t *ret_y) {
    if (s->finished) {
        return -1;
    }
    *ret_x = s->cx;
    *ret_y = s->cy;
    if (s->cx == s->ex && s->cy == s->ey) {
        s->finished = 1;
    } else {
        // Bresenham's algorithm, possible optimization: only consider 2 of 3
        // next points depending on current slope
        int32_t nx = s->cx;
        int32_t ny = s->cy + 2;
        int64_t ndelta = quarter_delta(s, nx, ny);
        if (nx > 1) {
            int64_t newdelta = quarter_delta(s, s->cx - 2, s->cy + 2);
            if (ndelta > newdelta) {
                nx = s->cx - 2;
                ny = s->cy + 2;
                ndelta = newdelta;
            }
            newdelta = quarter_delta(s, s->cx - 2, s->cy);
            if (ndelta > newdelta) {
                nx = s->cx - 2;
                ny = s->cy;
            }
        }
        s->cx = nx;
        s->cy = ny;
    }
    return 0;
}

// quarter_* stuff can "draw" a quarter of an ellipse with thickness 1, great.
// Now we use ellipse_* stuff to join all four quarters of two different sized
// ellipses and receive horizontal segments of a complete ellipse with
// specified thickness.
//
// Still using integer grid with step 2 at this point (like in quarter_*)
// to ease angle clipping in future.

typedef struct {
    quarter_state st_o, st_i;
    int32_t py, pl, pr;
    int32_t cy[4], cl[4], cr[4];
    int8_t bufcnt;
    int8_t finished;
    int8_t leftmost;
} ellipse_state;

void
ellipse_init(ellipse_state *s, int32_t a, int32_t b, int32_t w) {
    s->bufcnt = 0;
    s->leftmost = a % 2;
    quarter_init(&s->st_o, a, b);
    if (w < 1 || quarter_next(&s->st_o, &s->pr, &s->py) == -1) {
        s->finished = 1;
    } else {
        s->finished = 0;
        quarter_init(&s->st_i, a - 2 * (w - 1), b - 2 * (w - 1));
        s->pl = s->leftmost;
    }
}

int8_t
ellipse_next(ellipse_state *s, int32_t *ret_x0, int32_t *ret_y, int32_t *ret_x1) {
    if (s->bufcnt == 0) {
        if (s->finished) {
            return -1;
        }
        int32_t y = s->py;
        int32_t l = s->pl;
        int32_t r = s->pr;
        int32_t cx = 0, cy = 0;
        int8_t next_ret;
        while ((next_ret = quarter_next(&s->st_o, &cx, &cy)) != -1 && cy <= y) {
        }
        if (next_ret == -1) {
            s->finished = 1;
        } else {
            s->pr = cx;
            s->py = cy;
        }
        while ((next_ret = quarter_next(&s->st_i, &cx, &cy)) != -1 && cy <= y) {
            l = cx;
        }
        s->pl = next_ret == -1 ? s->leftmost : cx;

        if ((l > 0 || l < r) && y > 0) {
            s->cl[s->bufcnt] = l == 0 ? 2 : l;
            s->cy[s->bufcnt] = y;
            s->cr[s->bufcnt] = r;
            ++s->bufcnt;
        }
        if (y > 0) {
            s->cl[s->bufcnt] = -r;
            s->cy[s->bufcnt] = y;
            s->cr[s->bufcnt] = -l;
            ++s->bufcnt;
        }
        if (l > 0 || l < r) {
            s->cl[s->bufcnt] = l == 0 ? 2 : l;
            s->cy[s->bufcnt] = -y;
            s->cr[s->bufcnt] = r;
            ++s->bufcnt;
        }
        s->cl[s->bufcnt] = -r;
        s->cy[s->bufcnt] = -y;
        s->cr[s->bufcnt] = -l;
        ++s->bufcnt;
    }
    --s->bufcnt;
    *ret_x0 = s->cl[s->bufcnt];
    *ret_y = s->cy[s->bufcnt];
    *ret_x1 = s->cr[s->bufcnt];
    return 0;
}

// Clipping tree consists of half-plane clipping nodes and combining nodes.
// We can throw a horizontal segment in such a tree and collect an ordered set
// of resulting disjoint clipped segments organized into a sorted linked list
// of their end points.
typedef enum {
    CT_AND,  // intersection
    CT_OR,   // union
    CT_CLIP  // half-plane clipping
} clip_type;

typedef struct clip_node {
    clip_type type;
    double a, b, c;       // half-plane coeffs, only used in clipping nodes
    struct clip_node *l;  // child pointers, are only non-NULL in combining nodes
    struct clip_node *r;
} clip_node;

// Linked list for the ends of the clipped horizontal segments.
// Since the segment is always horizontal, we don't need to store Y coordinate.
typedef struct event_list {
    int32_t x;
    int8_t type;  // used internally, 1 for the left end (smaller X), -1 for the
                  // right end; pointless in output since the output segments
                  // are disjoint, therefore the types would always come in pairs
                  // and interchange (1 -1 1 -1 ...)
    struct event_list *next;
} event_list;

// Mirrors all the clipping nodes of the tree relative to the y = x line.
void
clip_tree_transpose(clip_node *root) {
    if (root != NULL) {
        if (root->type == CT_CLIP) {
            double t = root->a;
            root->a = root->b;
            root->b = t;
        }
        clip_tree_transpose(root->l);
        clip_tree_transpose(root->r);
    }
}

// Outputs a sequence of open-close events (types -1 and 1) for
// non-intersecting segments sorted by X coordinate.
// Combining nodes (AND, OR) may also accept sequences for intersecting
// segments, i.e. something like correct bracket sequences.
int
clip_tree_do_clip(
    clip_node *root, int32_t x0, int32_t y, int32_t x1, event_list **ret) {
    if (root == NULL) {
        event_list *start = malloc(sizeof(event_list));
        if (!start) {
            ImagingError_MemoryError();
            return -1;
        }
        event_list *end = malloc(sizeof(event_list));
        if (!end) {
            free(start);
            ImagingError_MemoryError();
            return -1;
        }
        start->x = x0;
        start->type = 1;
        start->next = end;
        end->x = x1;
        end->type = -1;
        end->next = NULL;
        *ret = start;
        return 0;
    }
    if (root->type == CT_CLIP) {
        double eps = 1e-9;
        double A = root->a;
        double B = root->b;
        double C = root->c;
        if (fabs(A) < eps) {
            if (B * y + C < -eps) {
                x0 = 1;
                x1 = 0;
            }
        } else {
            // X of intersection
            double ix = -(B * y + C) / A;
            if (A * x0 + B * y + C < eps) {
                x0 = lround(fmax(x0, ix));
            }
            if (A * x1 + B * y + C < eps) {
                x1 = lround(fmin(x1, ix));
            }
        }
        if (x0 <= x1) {
            event_list *start = malloc(sizeof(event_list));
            if (!start) {
                ImagingError_MemoryError();
                return -1;
            }
            event_list *end = malloc(sizeof(event_list));
            if (!end) {
                free(start);
                ImagingError_MemoryError();
                return -1;
            }
            start->x = x0;
            start->type = 1;
            start->next = end;
            end->x = x1;
            end->type = -1;
            end->next = NULL;
            *ret = start;
        } else {
            *ret = NULL;
        }
        return 0;
    }
    if (root->type == CT_OR || root->type == CT_AND) {
        event_list *l1;
        event_list *l2;
        if (clip_tree_do_clip(root->l, x0, y, x1, &l1) < 0) {
            return -1;
        }
        if (clip_tree_do_clip(root->r, x0, y, x1, &l2) < 0) {
            while (l1) {
                l2 = l1->next;
                free(l1);
                l1 = l2;
            }
            return -1;
        }
        *ret = NULL;
        event_list *tail = NULL;
        int32_t k1 = 0;
        int32_t k2 = 0;
        while (l1 != NULL || l2 != NULL) {
            event_list *t;
            if (l2 == NULL ||
                (l1 != NULL &&
                 (l1->x < l2->x || (l1->x == l2->x && l1->type > l2->type)))) {
                t = l1;
                k1 += t->type;
                assert(k1 >= 0);
                l1 = l1->next;
            } else {
                t = l2;
                k2 += t->type;
                assert(k2 >= 0);
                l2 = l2->next;
            }
            t->next = NULL;
            if ((root->type == CT_OR &&
                 ((t->type == 1 && (tail == NULL || tail->type == -1)) ||
                  (t->type == -1 && k1 == 0 && k2 == 0))) ||
                (root->type == CT_AND &&
                 ((t->type == 1 && (tail == NULL || tail->type == -1) && k1 > 0 &&
                   k2 > 0) ||
                  (t->type == -1 && tail != NULL && tail->type == 1 &&
                   (k1 == 0 || k2 == 0))))) {
                if (tail == NULL) {
                    *ret = t;
                } else {
                    tail->next = t;
                }
                tail = t;
            } else {
                free(t);
            }
        }
        return 0;
    }
    *ret = NULL;
    return 0;
}

// One more layer of processing on top of the regular ellipse.
// Uses the clipping tree.
// Used for producing ellipse derivatives such as arc, chord, pie, etc.
typedef struct {
    ellipse_state st;
    clip_node *root;
    clip_node nodes[7];
    int32_t node_count;
    event_list *head;
    int32_t y;
} clip_ellipse_state;

typedef void (*clip_ellipse_init)(
    clip_ellipse_state *, int32_t, int32_t, int32_t, float, float);

void
debug_clip_tree(clip_node *root, int space) {
    if (root == NULL) {
        return;
    }
    if (root->type == CT_CLIP) {
        int t = space;
        while (t--) {
            fputc(' ', stderr);
        }
        fprintf(stderr, "clip %+fx%+fy%+f > 0\n", root->a, root->b, root->c);
    } else {
        debug_clip_tree(root->l, space + 2);
        int t = space;
        while (t--) {
            fputc(' ', stderr);
        }
        fprintf(stderr, "%s\n", root->type == CT_AND ? "and" : "or");
        debug_clip_tree(root->r, space + 2);
    }
    if (space == 0) {
        fputc('\n', stderr);
    }
}

// Resulting angles will satisfy 0 <= al < 360, al <= ar <= al + 360
void
normalize_angles(float *al, float *ar) {
    if (*ar - *al >= 360) {
        *al = 0;
        *ar = 360;
    } else {
        *al = fmod(*al < 0 ? 360 - (fmod(-*al, 360)) : *al, 360);
        *ar = *al + fmod(*ar < *al ? 360 - fmod(*al - *ar, 360) : *ar - *al, 360);
    }
}

// An arc with caps orthogonal to the ellipse curve.
void
arc_init(clip_ellipse_state *s, int32_t a, int32_t b, int32_t w, float al, float ar) {
    if (a < b) {
        // transpose the coordinate system
        arc_init(s, b, a, w, 90 - ar, 90 - al);
        ellipse_init(&s->st, a, b, w);
        clip_tree_transpose(s->root);
    } else {
        // a >= b, based on "wide" ellipse
        ellipse_init(&s->st, a, b, w);

        s->head = NULL;
        s->node_count = 0;
        normalize_angles(&al, &ar);

        // building clipping tree, a lot of different cases
        if (ar == al + 360) {
            s->root = NULL;
        } else {
            clip_node *lc = s->nodes + s->node_count++;
            clip_node *rc = s->nodes + s->node_count++;
            lc->l = lc->r = rc->l = rc->r = NULL;
            lc->type = rc->type = CT_CLIP;
            lc->a = -a * sin(al * M_PI / 180.0);
            lc->b = b * cos(al * M_PI / 180.0);
            lc->c = (a * a - b * b) * sin(al * M_PI / 90.0) / 2.0;
            rc->a = a * sin(ar * M_PI / 180.0);
            rc->b = -b * cos(ar * M_PI / 180.0);
            rc->c = (b * b - a * a) * sin(ar * M_PI / 90.0) / 2.0;
            if (fmod(al, 180) == 0 || fmod(ar, 180) == 0) {
                s->root = s->nodes + s->node_count++;
                s->root->l = lc;
                s->root->r = rc;
                s->root->type = ar - al < 180 ? CT_AND : CT_OR;
            } else if (((int)(al / 180) + (int)(ar / 180)) % 2 == 1) {
                s->root = s->nodes + s->node_count++;
                s->root->l = s->nodes + s->node_count++;
                s->root->l->l = s->nodes + s->node_count++;
                s->root->l->r = lc;
                s->root->r = s->nodes + s->node_count++;
                s->root->r->l = s->nodes + s->node_count++;
                s->root->r->r = rc;
                s->root->type = CT_OR;
                s->root->l->type = CT_AND;
                s->root->r->type = CT_AND;
                s->root->l->l->type = CT_CLIP;
                s->root->r->l->type = CT_CLIP;
                s->root->l->l->l = s->root->l->l->r = NULL;
                s->root->r->l->l = s->root->r->l->r = NULL;
                s->root->l->l->a = s->root->l->l->c = 0;
                s->root->r->l->a = s->root->r->l->c = 0;
                s->root->l->l->b = (int)(al / 180) % 2 == 0 ? 1 : -1;
                s->root->r->l->b = (int)(ar / 180) % 2 == 0 ? 1 : -1;
            } else {
                s->root = s->nodes + s->node_count++;
                s->root->l = s->nodes + s->node_count++;
                s->root->r = s->nodes + s->node_count++;
                s->root->type = s->root->l->type = ar - al < 180 ? CT_AND : CT_OR;
                s->root->l->l = lc;
                s->root->l->r = rc;
                s->root->r->type = CT_CLIP;
                s->root->r->l = s->root->r->r = NULL;
                s->root->r->a = s->root->r->c = 0;
                s->root->r->b = ar < 180 || ar > 540 ? 1 : -1;
            }
        }
    }
}

// A chord line.
void
chord_line_init(
    clip_ellipse_state *s, int32_t a, int32_t b, int32_t w, float al, float ar) {
    ellipse_init(&s->st, a, b, a + b + 1);

    s->head = NULL;
    s->node_count = 0;

    // line equation for chord
    double xl = a * cos(al * M_PI / 180.0), xr = a * cos(ar * M_PI / 180.0);
    double yl = b * sin(al * M_PI / 180.0), yr = b * sin(ar * M_PI / 180.0);
    s->root = s->nodes + s->node_count++;
    s->root->l = s->nodes + s->node_count++;
    s->root->r = s->nodes + s->node_count++;
    s->root->type = CT_AND;
    s->root->l->type = s->root->r->type = CT_CLIP;
    s->root->l->l = s->root->l->r = s->root->r->l = s->root->r->r = NULL;
    s->root->l->a = yr - yl;
    s->root->l->b = xl - xr;
    s->root->l->c = -(s->root->l->a * xl + s->root->l->b * yl);
    s->root->r->a = -s->root->l->a;
    s->root->r->b = -s->root->l->b;
    s->root->r->c =
        2 * w * sqrt(pow(s->root->l->a, 2.0) + pow(s->root->l->b, 2.0)) - s->root->l->c;
}

// Pie side.
void
pie_side_init(
    clip_ellipse_state *s, int32_t a, int32_t b, int32_t w, float al, float _) {
    ellipse_init(&s->st, a, b, a + b + 1);

    s->head = NULL;
    s->node_count = 0;

    double xl = a * cos(al * M_PI / 180.0);
    double yl = b * sin(al * M_PI / 180.0);
    double a1 = -yl;
    double b1 = xl;
    double c1 = w * sqrt(a1 * a1 + b1 * b1);

    s->root = s->nodes + s->node_count++;
    s->root->type = CT_AND;
    s->root->l = s->nodes + s->node_count++;
    s->root->l->type = CT_AND;

    clip_node *cnode;
    cnode = s->nodes + s->node_count++;
    cnode->l = cnode->r = NULL;
    cnode->type = CT_CLIP;
    cnode->a = a1;
    cnode->b = b1;
    cnode->c = c1;
    s->root->l->l = cnode;
    cnode = s->nodes + s->node_count++;
    cnode->l = cnode->r = NULL;
    cnode->type = CT_CLIP;
    cnode->a = -a1;
    cnode->b = -b1;
    cnode->c = c1;
    s->root->l->r = cnode;
    cnode = s->nodes + s->node_count++;
    cnode->l = cnode->r = NULL;
    cnode->type = CT_CLIP;
    cnode->a = b1;
    cnode->b = -a1;
    cnode->c = 0;
    s->root->r = cnode;
}

// A chord.
void
chord_init(clip_ellipse_state *s, int32_t a, int32_t b, int32_t w, float al, float ar) {
    ellipse_init(&s->st, a, b, w);

    s->head = NULL;
    s->node_count = 0;

    // line equation for chord
    double xl = a * cos(al * M_PI / 180.0), xr = a * cos(ar * M_PI / 180.0);
    double yl = b * sin(al * M_PI / 180.0), yr = b * sin(ar * M_PI / 180.0);
    s->root = s->nodes + s->node_count++;
    s->root->l = s->root->r = NULL;
    s->root->type = CT_CLIP;
    s->root->a = yr - yl;
    s->root->b = xl - xr;
    s->root->c = -(s->root->a * xl + s->root->b * yl);
}

// A pie. Can also be used to draw an arc with ugly sharp caps.
void
pie_init(clip_ellipse_state *s, int32_t a, int32_t b, int32_t w, float al, float ar) {
    ellipse_init(&s->st, a, b, w);

    s->head = NULL;
    s->node_count = 0;

    // line equations for pie sides
    double xl = a * cos(al * M_PI / 180.0), xr = a * cos(ar * M_PI / 180.0);
    double yl = b * sin(al * M_PI / 180.0), yr = b * sin(ar * M_PI / 180.0);

    clip_node *lc = s->nodes + s->node_count++;
    clip_node *rc = s->nodes + s->node_count++;
    lc->l = lc->r = rc->l = rc->r = NULL;
    lc->type = rc->type = CT_CLIP;
    lc->a = -yl;
    lc->b = xl;
    lc->c = 0;
    rc->a = yr;
    rc->b = -xr;
    rc->c = 0;

    s->root = s->nodes + s->node_count++;
    s->root->l = lc;
    s->root->r = rc;
    s->root->type = ar - al < 180 ? CT_AND : CT_OR;

    // add one more semiplane to avoid spikes
    if (ar - al < 90) {
        clip_node *old_root = s->root;
        clip_node *spike_clipper = s->nodes + s->node_count++;
        s->root = s->nodes + s->node_count++;
        s->root->l = old_root;
        s->root->r = spike_clipper;
        s->root->type = CT_AND;

        spike_clipper->l = spike_clipper->r = NULL;
        spike_clipper->type = CT_CLIP;
        spike_clipper->a = (xl + xr) / 2.0;
        spike_clipper->b = (yl + yr) / 2.0;
        spike_clipper->c = 0;
    }
}

void
clip_ellipse_free(clip_ellipse_state *s) {
    while (s->head != NULL) {
        event_list *t = s->head;
        s->head = s->head->next;
        free(t);
    }
}

int8_t
clip_ellipse_next(
    clip_ellipse_state *s, int32_t *ret_x0, int32_t *ret_y, int32_t *ret_x1) {
    int32_t x0, y, x1;
    while (s->head == NULL && ellipse_next(&s->st, &x0, &y, &x1) >= 0) {
        if (clip_tree_do_clip(s->root, x0, y, x1, &s->head) < 0) {
            return -2;
        }
        s->y = y;
    }
    if (s->head != NULL) {
        *ret_y = s->y;
        event_list *t = s->head;
        s->head = s->head->next;
        *ret_x0 = t->x;
        free(t);
        t = s->head;
        assert(t != NULL);
        s->head = s->head->next;
        *ret_x1 = t->x;
        free(t);
        return 0;
    }
    return -1;
}

static int
ellipseNew(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    const void *ink_,
    int fill,
    int width,
    int op) {
    DRAW *draw;
    INT32 ink;
    DRAWINIT();

    int a = x1 - x0;
    int b = y1 - y0;
    if (a < 0 || b < 0) {
        return 0;
    }
    if (fill) {
        width = a + b;
    }

    ellipse_state st;
    ellipse_init(&st, a, b, width);
    int32_t X0, Y, X1;
    while (ellipse_next(&st, &X0, &Y, &X1) != -1) {
        draw->hline(im, x0 + (X0 + a) / 2, y0 + (Y + b) / 2, x0 + (X1 + a) / 2, ink);
    }
    return 0;
}

static int
clipEllipseNew(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    float start,
    float end,
    const void *ink_,
    int width,
    int op,
    clip_ellipse_init init) {
    DRAW *draw;
    INT32 ink;
    DRAWINIT();

    int a = x1 - x0;
    int b = y1 - y0;
    if (a < 0 || b < 0) {
        return 0;
    }

    clip_ellipse_state st;
    init(&st, a, b, width, start, end);
    // debug_clip_tree(st.root, 0);
    int32_t X0, Y, X1;
    int next_code;
    while ((next_code = clip_ellipse_next(&st, &X0, &Y, &X1)) >= 0) {
        draw->hline(im, x0 + (X0 + a) / 2, y0 + (Y + b) / 2, x0 + (X1 + a) / 2, ink);
    }
    clip_ellipse_free(&st);
    return next_code == -1 ? 0 : -1;
}
static int
arcNew(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    float start,
    float end,
    const void *ink_,
    int width,
    int op) {
    return clipEllipseNew(im, x0, y0, x1, y1, start, end, ink_, width, op, arc_init);
}

static int
chordNew(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    float start,
    float end,
    const void *ink_,
    int width,
    int op) {
    return clipEllipseNew(im, x0, y0, x1, y1, start, end, ink_, width, op, chord_init);
}

static int
chordLineNew(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    float start,
    float end,
    const void *ink_,
    int width,
    int op) {
    return clipEllipseNew(
        im, x0, y0, x1, y1, start, end, ink_, width, op, chord_line_init);
}

static int
pieNew(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    float start,
    float end,
    const void *ink_,
    int width,
    int op) {
    return clipEllipseNew(im, x0, y0, x1, y1, start, end, ink_, width, op, pie_init);
}

static int
pieSideNew(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    float start,
    const void *ink_,
    int width,
    int op) {
    return clipEllipseNew(im, x0, y0, x1, y1, start, 0, ink_, width, op, pie_side_init);
}

int
ImagingDrawEllipse(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    const void *ink,
    int fill,
    int width,
    int op) {
    return ellipseNew(im, x0, y0, x1, y1, ink, fill, width, op);
}

int
ImagingDrawArc(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    float start,
    float end,
    const void *ink,
    int width,
    int op) {
    normalize_angles(&start, &end);
    if (start + 360 == end) {
        return ImagingDrawEllipse(im, x0, y0, x1, y1, ink, 0, width, op);
    }
    if (start == end) {
        return 0;
    }
    return arcNew(im, x0, y0, x1, y1, start, end, ink, width, op);
}

int
ImagingDrawChord(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    float start,
    float end,
    const void *ink,
    int fill,
    int width,
    int op) {
    normalize_angles(&start, &end);
    if (start + 360 == end) {
        return ImagingDrawEllipse(im, x0, y0, x1, y1, ink, fill, width, op);
    }
    if (start == end) {
        return 0;
    }
    if (fill) {
        return chordNew(im, x0, y0, x1, y1, start, end, ink, x1 - x0 + y1 - y0 + 1, op);
    } else {
        if (chordLineNew(im, x0, y0, x1, y1, start, end, ink, width, op)) {
            return -1;
        }
        return chordNew(im, x0, y0, x1, y1, start, end, ink, width, op);
    }
}

int
ImagingDrawPieslice(
    Imaging im,
    int x0,
    int y0,
    int x1,
    int y1,
    float start,
    float end,
    const void *ink,
    int fill,
    int width,
    int op) {
    normalize_angles(&start, &end);
    if (start + 360 == end) {
        return ellipseNew(im, x0, y0, x1, y1, ink, fill, width, op);
    }
    if (start == end) {
        return 0;
    }
    if (fill) {
        return pieNew(im, x0, y0, x1, y1, start, end, ink, x1 + y1 - x0 - y0, op);
    } else {
        if (pieSideNew(im, x0, y0, x1, y1, start, ink, width, op)) {
            return -1;
        }
        if (pieSideNew(im, x0, y0, x1, y1, end, ink, width, op)) {
            return -1;
        }
        int xc = lround((x0 + x1 - width) / 2.0), yc = lround((y0 + y1 - width) / 2.0);
        ellipseNew(im, xc, yc, xc + width - 1, yc + width - 1, ink, 1, 0, op);
        return pieNew(im, x0, y0, x1, y1, start, end, ink, width, op);
    }
}

/* -------------------------------------------------------------------- */

/* experimental level 2 ("arrow") graphics stuff.  this implements
   portions of the arrow api on top of the Edge structure.  the
   semantics are ok, except that "curve" flattens the bezier curves by
   itself */

struct ImagingOutlineInstance {
    float x0, y0;

    float x, y;

    int count;
    Edge *edges;

    int size;
};

ImagingOutline
ImagingOutlineNew(void) {
    ImagingOutline outline;

    outline = calloc(1, sizeof(struct ImagingOutlineInstance));
    if (!outline) {
        return (ImagingOutline)ImagingError_MemoryError();
    }

    outline->edges = NULL;
    outline->count = outline->size = 0;

    ImagingOutlineMove(outline, 0, 0);

    return outline;
}

void
ImagingOutlineDelete(ImagingOutline outline) {
    if (!outline) {
        return;
    }

    if (outline->edges) {
        free(outline->edges);
    }

    free(outline);
}

static Edge *
allocate(ImagingOutline outline, int extra) {
    Edge *e;

    if (outline->count + extra > outline->size) {
        /* expand outline buffer */
        outline->size += extra + 25;
        if (!outline->edges) {
            /* malloc check ok, uses calloc for overflow */
            e = calloc(outline->size, sizeof(Edge));
        } else {
            if (outline->size > INT_MAX / (int)sizeof(Edge)) {
                return NULL;
            }
            /* malloc check ok, overflow checked above */
            e = realloc(outline->edges, outline->size * sizeof(Edge));
        }
        if (!e) {
            return NULL;
        }
        outline->edges = e;
    }

    e = outline->edges + outline->count;

    outline->count += extra;

    return e;
}

int
ImagingOutlineMove(ImagingOutline outline, float x0, float y0) {
    outline->x = outline->x0 = x0;
    outline->y = outline->y0 = y0;

    return 0;
}

int
ImagingOutlineLine(ImagingOutline outline, float x1, float y1) {
    Edge *e;

    e = allocate(outline, 1);
    if (!e) {
        return -1; /* out of memory */
    }

    add_edge(e, (int)outline->x, (int)outline->y, (int)x1, (int)y1);

    outline->x = x1;
    outline->y = y1;

    return 0;
}

int
ImagingOutlineCurve(
    ImagingOutline outline,
    float x1,
    float y1,
    float x2,
    float y2,
    float x3,
    float y3) {
    Edge *e;
    int i;
    float xo, yo;

#define STEPS 32

    e = allocate(outline, STEPS);
    if (!e) {
        return -1; /* out of memory */
    }

    xo = outline->x;
    yo = outline->y;

    /* flatten the bezier segment */

    for (i = 1; i <= STEPS; i++) {
        float t = ((float)i) / STEPS;
        float t2 = t * t;
        float t3 = t2 * t;

        float u = 1.0F - t;
        float u2 = u * u;
        float u3 = u2 * u;

        float x = outline->x * u3 + 3 * (x1 * t * u2 + x2 * t2 * u) + x3 * t3 + 0.5;
        float y = outline->y * u3 + 3 * (y1 * t * u2 + y2 * t2 * u) + y3 * t3 + 0.5;

        add_edge(e++, xo, yo, (int)x, (int)y);

        xo = x, yo = y;
    }

    outline->x = xo;
    outline->y = yo;

    return 0;
}

int
ImagingOutlineClose(ImagingOutline outline) {
    if (outline->x == outline->x0 && outline->y == outline->y0) {
        return 0;
    }
    return ImagingOutlineLine(outline, outline->x0, outline->y0);
}

int
ImagingOutlineTransform(ImagingOutline outline, double a[6]) {
    Edge *eIn;
    Edge *eOut;
    int i, n;
    int x0, y0, x1, y1;
    int X0, Y0, X1, Y1;

    double a0 = a[0];
    double a1 = a[1];
    double a2 = a[2];
    double a3 = a[3];
    double a4 = a[4];
    double a5 = a[5];

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
        if (eIn->x0 == eIn->xmin) {
            x1 = eIn->xmax;
        } else {
            x1 = eIn->xmin;
        }
        if (eIn->y0 == eIn->ymin) {
            y1 = eIn->ymax;
        } else {
            y1 = eIn->ymin;
        }

        /* full moon tonight!  if this doesn't work, you may need to
           upgrade your compiler (make sure you have the right service
           pack) */

        X0 = (int)(a0 * x0 + a1 * y0 + a2);
        Y0 = (int)(a3 * x0 + a4 * y0 + a5);
        X1 = (int)(a0 * x1 + a1 * y1 + a2);
        Y1 = (int)(a3 * x1 + a4 * y1 + a5);

        add_edge(eOut, X0, Y0, X1, Y1);

        eIn++;
        eOut++;
    }

    free(eIn);

    return 0;
}

int
ImagingDrawOutline(
    Imaging im, ImagingOutline outline, const void *ink_, int fill, int op) {
    DRAW *draw;
    INT32 ink;

    DRAWINIT();

    draw->polygon(im, outline->count, outline->edges, ink, 0);

    return 0;
}
