/*
    Python3 definition file to consistently map the code to Python 2.6 or
    Python 3.

    PyInt and PyLong were merged into PyLong in Python 3, so all PyInt functions
    are mapped to PyLong.

    PyString, on the other hand, was split into PyBytes and PyUnicode. We map
    both back onto PyString, so use PyBytes or PyUnicode where appropriate. The
    only exception to this is _imagingft.c, where PyUnicode is left alone.
*/

#if PY_VERSION_HEX >= 0x03000000
#define PY_ARG_BYTES_LENGTH             "y#"

/* Map PyInt -> PyLong */
#define PyInt_AsLong                PyLong_AsLong
#define PyInt_Check                 PyLong_Check
#define PyInt_FromLong              PyLong_FromLong
#define PyInt_AS_LONG               PyLong_AS_LONG
#define PyInt_FromSsize_t           PyLong_FromSsize_t

#else   /* PY_VERSION_HEX < 0x03000000 */
#define PY_ARG_BYTES_LENGTH             "s#"

#if !defined(KEEP_PY_UNICODE)
/* Map PyUnicode -> PyString */
#undef PyUnicode_AsString
#undef PyUnicode_AS_STRING
#undef PyUnicode_Check
#undef PyUnicode_FromStringAndSize
#undef PyUnicode_FromString
#undef PyUnicode_FromFormat
#undef PyUnicode_DecodeFSDefault

#define PyUnicode_AsString          PyString_AsString
#define PyUnicode_AS_STRING         PyString_AS_STRING
#define PyUnicode_Check             PyString_Check
#define PyUnicode_FromStringAndSize PyString_FromStringAndSize
#define PyUnicode_FromString        PyString_FromString
#define PyUnicode_FromFormat        PyString_FromFormat
#define PyUnicode_DecodeFSDefault   PyString_FromString
#endif

/* Map PyBytes -> PyString */
#define PyBytesObject               PyStringObject
#define PyBytes_AsString            PyString_AsString
#define PyBytes_AS_STRING           PyString_AS_STRING
#define PyBytes_Check               PyString_Check
#define PyBytes_AsStringAndSize     PyString_AsStringAndSize
#define PyBytes_FromStringAndSize   PyString_FromStringAndSize
#define PyBytes_FromString          PyString_FromString
#define _PyBytes_Resize             _PyString_Resize

#endif  /* PY_VERSION_HEX < 0x03000000 */
