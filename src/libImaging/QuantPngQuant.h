#ifndef __QUANT_PNGQUANT_H__
#define __QUANT_PNGQUANT_H__

#include "QuantTypes.h"

int
quantize_pngquant(
    Pixel *,
    unsigned int,
    unsigned int,
    uint32_t,
    Pixel **,
    uint32_t *,
    uint32_t **,
    int);

#endif
