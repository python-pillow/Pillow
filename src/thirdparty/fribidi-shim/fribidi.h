
#define FRIBIDI_MAJOR_VERSION 1

/* fribidi-types.h */

# if defined (_SVR4) || defined (SVR4) || defined (__OpenBSD__) || \
     defined (_sgi) || defined (__sun) || defined (sun) || \
     defined (__digital__) || defined (__HP_cc)
#  include <inttypes.h>
# elif defined (_AIX)
#  include <sys/inttypes.h>
# else
#  include <stdint.h>
# endif

typedef uint32_t FriBidiChar;
typedef int FriBidiStrIndex;

typedef FriBidiChar FriBidiBracketType;



/* fribidi-char-sets.h */

typedef enum
{
    _FRIBIDI_CHAR_SET_NOT_FOUND,
    FRIBIDI_CHAR_SET_UTF8,
    FRIBIDI_CHAR_SET_CAP_RTL,
    FRIBIDI_CHAR_SET_ISO8859_6,
    FRIBIDI_CHAR_SET_ISO8859_8,
    FRIBIDI_CHAR_SET_CP1255,
    FRIBIDI_CHAR_SET_CP1256,
    _FRIBIDI_CHAR_SETS_NUM_PLUS_ONE
}
FriBidiCharSet;



/* fribidi-bidi-types.h */

typedef signed char FriBidiLevel;

#define FRIBIDI_TYPE_LTR_VAL 0x00000110L
#define FRIBIDI_TYPE_RTL_VAL 0x00000111L
#define FRIBIDI_TYPE_ON_VAL 0x00000040L

typedef uint32_t FriBidiCharType;
#define FRIBIDI_TYPE_LTR FRIBIDI_TYPE_LTR_VAL

typedef uint32_t FriBidiParType;
#define FRIBIDI_PAR_LTR FRIBIDI_TYPE_LTR_VAL
#define FRIBIDI_PAR_RTL FRIBIDI_TYPE_RTL_VAL
#define FRIBIDI_PAR_ON FRIBIDI_TYPE_ON_VAL

#define FRIBIDI_LEVEL_IS_RTL(lev) ((lev) & 1)
#define FRIBIDI_DIR_TO_LEVEL(dir) ((FriBidiLevel) (FRIBIDI_IS_RTL(dir) ? 1 : 0))
#define FRIBIDI_IS_RTL(p) ((p) & 0x00000001L)
#define FRIBIDI_IS_EXPLICIT_OR_BN_OR_WS(p) ((p) & 0x00901000L)



/* functions */

#ifdef FRIBIDI_SHIM_IMPLEMENTATION
#ifdef _MSC_VER
#define FRIBIDI_ENTRY
#else
#define FRIBIDI_ENTRY __attribute__((visibility ("hidden")))
#endif
#else
#define FRIBIDI_ENTRY extern
#endif

#define FRIBIDI_FUNC(ret, name, ...) \
    typedef ret (*t_##name) (__VA_ARGS__); \
    FRIBIDI_ENTRY t_##name name;

FRIBIDI_FUNC(FriBidiStrIndex, fribidi_unicode_to_charset,
    FriBidiCharSet, const FriBidiChar *, FriBidiStrIndex, char *);

FRIBIDI_FUNC(FriBidiStrIndex, fribidi_charset_to_unicode,
    FriBidiCharSet, const char *, FriBidiStrIndex, FriBidiChar *);

FRIBIDI_FUNC(void, fribidi_get_bidi_types,
    const FriBidiChar *, const FriBidiStrIndex, FriBidiCharType *);

FRIBIDI_FUNC(FriBidiLevel, fribidi_get_par_embedding_levels,
    const FriBidiCharType *, const FriBidiStrIndex, FriBidiParType *,
    FriBidiLevel *);

/* FriBiDi>=1.0.0 */
FRIBIDI_FUNC(FriBidiLevel, fribidi_get_par_embedding_levels_ex,
    const FriBidiCharType *, const FriBidiBracketType *, const FriBidiStrIndex,
    FriBidiParType *, FriBidiLevel *);

/* FriBiDi>=1.0.0 */
FRIBIDI_FUNC(void, fribidi_get_bracket_types,
    const FriBidiChar *, const FriBidiStrIndex, const FriBidiCharType *,
    FriBidiBracketType *);

#undef FRIBIDI_FUNC

/* constant, not a function */
FRIBIDI_ENTRY const char *fribidi_version_info;



/* shim */

FRIBIDI_ENTRY void *p_fribidi;

FRIBIDI_ENTRY int load_fribidi(void);

#undef FRIBIDI_ENTRY
