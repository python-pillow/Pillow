/* 
 * pyCMS
 * a Python / PIL interface to the littleCMS ICC Color Management System
 * Copyright (C) 2002-2003 Kevin Cazabon
 * kevin@cazabon.com
 * http://www.cazabon.com
 * Adapted/reworked for PIL by Fredrik Lundh
 * Copyright (c) 2009 Fredrik Lundh
 * 
 * pyCMS home page:  http://www.cazabon.com/pyCMS
 * littleCMS home page:  http://www.littlecms.com
 * (littleCMS is Copyright (C) 1998-2001 Marti Maria)
 * 
 * Originally released under LGPL.  Graciously donated to PIL in
 * March 2009, for distribution under the standard PIL license
 */

#define COPYRIGHTINFO "\
pyCMS\n\
a Python / PIL interface to the littleCMS ICC Color Management System\n\
Copyright (C) 2002-2003 Kevin Cazabon\n\
kevin@cazabon.com\n\
http://www.cazabon.com\n\
"

#include "Python.h"
#include "lcms.h"
#include "Imaging.h"

#if PY_VERSION_HEX < 0x01060000
#define PyObject_New PyObject_NEW
#define PyObject_Del PyMem_DEL
#endif

#if LCMS_VERSION < 117
#define LCMSBOOL BOOL
#endif

#ifdef WIN32
#include <wingdi.h>
#endif

#define PYCMSVERSION "0.1.0 pil"

/* version history */

/*
  0.1.0 pil integration & refactoring
  0.0.2 alpha:  Minor updates, added interfaces to littleCMS features, Jan 6, 2003
  - fixed some memory holes in how transforms/profiles were created and passed back to Python
  due to improper destructor setup for PyCObjects
  - added buildProofTransformFromOpenProfiles() function
  - eliminated some code redundancy, centralizing several common tasks with internal functions

  0.0.1 alpha:  First public release Dec 26, 2002

*/

/* known to-do list with current version:

   Verify that PILmode->littleCMStype conversion in findLCMStype is correct for all PIL modes (it probably isn't for the more obscure ones)
  
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
    PyObject_HEAD
    cmsHPROFILE profile;
} CmsProfileObject;

staticforward PyTypeObject CmsProfile_Type;

#define CmsProfile_Check(op) ((op)->ob_type == &CmsProfile_Type)

static PyObject*
cms_profile_new(cmsHPROFILE profile)
{
    CmsProfileObject* self;

    self = PyObject_New(CmsProfileObject, &CmsProfile_Type);
    if (!self)
        return NULL;

    self->profile = profile;

    return (PyObject*) self;
}

static PyObject*
cms_profile_open(PyObject* self, PyObject* args)
{
    cmsHPROFILE hProfile;

    char* sProfile;
    if (!PyArg_ParseTuple(args, "s:profile_open", &sProfile))
        return NULL;

    cmsErrorAction(LCMS_ERROR_IGNORE);

    hProfile = cmsOpenProfileFromFile(sProfile, "r");
    if (!hProfile) {
        PyErr_SetString(PyExc_IOError, "cannot open profile file");
        return NULL;
    }

    return cms_profile_new(hProfile);
}

static PyObject*
cms_profile_fromstring(PyObject* self, PyObject* args)
{
    cmsHPROFILE hProfile;

    char* pProfile;
    int nProfile;
    if (!PyArg_ParseTuple(args, "s#:profile_fromstring", &pProfile, &nProfile))
        return NULL;

    cmsErrorAction(LCMS_ERROR_IGNORE);

    hProfile = cmsOpenProfileFromMem(pProfile, nProfile);
    if (!hProfile)
        PyErr_SetString(PyExc_IOError, "cannot open profile from string");

    return cms_profile_new(hProfile);
}

static void
cms_profile_dealloc(CmsProfileObject* self)
{
    (void) cmsCloseProfile(self->profile);
    PyObject_Del(self);
}

/* a transform represents the mapping between two profiles */

typedef struct {
    PyObject_HEAD
    char mode_in[8];
    char mode_out[8];
    cmsHTRANSFORM transform;
} CmsTransformObject;

staticforward PyTypeObject CmsTransform_Type;

#define CmsTransform_Check(op) ((op)->ob_type == &CmsTransform_Type)

static PyObject*
cms_transform_new(cmsHTRANSFORM transform, char* mode_in, char* mode_out)
{
    CmsTransformObject* self;

    self = PyObject_New(CmsTransformObject, &CmsTransform_Type);
    if (!self)
        return NULL;

    self->transform = transform;

    strcpy(self->mode_in, mode_in);
    strcpy(self->mode_out, mode_out);

    return (PyObject*) self;
}

static void
cms_transform_dealloc(CmsTransformObject* self)
{
    cmsDeleteTransform(self->transform);
    PyObject_Del(self);
}

/* -------------------------------------------------------------------- */
/* internal functions */

static const char*
findICmode(icColorSpaceSignature cs)
{
    switch (cs) {
    case icSigXYZData: return "XYZ";
    case icSigLabData: return "LAB";
    case icSigLuvData: return "LUV";
    case icSigYCbCrData: return "YCbCr";
    case icSigYxyData: return "YXY";
    case icSigRgbData: return "RGB";
    case icSigGrayData: return "L";
    case icSigHsvData: return "HSV";
    case icSigHlsData: return "HLS";
    case icSigCmykData: return "CMYK";
    case icSigCmyData: return "CMY";
    default: return ""; /* other TBA */
    }
}

static DWORD 
findLCMStype(char* PILmode)
{
    if (strcmp(PILmode, "RGB") == 0) {
        return TYPE_RGBA_8;
    }
    else if (strcmp(PILmode, "RGBA") == 0) {
        return TYPE_RGBA_8;
    }
    else if (strcmp(PILmode, "RGBX") == 0) {
        return TYPE_RGBA_8;
    }
    else if (strcmp(PILmode, "RGBA;16B") == 0) {
        return TYPE_RGBA_16;
    }
    else if (strcmp(PILmode, "CMYK") == 0) {
        return TYPE_CMYK_8;
    }
    else if (strcmp(PILmode, "L") == 0) {
        return TYPE_GRAY_8;
    }
    else if (strcmp(PILmode, "L;16") == 0) {
        return TYPE_GRAY_16;
    }
    else if (strcmp(PILmode, "L;16B") == 0) {
        return TYPE_GRAY_16_SE;
    }
    else if (strcmp(PILmode, "YCCA") == 0) {
        return TYPE_YCbCr_8;
    }
    else if (strcmp(PILmode, "YCC") == 0) {
        return TYPE_YCbCr_8;
    }

    else {
        /* take a wild guess... but you probably should fail instead. */
        return TYPE_GRAY_8; /* so there's no buffer overrun... */
    }
}

static int
pyCMSdoTransform(Imaging im, Imaging imOut, cmsHTRANSFORM hTransform)
{
    int i;

    if (im->xsize > imOut->xsize || im->ysize > imOut->ysize)
        return -1;

    Py_BEGIN_ALLOW_THREADS

    for (i = 0; i < im->ysize; i++)
        cmsDoTransform(hTransform, im->image[i], imOut->image[i], im->xsize);

    Py_END_ALLOW_THREADS

    return 0;
}

static cmsHTRANSFORM
_buildTransform(cmsHPROFILE hInputProfile, cmsHPROFILE hOutputProfile, char *sInMode, char *sOutMode, int iRenderingIntent, DWORD cmsFLAGS)
{
    cmsHTRANSFORM hTransform;

    cmsErrorAction(LCMS_ERROR_IGNORE);

    Py_BEGIN_ALLOW_THREADS

    /* create the transform */
    hTransform = cmsCreateTransform(hInputProfile,
                                    findLCMStype(sInMode),
                                    hOutputProfile,
                                    findLCMStype(sOutMode),
                                    iRenderingIntent, cmsFLAGS);

    Py_END_ALLOW_THREADS

    if (!hTransform)
        PyErr_SetString(PyExc_ValueError, "cannot build transform");

    return hTransform; /* if NULL, an exception is set */
}

static cmsHTRANSFORM
_buildProofTransform(cmsHPROFILE hInputProfile, cmsHPROFILE hOutputProfile, cmsHPROFILE hProofProfile, char *sInMode, char *sOutMode, int iRenderingIntent, int iProofIntent, DWORD cmsFLAGS)
{
    cmsHTRANSFORM hTransform;

    cmsErrorAction(LCMS_ERROR_IGNORE);

    Py_BEGIN_ALLOW_THREADS

    /* create the transform */
    hTransform =  cmsCreateProofingTransform(hInputProfile,
                                             findLCMStype(sInMode),
                                             hOutputProfile,
                                             findLCMStype(sOutMode),
                                             hProofProfile,
                                             iRenderingIntent,
                                             iProofIntent,
                                             cmsFLAGS);

    Py_END_ALLOW_THREADS

    if (!hTransform)
        PyErr_SetString(PyExc_ValueError, "cannot build proof transform");

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

    if (!PyArg_ParseTuple(args, "O!O!ss|ii:buildTransform", &CmsProfile_Type, &pInputProfile, &CmsProfile_Type, &pOutputProfile, &sInMode, &sOutMode, &iRenderingIntent, &cmsFLAGS))
        return NULL;

    cmsErrorAction(LCMS_ERROR_IGNORE);

    transform = _buildTransform(pInputProfile->profile, pOutputProfile->profile, sInMode, sOutMode, iRenderingIntent, cmsFLAGS);

    if (!transform)
        return NULL;

    return cms_transform_new(transform, sInMode, sOutMode);
}

static PyObject *
buildProofTransform(PyObject *self, PyObject *args)
{
    CmsProfileObject *pInputProfile;
    CmsProfileObject *pOutputProfile;
    CmsProfileObject *pProofProfile;
    char *sInMode;
    char *sOutMode;
    int iRenderingIntent = 0;
    int iProofIntent = 0;
    int cmsFLAGS = 0;

    cmsHTRANSFORM transform = NULL;

    if (!PyArg_ParseTuple(args, "O!O!O!ss|iii:buildProofTransform", &CmsProfile_Type, &pInputProfile, &CmsProfile_Type, &pOutputProfile, &CmsProfile_Type, &pProofProfile, &sInMode, &sOutMode, &iRenderingIntent, &iProofIntent, &cmsFLAGS))
        return NULL;

    cmsErrorAction(LCMS_ERROR_IGNORE);

    transform = _buildProofTransform(pInputProfile->profile, pOutputProfile->profile, pProofProfile->profile, sInMode, sOutMode, iRenderingIntent, iProofIntent, cmsFLAGS);
  
    if (!transform)
        return NULL;

    return cms_transform_new(transform, sInMode, sOutMode);

}

static PyObject *
cms_transform_apply(CmsTransformObject *self, PyObject *args)
{
    long idIn;
    long idOut;
    Imaging im;
    Imaging imOut;

    int result;

    if (!PyArg_ParseTuple(args, "ll:apply", &idIn, &idOut))
        return NULL;

    im = (Imaging) idIn;
    imOut = (Imaging) idOut;

    cmsErrorAction(LCMS_ERROR_IGNORE);

    result = pyCMSdoTransform(im, imOut, self->transform);

    return Py_BuildValue("i", result);
}

/* -------------------------------------------------------------------- */
/* Python-Callable On-The-Fly profile creation functions */

static PyObject *
createProfile(PyObject *self, PyObject *args)
{
    char *sColorSpace;
    cmsHPROFILE hProfile;
    int iColorTemp = 0;
    LPcmsCIExyY whitePoint = NULL;
    LCMSBOOL result;

    if (!PyArg_ParseTuple(args, "s|i:createProfile", &sColorSpace, &iColorTemp))
        return NULL;

    cmsErrorAction(LCMS_ERROR_IGNORE);

    if (strcmp(sColorSpace, "LAB") == 0) {
        if (iColorTemp > 0) {
            result = cmsWhitePointFromTemp(iColorTemp, whitePoint);
            if (!result) {
                PyErr_SetString(PyExc_ValueError, "ERROR: Could not calculate white point from color temperature provided, must be integer in degrees Kelvin");
                return NULL;
            }
            hProfile = cmsCreateLabProfile(whitePoint);
        } else
            hProfile = cmsCreateLabProfile(NULL);
    }
    else if (strcmp(sColorSpace, "XYZ") == 0)
        hProfile = cmsCreateXYZProfile();
    else if (strcmp(sColorSpace, "sRGB") == 0)
        hProfile = cmsCreate_sRGBProfile();
    else
        hProfile = NULL;

    if (!hProfile) {
        PyErr_SetString(PyExc_ValueError, "failed to create requested color space");
        return NULL;
    }

    return cms_profile_new(hProfile);
}

/* -------------------------------------------------------------------- */
/* profile methods */

static PyObject *
cms_profile_is_intent_supported(CmsProfileObject *self, PyObject *args)
{
    LCMSBOOL result;

    int intent;
    int direction;
    if (!PyArg_ParseTuple(args, "ii:is_intent_supported", &intent, &direction))
        return NULL;

    result = cmsIsIntentSupported(self->profile, intent, direction);

    /* printf("cmsIsIntentSupported(%p, %d, %d) => %d\n", self->profile, intent, direction, result); */

    return PyInt_FromLong(result != 0);
}

#ifdef WIN32
static PyObject *
cms_get_display_profile_win32(PyObject* self, PyObject* args)
{
    char filename[MAX_PATH];
    DWORD filename_size;
    BOOL ok;

    int handle = 0;
    int is_dc = 0;
    if (!PyArg_ParseTuple(args, "|ii:get_display_profile", &handle, &is_dc))
        return NULL;

    filename_size = sizeof(filename);

    if (is_dc) {
        ok = GetICMProfile((HDC) handle, &filename_size, filename);
    } else {
        HDC dc = GetDC((HWND) handle);
        ok = GetICMProfile(dc, &filename_size, filename);
        ReleaseDC((HWND) handle, dc);
    }

    if (ok)
        return PyString_FromStringAndSize(filename, filename_size-1);

    Py_INCREF(Py_None);
    return Py_None;
}
#endif

/* -------------------------------------------------------------------- */
/* Python interface setup */

static PyMethodDef pyCMSdll_methods[] = {

    {"profile_open", cms_profile_open, 1},
    {"profile_fromstring", cms_profile_fromstring, 1},

    /* profile and transform functions */
    {"buildTransform", buildTransform, 1},
    {"buildProofTransform", buildProofTransform, 1},
    {"createProfile", createProfile, 1},

    /* platform specific tools */
#ifdef WIN32
    {"get_display_profile_win32", cms_get_display_profile_win32, 1},
#endif

    {NULL, NULL}
};

static struct PyMethodDef cms_profile_methods[] = {
    {"is_intent_supported", (PyCFunction) cms_profile_is_intent_supported, 1},
    {NULL, NULL} /* sentinel */
};

static PyObject*  
cms_profile_getattr(CmsProfileObject* self, char* name)
{
    if (!strcmp(name, "product_name"))
        return PyString_FromString(cmsTakeProductName(self->profile));
    if (!strcmp(name, "product_desc"))
        return PyString_FromString(cmsTakeProductDesc(self->profile));
    if (!strcmp(name, "product_info"))
        return PyString_FromString(cmsTakeProductInfo(self->profile));
    if (!strcmp(name, "rendering_intent"))
        return PyInt_FromLong(cmsTakeRenderingIntent(self->profile));
    if (!strcmp(name, "pcs"))
        return PyString_FromString(findICmode(cmsGetPCS(self->profile)));
    if (!strcmp(name, "color_space"))
        return PyString_FromString(findICmode(cmsGetColorSpace(self->profile)));
    /* FIXME: add more properties (creation_datetime etc) */

    return Py_FindMethod(cms_profile_methods, (PyObject*) self, name);
}

statichere PyTypeObject CmsProfile_Type = {
    PyObject_HEAD_INIT(NULL)
    0, "CmsProfile", sizeof(CmsProfileObject), 0,
    /* methods */
    (destructor) cms_profile_dealloc, /*tp_dealloc*/
    0, /*tp_print*/
    (getattrfunc) cms_profile_getattr, /*tp_getattr*/
    0, /*tp_setattr*/
    0, /*tp_compare*/
    0, /*tp_repr*/
    0, /*tp_as_number */
    0, /*tp_as_sequence */
    0, /*tp_as_mapping */
    0 /*tp_hash*/
};

static struct PyMethodDef cms_transform_methods[] = {
    {"apply", (PyCFunction) cms_transform_apply, 1},
    {NULL, NULL} /* sentinel */
};

static PyObject*  
cms_transform_getattr(CmsTransformObject* self, char* name)
{
    if (!strcmp(name, "inputMode"))
        return PyString_FromString(self->mode_in);
    if (!strcmp(name, "outputMode"))
        return PyString_FromString(self->mode_out);

    return Py_FindMethod(cms_transform_methods, (PyObject*) self, name);
}

statichere PyTypeObject CmsTransform_Type = {
    PyObject_HEAD_INIT(NULL)
    0, "CmsTransform", sizeof(CmsTransformObject), 0,
    /* methods */
    (destructor) cms_transform_dealloc, /*tp_dealloc*/
    0, /*tp_print*/
    (getattrfunc) cms_transform_getattr, /*tp_getattr*/
    0, /*tp_setattr*/
    0, /*tp_compare*/
    0, /*tp_repr*/
    0, /*tp_as_number */
    0, /*tp_as_sequence */
    0, /*tp_as_mapping */
    0 /*tp_hash*/
};

DL_EXPORT(void)
init_imagingcms(void)
{
    PyObject *m;
    PyObject *d;
    PyObject *v;

    /* Patch up object types */
    CmsProfile_Type.ob_type = &PyType_Type;
    CmsTransform_Type.ob_type = &PyType_Type;

    m = Py_InitModule("_imagingcms", pyCMSdll_methods);
    d = PyModule_GetDict(m);

#if PY_VERSION_HEX >= 0x02020000
    v = PyString_FromFormat("%d.%d", LCMS_VERSION / 100, LCMS_VERSION % 100);
#else
    {
        char buffer[100];
        sprintf(buffer, "%d.%d", LCMS_VERSION / 100, LCMS_VERSION % 100);
        v = PyString_FromString(buffer);
    }
#endif
    PyDict_SetItemString(d, "littlecms_version", v);
}
