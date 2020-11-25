
#ifndef _WIN32
#include <dlfcn.h>
#else
#define WIN32_LEAN_AND_MEAN
#include <Windows.h>
#endif

#define FRIBIDI_SHIM_IMPLEMENTATION

#include "fribidi.h"

int load_fribidi(void) {
    int error = 0;

    p_fribidi = 0;

    /* Microsoft needs a totally different system */
#ifndef _WIN32
    p_fribidi = dlopen("libfribidi.so.1", RTLD_LAZY);
    if (!p_fribidi) {
        p_fribidi = dlopen("libfribidi.dylib", RTLD_LAZY);
    }
#else
    p_fribidi = LoadLibrary("fribidi");
    /* MSYS2 */
    if (!p_fribidi) {
        p_fribidi = LoadLibrary("libfribidi-0");
    }
#endif

    if (!p_fribidi) {
        return 1;
    }

#ifndef _WIN32
#define LOAD_FUNCTION(func) \
    func = (t_##func)dlsym(p_fribidi, #func); \
    error = error || (func == 0);
#else
#define LOAD_FUNCTION(func) \
    func = (t_##func)GetProcAddress(p_fribidi, #func); \
    error = error || (func == 0);
#endif

    LOAD_FUNCTION(fribidi_get_bidi_types);
    LOAD_FUNCTION(fribidi_get_bracket_types);
    LOAD_FUNCTION(fribidi_get_par_embedding_levels_ex);
//    LOAD_FUNCTION(fribidi_get_par_embedding_levels);
    LOAD_FUNCTION(fribidi_unicode_to_charset);
    LOAD_FUNCTION(fribidi_charset_to_unicode);

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
