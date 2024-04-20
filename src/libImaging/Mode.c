#include "Mode.h"
#include <string.h>


#define CREATE_MODE(TYPE, NAME, INIT) \
const TYPE IMAGING_##NAME##_VAL = INIT;\
const TYPE * const IMAGING_##NAME = &IMAGING_##NAME##_VAL;


CREATE_MODE(Mode, MODE_1, {"1"})
CREATE_MODE(Mode, MODE_CMYK, {"CMYK"})
CREATE_MODE(Mode, MODE_F, {"F"})
CREATE_MODE(Mode, MODE_HSV, {"HSV"})
CREATE_MODE(Mode, MODE_I, {"I"})
CREATE_MODE(Mode, MODE_L, {"L"})
CREATE_MODE(Mode, MODE_LA, {"LA"})
CREATE_MODE(Mode, MODE_LAB, {"LAB"})
CREATE_MODE(Mode, MODE_La, {"La"})
CREATE_MODE(Mode, MODE_P, {"P"})
CREATE_MODE(Mode, MODE_PA, {"PA"})
CREATE_MODE(Mode, MODE_RGB, {"RGB"})
CREATE_MODE(Mode, MODE_RGBA, {"RGBA"})
CREATE_MODE(Mode, MODE_RGBX, {"RGBX"})
CREATE_MODE(Mode, MODE_RGBa, {"RGBa"})
CREATE_MODE(Mode, MODE_YCbCr, {"YCbCr"})

const Mode * const MODES[] = {
    IMAGING_MODE_1,
    IMAGING_MODE_CMYK,
    IMAGING_MODE_F,
    IMAGING_MODE_HSV,
    IMAGING_MODE_I,
    IMAGING_MODE_L,
    IMAGING_MODE_LA,
    IMAGING_MODE_LAB,
    IMAGING_MODE_La,
    IMAGING_MODE_P,
    IMAGING_MODE_PA,
    IMAGING_MODE_RGB,
    IMAGING_MODE_RGBA,
    IMAGING_MODE_RGBX,
    IMAGING_MODE_RGBa,
    IMAGING_MODE_YCbCr,
    NULL
};

const Mode * findMode(const char * const name) {
    int i = 0;
    const Mode * mode;
    while ((mode = MODES[i++]) != NULL) {
        if (!strcmp(mode->name, name)) {
            return mode;
        }
    }
    return NULL;
}


// Alias all of the modes as rawmodes so that the addresses are the same.
#define ALIAS_MODE_AS_RAWMODE(NAME) const RawMode * const IMAGING_RAWMODE_##NAME = (const RawMode * const)IMAGING_MODE_##NAME;
ALIAS_MODE_AS_RAWMODE(1)
ALIAS_MODE_AS_RAWMODE(CMYK)
ALIAS_MODE_AS_RAWMODE(F)
ALIAS_MODE_AS_RAWMODE(HSV)
ALIAS_MODE_AS_RAWMODE(I)
ALIAS_MODE_AS_RAWMODE(L)
ALIAS_MODE_AS_RAWMODE(LA)
ALIAS_MODE_AS_RAWMODE(LAB)
ALIAS_MODE_AS_RAWMODE(La)
ALIAS_MODE_AS_RAWMODE(P)
ALIAS_MODE_AS_RAWMODE(PA)
ALIAS_MODE_AS_RAWMODE(RGB)
ALIAS_MODE_AS_RAWMODE(RGBA)
ALIAS_MODE_AS_RAWMODE(RGBX)
ALIAS_MODE_AS_RAWMODE(RGBa)
ALIAS_MODE_AS_RAWMODE(YCbCr)

CREATE_MODE(RawMode, RAWMODE_BGR_15, {"BGR;15"})
CREATE_MODE(RawMode, RAWMODE_BGR_16, {"BGR;16"})

const RawMode * const RAWMODES[] = {
    IMAGING_RAWMODE_1,
    IMAGING_RAWMODE_CMYK,
    IMAGING_RAWMODE_F,
    IMAGING_RAWMODE_HSV,
    IMAGING_RAWMODE_I,
    IMAGING_RAWMODE_L,
    IMAGING_RAWMODE_LA,
    IMAGING_RAWMODE_LAB,
    IMAGING_RAWMODE_La,
    IMAGING_RAWMODE_P,
    IMAGING_RAWMODE_PA,
    IMAGING_RAWMODE_RGB,
    IMAGING_RAWMODE_RGBA,
    IMAGING_RAWMODE_RGBX,
    IMAGING_RAWMODE_RGBa,
    IMAGING_RAWMODE_YCbCr,

    IMAGING_RAWMODE_BGR_15,
    IMAGING_RAWMODE_BGR_16,

    NULL
};

const RawMode * findRawMode(const char * const name) {
    int i = 0;
    const RawMode * rawmode;
    while ((rawmode = RAWMODES[i++]) != NULL) {
        const RawMode * const rawmode = RAWMODES[i];
        if (!strcmp(rawmode->name, name)) {
            return rawmode;
        }
    }
    return NULL;
}
