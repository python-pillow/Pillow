#include "Python.h"
#include "Imaging.h"

Py_ssize_t
_imaging_read_pyFd(PyObject *fd, char *dest, Py_ssize_t bytes) {
    /* dest should be a buffer bytes long, returns length of read
       -1 on error */

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
