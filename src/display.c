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

#define PY_SSIZE_T_CLEAN
#include "Python.h"

#include "libImaging/Imaging.h"

/* -------------------------------------------------------------------- */
/* Windows DIB support */

#ifdef _WIN32

#include "libImaging/ImDib.h"

#if SIZEOF_VOID_P == 8
#define F_HANDLE "K"
#else
#define F_HANDLE "k"
#endif

typedef struct {
    PyObject_HEAD ImagingDIB dib;
} ImagingDisplayObject;

static PyTypeObject ImagingDisplayType;

static ImagingDisplayObject *
_new(const char *mode, int xsize, int ysize) {
    ImagingDisplayObject *display;

    if (PyType_Ready(&ImagingDisplayType) < 0) {
        return NULL;
    }

    display = PyObject_New(ImagingDisplayObject, &ImagingDisplayType);
    if (display == NULL) {
        return NULL;
    }

    display->dib = ImagingNewDIB(mode, xsize, ysize);
    if (!display->dib) {
        Py_DECREF(display);
        return NULL;
    }

    return display;
}

static void
_delete(ImagingDisplayObject *display) {
    if (display->dib) {
        ImagingDeleteDIB(display->dib);
    }
    PyObject_Del(display);
}

static PyObject *
_expose(ImagingDisplayObject *display, PyObject *args) {
    HDC hdc;
    if (!PyArg_ParseTuple(args, F_HANDLE, &hdc)) {
        return NULL;
    }

    ImagingExposeDIB(display->dib, hdc);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_draw(ImagingDisplayObject *display, PyObject *args) {
    HDC hdc;
    int dst[4];
    int src[4];
    if (!PyArg_ParseTuple(
            args,
            F_HANDLE "(iiii)(iiii)",
            &hdc,
            dst + 0,
            dst + 1,
            dst + 2,
            dst + 3,
            src + 0,
            src + 1,
            src + 2,
            src + 3)) {
        return NULL;
    }

    ImagingDrawDIB(display->dib, hdc, dst, src);

    Py_INCREF(Py_None);
    return Py_None;
}

extern Imaging
PyImaging_AsImaging(PyObject *op);

static PyObject *
_paste(ImagingDisplayObject *display, PyObject *args) {
    Imaging im;

    PyObject *op;
    int xy[4];
    xy[0] = xy[1] = xy[2] = xy[3] = 0;
    if (!PyArg_ParseTuple(args, "O|(iiii)", &op, xy + 0, xy + 1, xy + 2, xy + 3)) {
        return NULL;
    }
    im = PyImaging_AsImaging(op);
    if (!im) {
        return NULL;
    }

    if (xy[2] <= xy[0]) {
        xy[2] = xy[0] + im->xsize;
    }
    if (xy[3] <= xy[1]) {
        xy[3] = xy[1] + im->ysize;
    }

    ImagingPasteDIB(display->dib, im, xy);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_query_palette(ImagingDisplayObject *display, PyObject *args) {
    HDC hdc;
    int status;

    if (!PyArg_ParseTuple(args, F_HANDLE, &hdc)) {
        return NULL;
    }

    status = ImagingQueryPaletteDIB(display->dib, hdc);

    return Py_BuildValue("i", status);
}

static PyObject *
_getdc(ImagingDisplayObject *display, PyObject *args) {
    HWND window;
    HDC dc;

    if (!PyArg_ParseTuple(args, F_HANDLE, &window)) {
        return NULL;
    }

    dc = GetDC(window);
    if (!dc) {
        PyErr_SetString(PyExc_OSError, "cannot create dc");
        return NULL;
    }

    return Py_BuildValue(F_HANDLE, dc);
}

static PyObject *
_releasedc(ImagingDisplayObject *display, PyObject *args) {
    HWND window;
    HDC dc;

    if (!PyArg_ParseTuple(args, F_HANDLE F_HANDLE, &window, &dc)) {
        return NULL;
    }

    ReleaseDC(window, dc);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_frombytes(ImagingDisplayObject *display, PyObject *args) {
    char *ptr;
    Py_ssize_t bytes;

    if (!PyArg_ParseTuple(args, "y#:frombytes", &ptr, &bytes)) {
        return NULL;
    }

    if (display->dib->ysize * display->dib->linesize != bytes) {
        PyErr_SetString(PyExc_ValueError, "wrong size");
        return NULL;
    }

    memcpy(display->dib->bits, ptr, bytes);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *
_tobytes(ImagingDisplayObject *display, PyObject *args) {
    if (!PyArg_ParseTuple(args, ":tobytes")) {
        return NULL;
    }

    return PyBytes_FromStringAndSize(
        display->dib->bits, display->dib->ysize * display->dib->linesize);
}

static struct PyMethodDef methods[] = {
    {"draw", (PyCFunction)_draw, METH_VARARGS},
    {"expose", (PyCFunction)_expose, METH_VARARGS},
    {"paste", (PyCFunction)_paste, METH_VARARGS},
    {"query_palette", (PyCFunction)_query_palette, METH_VARARGS},
    {"getdc", (PyCFunction)_getdc, METH_VARARGS},
    {"releasedc", (PyCFunction)_releasedc, METH_VARARGS},
    {"frombytes", (PyCFunction)_frombytes, METH_VARARGS},
    {"tobytes", (PyCFunction)_tobytes, METH_VARARGS},
    {NULL, NULL} /* sentinel */
};

static PyObject *
_getattr_mode(ImagingDisplayObject *self, void *closure) {
    return Py_BuildValue("s", self->dib->mode);
}

static PyObject *
_getattr_size(ImagingDisplayObject *self, void *closure) {
    return Py_BuildValue("ii", self->dib->xsize, self->dib->ysize);
}

static struct PyGetSetDef getsetters[] = {
    {"mode", (getter)_getattr_mode}, {"size", (getter)_getattr_size}, {NULL}};

static PyTypeObject ImagingDisplayType = {
    PyVarObject_HEAD_INIT(NULL, 0) "ImagingDisplay", /*tp_name*/
    sizeof(ImagingDisplayObject),                    /*tp_size*/
    0,                                               /*tp_itemsize*/
    /* methods */
    (destructor)_delete, /*tp_dealloc*/
    0,                   /*tp_print*/
    0,                   /*tp_getattr*/
    0,                   /*tp_setattr*/
    0,                   /*tp_compare*/
    0,                   /*tp_repr*/
    0,                   /*tp_as_number */
    0,                   /*tp_as_sequence */
    0,                   /*tp_as_mapping */
    0,                   /*tp_hash*/
    0,                   /*tp_call*/
    0,                   /*tp_str*/
    0,                   /*tp_getattro*/
    0,                   /*tp_setattro*/
    0,                   /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,  /*tp_flags*/
    0,                   /*tp_doc*/
    0,                   /*tp_traverse*/
    0,                   /*tp_clear*/
    0,                   /*tp_richcompare*/
    0,                   /*tp_weaklistoffset*/
    0,                   /*tp_iter*/
    0,                   /*tp_iternext*/
    methods,             /*tp_methods*/
    0,                   /*tp_members*/
    getsetters,          /*tp_getset*/
};

PyObject *
PyImaging_DisplayWin32(PyObject *self, PyObject *args) {
    ImagingDisplayObject *display;
    char *mode;
    int xsize, ysize;

    if (!PyArg_ParseTuple(args, "s(ii)", &mode, &xsize, &ysize)) {
        return NULL;
    }

    display = _new(mode, xsize, ysize);
    if (display == NULL) {
        return NULL;
    }

    return (PyObject *)display;
}

PyObject *
PyImaging_DisplayModeWin32(PyObject *self, PyObject *args) {
    char *mode;
    int size[2];

    mode = ImagingGetModeDIB(size);

    return Py_BuildValue("s(ii)", mode, size[0], size[1]);
}

/* -------------------------------------------------------------------- */
/* Windows screen grabber */

typedef HANDLE(__stdcall *Func_SetThreadDpiAwarenessContext)(HANDLE);

PyObject *
PyImaging_GrabScreenWin32(PyObject *self, PyObject *args) {
    int x = 0, y = 0, width, height;
    int includeLayeredWindows = 0, all_screens = 0;
    HBITMAP bitmap;
    BITMAPCOREHEADER core;
    HDC screen, screen_copy;
    DWORD rop;
    PyObject *buffer;
    HANDLE dpiAwareness;
    HMODULE user32;
    Func_SetThreadDpiAwarenessContext SetThreadDpiAwarenessContext_function;

    if (!PyArg_ParseTuple(args, "|ii", &includeLayeredWindows, &all_screens)) {
        return NULL;
    }

    /* step 1: create a memory DC large enough to hold the
       entire screen */

    screen = CreateDC("DISPLAY", NULL, NULL, NULL);
    screen_copy = CreateCompatibleDC(screen);

    // added in Windows 10 (1607)
    // loaded dynamically to avoid link errors
    user32 = LoadLibraryA("User32.dll");
    SetThreadDpiAwarenessContext_function =
        (Func_SetThreadDpiAwarenessContext)GetProcAddress(
            user32, "SetThreadDpiAwarenessContext");
    if (SetThreadDpiAwarenessContext_function != NULL) {
        // DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE = ((DPI_CONTEXT_HANDLE)-3)
        dpiAwareness = SetThreadDpiAwarenessContext_function((HANDLE)-3);
    }

    if (all_screens) {
        x = GetSystemMetrics(SM_XVIRTUALSCREEN);
        y = GetSystemMetrics(SM_YVIRTUALSCREEN);
        width = GetSystemMetrics(SM_CXVIRTUALSCREEN);
        height = GetSystemMetrics(SM_CYVIRTUALSCREEN);
    } else {
        width = GetDeviceCaps(screen, HORZRES);
        height = GetDeviceCaps(screen, VERTRES);
    }

    if (SetThreadDpiAwarenessContext_function != NULL) {
        SetThreadDpiAwarenessContext_function(dpiAwareness);
    }

    FreeLibrary(user32);

    bitmap = CreateCompatibleBitmap(screen, width, height);
    if (!bitmap) {
        goto error;
    }

    if (!SelectObject(screen_copy, bitmap)) {
        goto error;
    }

    /* step 2: copy bits into memory DC bitmap */

    rop = SRCCOPY;
    if (includeLayeredWindows) {
        rop |= CAPTUREBLT;
    }
    if (!BitBlt(screen_copy, 0, 0, width, height, screen, x, y, rop)) {
        goto error;
    }

    /* step 3: extract bits from bitmap */

    buffer = PyBytes_FromStringAndSize(NULL, height * ((width * 3 + 3) & -4));
    if (!buffer) {
        return NULL;
    }

    core.bcSize = sizeof(core);
    core.bcWidth = width;
    core.bcHeight = height;
    core.bcPlanes = 1;
    core.bcBitCount = 24;
    if (!GetDIBits(
            screen_copy,
            bitmap,
            0,
            height,
            PyBytes_AS_STRING(buffer),
            (BITMAPINFO *)&core,
            DIB_RGB_COLORS)) {
        goto error;
    }

    DeleteObject(bitmap);
    DeleteDC(screen_copy);
    DeleteDC(screen);

    return Py_BuildValue("(ii)(ii)N", x, y, width, height, buffer);

error:
    PyErr_SetString(PyExc_OSError, "screen grab failed");

    DeleteDC(screen_copy);
    DeleteDC(screen);

    return NULL;
}

static BOOL CALLBACK
list_windows_callback(HWND hwnd, LPARAM lParam) {
    PyObject *window_list = (PyObject *)lParam;
    PyObject *item;
    PyObject *title;
    RECT inner, outer;
    int title_size;
    int status;

    /* get window title */
    title_size = GetWindowTextLength(hwnd);
    if (title_size > 0) {
        title = PyUnicode_FromStringAndSize(NULL, title_size);
        if (title) {
            GetWindowTextW(hwnd, PyUnicode_AS_UNICODE(title), title_size + 1);
        }
    } else {
        title = PyUnicode_FromString("");
    }
    if (!title) {
        return 0;
    }

    /* get bounding boxes */
    GetClientRect(hwnd, &inner);
    GetWindowRect(hwnd, &outer);

    item = Py_BuildValue(
        F_HANDLE "N(iiii)(iiii)",
        hwnd,
        title,
        inner.left,
        inner.top,
        inner.right,
        inner.bottom,
        outer.left,
        outer.top,
        outer.right,
        outer.bottom);
    if (!item) {
        return 0;
    }

    status = PyList_Append(window_list, item);

    Py_DECREF(item);

    if (status < 0) {
        return 0;
    }

    return 1;
}

PyObject *
PyImaging_ListWindowsWin32(PyObject *self, PyObject *args) {
    PyObject *window_list;

    window_list = PyList_New(0);
    if (!window_list) {
        return NULL;
    }

    EnumWindows(list_windows_callback, (LPARAM)window_list);

    if (PyErr_Occurred()) {
        Py_DECREF(window_list);
        return NULL;
    }

    return window_list;
}

/* -------------------------------------------------------------------- */
/* Windows clipboard grabber */

PyObject *
PyImaging_GrabClipboardWin32(PyObject *self, PyObject *args) {
    int clip;
    HANDLE handle = NULL;
    int size;
    void *data;
    PyObject *result;
    UINT format;
    UINT formats[] = {CF_DIB, CF_DIBV5, CF_HDROP, RegisterClipboardFormatA("PNG"), 0};
    LPCSTR format_names[] = {"DIB", "DIB", "file", "png", NULL};

    if (!OpenClipboard(NULL)) {
        PyErr_SetString(PyExc_OSError, "failed to open clipboard");
        return NULL;
    }

    // find best format as set by clipboard owner
    format = 0;
    while (!handle && (format = EnumClipboardFormats(format))) {
        for (UINT i = 0; formats[i] != 0; i++) {
            if (format == formats[i]) {
                handle = GetClipboardData(format);
                format = i;
                break;
            }
        }
    }

    if (!handle) {
        CloseClipboard();
        return Py_BuildValue("zO", NULL, Py_None);
    }

    data = GlobalLock(handle);
    size = GlobalSize(handle);

    result = PyBytes_FromStringAndSize(data, size);

    GlobalUnlock(handle);
    CloseClipboard();

    return Py_BuildValue("zN", format_names[format], result);
}

/* -------------------------------------------------------------------- */
/* Windows class */

#ifndef WM_MOUSEWHEEL
#define WM_MOUSEWHEEL 522
#endif

static int mainloop = 0;

static void
callback_error(const char *handler) {
    PyObject *sys_stderr;

    sys_stderr = PySys_GetObject("stderr");

    if (sys_stderr) {
        PyFile_WriteString("*** ImageWin: error in ", sys_stderr);
        PyFile_WriteString((char *)handler, sys_stderr);
        PyFile_WriteString(":\n", sys_stderr);
    }

    PyErr_Print();
    PyErr_Clear();
}

static LRESULT CALLBACK
windowCallback(HWND wnd, UINT message, WPARAM wParam, LPARAM lParam) {
    PAINTSTRUCT ps;
    PyObject *callback = NULL;
    PyObject *result;
    PyThreadState *threadstate;
    PyThreadState *current_threadstate;
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
            callback = (PyObject *)GetWindowLongPtr(wnd, 0);
            if (callback) {
                threadstate =
                    (PyThreadState *)GetWindowLongPtr(wnd, sizeof(PyObject *));
                current_threadstate = PyThreadState_Swap(NULL);
                PyEval_RestoreThread(threadstate);
            } else {
                return DefWindowProc(wnd, message, wParam, lParam);
            }
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
                callback,
                "siiii",
                "damage",
                ps.rcPaint.left,
                ps.rcPaint.top,
                ps.rcPaint.right,
                ps.rcPaint.bottom);
            if (result) {
                Py_DECREF(result);
            } else {
                callback_error("window damage callback");
            }

            result = PyObject_CallFunction(
                callback,
                "s" F_HANDLE "iiii",
                "clear",
                dc,
                0,
                0,
                rect.right - rect.left,
                rect.bottom - rect.top);
            if (result) {
                Py_DECREF(result);
            } else {
                callback_error("window clear callback");
            }

            result = PyObject_CallFunction(
                callback,
                "s" F_HANDLE "iiii",
                "repair",
                dc,
                0,
                0,
                rect.right - rect.left,
                rect.bottom - rect.top);
            if (result) {
                Py_DECREF(result);
            } else {
                callback_error("window repair callback");
            }

            ReleaseDC(wnd, dc);
            EndPaint(wnd, &ps);
            break;

        case WM_SIZE:
            /* resize window */
            result = PyObject_CallFunction(
                callback, "sii", "resize", LOWORD(lParam), HIWORD(lParam));
            if (result) {
                InvalidateRect(wnd, NULL, 1);
                Py_DECREF(result);
            } else {
                callback_error("window resize callback");
            }
            break;

        case WM_DESTROY:
            /* destroy window */
            result = PyObject_CallFunction(callback, "s", "destroy");
            if (result) {
                Py_DECREF(result);
            } else {
                callback_error("window destroy callback");
            }
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

PyObject *
PyImaging_CreateWindowWin32(PyObject *self, PyObject *args) {
    HWND wnd;
    WNDCLASS windowClass;

    char *title;
    PyObject *callback;
    int width = 0, height = 0;
    if (!PyArg_ParseTuple(args, "sO|ii", &title, &callback, &width, &height)) {
        return NULL;
    }

    if (width <= 0) {
        width = CW_USEDEFAULT;
    }
    if (height <= 0) {
        height = CW_USEDEFAULT;
    }

    /* register toplevel window class */
    windowClass.style = CS_CLASSDC;
    windowClass.cbClsExtra = 0;
    windowClass.cbWndExtra = sizeof(PyObject *) + sizeof(PyThreadState *);
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
        0,
        windowClass.lpszClassName,
        title,
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        width,
        height,
        HWND_DESKTOP,
        NULL,
        NULL,
        NULL);

    if (!wnd) {
        PyErr_SetString(PyExc_OSError, "failed to create window");
        return NULL;
    }

    /* register window callback */
    Py_INCREF(callback);
    SetWindowLongPtr(wnd, 0, (LONG_PTR)callback);
    SetWindowLongPtr(wnd, sizeof(callback), (LONG_PTR)PyThreadState_Get());

    Py_BEGIN_ALLOW_THREADS ShowWindow(wnd, SW_SHOWNORMAL);
    SetForegroundWindow(wnd); /* to make sure it's visible */
    Py_END_ALLOW_THREADS

        return Py_BuildValue(F_HANDLE, wnd);
}

PyObject *
PyImaging_EventLoopWin32(PyObject *self, PyObject *args) {
    MSG msg;

    Py_BEGIN_ALLOW_THREADS while (mainloop && GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
    Py_END_ALLOW_THREADS

        Py_INCREF(Py_None);
    return Py_None;
}

/* -------------------------------------------------------------------- */
/* windows WMF renderer */

#define GET32(p, o) ((DWORD *)(p + o))[0]

PyObject *
PyImaging_DrawWmf(PyObject *self, PyObject *args) {
    HBITMAP bitmap;
    HENHMETAFILE meta;
    BITMAPCOREHEADER core;
    HDC dc;
    RECT rect;
    PyObject *buffer = NULL;
    char *ptr;

    char *data;
    Py_ssize_t datasize;
    int width, height;
    int x0, y0, x1, y1;
    if (!PyArg_ParseTuple(
            args,
            "y#(ii)(iiii):_load",
            &data,
            &datasize,
            &width,
            &height,
            &x0,
            &x1,
            &y0,
            &y1)) {
        return NULL;
    }

    /* step 1: copy metafile contents into METAFILE object */

    if (datasize > 22 && GET32(data, 0) == 0x9ac6cdd7) {
        /* placeable windows metafile (22-byte aldus header) */
        meta = SetWinMetaFileBits(datasize - 22, data + 22, NULL, NULL);

    } else if (datasize > 80 && GET32(data, 0) == 1 && GET32(data, 40) == 0x464d4520) {
        /* enhanced metafile */
        meta = SetEnhMetaFileBits(datasize, data);

    } else {
        /* unknown meta format */
        meta = NULL;
    }

    if (!meta) {
        PyErr_SetString(PyExc_OSError, "cannot load metafile");
        return NULL;
    }

    /* step 2: create bitmap */

    core.bcSize = sizeof(core);
    core.bcWidth = width;
    core.bcHeight = height;
    core.bcPlanes = 1;
    core.bcBitCount = 24;

    dc = CreateCompatibleDC(NULL);

    bitmap = CreateDIBSection(dc, (BITMAPINFO *)&core, DIB_RGB_COLORS, &ptr, NULL, 0);

    if (!bitmap) {
        PyErr_SetString(PyExc_OSError, "cannot create bitmap");
        goto error;
    }

    if (!SelectObject(dc, bitmap)) {
        PyErr_SetString(PyExc_OSError, "cannot select bitmap");
        goto error;
    }

    /* step 3: render metafile into bitmap */

    rect.left = rect.top = 0;
    rect.right = width;
    rect.bottom = height;

    /* FIXME: make background transparent? configurable? */
    FillRect(dc, &rect, GetStockObject(WHITE_BRUSH));

    if (!PlayEnhMetaFile(dc, meta, &rect)) {
        PyErr_SetString(PyExc_OSError, "cannot render metafile");
        goto error;
    }

    /* step 4: extract bits from bitmap */

    GdiFlush();

    buffer = PyBytes_FromStringAndSize(ptr, height * ((width * 3 + 3) & -4));

error:
    DeleteEnhMetaFile(meta);

    if (bitmap) {
        DeleteObject(bitmap);
    }

    DeleteDC(dc);

    return buffer;
}

#endif /* _WIN32 */

/* -------------------------------------------------------------------- */
/* X11 support */

#ifdef HAVE_XCB
#include <xcb/xcb.h>

/* -------------------------------------------------------------------- */
/* X11 screen grabber */

PyObject *
PyImaging_GrabScreenX11(PyObject *self, PyObject *args) {
    int width, height;
    char *display_name;
    xcb_connection_t *connection;
    int screen_number;
    xcb_screen_iterator_t iter;
    xcb_screen_t *screen = NULL;
    xcb_get_image_reply_t *reply;
    xcb_generic_error_t *error;
    PyObject *buffer = NULL;

    if (!PyArg_ParseTuple(args, "|z", &display_name)) {
        return NULL;
    }

    /* connect to X and get screen data */

    connection = xcb_connect(display_name, &screen_number);
    if (xcb_connection_has_error(connection)) {
        PyErr_Format(
            PyExc_OSError,
            "X connection failed: error %i",
            xcb_connection_has_error(connection));
        xcb_disconnect(connection);
        return NULL;
    }

    iter = xcb_setup_roots_iterator(xcb_get_setup(connection));
    for (; iter.rem; --screen_number, xcb_screen_next(&iter)) {
        if (screen_number == 0) {
            screen = iter.data;
            break;
        }
    }
    if (screen == NULL || screen->root == 0) {
        // this case is usually caught with "X connection failed: error 6" above
        xcb_disconnect(connection);
        PyErr_SetString(PyExc_OSError, "X screen not found");
        return NULL;
    }

    width = screen->width_in_pixels;
    height = screen->height_in_pixels;

    /* get image data */

    reply = xcb_get_image_reply(
        connection,
        xcb_get_image(
            connection,
            XCB_IMAGE_FORMAT_Z_PIXMAP,
            screen->root,
            0,
            0,
            width,
            height,
            0x00ffffff),
        &error);
    if (reply == NULL) {
        PyErr_Format(
            PyExc_OSError,
            "X get_image failed: error %i (%i, %i, %i)",
            error->error_code,
            error->major_code,
            error->minor_code,
            error->resource_id);
        free(error);
        xcb_disconnect(connection);
        return NULL;
    }

    /* store data in Python buffer */

    if (reply->depth == 24) {
        buffer = PyBytes_FromStringAndSize(
            (char *)xcb_get_image_data(reply), xcb_get_image_data_length(reply));
    } else {
        PyErr_Format(PyExc_OSError, "unsupported bit depth: %i", reply->depth);
    }

    free(reply);
    xcb_disconnect(connection);

    if (!buffer) {
        return NULL;
    }

    return Py_BuildValue("(ii)N", width, height, buffer);
}

#endif /* HAVE_XCB */
