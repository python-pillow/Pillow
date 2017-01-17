"""
PIL Exceptions
"""


class PILError(Exception):
    """
    Base exception for all PIL exceptions
    """
    pass


class PILReadError(PILError):
    """
    Some error happened while reading a file.
    """
    pass


class InvalidFileType(PILReadError):
    """
    The given file is not of the expected type.
    """


class NoPluginFound(PILError):
    """
    No plugin was found for the given format.
    """
    pass


class PILWriteError(PILError):
    """
    Some error happened while writing a file.
    """
    pass
