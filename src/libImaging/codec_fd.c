#include <Python.h>
#include "Imaging.h"

/**
 * Read from a Python file-like object into `dest`.
 *
 * @param fd Python file-like object with a `read` method
 * @param dest Caller-allocated buffer to read into; must be at least `bytes` long
 * @param bytes Number of bytes to read
 * @return Number of bytes read; or -1 on error, and a Python exception set.
 */
Py_ssize_t
_imaging_read_pyFd(PyObject *fd, char *dest, Py_ssize_t bytes) {
    PyObject *result;
    char *buffer;
    Py_ssize_t length;
    int bytes_result;

    result = PyObject_CallMethod(fd, "read", "n", bytes);
    if (result == NULL) {
        goto err;
    }

    bytes_result = PyBytes_AsStringAndSize(result, &buffer, &length);
    if (bytes_result == -1) {
        goto err;
    }

    if (length > bytes) {
        goto err;
    }

    memcpy(dest, buffer, length);

    Py_DECREF(result);
    return length;

err:
    Py_XDECREF(result);
    return -1;
}

Py_ssize_t
_imaging_write_pyFd(PyObject *fd, char *src, Py_ssize_t bytes) {
    PyObject *result;
    PyObject *byteObj;

    byteObj = PyBytes_FromStringAndSize(src, bytes);
    if (!byteObj) {
        return -1;
    }
    result = PyObject_CallMethod(fd, "write", "O", byteObj);

    Py_DECREF(byteObj);
    if (result == NULL) {
        return -1;
    }

    Py_DECREF(result);

    return bytes;
}

int
_imaging_seek_pyFd(PyObject *fd, Py_ssize_t offset, int whence) {
    PyObject *result;

    result = PyObject_CallMethod(fd, "seek", "ni", offset, whence);
    if (result == NULL) {
        return -1;
    }

    Py_DECREF(result);
    return 0;
}

Py_ssize_t
_imaging_tell_pyFd(PyObject *fd) {
    PyObject *result;
    Py_ssize_t location;

    result = PyObject_CallMethod(fd, "tell", NULL);
    if (result == NULL) {
        return -1;
    }
    location = PyLong_AsSsize_t(result);

    Py_DECREF(result);
    return location;
}
