/* Copyright (c) 2010 Oliver Tonnhofer <olt@bogosoft.com>, Omniscale
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
*/

/*
// This file implements a quantization using libimagequant, a part of pngquant.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "QuantPngQuant.h"

#ifdef HAVE_LIBIMAGEQUANT
#include "libimagequant.h"

int
quantize_pngquant(
    Pixel *pixelData,
    uint32_t width,
    uint32_t height,
    uint32_t quantPixels,
    Pixel **palette,
    uint32_t *paletteLength,
    uint32_t **quantizedPixels,
    int withAlpha)
{
    int result = 0;
    liq_image *image = NULL;
    liq_attr *attr = NULL;
    liq_result *remap = NULL;
    unsigned char *charMatrix = NULL;
    unsigned char **charMatrixRows = NULL;
    unsigned int i, y;
    *palette = NULL;
    *paletteLength = 0;
    *quantizedPixels = NULL;

    /* configure pngquant */
    attr = liq_attr_create();
    if (!attr) { goto err; }
    if (quantPixels) {
        liq_set_max_colors(attr, quantPixels);
    }

    /* prepare input image */
    image = liq_image_create_rgba(
        attr,
        pixelData,
        width,
        height,
        0.45455 /* gamma */);
    if (!image) { goto err; }

    /* quantize the image */
    remap = liq_quantize_image(attr, image);
    if (!remap) { goto err; }
    liq_set_output_gamma(remap, 0.45455);
    liq_set_dithering_level(remap, 1);

    /* write output palette */
    const liq_palette *l_palette = liq_get_palette(remap);
    *paletteLength = l_palette->count;
    *palette = malloc(sizeof(Pixel) * l_palette->count);
    if (!*palette) { goto err; }
    for (i = 0; i < l_palette->count; i++) {
        (*palette)[i].c.b = l_palette->entries[i].b;
        (*palette)[i].c.g = l_palette->entries[i].g;
        (*palette)[i].c.r = l_palette->entries[i].r;
        (*palette)[i].c.a = l_palette->entries[i].a;
    }

    /* write output pixels (pngquant uses char array) */
    charMatrix = malloc(width * height);
    if (!charMatrix) { goto err; }
    charMatrixRows = malloc(height * sizeof(unsigned char*));
    if (!charMatrixRows) { goto err; }
    for (y = 0; y < height; y++) {
        charMatrixRows[y] = &charMatrix[y * width];
    }
    if (LIQ_OK != liq_write_remapped_image_rows(remap, image, charMatrixRows)) {
        goto err;
    }

    /* transcribe output pixels (pillow uses uint32_t array) */
    *quantizedPixels = malloc(sizeof(uint32_t) * width * height);
    if (!*quantizedPixels) { goto err; }
    for (i = 0; i < width * height; i++) {
        (*quantizedPixels)[i] = charMatrix[i];
    }

    result = 1;

err:
    if (attr) liq_attr_destroy(attr);
    if (image) liq_image_destroy(image);
    if (remap) liq_result_destroy(remap);
    free(charMatrix);
    free(charMatrixRows);
    if (!result)  {
        free(*quantizedPixels);
        free(*palette);
    }
    return result;
}

#endif
