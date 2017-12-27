/* Raw.h */

typedef struct {

    /* CONFIGURATION */

    /* Distance between lines (0=no padding) */
    int stride;

    /* PRIVATE (initialized by decoder) */

    /* Padding between lines */
    int skip;

} RAWSTATE;
