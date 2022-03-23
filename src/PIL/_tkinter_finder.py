""" Find compiled module linking to Tcl / Tk libraries
"""
import sys
import tkinter
import warnings
from tkinter import _tkinter as tk

try:
    if hasattr(sys, "pypy_find_executable"):
        TKINTER_LIB = tk.tklib_cffi.__file__
    else:
        TKINTER_LIB = tk.__file__
except AttributeError:
    # _tkinter may be compiled directly into Python, in which case __file__ is
    # not available. load_tkinter_funcs will check the binary first in any case.
    TKINTER_LIB = None

tk_version = str(tkinter.TkVersion)
if tk_version == "8.4":
    warnings.warn(
        "Support for Tk/Tcl 8.4 is deprecated and will be removed"
        " in Pillow 10 (2023-07-01). Please upgrade to Tk/Tcl 8.5 "
        "or newer.",
        DeprecationWarning,
    )
