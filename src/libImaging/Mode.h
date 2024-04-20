#ifndef __MODE_H__
#define __MODE_H__


// Maximum length (including null terminator) for both mode and rawmode names.
#define IMAGING_MODE_LENGTH 6+1


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

const Mode * findMode(const char * const name);


typedef struct {
    const char * const name;
} RawMode;

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

extern const RawMode * const IMAGING_RAWMODE_BGR_15;
extern const RawMode * const IMAGING_RAWMODE_BGR_16;

const RawMode * findRawMode(const char * const name);


#endif // __MODE_H__
