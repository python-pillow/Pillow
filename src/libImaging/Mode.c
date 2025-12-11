#include "Mode.h"
#include <string.h>

#ifdef NDEBUG
#include <stdio.h>
#include <stdlib.h>
#endif

const ModeData MODES[] = {
    [IMAGING_MODE_UNKNOWN] = {""},

    [IMAGING_MODE_1] = {"1"},         [IMAGING_MODE_CMYK] = {"CMYK"},
    [IMAGING_MODE_F] = {"F"},         [IMAGING_MODE_HSV] = {"HSV"},
    [IMAGING_MODE_I] = {"I"},         [IMAGING_MODE_L] = {"L"},
    [IMAGING_MODE_LA] = {"LA"},       [IMAGING_MODE_LAB] = {"LAB"},
    [IMAGING_MODE_La] = {"La"},       [IMAGING_MODE_P] = {"P"},
    [IMAGING_MODE_PA] = {"PA"},       [IMAGING_MODE_RGB] = {"RGB"},
    [IMAGING_MODE_RGBA] = {"RGBA"},   [IMAGING_MODE_RGBX] = {"RGBX"},
    [IMAGING_MODE_RGBa] = {"RGBa"},   [IMAGING_MODE_YCbCr] = {"YCbCr"},

    [IMAGING_MODE_I_16] = {"I;16"},   [IMAGING_MODE_I_16L] = {"I;16L"},
    [IMAGING_MODE_I_16B] = {"I;16B"}, [IMAGING_MODE_I_16N] = {"I;16N"},
};

const ModeID
findModeID(const char *const name) {
    if (name == NULL) {
        return IMAGING_MODE_UNKNOWN;
    }
    for (size_t i = 0; i < sizeof(MODES) / sizeof(*MODES); i++) {
#ifdef NDEBUG
        if (MODES[i].name == NULL) {
            fprintf(stderr, "Mode ID %zu is not defined.\n", (size_t)i);
        } else
#endif
            if (strcmp(MODES[i].name, name) == 0) {
            return (ModeID)i;
        }
    }
    return IMAGING_MODE_UNKNOWN;
}

const ModeData *const
getModeData(const ModeID id) {
    if (id < 0 || id > sizeof(MODES) / sizeof(*MODES)) {
        return &MODES[IMAGING_MODE_UNKNOWN];
    }
    return &MODES[id];
}

const RawModeData RAWMODES[] = {
    [IMAGING_RAWMODE_UNKNOWN] = {""},

    [IMAGING_RAWMODE_1] = {"1"},
    [IMAGING_RAWMODE_CMYK] = {"CMYK"},
    [IMAGING_RAWMODE_F] = {"F"},
    [IMAGING_RAWMODE_HSV] = {"HSV"},
    [IMAGING_RAWMODE_I] = {"I"},
    [IMAGING_RAWMODE_L] = {"L"},
    [IMAGING_RAWMODE_LA] = {"LA"},
    [IMAGING_RAWMODE_LAB] = {"LAB"},
    [IMAGING_RAWMODE_La] = {"La"},
    [IMAGING_RAWMODE_P] = {"P"},
    [IMAGING_RAWMODE_PA] = {"PA"},
    [IMAGING_RAWMODE_RGB] = {"RGB"},
    [IMAGING_RAWMODE_RGBA] = {"RGBA"},
    [IMAGING_RAWMODE_RGBX] = {"RGBX"},
    [IMAGING_RAWMODE_RGBa] = {"RGBa"},
    [IMAGING_RAWMODE_YCbCr] = {"YCbCr"},

    [IMAGING_RAWMODE_BGR_15] = {"BGR;15"},
    [IMAGING_RAWMODE_BGR_16] = {"BGR;16"},

    [IMAGING_RAWMODE_I_16] = {"I;16"},
    [IMAGING_RAWMODE_I_16L] = {"I;16L"},
    [IMAGING_RAWMODE_I_16B] = {"I;16B"},
    [IMAGING_RAWMODE_I_16N] = {"I;16N"},
    [IMAGING_RAWMODE_I_32B] = {"I;32B"},

    [IMAGING_RAWMODE_1_8] = {"1;8"},
    [IMAGING_RAWMODE_1_I] = {"1;I"},
    [IMAGING_RAWMODE_1_IR] = {"1;IR"},
    [IMAGING_RAWMODE_1_R] = {"1;R"},
    [IMAGING_RAWMODE_A] = {"A"},
    [IMAGING_RAWMODE_ABGR] = {"ABGR"},
    [IMAGING_RAWMODE_ARGB] = {"ARGB"},
    [IMAGING_RAWMODE_A_16B] = {"A;16B"},
    [IMAGING_RAWMODE_A_16L] = {"A;16L"},
    [IMAGING_RAWMODE_A_16N] = {"A;16N"},
    [IMAGING_RAWMODE_B] = {"B"},
    [IMAGING_RAWMODE_BGAR] = {"BGAR"},
    [IMAGING_RAWMODE_BGR] = {"BGR"},
    [IMAGING_RAWMODE_BGRA] = {"BGRA"},
    [IMAGING_RAWMODE_BGRA_15] = {"BGRA;15"},
    [IMAGING_RAWMODE_BGRA_15Z] = {"BGRA;15Z"},
    [IMAGING_RAWMODE_BGRA_16B] = {"BGRA;16B"},
    [IMAGING_RAWMODE_BGRA_16L] = {"BGRA;16L"},
    [IMAGING_RAWMODE_BGRX] = {"BGRX"},
    [IMAGING_RAWMODE_BGR_5] = {"BGR;5"},
    [IMAGING_RAWMODE_BGRa] = {"BGRa"},
    [IMAGING_RAWMODE_BGXR] = {"BGXR"},
    [IMAGING_RAWMODE_B_16B] = {"B;16B"},
    [IMAGING_RAWMODE_B_16L] = {"B;16L"},
    [IMAGING_RAWMODE_B_16N] = {"B;16N"},
    [IMAGING_RAWMODE_C] = {"C"},
    [IMAGING_RAWMODE_CMYKX] = {"CMYKX"},
    [IMAGING_RAWMODE_CMYKXX] = {"CMYKXX"},
    [IMAGING_RAWMODE_CMYK_16B] = {"CMYK;16B"},
    [IMAGING_RAWMODE_CMYK_16L] = {"CMYK;16L"},
    [IMAGING_RAWMODE_CMYK_16N] = {"CMYK;16N"},
    [IMAGING_RAWMODE_CMYK_I] = {"CMYK;I"},
    [IMAGING_RAWMODE_CMYK_L] = {"CMYK;L"},
    [IMAGING_RAWMODE_C_I] = {"C;I"},
    [IMAGING_RAWMODE_Cb] = {"Cb"},
    [IMAGING_RAWMODE_Cr] = {"Cr"},
    [IMAGING_RAWMODE_F_16] = {"F;16"},
    [IMAGING_RAWMODE_F_16B] = {"F;16B"},
    [IMAGING_RAWMODE_F_16BS] = {"F;16BS"},
    [IMAGING_RAWMODE_F_16N] = {"F;16N"},
    [IMAGING_RAWMODE_F_16NS] = {"F;16NS"},
    [IMAGING_RAWMODE_F_16S] = {"F;16S"},
    [IMAGING_RAWMODE_F_32] = {"F;32"},
    [IMAGING_RAWMODE_F_32B] = {"F;32B"},
    [IMAGING_RAWMODE_F_32BF] = {"F;32BF"},
    [IMAGING_RAWMODE_F_32BS] = {"F;32BS"},
    [IMAGING_RAWMODE_F_32F] = {"F;32F"},
    [IMAGING_RAWMODE_F_32N] = {"F;32N"},
    [IMAGING_RAWMODE_F_32NF] = {"F;32NF"},
    [IMAGING_RAWMODE_F_32NS] = {"F;32NS"},
    [IMAGING_RAWMODE_F_32S] = {"F;32S"},
    [IMAGING_RAWMODE_F_64BF] = {"F;64BF"},
    [IMAGING_RAWMODE_F_64F] = {"F;64F"},
    [IMAGING_RAWMODE_F_64NF] = {"F;64NF"},
    [IMAGING_RAWMODE_F_8] = {"F;8"},
    [IMAGING_RAWMODE_F_8S] = {"F;8S"},
    [IMAGING_RAWMODE_G] = {"G"},
    [IMAGING_RAWMODE_G_16B] = {"G;16B"},
    [IMAGING_RAWMODE_G_16L] = {"G;16L"},
    [IMAGING_RAWMODE_G_16N] = {"G;16N"},
    [IMAGING_RAWMODE_H] = {"H"},
    [IMAGING_RAWMODE_I_12] = {"I;12"},
    [IMAGING_RAWMODE_I_16BS] = {"I;16BS"},
    [IMAGING_RAWMODE_I_16NS] = {"I;16NS"},
    [IMAGING_RAWMODE_I_16R] = {"I;16R"},
    [IMAGING_RAWMODE_I_16S] = {"I;16S"},
    [IMAGING_RAWMODE_I_32] = {"I;32"},
    [IMAGING_RAWMODE_I_32BS] = {"I;32BS"},
    [IMAGING_RAWMODE_I_32N] = {"I;32N"},
    [IMAGING_RAWMODE_I_32NS] = {"I;32NS"},
    [IMAGING_RAWMODE_I_32S] = {"I;32S"},
    [IMAGING_RAWMODE_I_8] = {"I;8"},
    [IMAGING_RAWMODE_I_8S] = {"I;8S"},
    [IMAGING_RAWMODE_K] = {"K"},
    [IMAGING_RAWMODE_K_I] = {"K;I"},
    [IMAGING_RAWMODE_LA_16B] = {"LA;16B"},
    [IMAGING_RAWMODE_LA_L] = {"LA;L"},
    [IMAGING_RAWMODE_L_16] = {"L;16"},
    [IMAGING_RAWMODE_L_16B] = {"L;16B"},
    [IMAGING_RAWMODE_L_2] = {"L;2"},
    [IMAGING_RAWMODE_L_2I] = {"L;2I"},
    [IMAGING_RAWMODE_L_2IR] = {"L;2IR"},
    [IMAGING_RAWMODE_L_2R] = {"L;2R"},
    [IMAGING_RAWMODE_L_4] = {"L;4"},
    [IMAGING_RAWMODE_L_4I] = {"L;4I"},
    [IMAGING_RAWMODE_L_4IR] = {"L;4IR"},
    [IMAGING_RAWMODE_L_4R] = {"L;4R"},
    [IMAGING_RAWMODE_L_I] = {"L;I"},
    [IMAGING_RAWMODE_L_R] = {"L;R"},
    [IMAGING_RAWMODE_M] = {"M"},
    [IMAGING_RAWMODE_M_I] = {"M;I"},
    [IMAGING_RAWMODE_PA_L] = {"PA;L"},
    [IMAGING_RAWMODE_PX] = {"PX"},
    [IMAGING_RAWMODE_P_1] = {"P;1"},
    [IMAGING_RAWMODE_P_2] = {"P;2"},
    [IMAGING_RAWMODE_P_2L] = {"P;2L"},
    [IMAGING_RAWMODE_P_4] = {"P;4"},
    [IMAGING_RAWMODE_P_4L] = {"P;4L"},
    [IMAGING_RAWMODE_P_R] = {"P;R"},
    [IMAGING_RAWMODE_R] = {"R"},
    [IMAGING_RAWMODE_RGBAX] = {"RGBAX"},
    [IMAGING_RAWMODE_RGBAXX] = {"RGBAXX"},
    [IMAGING_RAWMODE_RGBA_15] = {"RGBA;15"},
    [IMAGING_RAWMODE_RGBA_16B] = {"RGBA;16B"},
    [IMAGING_RAWMODE_RGBA_16L] = {"RGBA;16L"},
    [IMAGING_RAWMODE_RGBA_16N] = {"RGBA;16N"},
    [IMAGING_RAWMODE_RGBA_4B] = {"RGBA;4B"},
    [IMAGING_RAWMODE_RGBA_I] = {"RGBA;I"},
    [IMAGING_RAWMODE_RGBA_L] = {"RGBA;L"},
    [IMAGING_RAWMODE_RGBXX] = {"RGBXX"},
    [IMAGING_RAWMODE_RGBXXX] = {"RGBXXX"},
    [IMAGING_RAWMODE_RGBX_16B] = {"RGBX;16B"},
    [IMAGING_RAWMODE_RGBX_16L] = {"RGBX;16L"},
    [IMAGING_RAWMODE_RGBX_16N] = {"RGBX;16N"},
    [IMAGING_RAWMODE_RGBX_L] = {"RGBX;L"},
    [IMAGING_RAWMODE_RGB_15] = {"RGB;15"},
    [IMAGING_RAWMODE_RGB_16] = {"RGB;16"},
    [IMAGING_RAWMODE_RGB_16B] = {"RGB;16B"},
    [IMAGING_RAWMODE_RGB_16L] = {"RGB;16L"},
    [IMAGING_RAWMODE_RGB_16N] = {"RGB;16N"},
    [IMAGING_RAWMODE_RGB_4B] = {"RGB;4B"},
    [IMAGING_RAWMODE_RGB_L] = {"RGB;L"},
    [IMAGING_RAWMODE_RGB_R] = {"RGB;R"},
    [IMAGING_RAWMODE_RGBaX] = {"RGBaX"},
    [IMAGING_RAWMODE_RGBaXX] = {"RGBaXX"},
    [IMAGING_RAWMODE_RGBa_16B] = {"RGBa;16B"},
    [IMAGING_RAWMODE_RGBa_16L] = {"RGBa;16L"},
    [IMAGING_RAWMODE_RGBa_16N] = {"RGBa;16N"},
    [IMAGING_RAWMODE_R_16B] = {"R;16B"},
    [IMAGING_RAWMODE_R_16L] = {"R;16L"},
    [IMAGING_RAWMODE_R_16N] = {"R;16N"},
    [IMAGING_RAWMODE_S] = {"S"},
    [IMAGING_RAWMODE_V] = {"V"},
    [IMAGING_RAWMODE_X] = {"X"},
    [IMAGING_RAWMODE_XBGR] = {"XBGR"},
    [IMAGING_RAWMODE_XRGB] = {"XRGB"},
    [IMAGING_RAWMODE_Y] = {"Y"},
    [IMAGING_RAWMODE_YCCA_P] = {"YCCA;P"},
    [IMAGING_RAWMODE_YCC_P] = {"YCC;P"},
    [IMAGING_RAWMODE_YCbCrK] = {"YCbCrK"},
    [IMAGING_RAWMODE_YCbCrX] = {"YCbCrX"},
    [IMAGING_RAWMODE_YCbCr_L] = {"YCbCr;L"},
    [IMAGING_RAWMODE_Y_I] = {"Y;I"},
    [IMAGING_RAWMODE_aBGR] = {"aBGR"},
    [IMAGING_RAWMODE_aRGB] = {"aRGB"},
};

const RawModeID
findRawModeID(const char *const name) {
    if (name == NULL) {
        return IMAGING_RAWMODE_UNKNOWN;
    }
    for (size_t i = 0; i < sizeof(RAWMODES) / sizeof(*RAWMODES); i++) {
#ifdef NDEBUG
        if (RAWMODES[i].name == NULL) {
            fprintf(stderr, "Rawmode ID %zu is not defined.\n", (size_t)i);
        } else
#endif
            if (strcmp(RAWMODES[i].name, name) == 0) {
            return (RawModeID)i;
        }
    }
    return IMAGING_RAWMODE_UNKNOWN;
}

const RawModeData *const
getRawModeData(const RawModeID id) {
    if (id < 0 || id > sizeof(RAWMODES) / sizeof(*RAWMODES)) {
        return &RAWMODES[IMAGING_RAWMODE_UNKNOWN];
    }
    return &RAWMODES[id];
}

int
isModeI16(const ModeID mode) {
    return mode == IMAGING_MODE_I_16 || mode == IMAGING_MODE_I_16L ||
           mode == IMAGING_MODE_I_16B || mode == IMAGING_MODE_I_16N;
}
