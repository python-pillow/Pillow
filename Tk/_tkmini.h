/* Small excerpts from the Tcl / Tk 8.6 headers
 *
 * License terms copied from:
 * http://www.tcl.tk/software/tcltk/license.html
 * as of 20 May 2016.
 *
 * Copyright (c) 1987-1994 The Regents of the University of California.
 * Copyright (c) 1993-1996 Lucent Technologies.
 * Copyright (c) 1994-1998 Sun Microsystems, Inc.
 * Copyright (c) 1998-2000 by Scriptics Corporation.
 * Copyright (c) 2002 by Kevin B. Kenny.  All rights reserved.
 *
 * This software is copyrighted by the Regents of the University
 * of California, Sun Microsystems, Inc., Scriptics Corporation,
 * and other parties. The following terms apply to all files
 * associated with the software unless explicitly disclaimed in
 * individual files.
 *
 * The authors hereby grant permission to use, copy, modify,
 * distribute, and license this software and its documentation
 * for any purpose, provided that existing copyright notices are
 * retained in all copies and that this notice is included
 * verbatim in any distributions. No written agreement, license,
 * or royalty fee is required for any of the authorized uses.
 * Modifications to this software may be copyrighted by their
 * authors and need not follow the licensing terms described
 * here, provided that the new terms are clearly indicated on
 * the first page of each file where they apply.
 *
 * IN NO EVENT SHALL THE AUTHORS OR DISTRIBUTORS BE LIABLE TO
 * ANY PARTY FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR
 * CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF THIS
 * SOFTWARE, ITS DOCUMENTATION, OR ANY DERIVATIVES THEREOF, EVEN
 * IF THE AUTHORS HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH
 * DAMAGE.
 *
 * THE AUTHORS AND DISTRIBUTORS SPECIFICALLY DISCLAIM ANY
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
 * PURPOSE, AND NON-INFRINGEMENT. THIS SOFTWARE IS PROVIDED ON
 * AN "AS IS" BASIS, AND THE AUTHORS AND DISTRIBUTORS HAVE NO
 * OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
 * ENHANCEMENTS, OR MODIFICATIONS.
 *
 * GOVERNMENT USE: If you are acquiring this software on behalf
 * of the U.S. government, the Government shall have only
 * "Restricted Rights" in the software and related documentation
 * as defined in the Federal Acquisition Regulations (FARs) in
 * Clause 52.227.19 (c) (2). If you are acquiring the software
 * on behalf of the Department of Defense, the software shall be
 * classified as "Commercial Computer Software" and the
 * Government shall have only "Restricted Rights" as defined in
 * Clause 252.227-7013 (c) (1) of DFARs. Notwithstanding the
 * foregoing, the authors grant the U.S. Government and others
 * acting in its behalf permission to use and distribute the
 * software in accordance with the terms specified in this
 * license
 */

/*
 * Unless otherwise noted, these definitions are stable from Tcl / Tk 8.4
 * through Tcl / Tk master as of 21 May 2016
 */

#ifdef __cplusplus
extern "C" {
#endif

/* Tcl header excerpts */
#define TCL_OK 0
#define TCL_ERROR 1

/*
 * Users of versions of Tcl >= 8.6 encouraged to treat Tcl_Interp as an opaque
 * pointer.  The following definition results when TCL_NO_DEPRECATED defined.
 */
typedef struct Tcl_Interp Tcl_Interp;

typedef struct Tcl_Command_ *Tcl_Command;
typedef void *ClientData;

typedef int (Tcl_CmdProc) (ClientData clientData, Tcl_Interp
        *interp, int argc, const char *argv[]);
typedef void (Tcl_CmdDeleteProc) (ClientData clientData);

/* Typedefs derived from function signatures in Tcl header */
/* Tcl_CreateCommand */
typedef Tcl_Command (*Tcl_CreateCommand_t)(Tcl_Interp *interp,
        const char *cmdName, Tcl_CmdProc *proc,
        ClientData clientData,
        Tcl_CmdDeleteProc *deleteProc);
/* Tcl_AppendResult */
typedef void (*Tcl_AppendResult_t) (Tcl_Interp *interp, ...);

/* Tk header excerpts */

/*
 * The following values control how blocks are combined into photo
 * images when the alpha component of a pixel is not 255, a.k.a. the
 * compositing rule.
 */

#define TK_PHOTO_COMPOSITE_OVERLAY 0
#define TK_PHOTO_COMPOSITE_SET 1

typedef struct Tk_Window_ *Tk_Window;

typedef void *Tk_PhotoHandle;

typedef struct Tk_PhotoImageBlock
{
    unsigned char *pixelPtr;
    int width;
    int height;
    int pitch;
    int pixelSize;
    int offset[4];
} Tk_PhotoImageBlock;

/* Typedefs derived from function signatures in Tk header */
/* Tk_PhotoPutBlock for Tk <= 8.4 */
typedef void (*Tk_PhotoPutBlock_84_t) (Tk_PhotoHandle handle,
        Tk_PhotoImageBlock *blockPtr, int x, int y,
        int width, int height, int compRule);
/* Tk_PhotoPutBlock for Tk >= 8.5 */
typedef int (*Tk_PhotoPutBlock_85_t) (Tcl_Interp * interp,
        Tk_PhotoHandle handle,
        Tk_PhotoImageBlock * blockPtr, int x, int y,
        int width, int height, int compRule);
/* Tk_PhotoSetSize for Tk <= 8.4 */
typedef void (*Tk_PhotoSetSize_84_t) (Tk_PhotoHandle handle,
        int width, int height);
/* Tk_FindPhoto */
typedef Tk_PhotoHandle (*Tk_FindPhoto_t) (Tcl_Interp *interp,
        const char *imageName);
/* Tk_PhotoGetImage */
typedef int (*Tk_PhotoGetImage_t) (Tk_PhotoHandle handle,
        Tk_PhotoImageBlock * blockPtr);

/*
 * end block for C++
 */

#ifdef __cplusplus
}
#endif
