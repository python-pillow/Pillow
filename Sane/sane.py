# sane.py
#
# Python wrapper on top of the _sane module, which is in turn a very
# thin wrapper on top of the SANE library.  For a complete understanding
# of SANE, consult the documentation at the SANE home page:
# http://www.mostang.com/sane/ .

__version__ = '2.0'
__author__  = ['Andrew Kuchling', 'Ralph Heinkel']

from PIL import Image

import _sane
from _sane import *

TYPE_STR = { TYPE_BOOL:   "TYPE_BOOL",   TYPE_INT:    "TYPE_INT",
             TYPE_FIXED:  "TYPE_FIXED",  TYPE_STRING: "TYPE_STRING",
             TYPE_BUTTON: "TYPE_BUTTON", TYPE_GROUP:  "TYPE_GROUP" }

UNIT_STR = { UNIT_NONE:        "UNIT_NONE",
             UNIT_PIXEL:       "UNIT_PIXEL",
             UNIT_BIT:         "UNIT_BIT",
             UNIT_MM:          "UNIT_MM",
             UNIT_DPI:         "UNIT_DPI",
             UNIT_PERCENT:     "UNIT_PERCENT",
             UNIT_MICROSECOND: "UNIT_MICROSECOND" }


class Option:
    """Class representing a SANE option.
    Attributes:
    index -- number from 0 to n, giving the option number
    name -- a string uniquely identifying the option
    title -- single-line string containing a title for the option
    desc -- a long string describing the option; useful as a help message
    type -- type of this option.  Possible values: TYPE_BOOL,
            TYPE_INT, TYPE_STRING, and so forth.
    unit -- units of this option.  Possible values: UNIT_NONE,
            UNIT_PIXEL, etc.
    size -- size of the value in bytes
    cap -- capabilities available; CAP_EMULATED, CAP_SOFT_SELECT, etc.
    constraint -- constraint on values.  Possible values:
        None : No constraint
        (min,max,step)  Integer values, from min to max, stepping by
        list of integers or strings: only the listed values are allowed
    """

    def __init__(self, args, scanDev):
        self.scanDev = scanDev # needed to get current value of this option
        self.index, self.name = args[0], args[1]
        self.title, self.desc = args[2], args[3]
        self.type, self.unit  = args[4], args[5]
        self.size, self.cap   = args[6], args[7]
        self.constraint = args[8]
        def f(x):
            if x=='-': return '_'
            else: return x
        if not isinstance(self.name, str): self.py_name=str(self.name)
        else: self.py_name=''.join(map(f, self.name))

    def is_active(self):
        return _sane.OPTION_IS_ACTIVE(self.cap)
    def is_settable(self):
        return _sane.OPTION_IS_SETTABLE(self.cap)
    def __repr__(self):
        if self.is_settable():
            settable = 'yes'
        else:
            settable = 'no'
        if self.is_active():
            active = 'yes'
            curValue = repr(getattr(self.scanDev, self.py_name))
        else:
            active = 'no'
            curValue = '<not available, inactive option>'
        s = """\nName:      %s
Cur value: %s
Index:     %d
Title:     %s
Desc:      %s
Type:      %s
Unit:      %s
Constr:    %s
active:    %s
settable:  %s\n""" % (self.py_name, curValue,
                      self.index, self.title, self.desc,
                      TYPE_STR[self.type], UNIT_STR[self.unit],
                      repr(self.constraint), active, settable)
        return s


class _SaneIterator:
    """ intended for ADF scans.
    """

    def __init__(self, device):
        self.device = device

    def __iter__(self):
        return self

    def __del__(self):
        self.device.cancel()

    def next(self):
        try:
            self.device.start()
        except error as v:
            if v == 'Document feeder out of documents':
                raise StopIteration
            else:
                raise
        return self.device.snap(1)



class SaneDev:
    """Class representing a SANE device.
    Methods:
    start()    -- initiate a scan, using the current settings
    snap()     -- snap a picture, returning an Image object
    arr_snap() -- snap a picture, returning a numarray object
    cancel()   -- cancel an in-progress scanning operation
    fileno()   -- return the file descriptor for the scanner (handy for select)

    Also available, but rather low-level:
    get_parameters() -- get the current parameter settings of the device
    get_options()    -- return a list of tuples describing all the options.

    Attributes:
    optlist -- list of option names

    You can also access an option name to retrieve its value, and to
    set it.  For example, if one option has a .name attribute of
    imagemode, and scanner is a SaneDev object, you can do:
         print scanner.imagemode
         scanner.imagemode = 'Full frame'
         scanner.['imagemode'] returns the corresponding Option object.
    """
    def __init__(self, devname):
        d=self.__dict__
        d['sane_signature'] = self._getSaneSignature(devname)
        d['scanner_model']  = d['sane_signature'][1:3]
        d['dev'] = _sane._open(devname)
        self.__load_option_dict()

    def _getSaneSignature(self, devname):
        devices = get_devices()
        if not devices:
            raise RuntimeError('no scanner available')
        for dev in devices:
            if devname == dev[0]:
                return dev
        raise RuntimeError('no such scan device "%s"' % devname)

    def __load_option_dict(self):
        d=self.__dict__
        d['opt']={}
        optlist=d['dev'].get_options()
        for t in optlist:
            o=Option(t, self)
            if o.type!=TYPE_GROUP:
                d['opt'][o.py_name]=o

    def __setattr__(self, key, value):
        dev=self.__dict__['dev']
        optdict=self.__dict__['opt']
        if key not in optdict:
            self.__dict__[key]=value ; return
        opt=optdict[key]
        if opt.type==TYPE_GROUP:
            raise AttributeError("Groups can't be set: "+key)
        if not _sane.OPTION_IS_ACTIVE(opt.cap):
            raise AttributeError('Inactive option: '+key)
        if not _sane.OPTION_IS_SETTABLE(opt.cap):
            raise AttributeError("Option can't be set by software: "+key)
        if isinstance(value, int) and opt.type == TYPE_FIXED:
            # avoid annoying errors of backend if int is given instead float:
            value = float(value)
        self.last_opt = dev.set_option(opt.index, value)
        # do binary AND to find if we have to reload options:
        if self.last_opt & INFO_RELOAD_OPTIONS:
            self.__load_option_dict()

    def __getattr__(self, key):
        dev=self.__dict__['dev']
        optdict=self.__dict__['opt']
        if key=='optlist':
            return list(self.opt.keys())
        if key=='area':
            return (self.tl_x, self.tl_y),(self.br_x, self.br_y)
        if key not in optdict:
            raise AttributeError('No such attribute: '+key)
        opt=optdict[key]
        if opt.type==TYPE_BUTTON:
            raise AttributeError("Buttons don't have values: "+key)
        if opt.type==TYPE_GROUP:
            raise AttributeError("Groups don't have values: "+key)
        if not _sane.OPTION_IS_ACTIVE(opt.cap):
            raise AttributeError('Inactive option: '+key)
        value = dev.get_option(opt.index)
        return value

    def __getitem__(self, key):
        return self.opt[key]

    def get_parameters(self):
        """Return a 5-tuple holding all the current device settings:
   (format, last_frame, (pixels_per_line, lines), depth, bytes_per_line)

- format is one of 'L' (grey), 'RGB', 'R' (red), 'G' (green), 'B' (blue).
- last_frame [bool] indicates if this is the last frame of a multi frame image
- (pixels_per_line, lines) specifies the size of the scanned image (x,y)
- lines denotes the number of scanlines per frame
- depth gives number of pixels per sample
"""
        return self.dev.get_parameters()

    def get_options(self):
        "Return a list of tuples describing all the available options"
        return self.dev.get_options()

    def start(self):
        "Initiate a scanning operation"
        return self.dev.start()

    def cancel(self):
        "Cancel an in-progress scanning operation"
        return self.dev.cancel()

    def snap(self, no_cancel=0):
        "Snap a picture, returning a PIL image object with the results"
        (mode, last_frame,
         (xsize, ysize), depth, bytes_per_line) = self.get_parameters()
        if mode in ['gray', 'red', 'green', 'blue']:
            format = 'L'
        elif mode == 'color':
            format = 'RGB'
        else:
            raise ValueError('got unknown "mode" from self.get_parameters()')
        im=Image.new(format, (xsize,ysize))
        self.dev.snap( im.im.id, no_cancel )
        return im

    def scan(self):
        self.start()
        return self.snap()

    def multi_scan(self):
        return _SaneIterator(self)

    def arr_snap(self, multipleOf=1):
        """Snap a picture, returning a numarray object with the results.
        By default the resulting array has the same number of pixels per
        line as specified in self.get_parameters()[2][0]
        However sometimes it is necessary to obtain arrays where
        the number of pixels per line is e.g. a multiple of 4. This can then
        be achieved with the option 'multipleOf=4'. So if the scanner
        scanned 34 pixels per line, you will obtain an array with 32 pixels
        per line.
        """
        (mode, last_frame, (xsize, ysize), depth, bpl) = self.get_parameters()
        if not mode in ['gray', 'red', 'green', 'blue']:
            raise RuntimeError('arr_snap() only works with monochrome images')
        if multipleOf < 1:
            raise ValueError('option "multipleOf" must be a positive number')
        elif multipleOf > 1:
            pixels_per_line = xsize - divmod(xsize, 4)[1]
        else:
            pixels_per_line = xsize
        return self.dev.arr_snap(pixels_per_line)

    def arr_scan(self, multipleOf=1):
        self.start()
        return self.arr_snap(multipleOf=multipleOf)

    def fileno(self):
        "Return the file descriptor for the scanning device"
        return self.dev.fileno()

    def close(self):
        self.dev.close()


def open(devname):
    "Open a device for scanning"
    new=SaneDev(devname)
    return new
