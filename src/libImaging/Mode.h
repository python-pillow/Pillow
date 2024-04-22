#ifndef __MODE_H__
#define __MODE_H__


typedef struct {
    const char * const name;
} Mode;

extern const Mode * const IMAGING_MODE_1;
extern const Mode * const IMAGING_MODE_CMYK;
extern const Mode * const IMAGING_MODE_F;
extern const Mode * const IMAGING_MODE_HSV;
extern const Mode * const IMAGING_MODE_I;
extern const Mode * const IMAGING_MODE_L;
extern const Mode * const IMAGING_MODE_LA;
extern const Mode * const IMAGING_MODE_LAB;
extern const Mode * const IMAGING_MODE_La;
extern const Mode * const IMAGING_MODE_P;
extern const Mode * const IMAGING_MODE_PA;
extern const Mode * const IMAGING_MODE_RGB;
extern const Mode * const IMAGING_MODE_RGBA;
extern const Mode * const IMAGING_MODE_RGBX;
extern const Mode * const IMAGING_MODE_RGBa;
extern const Mode * const IMAGING_MODE_YCbCr;

extern const Mode * const IMAGING_MODE_BGR_15;
extern const Mode * const IMAGING_MODE_BGR_16;
extern const Mode * const IMAGING_MODE_BGR_24;

extern const Mode * const IMAGING_MODE_I_16;
extern const Mode * const IMAGING_MODE_I_16L;
extern const Mode * const IMAGING_MODE_I_16B;
extern const Mode * const IMAGING_MODE_I_16N;
extern const Mode * const IMAGING_MODE_I_32L;
extern const Mode * const IMAGING_MODE_I_32B;

const Mode * findMode(const char * const name);


typedef struct {
    const char * const name;
} RawMode;

// Non-rawmode aliases.
extern const RawMode * const IMAGING_RAWMODE_1;
extern const RawMode * const IMAGING_RAWMODE_CMYK;
extern const RawMode * const IMAGING_RAWMODE_F;
extern const RawMode * const IMAGING_RAWMODE_HSV;
extern const RawMode * const IMAGING_RAWMODE_I;
extern const RawMode * const IMAGING_RAWMODE_L;
extern const RawMode * const IMAGING_RAWMODE_LA;
extern const RawMode * const IMAGING_RAWMODE_LAB;
extern const RawMode * const IMAGING_RAWMODE_La;
extern const RawMode * const IMAGING_RAWMODE_P;
extern const RawMode * const IMAGING_RAWMODE_PA;
extern const RawMode * const IMAGING_RAWMODE_RGB;
extern const RawMode * const IMAGING_RAWMODE_RGBA;
extern const RawMode * const IMAGING_RAWMODE_RGBX;
extern const RawMode * const IMAGING_RAWMODE_RGBa;
extern const RawMode * const IMAGING_RAWMODE_YCbCr;

// BGR modes.
extern const RawMode * const IMAGING_RAWMODE_BGR_15;
extern const RawMode * const IMAGING_RAWMODE_BGR_16;
extern const RawMode * const IMAGING_RAWMODE_BGR_24;
extern const RawMode * const IMAGING_RAWMODE_BGR_32;

// I;* modes.
extern const RawMode * const IMAGING_RAWMODE_I_16;
extern const RawMode * const IMAGING_RAWMODE_I_16L;
extern const RawMode * const IMAGING_RAWMODE_I_16B;
extern const RawMode * const IMAGING_RAWMODE_I_16N;
extern const RawMode * const IMAGING_RAWMODE_I_32L;
extern const RawMode * const IMAGING_RAWMODE_I_32B;

// Rawmodes
extern const RawMode * const IMAGING_RAWMODE_1_8;
extern const RawMode * const IMAGING_RAWMODE_1_I;
extern const RawMode * const IMAGING_RAWMODE_1_IR;
extern const RawMode * const IMAGING_RAWMODE_1_R;
extern const RawMode * const IMAGING_RAWMODE_A;
extern const RawMode * const IMAGING_RAWMODE_ABGR;
extern const RawMode * const IMAGING_RAWMODE_ARGB;
extern const RawMode * const IMAGING_RAWMODE_A_16B;
extern const RawMode * const IMAGING_RAWMODE_A_16L;
extern const RawMode * const IMAGING_RAWMODE_A_16N;
extern const RawMode * const IMAGING_RAWMODE_B;
extern const RawMode * const IMAGING_RAWMODE_BGAR;
extern const RawMode * const IMAGING_RAWMODE_BGR;
extern const RawMode * const IMAGING_RAWMODE_BGRA;
extern const RawMode * const IMAGING_RAWMODE_BGRA_15;
extern const RawMode * const IMAGING_RAWMODE_BGRA_15Z;
extern const RawMode * const IMAGING_RAWMODE_BGRA_16B;
extern const RawMode * const IMAGING_RAWMODE_BGRA_16L;
extern const RawMode * const IMAGING_RAWMODE_BGRX;
extern const RawMode * const IMAGING_RAWMODE_BGR_5;
extern const RawMode * const IMAGING_RAWMODE_BGRa;
extern const RawMode * const IMAGING_RAWMODE_BGXR;
extern const RawMode * const IMAGING_RAWMODE_B_16B;
extern const RawMode * const IMAGING_RAWMODE_B_16L;
extern const RawMode * const IMAGING_RAWMODE_B_16N;
extern const RawMode * const IMAGING_RAWMODE_C;
extern const RawMode * const IMAGING_RAWMODE_CMYKX;
extern const RawMode * const IMAGING_RAWMODE_CMYKXX;
extern const RawMode * const IMAGING_RAWMODE_CMYK_16B;
extern const RawMode * const IMAGING_RAWMODE_CMYK_16L;
extern const RawMode * const IMAGING_RAWMODE_CMYK_16N;
extern const RawMode * const IMAGING_RAWMODE_CMYK_I;
extern const RawMode * const IMAGING_RAWMODE_CMYK_L;
extern const RawMode * const IMAGING_RAWMODE_C_I;
extern const RawMode * const IMAGING_RAWMODE_Cb;
extern const RawMode * const IMAGING_RAWMODE_Cr;
extern const RawMode * const IMAGING_RAWMODE_F_16;
extern const RawMode * const IMAGING_RAWMODE_F_16B;
extern const RawMode * const IMAGING_RAWMODE_F_16BS;
extern const RawMode * const IMAGING_RAWMODE_F_16N;
extern const RawMode * const IMAGING_RAWMODE_F_16NS;
extern const RawMode * const IMAGING_RAWMODE_F_16S;
extern const RawMode * const IMAGING_RAWMODE_F_32;
extern const RawMode * const IMAGING_RAWMODE_F_32B;
extern const RawMode * const IMAGING_RAWMODE_F_32BF;
extern const RawMode * const IMAGING_RAWMODE_F_32BS;
extern const RawMode * const IMAGING_RAWMODE_F_32F;
extern const RawMode * const IMAGING_RAWMODE_F_32N;
extern const RawMode * const IMAGING_RAWMODE_F_32NF;
extern const RawMode * const IMAGING_RAWMODE_F_32NS;
extern const RawMode * const IMAGING_RAWMODE_F_32S;
extern const RawMode * const IMAGING_RAWMODE_F_64BF;
extern const RawMode * const IMAGING_RAWMODE_F_64F;
extern const RawMode * const IMAGING_RAWMODE_F_64NF;
extern const RawMode * const IMAGING_RAWMODE_F_8;
extern const RawMode * const IMAGING_RAWMODE_F_8S;
extern const RawMode * const IMAGING_RAWMODE_G;
extern const RawMode * const IMAGING_RAWMODE_G_16B;
extern const RawMode * const IMAGING_RAWMODE_G_16L;
extern const RawMode * const IMAGING_RAWMODE_G_16N;
extern const RawMode * const IMAGING_RAWMODE_H;
extern const RawMode * const IMAGING_RAWMODE_I_12;
extern const RawMode * const IMAGING_RAWMODE_I_16BS;
extern const RawMode * const IMAGING_RAWMODE_I_16NS;
extern const RawMode * const IMAGING_RAWMODE_I_16R;
extern const RawMode * const IMAGING_RAWMODE_I_16S;
extern const RawMode * const IMAGING_RAWMODE_I_32;
extern const RawMode * const IMAGING_RAWMODE_I_32BS;
extern const RawMode * const IMAGING_RAWMODE_I_32N;
extern const RawMode * const IMAGING_RAWMODE_I_32NS;
extern const RawMode * const IMAGING_RAWMODE_I_32S;
extern const RawMode * const IMAGING_RAWMODE_I_8;
extern const RawMode * const IMAGING_RAWMODE_I_8S;
extern const RawMode * const IMAGING_RAWMODE_K;
extern const RawMode * const IMAGING_RAWMODE_K_I;
extern const RawMode * const IMAGING_RAWMODE_LA_16B;
extern const RawMode * const IMAGING_RAWMODE_LA_L;
extern const RawMode * const IMAGING_RAWMODE_L_16;
extern const RawMode * const IMAGING_RAWMODE_L_16B;
extern const RawMode * const IMAGING_RAWMODE_L_2;
extern const RawMode * const IMAGING_RAWMODE_L_2I;
extern const RawMode * const IMAGING_RAWMODE_L_2IR;
extern const RawMode * const IMAGING_RAWMODE_L_2R;
extern const RawMode * const IMAGING_RAWMODE_L_4;
extern const RawMode * const IMAGING_RAWMODE_L_4I;
extern const RawMode * const IMAGING_RAWMODE_L_4IR;
extern const RawMode * const IMAGING_RAWMODE_L_4R;
extern const RawMode * const IMAGING_RAWMODE_L_I;
extern const RawMode * const IMAGING_RAWMODE_L_R;
extern const RawMode * const IMAGING_RAWMODE_M;
extern const RawMode * const IMAGING_RAWMODE_M_I;
extern const RawMode * const IMAGING_RAWMODE_PA_L;
extern const RawMode * const IMAGING_RAWMODE_PX;
extern const RawMode * const IMAGING_RAWMODE_P_1;
extern const RawMode * const IMAGING_RAWMODE_P_2;
extern const RawMode * const IMAGING_RAWMODE_P_2L;
extern const RawMode * const IMAGING_RAWMODE_P_4;
extern const RawMode * const IMAGING_RAWMODE_P_4L;
extern const RawMode * const IMAGING_RAWMODE_P_R;
extern const RawMode * const IMAGING_RAWMODE_R;
extern const RawMode * const IMAGING_RAWMODE_RGBAX;
extern const RawMode * const IMAGING_RAWMODE_RGBAXX;
extern const RawMode * const IMAGING_RAWMODE_RGBA_15;
extern const RawMode * const IMAGING_RAWMODE_RGBA_16B;
extern const RawMode * const IMAGING_RAWMODE_RGBA_16L;
extern const RawMode * const IMAGING_RAWMODE_RGBA_16N;
extern const RawMode * const IMAGING_RAWMODE_RGBA_4B;
extern const RawMode * const IMAGING_RAWMODE_RGBA_I;
extern const RawMode * const IMAGING_RAWMODE_RGBA_L;
extern const RawMode * const IMAGING_RAWMODE_RGBXX;
extern const RawMode * const IMAGING_RAWMODE_RGBXXX;
extern const RawMode * const IMAGING_RAWMODE_RGBX_16B;
extern const RawMode * const IMAGING_RAWMODE_RGBX_16L;
extern const RawMode * const IMAGING_RAWMODE_RGBX_16N;
extern const RawMode * const IMAGING_RAWMODE_RGBX_L;
extern const RawMode * const IMAGING_RAWMODE_RGB_15;
extern const RawMode * const IMAGING_RAWMODE_RGB_16;
extern const RawMode * const IMAGING_RAWMODE_RGB_16B;
extern const RawMode * const IMAGING_RAWMODE_RGB_16L;
extern const RawMode * const IMAGING_RAWMODE_RGB_16N;
extern const RawMode * const IMAGING_RAWMODE_RGB_4B;
extern const RawMode * const IMAGING_RAWMODE_RGB_L;
extern const RawMode * const IMAGING_RAWMODE_RGB_R;
extern const RawMode * const IMAGING_RAWMODE_RGBaX;
extern const RawMode * const IMAGING_RAWMODE_RGBaXX;
extern const RawMode * const IMAGING_RAWMODE_RGBa_16B;
extern const RawMode * const IMAGING_RAWMODE_RGBa_16L;
extern const RawMode * const IMAGING_RAWMODE_RGBa_16N;
extern const RawMode * const IMAGING_RAWMODE_R_16B;
extern const RawMode * const IMAGING_RAWMODE_R_16L;
extern const RawMode * const IMAGING_RAWMODE_R_16N;
extern const RawMode * const IMAGING_RAWMODE_S;
extern const RawMode * const IMAGING_RAWMODE_V;
extern const RawMode * const IMAGING_RAWMODE_X;
extern const RawMode * const IMAGING_RAWMODE_XBGR;
extern const RawMode * const IMAGING_RAWMODE_XRGB;
extern const RawMode * const IMAGING_RAWMODE_Y;
extern const RawMode * const IMAGING_RAWMODE_YCCA_P;
extern const RawMode * const IMAGING_RAWMODE_YCC_P;
extern const RawMode * const IMAGING_RAWMODE_YCbCrK;
extern const RawMode * const IMAGING_RAWMODE_YCbCrX;
extern const RawMode * const IMAGING_RAWMODE_YCbCr_L;
extern const RawMode * const IMAGING_RAWMODE_Y_I;
extern const RawMode * const IMAGING_RAWMODE_aBGR;
extern const RawMode * const IMAGING_RAWMODE_aRGB;

const RawMode * findRawMode(const char * const name);


int isModeI16(const Mode * const mode);

#endif // __MODE_H__
