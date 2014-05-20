/*
 * The Python Imaging Library.
 *
 * display support (and other windows-related stuff)
 *
 * History:
 * 1996-05-13 fl  Windows DIB support
 * 1996-05-21 fl  Added palette stuff
 * 1996-05-28 fl  Added display_mode stuff
 * 1997-09-21 fl  Added draw primitive
 * 2001-09-17 fl  Added ImagingGrabScreen (from _grabscreen.c)
 * 2002-05-12 fl  Added ImagingListWindows
 * 2002-11-19 fl  Added clipboard support
 * 2002-11-25 fl  Added GetDC/ReleaseDC helpers
 * 2003-05-21 fl  Added create window support (including window callback)
 * 2003-09-05 fl  Added fromstring/tostring methods
 * 2009-03-14 fl  Added WMF support (from pilwmf)
 *
 * Copyright (c) 1997-2003 by Secret Labs AB.
 * Copyright (c) 1996-1997 by Fredrik Lundh.
 *
 * See the README file for information on usage and redistribution.
 */


#include "Python.h"

#include "Imaging.h"
#include "py3.h"

/* -------------------------------------------------------------------- */
/* Windows DIB support	*/

#ifdef _WIN32

#include "ImDib.h"

typedef struct {
    PyObject_HEAD
    ImagingDIB dib;
} ImagingDisplayObject;

static PyTypeObject ImagingDisplayType;

static ImagingDisplayObject*
_new(const char* mode, int xsize, int ysize)
{
    ImagingDisplayObject *display;

    if (PyType_Ready(&ImagingDisplayType) < 0)
        return NULL;

    display = PyObject_New(ImagingDisplayObject, &ImagingDisplayType);
    if (display == NULL)
	return NULL;

    display->dib = ImagingNewDIB(mode, xsize, ysize);
    if (!display->dib) {
	Py_DECREF(display);
	return NULL;
    }

    return display;
}

static void
_delete(ImagingDisplayObject* display)
{
    if (display->dib)
	ImagingDeleteDIB(display->dib);
    PyObject_Del(display);
}

static PyObject*
_expose(ImagingDisplayObject* display, PyObject* args)
{
    int hdc;
    if (!PyArg_ParseTuple(args, "i", &hdc))
	return NULL;

    ImagingExposeDIB(display->dib, hdc);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_draw(ImagingDisplayObject* display, PyObject* args)
{
    int hdc;
    int dst[4];
    int src[4];
    if (!PyArg_ParseTuple(args, "i(iiii)(iiii)", &hdc,
                          dst+0, dst+1, dst+2, dst+3,
                          src+0, src+1, src+2, src+3))
	return NULL;

    ImagingDrawDIB(display->dib, hdc, dst, src);

    Py_INCREF(Py_None);
    return Py_None;
}

extern Imaging PyImaging_AsImaging(PyObject *op);

static PyObject*
_paste(ImagingDisplayObject* display, PyObject* args)
{
    Imaging im;

    PyObject* op;
    int xy[4];
    xy[0] = xy[1] = xy[2] = xy[3] = 0;
    if (!PyArg_ParseTuple(args, "O|(iiii)", &op, xy+0, xy+1, xy+2, xy+3))
	return NULL;
    im = PyImaging_AsImaging(op);
    if (!im)
	return NULL;

    if (xy[2] <= xy[0])
	xy[2] = xy[0] + im->xsize;
    if (xy[3] <= xy[1])
	xy[3] = xy[1] + im->ysize;

    ImagingPasteDIB(display->dib, im, xy);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_query_palette(ImagingDisplayObject* display, PyObject* args)
{
    int hdc;
    int status;

    if (!PyArg_ParseTuple(args, "i", &hdc))
	return NULL;

    status = ImagingQueryPaletteDIB(display->dib, hdc);

    return Py_BuildValue("i", status);
}

static PyObject*
_getdc(ImagingDisplayObject* display, PyObject* args)
{
    int window;
    HDC dc;

    if (!PyArg_ParseTuple(args, "i", &window))
	return NULL;

    dc = GetDC((HWND) window);
    if (!dc) {
        PyErr_SetString(PyExc_IOError, "cannot create dc");
        return NULL;
    }

    return Py_BuildValue("i", (int) dc);
}

static PyObject*
_releasedc(ImagingDisplayObject* display, PyObject* args)
{
    int window, dc;

    if (!PyArg_ParseTuple(args, "ii", &window, &dc))
	return NULL;

    ReleaseDC((HWND) window, (HDC) dc);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_frombytes(ImagingDisplayObject* display, PyObject* args)
{
    char* ptr;
    int bytes;

#if PY_VERSION_HEX >= 0x03000000
    if (!PyArg_ParseTuple(args, "y#:frombytes", &ptr, &bytes))
        return NULL;
#else
    if (!PyArg_ParseTuple(args, "s#:fromstring", &ptr, &bytes))
        return NULL;
#endif

    if (display->dib->ysize * display->dib->linesize != bytes) {
        PyErr_SetString(PyExc_ValueError, "wrong size");
        return NULL;
    }

    memcpy(display->dib->bits, ptr, bytes);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
_tobytes(ImagingDisplayObject* display, PyObject* args)
{
#if PY_VERSION_HEX >= 0x03000000
    if (!PyArg_ParseTuple(args, ":tobytes"))
        return NULL;
#else
    if (!PyArg_ParseTuple(args, ":tostring"))
        return NULL;
#endif

    return PyBytes_FromStringAndSize(
        display->dib->bits, display->dib->ysize * display->dib->linesize
        );
}

static struct PyMethodDef methods[] = {
    {"draw", (PyCFunction)_draw, 1},
    {"expose", (PyCFunction)_expose, 1},
    {"paste", (PyCFunction)_paste, 1},
    {"query_palette", (PyCFunction)_query_palette, 1},
    {"getdc", (PyCFunction)_getdc, 1},
    {"releasedc", (PyCFunction)_releasedc, 1},
    {"frombytes", (PyCFunction)_frombytes, 1},
    {"tobytes", (PyCFunction)_tobytes, 1},
    {"fromstring", (PyCFunction)_frombytes, 1},
    {"tostring", (PyCFunction)_tobytes, 1},
    {NULL, NULL} /* sentinel */
};

static PyObject*
_getattr_mode(ImagingDisplayObject* self, void* closure)
{
	return Py_BuildValue("s", self->dib->mode);
}

static PyObject*
_getattr_size(ImagingDisplayObject* self, void* closure)
{
	return Py_BuildValue("ii", self->dib->xsize, self->dib->ysize);
}

static struct PyGetSetDef getsetters[] = {
    { "mode",   (getter) _getattr_mode },
    { "size",   (getter) _getattr_size },
    { NULL }
};

static PyTypeObject ImagingDisplayType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"ImagingDisplay",		/*tp_name*/
	sizeof(ImagingDisplayObject),	/*tp_size*/
	0,				/*tp_itemsize*/
	/* methods */
	(destructor)_delete,		/*tp_dealloc*/
	0,				/*tp_print*/
    0,                          /*tp_getattr*/
    0,                          /*tp_setattr*/
    0,                          /*tp_compare*/
    0,                          /*tp_repr*/
    0,                          /*tp_as_number */
    0,                          /*tp_as_sequence */
    0,                          /*tp_as_mapping */
    0,                          /*tp_hash*/
    0,                          /*tp_call*/
    0,                          /*tp_str*/
    0,                          /*tp_getattro*/
    0,                          /*tp_setattro*/
    0,                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,         /*tp_flags*/
    0,                          /*tp_doc*/
    0,                          /*tp_traverse*/
    0,                          /*tp_clear*/
    0,                          /*tp_richcompare*/
    0,                          /*tp_weaklistoffset*/
    0,                          /*tp_iter*/
    0,                          /*tp_iternext*/
    methods,                    /*tp_methods*/
    0,                          /*tp_members*/
    getsetters,                 /*tp_getset*/
};

PyObject*
PyImaging_DisplayWin32(PyObject* self, PyObject* args)
{
    ImagingDisplayObject* display;
    char *mode;
    int xsize, ysize;

    if (!PyArg_ParseTuple(args, "s(ii)", &mode, &xsize, &ysize))
	return NULL;

    display = _new(mode, xsize, ysize);
    if (display == NULL)
	return NULL;

    return (PyObject*) display;
}

PyObject*
PyImaging_DisplayModeWin32(PyObject* self, PyObject* args)
{
    char *mode;
    int size[2];

    mode = ImagingGetModeDIB(size);

    return Py_BuildValue("s(ii)", mode, size[0], size[1]);
}

/* -------------------------------------------------------------------- */
/* Windows screen grabber */

PyObject*
PyImaging_GrabScreenWin32(PyObject* self, PyObject* args)
{
    int width, height;
    HBITMAP bitmap;
    BITMAPCOREHEADER core;
    HDC screen, screen_copy;
    PyObject* buffer;

    /* step 1: create a memory DC large enough to hold the
       entire screen */

    screen = CreateDC("DISPLAY", NULL, NULL, NULL);
    screen_copy = CreateCompatibleDC(screen);

    width = GetDeviceCaps(screen, HORZRES);
    height = GetDeviceCaps(screen, VERTRES);

    bitmap = CreateCompatibleBitmap(screen, width, height);
    if (!bitmap)
        goto error;

    if (!SelectObject(screen_copy, bitmap))
        goto error;

    /* step 2: copy bits into memory DC bitmap */

    if (!BitBlt(screen_copy, 0, 0, width, height, screen, 0, 0, SRCCOPY))
        goto error;

    /* step 3: extract bits from bitmap */

    buffer = PyBytes_FromStringAndSize(NULL, height * ((width*3 + 3) & -4));
    if (!buffer)
        return NULL;

    core.bcSize = sizeof(core);
    core.bcWidth = width;
    core.bcHeight = height;
    core.bcPlanes = 1;
    core.bcBitCount = 24;
    if (!GetDIBits(screen_copy, bitmap, 0, height, PyBytes_AS_STRING(buffer),
                   (BITMAPINFO*) &core, DIB_RGB_COLORS))
        goto error;

    DeleteObject(bitmap);
    DeleteDC(screen_copy);
    DeleteDC(screen);

    return Py_BuildValue("(ii)N", width, height, buffer);

error:
    PyErr_SetString(PyExc_IOError, "screen grab failed");

    DeleteDC(screen_copy);
    DeleteDC(screen);

    return NULL;
}

static BOOL CALLBACK list_windows_callback(HWND hwnd, LPARAM lParam)
{
    PyObject* window_list = (PyObject*) lParam;
    PyObject* item;
    PyObject* title;
    RECT inner, outer;
    int title_size;
    int status;

    /* get window title */
    title_size = GetWindowTextLength(hwnd);
    if (title_size > 0) {
        title = PyUnicode_FromStringAndSize(NULL, title_size);
        if (title)
            GetWindowText(hwnd, PyUnicode_AS_UNICODE(title), title_size+1);
    } else
        title = PyUnicode_FromString("");
    if (!title)
        return 0;

    /* get bounding boxes */
    GetClientRect(hwnd, &inner);
    GetWindowRect(hwnd, &outer);

    item = Py_BuildValue(
        "nN(iiii)(iiii)", (Py_ssize_t) hwnd, title,
        inner.left, inner.top, inner.right, inner.bottom,
        outer.left, outer.top, outer.right, outer.bottom
        );
    if (!item)
        return 0;

    status = PyList_Append(window_list, item);

    Py_DECREF(item);

    if (status < 0)
        return 0;

    return 1;
}

PyObject*
PyImaging_ListWindowsWin32(PyObject* self, PyObject* args)
{
    PyObject* window_list;

    window_list = PyList_New(0);
    if (!window_list)
        return NULL;

    EnumWindows(list_windows_callback, (LPARAM) window_list);

    if (PyErr_Occurred()) {
        Py_DECREF(window_list);
        return NULL;
    }

    return window_list;
}

/* -------------------------------------------------------------------- */
/* Windows clipboard grabber */

PyObject*
PyImaging_GrabClipboardWin32(PyObject* self, PyObject* args)
{
    int clip;
    HANDLE handle;
    int size;
    void* data;
    PyObject* result;

    int verbose = 0; /* debugging; will be removed in future versions */
    if (!PyArg_ParseTuple(args, "|i", &verbose))
	return NULL;


    clip = OpenClipboard(NULL);
    /* FIXME: check error status */

    if (verbose) {
        UINT format = EnumClipboardFormats(0);
        char buffer[200];
        char* result;
        while (format != 0) {
            if (GetClipboardFormatName(format, buffer, sizeof buffer) > 0)
                result = buffer;
            else
                switch (format) {
                case CF_BITMAP:
                    result = "CF_BITMAP";
                    break;
                case CF_DIB:
                    result = "CF_DIB";
                    break;
                case CF_DIF:
                    result = "CF_DIF";
                    break;
                case CF_ENHMETAFILE:
                    result = "CF_ENHMETAFILE";
                    break;
                case CF_HDROP:
                    result = "CF_HDROP";
                    break;
                case CF_LOCALE:
                    result = "CF_LOCALE";
                    break;
                case CF_METAFILEPICT:
                    result = "CF_METAFILEPICT";
                    break;
                case CF_OEMTEXT:
                    result = "CF_OEMTEXT";
                    break;
                case CF_OWNERDISPLAY:
                    result = "CF_OWNERDISPLAY";
                    break;
                case CF_PALETTE:
                    result = "CF_PALETTE";
                    break;
                case CF_PENDATA:
                    result = "CF_PENDATA";
                    break;
                case CF_RIFF:
                    result = "CF_RIFF";
                    break;
                case CF_SYLK:
                    result = "CF_SYLK";
                    break;
                case CF_TEXT:
                    result = "CF_TEXT";
                    break;
                case CF_WAVE:
                    result = "CF_WAVE";
                    break;
                case CF_TIFF:
                    result = "CF_TIFF";
                    break;
                case CF_UNICODETEXT:
                    result = "CF_UNICODETEXT";
                    break;
                default:
                    sprintf(buffer, "[%d]", format);
                    result = buffer;
                    break;
                }
            printf("%s (%d)\n", result, format);
            format = EnumClipboardFormats(format);
        }
    }

    handle = GetClipboardData(CF_DIB);
    if (!handle) {
        /* FIXME: add CF_HDROP support to allow cut-and-paste from
           the explorer */
        CloseClipboard();
        Py_INCREF(Py_None);
        return Py_None;
    }

    size = GlobalSize(handle);
    data = GlobalLock(handle);

#if 0
    /* calculate proper size for string formats */
    if (format == CF_TEXT || format == CF_OEMTEXT)
        size = strlen(data);
    else if (format == CF_UNICODETEXT)
        size = wcslen(data) * 2;
#endif

    result = PyBytes_FromStringAndSize(data, size);

    GlobalUnlock(handle);

    CloseClipboard();

    return result;
}

/* -------------------------------------------------------------------- */
/* Windows class */

#ifndef WM_MOUSEWHEEL
#define WM_MOUSEWHEEL 522
#endif

static int mainloop = 0;

static void
callback_error(const char* handler)
{
    PyObject* sys_stderr;

    sys_stderr = PySys_GetObject("stderr");

    if (sys_stderr) {
        PyFile_WriteString("*** ImageWin: error in ", sys_stderr);
        PyFile_WriteString((char*) handler, sys_stderr);
        PyFile_WriteString(":\n", sys_stderr);
    }

    PyErr_Print();
    PyErr_Clear();
}

static LRESULT CALLBACK
windowCallback(HWND wnd, UINT message, WPARAM wParam, LPARAM lParam)
{
    PAINTSTRUCT ps;
    PyObject* callback = NULL;
    PyObject* result;
    PyThreadState* threadstate;
    PyThreadState* current_threadstate;
    HDC dc;
    RECT rect;
    LRESULT status = 0;

    /* set up threadstate for messages that calls back into python */
    switch (message) {
    case WM_CREATE:
        mainloop++;
        break;
    case WM_DESTROY:
        mainloop--;
        /* fall through... */
    case WM_PAINT:
    case WM_SIZE:
        callback = (PyObject*) GetWindowLong(wnd, 0);
        if (callback) {
            threadstate = (PyThreadState*)
                GetWindowLong(wnd, sizeof(PyObject*));
            current_threadstate = PyThreadState_Swap(NULL);
            PyEval_RestoreThread(threadstate);
        } else
            return DefWindowProc(wnd, message, wParam, lParam);
    }

    /* process message */
    switch (message) {

    case WM_PAINT:
        /* redraw (part of) window.  this generates a WCK-style
           damage/clear/repair cascade */
        BeginPaint(wnd, &ps);
        dc = GetDC(wnd);
        GetWindowRect(wnd, &rect); /* in screen coordinates */

        result = PyObject_CallFunction(
            callback, "siiii", "damage",
            ps.rcPaint.left, ps.rcPaint.top,
            ps.rcPaint.right, ps.rcPaint.bottom
            );
        if (result)
            Py_DECREF(result);
        else
            callback_error("window damage callback");

        result = PyObject_CallFunction(
            callback, "siiiii", "clear", (int) dc,
            0, 0, rect.right-rect.left, rect.bottom-rect.top
            );
        if (result)
            Py_DECREF(result);
        else
            callback_error("window clear callback");

        result = PyObject_CallFunction(
            callback, "siiiii", "repair", (int) dc,
            0, 0, rect.right-rect.left, rect.bottom-rect.top
            );
        if (result)
            Py_DECREF(result);
        else
            callback_error("window repair callback");

        ReleaseDC(wnd, dc);
        EndPaint(wnd, &ps);
        break;

    case WM_SIZE:
        /* resize window */
        result = PyObject_CallFunction(
            callback, "sii", "resize", LOWORD(lParam), HIWORD(lParam)
            );
        if (result) {
            InvalidateRect(wnd, NULL, 1);
            Py_DECREF(result);
        } else
            callback_error("window resize callback");
        break;

    case WM_DESTROY:
        /* destroy window */
        result = PyObject_CallFunction(callback, "s", "destroy");
        if (result)
            Py_DECREF(result);
        else
            callback_error("window destroy callback");
        Py_DECREF(callback);
        break;

    default:
        status = DefWindowProc(wnd, message, wParam, lParam);
    }

    if (callback) {
        /* restore thread state */
        PyEval_SaveThread();
        PyThreadState_Swap(threadstate);
    }

    return status;
}

PyObject*
PyImaging_CreateWindowWin32(PyObject* self, PyObject* args)
{
    HWND wnd;
    WNDCLASS windowClass;

    char* title;
    PyObject* callback;
    int width = 0, height = 0;
    if (!PyArg_ParseTuple(args, "sO|ii", &title, &callback, &width, &height))
	return NULL;

    if (width <= 0)
        width = CW_USEDEFAULT;
    if (height <= 0)
        height = CW_USEDEFAULT;

    /* register toplevel window class */
    windowClass.style = CS_CLASSDC;
    windowClass.cbClsExtra = 0;
    windowClass.cbWndExtra = sizeof(PyObject*) + sizeof(PyThreadState*);
    windowClass.hInstance = GetModuleHandle(NULL);
    /* windowClass.hbrBackground = (HBRUSH) (COLOR_BTNFACE + 1); */
    windowClass.hbrBackground = NULL;
    windowClass.lpszMenuName = NULL;
    windowClass.lpszClassName = "pilWindow";
    windowClass.lpfnWndProc = windowCallback;
    windowClass.hIcon = LoadIcon(GetModuleHandle(NULL), MAKEINTRESOURCE(1));
    windowClass.hCursor = LoadCursor(NULL, IDC_ARROW); /* CROSS? */

    RegisterClass(&windowClass); /* FIXME: check return status */

    wnd = CreateWindowEx(
        0, windowClass.lpszClassName, title,
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, width, height,
        HWND_DESKTOP, NULL, NULL, NULL
        );

    if (!wnd) {
        PyErr_SetString(PyExc_IOError, "failed to create window");
        return NULL;
    }

    /* register window callback */
    Py_INCREF(callback);
    SetWindowLongPtr(wnd, 0, (LONG_PTR) callback);
    SetWindowLongPtr(wnd, sizeof(callback), (LONG_PTR) PyThreadState_Get());

    Py_BEGIN_ALLOW_THREADS
    ShowWindow(wnd, SW_SHOWNORMAL);
    SetForegroundWindow(wnd); /* to make sure it's visible */
    Py_END_ALLOW_THREADS

    return Py_BuildValue("n", (Py_ssize_t) wnd);
}

PyObject*
PyImaging_EventLoopWin32(PyObject* self, PyObject* args)
{
    MSG msg;

    Py_BEGIN_ALLOW_THREADS
    while (mainloop && GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    Py_END_ALLOW_THREADS

    Py_INCREF(Py_None);
    return Py_None;
}

/* -------------------------------------------------------------------- */
/* windows WMF renderer */

#define GET32(p,o) ((DWORD*)(p+o))[0]

PyObject *
PyImaging_DrawWmf(PyObject* self, PyObject* args)
{
    HBITMAP bitmap;
    HENHMETAFILE meta;
    BITMAPCOREHEADER core;
    HDC dc;
    RECT rect;
    PyObject* buffer = NULL;
    char* ptr;

    char* data;
    int datasize;
    int width, height;
    int x0, y0, x1, y1;
    if (!PyArg_ParseTuple(args, PY_ARG_BYTES_LENGTH"(ii)(iiii):_load", &data, &datasize,
                          &width, &height, &x0, &x1, &y0, &y1))
        return NULL;

    /* step 1: copy metafile contents into METAFILE object */

    if (datasize > 22 && GET32(data, 0) == 0x9ac6cdd7) {

        /* placeable windows metafile (22-byte aldus header) */
        meta = SetWinMetaFileBits(datasize-22, data+22, NULL, NULL);

    } else if (datasize > 80 && GET32(data, 0) == 1 &&
               GET32(data, 40) == 0x464d4520) {

        /* enhanced metafile */
        meta = SetEnhMetaFileBits(datasize, data);

    } else {

        /* unknown meta format */
        meta = NULL;

    }

    if (!meta) {
        PyErr_SetString(PyExc_IOError, "cannot load metafile");
        return NULL;
    }

    /* step 2: create bitmap */

    core.bcSize = sizeof(core);
    core.bcWidth = width;
    core.bcHeight = height;
    core.bcPlanes = 1;
    core.bcBitCount = 24;

    dc = CreateCompatibleDC(NULL);

    bitmap = CreateDIBSection(
        dc, (BITMAPINFO*) &core, DIB_RGB_COLORS, &ptr, NULL, 0
        );

    if (!bitmap) {
        PyErr_SetString(PyExc_IOError, "cannot create bitmap");
        goto error;
    }

    if (!SelectObject(dc, bitmap)) {
        PyErr_SetString(PyExc_IOError, "cannot select bitmap");
        goto error;
    }

    /* step 3: render metafile into bitmap */

    rect.left = rect.top = 0;
    rect.right = width;
    rect.bottom = height;

    /* FIXME: make background transparent? configurable? */
    FillRect(dc, &rect, GetStockObject(WHITE_BRUSH));

    if (!PlayEnhMetaFile(dc, meta, &rect)) {
        PyErr_SetString(PyExc_IOError, "cannot render metafile");
        goto error;
    }

    /* step 4: extract bits from bitmap */

    GdiFlush();

    buffer = PyBytes_FromStringAndSize(ptr, height * ((width*3 + 3) & -4));

error:
    DeleteEnhMetaFile(meta);

    if (bitmap)
        DeleteObject(bitmap);

    DeleteDC(dc);

    return buffer;
}

#endif /* _WIN32 */
