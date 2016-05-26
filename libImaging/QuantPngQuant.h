#ifndef __QUANT_PNGQUANT_H__
#define __QUANT_PNGQUANT_H__

#include "QuantTypes.h"

int quantize_pngquant(Pixel *,
    int,
    int,
    uint32_t,
    Pixel **,
    uint32_t *,
    uint32_t **,
    int);

#endif
