#
# The Python Imaging Library.
# $Id$
#
# standard mode descriptors
#
# History:
# 2006-03-20 fl   Added
#
# Copyright (c) 2006 by Secret Labs AB.
# Copyright (c) 2006 by Fredrik Lundh.
#
# See the README file for information on usage and redistribution.
#

# mode descriptor cache
_modes = {}

##
# Wrapper for mode strings.

class ModeDescriptor:

    def __init__(self, mode, bands, basemode, basetype):
        self.mode = mode
        self.bands = bands
        self.basemode = basemode
        self.basetype = basetype

    def __str__(self):
        return self.mode

##
# Gets a mode descriptor for the given mode.

def getmode(mode):
    if not _modes:
        # initialize mode cache
        import Image
        # core modes
        for m, (basemode, basetype, bands) in Image._MODEINFO.items():
            _modes[m] = ModeDescriptor(m, bands, basemode, basetype)
        # extra experimental modes
        _modes["LA"] = ModeDescriptor("LA", ("L", "A"), "L", "L")
        _modes["PA"] = ModeDescriptor("PA", ("P", "A"), "RGB", "L")
        # mapping modes
        _modes["I;16"] = ModeDescriptor("I;16", "I", "L", "L")
        _modes["I;16L"] = ModeDescriptor("I;16L", "I", "L", "L")
        _modes["I;16B"] = ModeDescriptor("I;16B", "I", "L", "L")
    return _modes[mode]
