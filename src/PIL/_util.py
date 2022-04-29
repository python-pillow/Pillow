import os


def is_path(f):
    """
    Checks whether the given object is a string or path-like object that
    isn't also a file-like object
    """
    return isinstance(f, (bytes, str, os.PathLike)) and not hasattr(f, "read")


def is_directory(f):
    """Checks if an object is a string, and that it points to a directory."""
    return is_path(f) and os.path.isdir(f)


class DeferredError:
    def __init__(self, ex):
        self.ex = ex

    def __getattr__(self, elt):
        raise self.ex
