/*
 * The Python Imaging Library.
 * $Id$
 *
 * TK interface for Python Imaging objects
 *
 * Copies (parts of) a named display memory to a photo image object.
 * Also contains code to create an display memory.  Under Tk, a
 * display memory is simply an "L" or "RGB" image memory that is
 * allocated in a single block.
 *
 * To use this module, import the _imagingtk module (ImageTk does
 * this for you).
 *
 * If you're using Python in an embedded context, you can add the
 * following lines to your Tcl_AppInit function (in tkappinit.c)
 * instead.  Put them after the calls to Tcl_Init and Tk_Init:
 *
 *      {
 *          extern void TkImaging_Init(Tcl_Interp* interp);
 *          TkImaging_Init(interp);
 *      }
 *
 * This registers a Tcl command called "PyImagingPhoto", which is used
 * to communicate between PIL and Tk's PhotoImage handler.
 *

 * History:
 * 1995-09-12 fl  Created
 * 1996-04-08 fl  Ready for release
 * 1997-05-09 fl  Use command instead of image type
 * 2001-03-18 fl  Initialize alpha layer pointer (struct changed in 8.3)
 * 2003-04-23 fl  Fixed building for Tk 8.4.1 and later (Jack Jansen)
 * 2004-06-24 fl  Fixed building for Tk 8.4.6 and later.
 *
 * Copyright (c) 1997-2004 by Secret Labs AB
 * Copyright (c) 1995-2004 by Fredrik Lundh
 *
 * See the README file for information on usage and redistribution.
 */

#include "../libImaging/Imaging.h"
#include "_tkmini.h"

#include <stdlib.h>

/*
 * Global vars for Tcl / Tk functions.  We load these symbols from the tkinter
 * extension module or loaded Tcl / Tk libraries at run-time.
 */
static int TK_LT_85 = 0;
static Tcl_CreateCommand_t TCL_CREATE_COMMAND;
static Tcl_AppendResult_t TCL_APPEND_RESULT;
static Tk_FindPhoto_t TK_FIND_PHOTO;
static Tk_PhotoGetImage_t TK_PHOTO_GET_IMAGE;
static Tk_PhotoPutBlock_84_t TK_PHOTO_PUT_BLOCK_84;
static Tk_PhotoSetSize_84_t TK_PHOTO_SET_SIZE_84;
static Tk_PhotoPutBlock_85_t TK_PHOTO_PUT_BLOCK_85;

static Imaging
ImagingFind(const char *name) {
    Py_ssize_t id;

    /* FIXME: use CObject instead? */
#if defined(_WIN64)
    id = _atoi64(name);
#else
    id = atol(name);
#endif
    if (!id) {
        return NULL;
    }

    return (Imaging)id;
}

static int
PyImagingPhotoPut(
    ClientData clientdata, Tcl_Interp *interp, int argc, const char **argv) {
    Imaging im;
    Tk_PhotoHandle photo;
    Tk_PhotoImageBlock block;

    if (argc != 3) {
        TCL_APPEND_RESULT(
            interp, "usage: ", argv[0], " destPhoto srcImage", (char *)NULL);
        return TCL_ERROR;
    }

    /* get Tcl PhotoImage handle */
    photo = TK_FIND_PHOTO(interp, argv[1]);
    if (photo == NULL) {
        TCL_APPEND_RESULT(interp, "destination photo must exist", (char *)NULL);
        return TCL_ERROR;
    }

    /* get PIL Image handle */
    im = ImagingFind(argv[2]);
    if (!im) {
        TCL_APPEND_RESULT(interp, "bad name", (char *)NULL);
        return TCL_ERROR;
    }
    if (!im->block) {
        TCL_APPEND_RESULT(interp, "bad display memory", (char *)NULL);
        return TCL_ERROR;
    }

    /* Mode */

    if (strcmp(im->mode, "1") == 0 || strcmp(im->mode, "L") == 0) {
        block.pixelSize = 1;
        block.offset[0] = block.offset[1] = block.offset[2] = block.offset[3] = 0;
    } else if (strncmp(im->mode, "RGB", 3) == 0) {
        block.pixelSize = 4;
        block.offset[0] = 0;
        block.offset[1] = 1;
        block.offset[2] = 2;
        if (strcmp(im->mode, "RGBA") == 0) {
            block.offset[3] = 3; /* alpha (or reserved, under 8.2) */
        } else {
            block.offset[3] = 0; /* no alpha */
        }
    } else {
        TCL_APPEND_RESULT(interp, "Bad mode", (char *)NULL);
        return TCL_ERROR;
    }

    block.width = im->xsize;
    block.height = im->ysize;
    block.pitch = im->linesize;
    block.pixelPtr = (unsigned char *)im->block;

    if (TK_LT_85) { /* Tk 8.4 */
        TK_PHOTO_PUT_BLOCK_84(
            photo, &block, 0, 0, block.width, block.height, TK_PHOTO_COMPOSITE_SET);
        if (strcmp(im->mode, "RGBA") == 0) {
            /* Tk workaround: we need apply ToggleComplexAlphaIfNeeded */
            /* (fixed in Tk 8.5a3) */
            TK_PHOTO_SET_SIZE_84(photo, block.width, block.height);
        }
    } else {
        /* Tk >=8.5 */
        TK_PHOTO_PUT_BLOCK_85(
            interp,
            photo,
            &block,
            0,
            0,
            block.width,
            block.height,
            TK_PHOTO_COMPOSITE_SET);
    }

    return TCL_OK;
}

static int
PyImagingPhotoGet(
    ClientData clientdata, Tcl_Interp *interp, int argc, const char **argv) {
    Imaging im;
    Tk_PhotoHandle photo;
    Tk_PhotoImageBlock block;
    int x, y, z;

    if (argc != 3) {
        TCL_APPEND_RESULT(
            interp, "usage: ", argv[0], " srcPhoto destImage", (char *)NULL);
        return TCL_ERROR;
    }

    /* get Tcl PhotoImage handle */
    photo = TK_FIND_PHOTO(interp, argv[1]);
    if (photo == NULL) {
        TCL_APPEND_RESULT(interp, "source photo must exist", (char *)NULL);
        return TCL_ERROR;
    }

    /* get PIL Image handle */
    im = ImagingFind(argv[2]);
    if (!im) {
        TCL_APPEND_RESULT(interp, "bad name", (char *)NULL);
        return TCL_ERROR;
    }

    TK_PHOTO_GET_IMAGE(photo, &block);

    for (y = 0; y < block.height; y++) {
        UINT8 *out = (UINT8 *)im->image32[y];
        for (x = 0; x < block.pitch; x += block.pixelSize) {
            for (z = 0; z < block.pixelSize; z++) {
                int offset = block.offset[z];
                out[x + offset] = block.pixelPtr[y * block.pitch + x + offset];
            }
        }
    }

    return TCL_OK;
}

void
TkImaging_Init(Tcl_Interp *interp) {
    TCL_CREATE_COMMAND(
        interp,
        "PyImagingPhoto",
        PyImagingPhotoPut,
        (ClientData)0,
        (Tcl_CmdDeleteProc *)NULL);
    TCL_CREATE_COMMAND(
        interp,
        "PyImagingPhotoGet",
        PyImagingPhotoGet,
        (ClientData)0,
        (Tcl_CmdDeleteProc *)NULL);
}

/*
 * Functions to fill global Tcl / Tk function pointers by dynamic loading
 */

#define TKINTER_FINDER "PIL._tkinter_finder"

#if defined(_WIN32) || defined(__WIN32__) || defined(WIN32)

/*
 * On Windows, we can't load the tkinter module to get the Tcl or Tk symbols,
 * because Windows does not load symbols into the library name-space of
 * importing modules. So, knowing that tkinter has already been imported by
 * Python, we scan all modules in the running process for the Tcl and Tk
 * function names.
 */
#include <windows.h>
#define PSAPI_VERSION 1
#include <psapi.h>
/* Must be linked with 'psapi' library */

#define TKINTER_PKG "tkinter"

FARPROC
_dfunc(HMODULE lib_handle, const char *func_name) {
    /*
     * Load function `func_name` from `lib_handle`.
     * Set Python exception if we can't find `func_name` in `lib_handle`.
     * Returns function pointer or NULL if not present.
     */

    char message[100];

    FARPROC func = GetProcAddress(lib_handle, func_name);
    if (func == NULL) {
        sprintf(message, "Cannot load function %s", func_name);
        PyErr_SetString(PyExc_RuntimeError, message);
    }
    return func;
}

int
get_tcl(HMODULE hMod) {
    /*
     * Try to fill Tcl global vars with function pointers. Return 0 for no
     * functions found, 1 for all functions found, -1 for some but not all
     * functions found.
     */

    if ((TCL_CREATE_COMMAND =
             (Tcl_CreateCommand_t)GetProcAddress(hMod, "Tcl_CreateCommand")) == NULL) {
        return 0; /* Maybe not Tcl module */
    }
    return ((TCL_APPEND_RESULT =
                 (Tcl_AppendResult_t)_dfunc(hMod, "Tcl_AppendResult")) == NULL)
               ? -1
               : 1;
}

int
get_tk(HMODULE hMod) {
    /*
     * Try to fill Tk global vars with function pointers. Return 0 for no
     * functions found, 1 for all functions found, -1 for some but not all
     * functions found.
     */

    FARPROC func = GetProcAddress(hMod, "Tk_PhotoPutBlock");
    if (func == NULL) { /* Maybe not Tk module */
        return 0;
    }
    if ((TK_PHOTO_GET_IMAGE = (Tk_PhotoGetImage_t)_dfunc(hMod, "Tk_PhotoGetImage")) ==
        NULL) {
        return -1;
    };
    if ((TK_FIND_PHOTO = (Tk_FindPhoto_t)_dfunc(hMod, "Tk_FindPhoto")) == NULL) {
        return -1;
    };
    TK_LT_85 = GetProcAddress(hMod, "Tk_PhotoPutBlock_Panic") == NULL;
    /* Tk_PhotoPutBlock_Panic defined as of 8.5.0 */
    if (TK_LT_85) {
        TK_PHOTO_PUT_BLOCK_84 = (Tk_PhotoPutBlock_84_t)func;
        return ((TK_PHOTO_SET_SIZE_84 =
                     (Tk_PhotoSetSize_84_t)_dfunc(hMod, "Tk_PhotoSetSize")) == NULL)
                   ? -1
                   : 1;
    }
    TK_PHOTO_PUT_BLOCK_85 = (Tk_PhotoPutBlock_85_t)func;
    return 1;
}

int
load_tkinter_funcs(void) {
    /*
     * Load Tcl and Tk functions by searching all modules in current process.
     * Return 0 for success, non-zero for failure.
     */

    HMODULE hMods[1024];
    HANDLE hProcess;
    DWORD cbNeeded;
    unsigned int i;
    int found_tcl = 0;
    int found_tk = 0;

    /* First load tkinter module to make sure libraries are loaded */
    PyObject *pModule = PyImport_ImportModule(TKINTER_PKG);
    if (pModule == NULL) {
        return 1;
    }
    Py_DECREF(pModule);

    /* Returns pseudo-handle that does not need to be closed */
    hProcess = GetCurrentProcess();

    /* Iterate through modules in this process looking for Tcl / Tk names */
    if (EnumProcessModules(hProcess, hMods, sizeof(hMods), &cbNeeded)) {
        for (i = 0; i < (cbNeeded / sizeof(HMODULE)); i++) {
            if (!found_tcl) {
                found_tcl = get_tcl(hMods[i]);
                if (found_tcl == -1) {
                    return 1;
                }
            }
            if (!found_tk) {
                found_tk = get_tk(hMods[i]);
                if (found_tk == -1) {
                    return 1;
                }
            }
            if (found_tcl && found_tk) {
                return 0;
            }
        }
    }

    if (found_tcl == 0) {
        PyErr_SetString(PyExc_RuntimeError, "Could not find Tcl routines");
    } else {
        PyErr_SetString(PyExc_RuntimeError, "Could not find Tk routines");
    }
    return 1;
}

#else /* not Windows */

/*
 * On Unix, we can get the Tcl and Tk symbols from the tkinter module, because
 * tkinter uses these symbols, and the symbols are therefore visible in the
 * tkinter dynamic library (module).
 */

/* From module __file__ attribute to char *string for dlopen. */
char *
fname2char(PyObject *fname) {
    PyObject *bytes;
    bytes = PyUnicode_EncodeFSDefault(fname);
    if (bytes == NULL) {
        return NULL;
    }
    return PyBytes_AsString(bytes);
}

#include <dlfcn.h>

void *
_dfunc(void *lib_handle, const char *func_name) {
    /*
     * Load function `func_name` from `lib_handle`.
     * Set Python exception if we can't find `func_name` in `lib_handle`.
     * Returns function pointer or NULL if not present.
     */

    void *func;
    /* Reset errors. */
    dlerror();
    func = dlsym(lib_handle, func_name);
    if (func == NULL) {
        const char *error = dlerror();
        PyErr_SetString(PyExc_RuntimeError, error);
    }
    return func;
}

int
_func_loader(void *lib) {
    /*
     * Fill global function pointers from dynamic lib.
     * Return 1 if any pointer is NULL, 0 otherwise.
     */

    if ((TCL_CREATE_COMMAND = (Tcl_CreateCommand_t)_dfunc(lib, "Tcl_CreateCommand")) ==
        NULL) {
        return 1;
    }
    if ((TCL_APPEND_RESULT = (Tcl_AppendResult_t)_dfunc(lib, "Tcl_AppendResult")) ==
        NULL) {
        return 1;
    }
    if ((TK_PHOTO_GET_IMAGE = (Tk_PhotoGetImage_t)_dfunc(lib, "Tk_PhotoGetImage")) ==
        NULL) {
        return 1;
    }
    if ((TK_FIND_PHOTO = (Tk_FindPhoto_t)_dfunc(lib, "Tk_FindPhoto")) == NULL) {
        return 1;
    }
    /* Tk_PhotoPutBlock_Panic defined as of 8.5.0 */
    TK_LT_85 = (dlsym(lib, "Tk_PhotoPutBlock_Panic") == NULL);
    if (TK_LT_85) {
        return (
            ((TK_PHOTO_PUT_BLOCK_84 =
                  (Tk_PhotoPutBlock_84_t)_dfunc(lib, "Tk_PhotoPutBlock")) == NULL) ||
            ((TK_PHOTO_SET_SIZE_84 =
                  (Tk_PhotoSetSize_84_t)_dfunc(lib, "Tk_PhotoSetSize")) == NULL));
    }
    return (
        (TK_PHOTO_PUT_BLOCK_85 =
             (Tk_PhotoPutBlock_85_t)_dfunc(lib, "Tk_PhotoPutBlock")) == NULL);
}

int
load_tkinter_funcs(void) {
    /*
     * Load tkinter global funcs from tkinter compiled module.
     * Return 0 for success, non-zero for failure.
     */

    int ret = -1;
    void *main_program, *tkinter_lib;
    char *tkinter_libname;
    PyObject *pModule = NULL, *pString = NULL;

    /* Try loading from the main program namespace first */
    main_program = dlopen(NULL, RTLD_LAZY);
    if (_func_loader(main_program) == 0) {
        dlclose(main_program);
        return 0;
    }
    /* Clear exception triggered when we didn't find symbols above */
    PyErr_Clear();

    /* Now try finding the tkinter compiled module */
    pModule = PyImport_ImportModule(TKINTER_FINDER);
    if (pModule == NULL) {
        goto exit;
    }
    pString = PyObject_GetAttrString(pModule, "TKINTER_LIB");
    if (pString == NULL) {
        goto exit;
    }
    tkinter_libname = fname2char(pString);
    if (tkinter_libname == NULL) {
        goto exit;
    }
    tkinter_lib = dlopen(tkinter_libname, RTLD_LAZY);
    if (tkinter_lib == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Cannot dlopen tkinter module file");
        goto exit;
    }
    ret = _func_loader(tkinter_lib);
    /* dlclose probably safe because tkinter has been imported. */
    dlclose(tkinter_lib);
exit:
    dlclose(main_program);
    Py_XDECREF(pModule);
    Py_XDECREF(pString);
    return ret;
}
#endif /* end not Windows */
