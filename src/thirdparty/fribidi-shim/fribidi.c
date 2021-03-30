
#ifndef _WIN32
#include <dlfcn.h>
#else
#define WIN32_LEAN_AND_MEAN
#include <Windows.h>
#endif

#define FRIBIDI_SHIM_IMPLEMENTATION

#include "fribidi.h"


/* FriBiDi>=1.0.0 adds bracket_types param, ignore and call legacy function */
FriBidiLevel fribidi_get_par_embedding_levels_ex_compat(
    const FriBidiCharType *bidi_types,
    const FriBidiBracketType *bracket_types,
    const FriBidiStrIndex len,
    FriBidiParType *pbase_dir,
    FriBidiLevel *embedding_levels)
{
    return fribidi_get_par_embedding_levels(
        bidi_types, len, pbase_dir, embedding_levels);
}

/* FriBiDi>=1.0.0 gets bracket types here, ignore */
void fribidi_get_bracket_types_compat(
    const FriBidiChar *str,
    const FriBidiStrIndex len,
    const FriBidiCharType *types,
    FriBidiBracketType *btypes)
{ /* no-op*/ }


int load_fribidi(void) {
    int error = 0;

    p_fribidi = 0;

    /* Microsoft needs a totally different system */
#ifndef _WIN32
#define LOAD_FUNCTION(func) \
    func = (t_##func)dlsym(p_fribidi, #func); \
    error = error || (func == 0);

    p_fribidi = dlopen("libfribidi.so", RTLD_LAZY);
    if (!p_fribidi) {
        p_fribidi = dlopen("libfribidi.so.0", RTLD_LAZY);
    }
    if (!p_fribidi) {
        p_fribidi = dlopen("libfribidi.dylib", RTLD_LAZY);
    }
#else
#define LOAD_FUNCTION(func) \
    func = (t_##func)GetProcAddress(p_fribidi, #func); \
    error = error || (func == 0);

    p_fribidi = LoadLibrary("fribidi");
    if (!p_fribidi) {
        p_fribidi = LoadLibrary("fribidi-0");
    }
    /* MSYS2 */
    if (!p_fribidi) {
        p_fribidi = LoadLibrary("libfribidi-0");
    }
#endif

    if (!p_fribidi) {
        return 1;
    }

    /* load FriBiDi>=1.0.0 functions first, use error to detect version */
    LOAD_FUNCTION(fribidi_get_par_embedding_levels_ex);
    LOAD_FUNCTION(fribidi_get_bracket_types);
    if (error) {
        /* using FriBiDi<1.0.0, ignore new parameters */
        error = 0;
        fribidi_get_par_embedding_levels_ex = &fribidi_get_par_embedding_levels_ex_compat;
        fribidi_get_bracket_types = &fribidi_get_bracket_types_compat;
    }

    LOAD_FUNCTION(fribidi_unicode_to_charset);
    LOAD_FUNCTION(fribidi_charset_to_unicode);
    LOAD_FUNCTION(fribidi_get_bidi_types);
    LOAD_FUNCTION(fribidi_get_par_embedding_levels);

#ifndef _WIN32
    fribidi_version_info = *(const char**)dlsym(p_fribidi, "fribidi_version_info");
    if (dlerror() || error || (fribidi_version_info == 0)) {
        dlclose(p_fribidi);
        p_fribidi = 0;
        return 2;
    }
#else
    fribidi_version_info = *(const char**)GetProcAddress(p_fribidi, "fribidi_version_info");
    if (error || (fribidi_version_info == 0)) {
        FreeLibrary(p_fribidi);
        p_fribidi = 0;
        return 2;
    }
#endif

    return 0;
}
