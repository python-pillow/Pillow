/*
 * pyCMS
 * a Python / PIL interface to the littleCMS ICC Color Management System
 * Copyright (C) 2002-2003 Kevin Cazabon
 * kevin@cazabon.com
 * https://www.cazabon.com
 * Adapted/reworked for PIL by Fredrik Lundh
 * Copyright (c) 2009 Fredrik Lundh
 * Updated to LCMS2
 * Copyright (c) 2013 Eric Soroos
 *
 * pyCMS home page:  https://www.cazabon.com/pyCMS
 * littleCMS home page:  https://www.littlecms.com
 * (littleCMS is Copyright (C) 1998-2001 Marti Maria)
 *
 * Originally released under LGPL.  Graciously donated to PIL in
 * March 2009, for distribution under the standard PIL license
 */

#define COPYRIGHTINFO \
    "\
pyCMS\n\
a Python / PIL interface to the littleCMS ICC Color Management System\n\
Copyright (C) 2002-2003 Kevin Cazabon\n\
kevin@cazabon.com\n\
https://www.cazabon.com\n\
"

#define PY_SSIZE_T_CLEAN
#include "Python.h"  // Include before wchar.h so _GNU_SOURCE is set
#include "wchar.h"
#include "datetime.h"

#include "lcms2.h"
#include "libImaging/Imaging.h"

#define PYCMSVERSION "1.0.0 pil"

/* version history */

/*
  1.0.0 pil Integrating littleCMS2
  0.1.0 pil integration & refactoring
  0.0.2 alpha:  Minor updates, added interfaces to littleCMS features, Jan 6, 2003
  - fixed some memory holes in how transforms/profiles were created and passed back to
  Python due to improper destructor setup for PyCObjects
  - added buildProofTransformFromOpenProfiles() function
  - eliminated some code redundancy, centralizing several common tasks with internal
  functions

  0.0.1 alpha:  First public release Dec 26, 2002

*/

/* known to-do list with current version:

   Verify that PILmode->littleCMStype conversion in findLCMStype is correct for all
   PIL modes (it probably isn't for the more obscure ones)

   Add support for creating custom RGB profiles on the fly
   Add support for checking presence of a specific tag in a profile
   Add support for other littleCMS features as required

*/

/*
  INTENT_PERCEPTUAL                 0
  INTENT_RELATIVE_COLORIMETRIC      1
  INTENT_SATURATION                 2
  INTENT_ABSOLUTE_COLORIMETRIC      3
*/

/* -------------------------------------------------------------------- */
/* wrapper classes */

/* a profile represents the ICC characteristics for a specific device */

typedef struct {
    PyObject_HEAD cmsHPROFILE profile;
} CmsProfileObject;

static PyTypeObject CmsProfile_Type;

#define CmsProfile_Check(op) (Py_TYPE(op) == &CmsProfile_Type)

static PyObject *
cms_profile_new(cmsHPROFILE profile) {
    CmsProfileObject *self;

    self = PyObject_New(CmsProfileObject, &CmsProfile_Type);
    if (!self) {
        return NULL;
    }

    self->profile = profile;

    return (PyObject *)self;
}

static PyObject *
cms_profile_open(PyObject *self, PyObject *args) {
    cmsHPROFILE hProfile;

    char *sProfile;
    if (!PyArg_ParseTuple(args, "s:profile_open", &sProfile)) {
        return NULL;
    }

    hProfile = cmsOpenProfileFromFile(sProfile, "r");
    if (!hProfile) {
        PyErr_SetString(PyExc_OSError, "cannot open profile file");
        return NULL;
    }

    return cms_profile_new(hProfile);
}

static PyObject *
cms_profile_frombytes(PyObject *self, PyObject *args) {
    cmsHPROFILE hProfile;

    char *pProfile;
    Py_ssize_t nProfile;
    if (!PyArg_ParseTuple(args, "y#:profile_frombytes", &pProfile, &nProfile)) {
        return NULL;
    }

    hProfile = cmsOpenProfileFromMem(pProfile, nProfile);
    if (!hProfile) {
        PyErr_SetString(PyExc_OSError, "cannot open profile from string");
        return NULL;
    }

    return cms_profile_new(hProfile);
}

static PyObject *
cms_profile_tobytes(PyObject *self, PyObject *args) {
    char *pProfile = NULL;
    cmsUInt32Number nProfile;
    PyObject *CmsProfile;

    cmsHPROFILE *profile;

    PyObject *ret;
    if (!PyArg_ParseTuple(args, "O", &CmsProfile)) {
        return NULL;
    }

    profile = ((CmsProfileObject *)CmsProfile)->profile;

    if (!cmsSaveProfileToMem(profile, pProfile, &nProfile)) {
        PyErr_SetString(PyExc_OSError, "Could not determine profile size");
        return NULL;
    }

    pProfile = (char *)malloc(nProfile);
    if (!pProfile) {
        PyErr_SetString(PyExc_OSError, "Out of Memory");
        return NULL;
    }

    if (!cmsSaveProfileToMem(profile, pProfile, &nProfile)) {
        PyErr_SetString(PyExc_OSError, "Could not get profile");
        free(pProfile);
        return NULL;
    }

    ret = PyBytes_FromStringAndSize(pProfile, (Py_ssize_t)nProfile);

    free(pProfile);
    return ret;
}

static void
cms_profile_dealloc(CmsProfileObject *self) {
    (void)cmsCloseProfile(self->profile);
    PyObject_Del(self);
}

/* a transform represents the mapping between two profiles */

typedef struct {
    PyObject_HEAD char mode_in[8];
    char mode_out[8];
    cmsHTRANSFORM transform;
} CmsTransformObject;

static PyTypeObject CmsTransform_Type;

#define CmsTransform_Check(op) (Py_TYPE(op) == &CmsTransform_Type)

static PyObject *
cms_transform_new(cmsHTRANSFORM transform, char *mode_in, char *mode_out) {
    CmsTransformObject *self;

    self = PyObject_New(CmsTransformObject, &CmsTransform_Type);
    if (!self) {
        return NULL;
    }

    self->transform = transform;

    strcpy(self->mode_in, mode_in);
    strcpy(self->mode_out, mode_out);

    return (PyObject *)self;
}

static void
cms_transform_dealloc(CmsTransformObject *self) {
    cmsDeleteTransform(self->transform);
    PyObject_Del(self);
}

/* -------------------------------------------------------------------- */
/* internal functions */

static cmsUInt32Number
findLCMStype(char *PILmode) {
    if (strcmp(PILmode, "RGB") == 0) {
        return TYPE_RGBA_8;
    } else if (strcmp(PILmode, "RGBA") == 0) {
        return TYPE_RGBA_8;
    } else if (strcmp(PILmode, "RGBX") == 0) {
        return TYPE_RGBA_8;
    } else if (strcmp(PILmode, "RGBA;16B") == 0) {
        return TYPE_RGBA_16;
    } else if (strcmp(PILmode, "CMYK") == 0) {
        return TYPE_CMYK_8;
    } else if (strcmp(PILmode, "L") == 0) {
        return TYPE_GRAY_8;
    } else if (strcmp(PILmode, "L;16") == 0) {
        return TYPE_GRAY_16;
    } else if (strcmp(PILmode, "L;16B") == 0) {
        return TYPE_GRAY_16_SE;
    } else if (strcmp(PILmode, "YCCA") == 0) {
        return TYPE_YCbCr_8;
    } else if (strcmp(PILmode, "YCC") == 0) {
        return TYPE_YCbCr_8;
    } else if (strcmp(PILmode, "LAB") == 0) {
        // LabX equivalent like ALab, but not reversed -- no #define in lcms2
        return (COLORSPACE_SH(PT_LabV2) | CHANNELS_SH(3) | BYTES_SH(1) | EXTRA_SH(1));
    }

    else {
        /* take a wild guess... but you probably should fail instead. */
        return TYPE_GRAY_8; /* so there's no buffer overrun... */
    }
}

#define Cms_Min(a, b) ((a) < (b) ? (a) : (b))

static int
pyCMSgetAuxChannelChannel(cmsUInt32Number format, int auxChannelNdx) {
    int numColors = T_CHANNELS(format);
    int numExtras = T_EXTRA(format);

    if (T_SWAPFIRST(format) && T_DOSWAP(format)) {
        // reverse order, before anything but last extra is shifted last
        if (auxChannelNdx == numExtras - 1) {
            return numColors + numExtras - 1;
        } else {
            return numExtras - 2 - auxChannelNdx;
        }
    } else if (T_SWAPFIRST(format)) {
        // in order, after color channels, but last extra is shifted to first
        if (auxChannelNdx == numExtras - 1) {
            return 0;
        } else {
            return numColors + 1 + auxChannelNdx;
        }
    } else if (T_DOSWAP(format)) {
        // reverse order, before anything
        return numExtras - 1 - auxChannelNdx;
    } else {
        // in order, after color channels
        return numColors + auxChannelNdx;
    }
}

static void
pyCMScopyAux(cmsHTRANSFORM hTransform, Imaging imDst, const Imaging imSrc) {
    cmsUInt32Number dstLCMSFormat;
    cmsUInt32Number srcLCMSFormat;
    int numSrcExtras;
    int numDstExtras;
    int numExtras;
    int ySize;
    int xSize;
    int channelSize;
    int srcChunkSize;
    int dstChunkSize;
    int e;

    // trivially copied
    if (imDst == imSrc) {
        return;
    }

    dstLCMSFormat = cmsGetTransformOutputFormat(hTransform);
    srcLCMSFormat = cmsGetTransformInputFormat(hTransform);

    // currently, all Pillow formats are chunky formats, but check it anyway
    if (T_PLANAR(dstLCMSFormat) || T_PLANAR(srcLCMSFormat)) {
        return;
    }

    // copy only if channel format is identical, except OPTIMIZED is ignored as it
    // does not affect the aux channel
    if (T_FLOAT(dstLCMSFormat) != T_FLOAT(srcLCMSFormat) ||
        T_FLAVOR(dstLCMSFormat) != T_FLAVOR(srcLCMSFormat) ||
        T_ENDIAN16(dstLCMSFormat) != T_ENDIAN16(srcLCMSFormat) ||
        T_BYTES(dstLCMSFormat) != T_BYTES(srcLCMSFormat)) {
        return;
    }

    numSrcExtras = T_EXTRA(srcLCMSFormat);
    numDstExtras = T_EXTRA(dstLCMSFormat);
    numExtras = Cms_Min(numSrcExtras, numDstExtras);
    ySize = Cms_Min(imSrc->ysize, imDst->ysize);
    xSize = Cms_Min(imSrc->xsize, imDst->xsize);
    channelSize = T_BYTES(dstLCMSFormat);
    srcChunkSize = (T_CHANNELS(srcLCMSFormat) + T_EXTRA(srcLCMSFormat)) * channelSize;
    dstChunkSize = (T_CHANNELS(dstLCMSFormat) + T_EXTRA(dstLCMSFormat)) * channelSize;

    for (e = 0; e < numExtras; ++e) {
        int y;
        int dstChannel = pyCMSgetAuxChannelChannel(dstLCMSFormat, e);
        int srcChannel = pyCMSgetAuxChannelChannel(srcLCMSFormat, e);

        for (y = 0; y < ySize; y++) {
            int x;
            char *pDstExtras = imDst->image[y] + dstChannel * channelSize;
            const char *pSrcExtras = imSrc->image[y] + srcChannel * channelSize;

            for (x = 0; x < xSize; x++) {
                memcpy(
                    pDstExtras + x * dstChunkSize,
                    pSrcExtras + x * srcChunkSize,
                    channelSize);
            }
        }
    }
}

static int
pyCMSdoTransform(Imaging im, Imaging imOut, cmsHTRANSFORM hTransform) {
    int i;

    if (im->xsize > imOut->xsize || im->ysize > imOut->ysize) {
        return -1;
    }

    Py_BEGIN_ALLOW_THREADS

        // transform color channels only
        for (i = 0; i < im->ysize; i++) {
        cmsDoTransform(hTransform, im->image[i], imOut->image[i], im->xsize);
    }

    // lcms by default does nothing to the auxiliary channels leaving those
    // unchanged. To do "the right thing" here, i.e. maintain identical results
    // with and without inPlace, we replicate those channels to the output.
    //
    // As of lcms 2.8, a new cmsFLAGS_COPY_ALPHA flag is introduced which would
    // do the same thing automagically. Unfortunately, lcms2.8 is not yet widely
    // enough available on all platforms, so we polyfill it here for now.
    pyCMScopyAux(hTransform, imOut, im);

    Py_END_ALLOW_THREADS

        return 0;
}

static cmsHTRANSFORM
_buildTransform(
    cmsHPROFILE hInputProfile,
    cmsHPROFILE hOutputProfile,
    char *sInMode,
    char *sOutMode,
    int iRenderingIntent,
    cmsUInt32Number cmsFLAGS) {
    cmsHTRANSFORM hTransform;

    Py_BEGIN_ALLOW_THREADS

        /* create the transform */
        hTransform = cmsCreateTransform(
            hInputProfile,
            findLCMStype(sInMode),
            hOutputProfile,
            findLCMStype(sOutMode),
            iRenderingIntent,
            cmsFLAGS);

    Py_END_ALLOW_THREADS

        if (!hTransform) {
        PyErr_SetString(PyExc_ValueError, "cannot build transform");
    }

    return hTransform; /* if NULL, an exception is set */
}

static cmsHTRANSFORM
_buildProofTransform(
    cmsHPROFILE hInputProfile,
    cmsHPROFILE hOutputProfile,
    cmsHPROFILE hProofProfile,
    char *sInMode,
    char *sOutMode,
    int iRenderingIntent,
    int iProofIntent,
    cmsUInt32Number cmsFLAGS) {
    cmsHTRANSFORM hTransform;

    Py_BEGIN_ALLOW_THREADS

        /* create the transform */
        hTransform = cmsCreateProofingTransform(
            hInputProfile,
            findLCMStype(sInMode),
            hOutputProfile,
            findLCMStype(sOutMode),
            hProofProfile,
            iRenderingIntent,
            iProofIntent,
            cmsFLAGS);

    Py_END_ALLOW_THREADS

        if (!hTransform) {
        PyErr_SetString(PyExc_ValueError, "cannot build proof transform");
    }

    return hTransform; /* if NULL, an exception is set */
}

/* -------------------------------------------------------------------- */
/* Python callable functions */

static PyObject *
buildTransform(PyObject *self, PyObject *args) {
    CmsProfileObject *pInputProfile;
    CmsProfileObject *pOutputProfile;
    char *sInMode;
    char *sOutMode;
    int iRenderingIntent = 0;
    int cmsFLAGS = 0;

    cmsHTRANSFORM transform = NULL;

    if (!PyArg_ParseTuple(
            args,
            "O!O!ss|ii:buildTransform",
            &CmsProfile_Type,
            &pInputProfile,
            &CmsProfile_Type,
            &pOutputProfile,
            &sInMode,
            &sOutMode,
            &iRenderingIntent,
            &cmsFLAGS)) {
        return NULL;
    }

    transform = _buildTransform(
        pInputProfile->profile,
        pOutputProfile->profile,
        sInMode,
        sOutMode,
        iRenderingIntent,
        cmsFLAGS);

    if (!transform) {
        return NULL;
    }

    return cms_transform_new(transform, sInMode, sOutMode);
}

static PyObject *
buildProofTransform(PyObject *self, PyObject *args) {
    CmsProfileObject *pInputProfile;
    CmsProfileObject *pOutputProfile;
    CmsProfileObject *pProofProfile;
    char *sInMode;
    char *sOutMode;
    int iRenderingIntent = 0;
    int iProofIntent = 0;
    int cmsFLAGS = 0;

    cmsHTRANSFORM transform = NULL;

    if (!PyArg_ParseTuple(
            args,
            "O!O!O!ss|iii:buildProofTransform",
            &CmsProfile_Type,
            &pInputProfile,
            &CmsProfile_Type,
            &pOutputProfile,
            &CmsProfile_Type,
            &pProofProfile,
            &sInMode,
            &sOutMode,
            &iRenderingIntent,
            &iProofIntent,
            &cmsFLAGS)) {
        return NULL;
    }

    transform = _buildProofTransform(
        pInputProfile->profile,
        pOutputProfile->profile,
        pProofProfile->profile,
        sInMode,
        sOutMode,
        iRenderingIntent,
        iProofIntent,
        cmsFLAGS);

    if (!transform) {
        return NULL;
    }

    return cms_transform_new(transform, sInMode, sOutMode);
}

static PyObject *
cms_transform_apply(CmsTransformObject *self, PyObject *args) {
    Py_ssize_t idIn;
    Py_ssize_t idOut;
    Imaging im;
    Imaging imOut;

    int result;

    if (!PyArg_ParseTuple(args, "nn:apply", &idIn, &idOut)) {
        return NULL;
    }

    im = (Imaging)idIn;
    imOut = (Imaging)idOut;

    result = pyCMSdoTransform(im, imOut, self->transform);

    return Py_BuildValue("i", result);
}

/* -------------------------------------------------------------------- */
/* Python-Callable On-The-Fly profile creation functions */

static PyObject *
createProfile(PyObject *self, PyObject *args) {
    char *sColorSpace;
    cmsHPROFILE hProfile;
    cmsFloat64Number dColorTemp = 0.0;
    cmsCIExyY whitePoint;
    cmsBool result;

    if (!PyArg_ParseTuple(args, "s|d:createProfile", &sColorSpace, &dColorTemp)) {
        return NULL;
    }

    if (strcmp(sColorSpace, "LAB") == 0) {
        if (dColorTemp > 0.0) {
            result = cmsWhitePointFromTemp(&whitePoint, dColorTemp);
            if (!result) {
                PyErr_SetString(
                    PyExc_ValueError,
                    "ERROR: Could not calculate white point from color temperature "
                    "provided, must be float in degrees Kelvin");
                return NULL;
            }
            hProfile = cmsCreateLab2Profile(&whitePoint);
        } else {
            hProfile = cmsCreateLab2Profile(NULL);
        }
    } else if (strcmp(sColorSpace, "XYZ") == 0) {
        hProfile = cmsCreateXYZProfile();
    } else if (strcmp(sColorSpace, "sRGB") == 0) {
        hProfile = cmsCreate_sRGBProfile();
    } else {
        hProfile = NULL;
    }

    if (!hProfile) {
        PyErr_SetString(PyExc_ValueError, "failed to create requested color space");
        return NULL;
    }

    return cms_profile_new(hProfile);
}

/* -------------------------------------------------------------------- */
/* profile methods */

static PyObject *
cms_profile_is_intent_supported(CmsProfileObject *self, PyObject *args) {
    cmsBool result;

    int intent;
    int direction;
    if (!PyArg_ParseTuple(args, "ii:is_intent_supported", &intent, &direction)) {
        return NULL;
    }

    result = cmsIsIntentSupported(self->profile, intent, direction);

    /* printf("cmsIsIntentSupported(%p, %d, %d) => %d\n", self->profile, intent,
     * direction, result); */

    return PyLong_FromLong(result != 0);
}

#ifdef _WIN32

#ifdef _WIN64
#define F_HANDLE "K"
#else
#define F_HANDLE "k"
#endif

static PyObject *
cms_get_display_profile_win32(PyObject *self, PyObject *args) {
    char filename[MAX_PATH];
    cmsUInt32Number filename_size;
    BOOL ok;

    HANDLE handle = 0;
    int is_dc = 0;
    if (!PyArg_ParseTuple(
            args, "|" F_HANDLE "i:get_display_profile", &handle, &is_dc)) {
        return NULL;
    }

    filename_size = sizeof(filename);

    if (is_dc) {
        ok = GetICMProfile((HDC)handle, &filename_size, filename);
    } else {
        HDC dc = GetDC((HWND)handle);
        ok = GetICMProfile(dc, &filename_size, filename);
        ReleaseDC((HWND)handle, dc);
    }

    if (ok) {
        return PyUnicode_FromStringAndSize(filename, filename_size - 1);
    }

    Py_INCREF(Py_None);
    return Py_None;
}
#endif

/* -------------------------------------------------------------------- */
/* Helper functions.  */

static PyObject *
_profile_read_mlu(CmsProfileObject *self, cmsTagSignature info) {
    PyObject *uni;
    char *lc = "en";
    char *cc = cmsNoCountry;
    cmsMLU *mlu;
    cmsUInt32Number len;
    wchar_t *buf;

    if (!cmsIsTag(self->profile, info)) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    mlu = cmsReadTag(self->profile, info);
    if (!mlu) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    len = cmsMLUgetWide(mlu, lc, cc, NULL, 0);
    if (len == 0) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    buf = malloc(len);
    if (!buf) {
        PyErr_SetString(PyExc_OSError, "Out of Memory");
        return NULL;
    }
    /* Just in case the next call fails.  */
    buf[0] = '\0';

    cmsMLUgetWide(mlu, lc, cc, buf, len);
    // buf contains additional junk after \0
    uni = PyUnicode_FromWideChar(buf, wcslen(buf));
    free(buf);

    return uni;
}

static PyObject *
_profile_read_int_as_string(cmsUInt32Number nr) {
    PyObject *ret;
    char buf[5];
    buf[0] = (char)((nr >> 24) & 0xff);
    buf[1] = (char)((nr >> 16) & 0xff);
    buf[2] = (char)((nr >> 8) & 0xff);
    buf[3] = (char)(nr & 0xff);
    buf[4] = 0;

    ret = PyUnicode_DecodeASCII(buf, 4, NULL);
    return ret;
}

static PyObject *
_profile_read_signature(CmsProfileObject *self, cmsTagSignature info) {
    unsigned int *sig;

    if (!cmsIsTag(self->profile, info)) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    sig = (unsigned int *)cmsReadTag(self->profile, info);
    if (!sig) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return _profile_read_int_as_string(*sig);
}

static PyObject *
_xyz_py(cmsCIEXYZ *XYZ) {
    cmsCIExyY xyY;
    cmsXYZ2xyY(&xyY, XYZ);
    return Py_BuildValue(
        "((d,d,d),(d,d,d))", XYZ->X, XYZ->Y, XYZ->Z, xyY.x, xyY.y, xyY.Y);
}

static PyObject *
_xyz3_py(cmsCIEXYZ *XYZ) {
    cmsCIExyY xyY[3];
    cmsXYZ2xyY(&xyY[0], &XYZ[0]);
    cmsXYZ2xyY(&xyY[1], &XYZ[1]);
    cmsXYZ2xyY(&xyY[2], &XYZ[2]);

    return Py_BuildValue(
        "(((d,d,d),(d,d,d),(d,d,d)),((d,d,d),(d,d,d),(d,d,d)))",
        XYZ[0].X,
        XYZ[0].Y,
        XYZ[0].Z,
        XYZ[1].X,
        XYZ[1].Y,
        XYZ[1].Z,
        XYZ[2].X,
        XYZ[2].Y,
        XYZ[2].Z,
        xyY[0].x,
        xyY[0].y,
        xyY[0].Y,
        xyY[1].x,
        xyY[1].y,
        xyY[1].Y,
        xyY[2].x,
        xyY[2].y,
        xyY[2].Y);
}

static PyObject *
_profile_read_ciexyz(CmsProfileObject *self, cmsTagSignature info, int multi) {
    cmsCIEXYZ *XYZ;

    if (!cmsIsTag(self->profile, info)) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    XYZ = (cmsCIEXYZ *)cmsReadTag(self->profile, info);
    if (!XYZ) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    if (multi) {
        return _xyz3_py(XYZ);
    } else {
        return _xyz_py(XYZ);
    }
}

static PyObject *
_profile_read_ciexyy_triple(CmsProfileObject *self, cmsTagSignature info) {
    cmsCIExyYTRIPLE *triple;

    if (!cmsIsTag(self->profile, info)) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    triple = (cmsCIExyYTRIPLE *)cmsReadTag(self->profile, info);
    if (!triple) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    /* Note: lcms does all the heavy lifting and error checking (nr of
       channels == 3).  */
    return Py_BuildValue(
        "((d,d,d),(d,d,d),(d,d,d)),",
        triple->Red.x,
        triple->Red.y,
        triple->Red.Y,
        triple->Green.x,
        triple->Green.y,
        triple->Green.Y,
        triple->Blue.x,
        triple->Blue.y,
        triple->Blue.Y);
}

static PyObject *
_profile_read_named_color_list(CmsProfileObject *self, cmsTagSignature info) {
    cmsNAMEDCOLORLIST *ncl;
    int i, n;
    char name[cmsMAX_PATH];
    PyObject *result;

    if (!cmsIsTag(self->profile, info)) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    ncl = (cmsNAMEDCOLORLIST *)cmsReadTag(self->profile, info);
    if (ncl == NULL) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    n = cmsNamedColorCount(ncl);
    result = PyList_New(n);
    if (!result) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    for (i = 0; i < n; i++) {
        PyObject *str;
        cmsNamedColorInfo(ncl, i, name, NULL, NULL, NULL, NULL);
        str = PyUnicode_FromString(name);
        if (str == NULL) {
            Py_DECREF(result);
            Py_INCREF(Py_None);
            return Py_None;
        }
        PyList_SET_ITEM(result, i, str);
    }

    return result;
}

static cmsBool
_calculate_rgb_primaries(CmsProfileObject *self, cmsCIEXYZTRIPLE *result) {
    double input[3][3] = {{1, 0, 0}, {0, 1, 0}, {0, 0, 1}};
    cmsHPROFILE hXYZ;
    cmsHTRANSFORM hTransform;

    /* https://littlecms2.blogspot.com/2009/07/less-is-more.html */

    // double array of RGB values with max on each identity
    hXYZ = cmsCreateXYZProfile();
    if (hXYZ == NULL) {
        return 0;
    }

    // transform from our profile to XYZ using doubles for highest precision
    hTransform = cmsCreateTransform(
        self->profile,
        TYPE_RGB_DBL,
        hXYZ,
        TYPE_XYZ_DBL,
        INTENT_RELATIVE_COLORIMETRIC,
        cmsFLAGS_NOCACHE | cmsFLAGS_NOOPTIMIZE);
    cmsCloseProfile(hXYZ);
    if (hTransform == NULL) {
        return 0;
    }

    cmsDoTransform(hTransform, (void *)input, result, 3);
    cmsDeleteTransform(hTransform);
    return 1;
}

static cmsBool
_check_intent(
    int clut,
    cmsHPROFILE hProfile,
    cmsUInt32Number Intent,
    cmsUInt32Number UsedDirection) {
    if (clut) {
        return cmsIsCLUT(hProfile, Intent, UsedDirection);
    } else {
        return cmsIsIntentSupported(hProfile, Intent, UsedDirection);
    }
}

#define INTENTS 200

static PyObject *
_is_intent_supported(CmsProfileObject *self, int clut) {
    PyObject *result;
    int n;
    int i;
    cmsUInt32Number intent_ids[INTENTS];
    char *intent_descs[INTENTS];

    result = PyDict_New();
    if (result == NULL) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    n = cmsGetSupportedIntents(INTENTS, intent_ids, intent_descs);
    for (i = 0; i < n; i++) {
        int intent = (int)intent_ids[i];
        PyObject *id;
        PyObject *entry;

        /* Only valid for ICC Intents (otherwise we read invalid memory in lcms
         * cmsio1.c). */
        if (!(intent == INTENT_PERCEPTUAL || intent == INTENT_RELATIVE_COLORIMETRIC ||
              intent == INTENT_SATURATION || intent == INTENT_ABSOLUTE_COLORIMETRIC)) {
            continue;
        }

        id = PyLong_FromLong((long)intent);
        entry = Py_BuildValue(
            "(OOO)",
            _check_intent(clut, self->profile, intent, LCMS_USED_AS_INPUT) ? Py_True
                                                                           : Py_False,
            _check_intent(clut, self->profile, intent, LCMS_USED_AS_OUTPUT) ? Py_True
                                                                            : Py_False,
            _check_intent(clut, self->profile, intent, LCMS_USED_AS_PROOF) ? Py_True
                                                                           : Py_False);
        if (id == NULL || entry == NULL) {
            Py_XDECREF(id);
            Py_XDECREF(entry);
            Py_XDECREF(result);
            Py_INCREF(Py_None);
            return Py_None;
        }
        PyDict_SetItem(result, id, entry);
        Py_DECREF(id);
        Py_DECREF(entry);
    }
    return result;
}

/* -------------------------------------------------------------------- */
/* Python interface setup */

static PyMethodDef pyCMSdll_methods[] = {

    {"profile_open", cms_profile_open, METH_VARARGS},
    {"profile_frombytes", cms_profile_frombytes, METH_VARARGS},
    {"profile_tobytes", cms_profile_tobytes, METH_VARARGS},

    /* profile and transform functions */
    {"buildTransform", buildTransform, METH_VARARGS},
    {"buildProofTransform", buildProofTransform, METH_VARARGS},
    {"createProfile", createProfile, METH_VARARGS},

/* platform specific tools */
#ifdef _WIN32
    {"get_display_profile_win32", cms_get_display_profile_win32, METH_VARARGS},
#endif

    {NULL, NULL}};

static struct PyMethodDef cms_profile_methods[] = {
    {"is_intent_supported", (PyCFunction)cms_profile_is_intent_supported, METH_VARARGS},
    {NULL, NULL} /* sentinel */
};

static PyObject *
cms_profile_getattr_rendering_intent(CmsProfileObject *self, void *closure) {
    return PyLong_FromLong(cmsGetHeaderRenderingIntent(self->profile));
}

/* New-style unicode interfaces.  */
static PyObject *
cms_profile_getattr_copyright(CmsProfileObject *self, void *closure) {
    return _profile_read_mlu(self, cmsSigCopyrightTag);
}

static PyObject *
cms_profile_getattr_target(CmsProfileObject *self, void *closure) {
    return _profile_read_mlu(self, cmsSigCharTargetTag);
}

static PyObject *
cms_profile_getattr_manufacturer(CmsProfileObject *self, void *closure) {
    return _profile_read_mlu(self, cmsSigDeviceMfgDescTag);
}

static PyObject *
cms_profile_getattr_model(CmsProfileObject *self, void *closure) {
    return _profile_read_mlu(self, cmsSigDeviceModelDescTag);
}

static PyObject *
cms_profile_getattr_profile_description(CmsProfileObject *self, void *closure) {
    return _profile_read_mlu(self, cmsSigProfileDescriptionTag);
}

static PyObject *
cms_profile_getattr_screening_description(CmsProfileObject *self, void *closure) {
    return _profile_read_mlu(self, cmsSigScreeningDescTag);
}

static PyObject *
cms_profile_getattr_viewing_condition(CmsProfileObject *self, void *closure) {
    return _profile_read_mlu(self, cmsSigViewingCondDescTag);
}

static PyObject *
cms_profile_getattr_creation_date(CmsProfileObject *self, void *closure) {
    cmsBool result;
    struct tm ct;

    result = cmsGetHeaderCreationDateTime(self->profile, &ct);
    if (!result) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return PyDateTime_FromDateAndTime(
        1900 + ct.tm_year, ct.tm_mon, ct.tm_mday, ct.tm_hour, ct.tm_min, ct.tm_sec, 0);
}

static PyObject *
cms_profile_getattr_version(CmsProfileObject *self, void *closure) {
    cmsFloat64Number version = cmsGetProfileVersion(self->profile);
    return PyFloat_FromDouble(version);
}

static PyObject *
cms_profile_getattr_icc_version(CmsProfileObject *self, void *closure) {
    return PyLong_FromLong((long)cmsGetEncodedICCversion(self->profile));
}

static PyObject *
cms_profile_getattr_attributes(CmsProfileObject *self, void *closure) {
    cmsUInt64Number attr;
    cmsGetHeaderAttributes(self->profile, &attr);
    /* This works just as well on Windows (LLP64), 32-bit Linux
       (ILP32) and 64-bit Linux (LP64) systems.  */
    return PyLong_FromUnsignedLongLong((unsigned long long)attr);
}

static PyObject *
cms_profile_getattr_header_flags(CmsProfileObject *self, void *closure) {
    cmsUInt32Number flags = cmsGetHeaderFlags(self->profile);
    return PyLong_FromLong(flags);
}

static PyObject *
cms_profile_getattr_header_manufacturer(CmsProfileObject *self, void *closure) {
    return _profile_read_int_as_string(cmsGetHeaderManufacturer(self->profile));
}

static PyObject *
cms_profile_getattr_header_model(CmsProfileObject *self, void *closure) {
    return _profile_read_int_as_string(cmsGetHeaderModel(self->profile));
}

static PyObject *
cms_profile_getattr_device_class(CmsProfileObject *self, void *closure) {
    return _profile_read_int_as_string(cmsGetDeviceClass(self->profile));
}

static PyObject *
cms_profile_getattr_connection_space(CmsProfileObject *self, void *closure) {
    return _profile_read_int_as_string(cmsGetPCS(self->profile));
}

static PyObject *
cms_profile_getattr_xcolor_space(CmsProfileObject *self, void *closure) {
    return _profile_read_int_as_string(cmsGetColorSpace(self->profile));
}

static PyObject *
cms_profile_getattr_profile_id(CmsProfileObject *self, void *closure) {
    cmsUInt8Number id[16];
    cmsGetHeaderProfileID(self->profile, id);
    return PyBytes_FromStringAndSize((char *)id, 16);
}

static PyObject *
cms_profile_getattr_is_matrix_shaper(CmsProfileObject *self, void *closure) {
    return PyBool_FromLong((long)cmsIsMatrixShaper(self->profile));
}

static PyObject *
cms_profile_getattr_technology(CmsProfileObject *self, void *closure) {
    return _profile_read_signature(self, cmsSigTechnologyTag);
}

static PyObject *
cms_profile_getattr_colorimetric_intent(CmsProfileObject *self, void *closure) {
    return _profile_read_signature(self, cmsSigColorimetricIntentImageStateTag);
}

static PyObject *
cms_profile_getattr_perceptual_rendering_intent_gamut(
    CmsProfileObject *self, void *closure) {
    return _profile_read_signature(self, cmsSigPerceptualRenderingIntentGamutTag);
}

static PyObject *
cms_profile_getattr_saturation_rendering_intent_gamut(
    CmsProfileObject *self, void *closure) {
    return _profile_read_signature(self, cmsSigSaturationRenderingIntentGamutTag);
}

static PyObject *
cms_profile_getattr_red_colorant(CmsProfileObject *self, void *closure) {
    if (!cmsIsMatrixShaper(self->profile)) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    return _profile_read_ciexyz(self, cmsSigRedColorantTag, 0);
}

static PyObject *
cms_profile_getattr_green_colorant(CmsProfileObject *self, void *closure) {
    if (!cmsIsMatrixShaper(self->profile)) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    return _profile_read_ciexyz(self, cmsSigGreenColorantTag, 0);
}

static PyObject *
cms_profile_getattr_blue_colorant(CmsProfileObject *self, void *closure) {
    if (!cmsIsMatrixShaper(self->profile)) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    return _profile_read_ciexyz(self, cmsSigBlueColorantTag, 0);
}

static PyObject *
cms_profile_getattr_media_white_point_temperature(
    CmsProfileObject *self, void *closure) {
    cmsCIEXYZ *XYZ;
    cmsCIExyY xyY;
    cmsFloat64Number tempK;
    cmsTagSignature info = cmsSigMediaWhitePointTag;
    cmsBool result;

    if (!cmsIsTag(self->profile, info)) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    XYZ = (cmsCIEXYZ *)cmsReadTag(self->profile, info);
    if (XYZ == NULL || XYZ->X == 0) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    cmsXYZ2xyY(&xyY, XYZ);
    result = cmsTempFromWhitePoint(&tempK, &xyY);
    if (!result) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    return PyFloat_FromDouble(tempK);
}

static PyObject *
cms_profile_getattr_media_white_point(CmsProfileObject *self, void *closure) {
    return _profile_read_ciexyz(self, cmsSigMediaWhitePointTag, 0);
}

static PyObject *
cms_profile_getattr_media_black_point(CmsProfileObject *self, void *closure) {
    return _profile_read_ciexyz(self, cmsSigMediaBlackPointTag, 0);
}

static PyObject *
cms_profile_getattr_luminance(CmsProfileObject *self, void *closure) {
    return _profile_read_ciexyz(self, cmsSigLuminanceTag, 0);
}

static PyObject *
cms_profile_getattr_chromatic_adaptation(CmsProfileObject *self, void *closure) {
    return _profile_read_ciexyz(self, cmsSigChromaticAdaptationTag, 1);
}

static PyObject *
cms_profile_getattr_chromaticity(CmsProfileObject *self, void *closure) {
    return _profile_read_ciexyy_triple(self, cmsSigChromaticityTag);
}

static PyObject *
cms_profile_getattr_red_primary(CmsProfileObject *self, void *closure) {
    cmsBool result = 0;
    cmsCIEXYZTRIPLE primaries;

    if (cmsIsMatrixShaper(self->profile)) {
        result = _calculate_rgb_primaries(self, &primaries);
    }
    if (!result) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return _xyz_py(&primaries.Red);
}

static PyObject *
cms_profile_getattr_green_primary(CmsProfileObject *self, void *closure) {
    cmsBool result = 0;
    cmsCIEXYZTRIPLE primaries;

    if (cmsIsMatrixShaper(self->profile)) {
        result = _calculate_rgb_primaries(self, &primaries);
    }
    if (!result) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return _xyz_py(&primaries.Green);
}

static PyObject *
cms_profile_getattr_blue_primary(CmsProfileObject *self, void *closure) {
    cmsBool result = 0;
    cmsCIEXYZTRIPLE primaries;

    if (cmsIsMatrixShaper(self->profile)) {
        result = _calculate_rgb_primaries(self, &primaries);
    }
    if (!result) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return _xyz_py(&primaries.Blue);
}

static PyObject *
cms_profile_getattr_colorant_table(CmsProfileObject *self, void *closure) {
    return _profile_read_named_color_list(self, cmsSigColorantTableTag);
}

static PyObject *
cms_profile_getattr_colorant_table_out(CmsProfileObject *self, void *closure) {
    return _profile_read_named_color_list(self, cmsSigColorantTableOutTag);
}

static PyObject *
cms_profile_getattr_is_intent_supported(CmsProfileObject *self, void *closure) {
    return _is_intent_supported(self, 0);
}

static PyObject *
cms_profile_getattr_is_clut(CmsProfileObject *self, void *closure) {
    return _is_intent_supported(self, 1);
}

static const char *
_illu_map(int i) {
    switch (i) {
        case 0:
            return "unknown";
        case 1:
            return "D50";
        case 2:
            return "D65";
        case 3:
            return "D93";
        case 4:
            return "F2";
        case 5:
            return "D55";
        case 6:
            return "A";
        case 7:
            return "E";
        case 8:
            return "F8";
        default:
            return NULL;
    }
}

static PyObject *
cms_profile_getattr_icc_measurement_condition(CmsProfileObject *self, void *closure) {
    cmsICCMeasurementConditions *mc;
    cmsTagSignature info = cmsSigMeasurementTag;
    const char *geo;

    if (!cmsIsTag(self->profile, info)) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    mc = (cmsICCMeasurementConditions *)cmsReadTag(self->profile, info);
    if (!mc) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    if (mc->Geometry == 1) {
        geo = "45/0, 0/45";
    } else if (mc->Geometry == 2) {
        geo = "0d, d/0";
    } else {
        geo = "unknown";
    }

    return Py_BuildValue(
        "{s:i,s:(ddd),s:s,s:d,s:s}",
        "observer",
        mc->Observer,
        "backing",
        mc->Backing.X,
        mc->Backing.Y,
        mc->Backing.Z,
        "geo",
        geo,
        "flare",
        mc->Flare,
        "illuminant_type",
        _illu_map(mc->IlluminantType));
}

static PyObject *
cms_profile_getattr_icc_viewing_condition(CmsProfileObject *self, void *closure) {
    cmsICCViewingConditions *vc;
    cmsTagSignature info = cmsSigViewingConditionsTag;

    if (!cmsIsTag(self->profile, info)) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    vc = (cmsICCViewingConditions *)cmsReadTag(self->profile, info);
    if (!vc) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    return Py_BuildValue(
        "{s:(ddd),s:(ddd),s:s}",
        "illuminant",
        vc->IlluminantXYZ.X,
        vc->IlluminantXYZ.Y,
        vc->IlluminantXYZ.Z,
        "surround",
        vc->SurroundXYZ.X,
        vc->SurroundXYZ.Y,
        vc->SurroundXYZ.Z,
        "illuminant_type",
        _illu_map(vc->IlluminantType));
}

static struct PyGetSetDef cms_profile_getsetters[] = {
    /* New style interfaces.  */
    {"rendering_intent", (getter)cms_profile_getattr_rendering_intent},
    {"creation_date", (getter)cms_profile_getattr_creation_date},
    {"copyright", (getter)cms_profile_getattr_copyright},
    {"target", (getter)cms_profile_getattr_target},
    {"manufacturer", (getter)cms_profile_getattr_manufacturer},
    {"model", (getter)cms_profile_getattr_model},
    {"profile_description", (getter)cms_profile_getattr_profile_description},
    {"screening_description", (getter)cms_profile_getattr_screening_description},
    {"viewing_condition", (getter)cms_profile_getattr_viewing_condition},
    {"version", (getter)cms_profile_getattr_version},
    {"icc_version", (getter)cms_profile_getattr_icc_version},
    {"attributes", (getter)cms_profile_getattr_attributes},
    {"header_flags", (getter)cms_profile_getattr_header_flags},
    {"header_manufacturer", (getter)cms_profile_getattr_header_manufacturer},
    {"header_model", (getter)cms_profile_getattr_header_model},
    {"device_class", (getter)cms_profile_getattr_device_class},
    {"connection_space", (getter)cms_profile_getattr_connection_space},
    {"xcolor_space", (getter)cms_profile_getattr_xcolor_space},
    {"profile_id", (getter)cms_profile_getattr_profile_id},
    {"is_matrix_shaper", (getter)cms_profile_getattr_is_matrix_shaper},
    {"technology", (getter)cms_profile_getattr_technology},
    {"colorimetric_intent", (getter)cms_profile_getattr_colorimetric_intent},
    {"perceptual_rendering_intent_gamut",
     (getter)cms_profile_getattr_perceptual_rendering_intent_gamut},
    {"saturation_rendering_intent_gamut",
     (getter)cms_profile_getattr_saturation_rendering_intent_gamut},
    {"red_colorant", (getter)cms_profile_getattr_red_colorant},
    {"green_colorant", (getter)cms_profile_getattr_green_colorant},
    {"blue_colorant", (getter)cms_profile_getattr_blue_colorant},
    {"red_primary", (getter)cms_profile_getattr_red_primary},
    {"green_primary", (getter)cms_profile_getattr_green_primary},
    {"blue_primary", (getter)cms_profile_getattr_blue_primary},
    {"media_white_point_temperature",
     (getter)cms_profile_getattr_media_white_point_temperature},
    {"media_white_point", (getter)cms_profile_getattr_media_white_point},
    {"media_black_point", (getter)cms_profile_getattr_media_black_point},
    {"luminance", (getter)cms_profile_getattr_luminance},
    {"chromatic_adaptation", (getter)cms_profile_getattr_chromatic_adaptation},
    {"chromaticity", (getter)cms_profile_getattr_chromaticity},
    {"colorant_table", (getter)cms_profile_getattr_colorant_table},
    {"colorant_table_out", (getter)cms_profile_getattr_colorant_table_out},
    {"intent_supported", (getter)cms_profile_getattr_is_intent_supported},
    {"clut", (getter)cms_profile_getattr_is_clut},
    {"icc_measurement_condition",
     (getter)cms_profile_getattr_icc_measurement_condition},
    {"icc_viewing_condition", (getter)cms_profile_getattr_icc_viewing_condition},

    {NULL}};

static PyTypeObject CmsProfile_Type = {
    PyVarObject_HEAD_INIT(NULL, 0) "PIL._imagingcms.CmsProfile", /*tp_name*/
    sizeof(CmsProfileObject),                                    /*tp_basicsize*/
    0,                                                           /*tp_itemsize*/
    /* methods */
    (destructor)cms_profile_dealloc, /*tp_dealloc*/
    0,                               /*tp_vectorcall_offset*/
    0,                               /*tp_getattr*/
    0,                               /*tp_setattr*/
    0,                               /*tp_as_async*/
    0,                               /*tp_repr*/
    0,                               /*tp_as_number*/
    0,                               /*tp_as_sequence*/
    0,                               /*tp_as_mapping*/
    0,                               /*tp_hash*/
    0,                               /*tp_call*/
    0,                               /*tp_str*/
    0,                               /*tp_getattro*/
    0,                               /*tp_setattro*/
    0,                               /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,              /*tp_flags*/
    0,                               /*tp_doc*/
    0,                               /*tp_traverse*/
    0,                               /*tp_clear*/
    0,                               /*tp_richcompare*/
    0,                               /*tp_weaklistoffset*/
    0,                               /*tp_iter*/
    0,                               /*tp_iternext*/
    cms_profile_methods,             /*tp_methods*/
    0,                               /*tp_members*/
    cms_profile_getsetters,          /*tp_getset*/
};

static struct PyMethodDef cms_transform_methods[] = {
    {"apply", (PyCFunction)cms_transform_apply, 1}, {NULL, NULL} /* sentinel */
};

static PyObject *
cms_transform_getattr_inputMode(CmsTransformObject *self, void *closure) {
    return PyUnicode_FromString(self->mode_in);
}

static PyObject *
cms_transform_getattr_outputMode(CmsTransformObject *self, void *closure) {
    return PyUnicode_FromString(self->mode_out);
}

static struct PyGetSetDef cms_transform_getsetters[] = {
    {"inputMode", (getter)cms_transform_getattr_inputMode},
    {"outputMode", (getter)cms_transform_getattr_outputMode},
    {NULL}};

static PyTypeObject CmsTransform_Type = {
    PyVarObject_HEAD_INIT(NULL, 0) "CmsTransform", /*tp_name*/
    sizeof(CmsTransformObject),                    /*tp_basicsize*/
    0,                                             /*tp_itemsize*/
    /* methods */
    (destructor)cms_transform_dealloc, /*tp_dealloc*/
    0,                                 /*tp_vectorcall_offset*/
    0,                                 /*tp_getattr*/
    0,                                 /*tp_setattr*/
    0,                                 /*tp_as_async*/
    0,                                 /*tp_repr*/
    0,                                 /*tp_as_number*/
    0,                                 /*tp_as_sequence*/
    0,                                 /*tp_as_mapping*/
    0,                                 /*tp_hash*/
    0,                                 /*tp_call*/
    0,                                 /*tp_str*/
    0,                                 /*tp_getattro*/
    0,                                 /*tp_setattro*/
    0,                                 /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,                /*tp_flags*/
    0,                                 /*tp_doc*/
    0,                                 /*tp_traverse*/
    0,                                 /*tp_clear*/
    0,                                 /*tp_richcompare*/
    0,                                 /*tp_weaklistoffset*/
    0,                                 /*tp_iter*/
    0,                                 /*tp_iternext*/
    cms_transform_methods,             /*tp_methods*/
    0,                                 /*tp_members*/
    cms_transform_getsetters,          /*tp_getset*/
};

static int
setup_module(PyObject *m) {
    PyObject *d;
    PyObject *v;
    int vn;

    CmsProfile_Type.tp_new = PyType_GenericNew;

    /* Ready object types */
    PyType_Ready(&CmsProfile_Type);
    PyType_Ready(&CmsTransform_Type);

    Py_INCREF(&CmsProfile_Type);
    PyModule_AddObject(m, "CmsProfile", (PyObject *)&CmsProfile_Type);

    d = PyModule_GetDict(m);

    /* this check is also in PIL.features.pilinfo() */
#if LCMS_VERSION < 2070
    vn = LCMS_VERSION;
#else
    vn = cmsGetEncodedCMMversion();
#endif
    if (vn % 10) {
        v = PyUnicode_FromFormat("%d.%d.%d", vn / 1000, (vn / 10) % 100, vn % 10);
    } else {
        v = PyUnicode_FromFormat("%d.%d", vn / 1000, (vn / 10) % 100);
    }
    PyDict_SetItemString(d, "littlecms_version", v ? v : Py_None);
    Py_XDECREF(v);

    return 0;
}

PyMODINIT_FUNC
PyInit__imagingcms(void) {
    PyObject *m;

    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_imagingcms",    /* m_name */
        NULL,             /* m_doc */
        -1,               /* m_size */
        pyCMSdll_methods, /* m_methods */
    };

    m = PyModule_Create(&module_def);

    if (setup_module(m) < 0) {
        return NULL;
    }

    PyDateTime_IMPORT;

    return m;
}
