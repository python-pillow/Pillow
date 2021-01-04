/*
 * The Python Imaging Library
 * $Id$
 *
 * default exception handling
 *
 * This module is usually overridden by application code (e.g.
 * _imaging.c for PIL's standard Python bindings).  If you get
 * linking errors, remove this file from your project/library.
 *
 * history:
 * 1995-06-15 fl   Created
 * 1998-12-29 fl   Minor tweaks
 * 2003-09-13 fl   Added ImagingEnter/LeaveSection()
 *
 * Copyright (c) 1997-2003 by Secret Labs AB.
 * Copyright (c) 1995-2003 by Fredrik Lundh.
 *
 * See the README file for information on usage and redistribution.
 */

#include "Imaging.h"

/* exception state */

void *
ImagingError_OSError(void) {
    fprintf(stderr, "*** exception: file access error\n");
    return NULL;
}

void *
ImagingError_MemoryError(void) {
    fprintf(stderr, "*** exception: out of memory\n");
    return NULL;
}

void *
ImagingError_ModeError(void) {
    return ImagingError_ValueError("bad image mode");
}

void *
ImagingError_Mismatch(void) {
    return ImagingError_ValueError("images don't match");
}

void *
ImagingError_ValueError(const char *message) {
    if (!message) {
        message = "exception: bad argument to function";
    }
    fprintf(stderr, "*** %s\n", message);
    return NULL;
}

void
ImagingError_Clear(void) {
    /* nop */;
}

/* thread state */

void
ImagingSectionEnter(ImagingSectionCookie *cookie) {
    /* pass */
}

void
ImagingSectionLeave(ImagingSectionCookie *cookie) {
    /* pass */
}
