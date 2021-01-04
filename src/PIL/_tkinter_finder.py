""" Find compiled module linking to Tcl / Tk libraries
"""
import sys
from tkinter import _tkinter as tk

if hasattr(sys, "pypy_find_executable"):
    TKINTER_LIB = tk.tklib_cffi.__file__
else:
    TKINTER_LIB = tk.__file__
