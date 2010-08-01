#!/usr/bin/env python
#
# Setup script for PIL 1.1.5 and later (repackaged by Chris McDonough and
# Hanno Schlichting for setuptools compatibility)
#
# Usage: python setup.py install
#

import glob, os, re, struct, string, sys

def libinclude(root):
    # map root to (root/lib, root/include)
    return os.path.join(root, "lib"), os.path.join(root, "include")

# --------------------------------------------------------------------
# Library pointers.
#
# Use None to look for the libraries in well-known library locations.
# Use a string to specify a single directory, for both the library and
# the include files.  Use a tuple to specify separate directories:
# (libpath, includepath).  Examples:
#
# JPEG_ROOT = "/home/libraries/jpeg-6b"
# TIFF_ROOT = "/opt/tiff/lib", "/opt/tiff/include"
#
# If you have "lib" and "include" directories under a common parent,
# you can use the "libinclude" helper:
#
# TIFF_ROOT = libinclude("/opt/tiff")

TCL_ROOT = None
JPEG_ROOT = None
ZLIB_ROOT = None
TIFF_ROOT = None
FREETYPE_ROOT = None
LCMS_ROOT = None

# FIXME: add mechanism to explicitly *disable* the use of a library

# --------------------------------------------------------------------
# Identification

NAME = "Pillow"
DESCRIPTION = "Python Imaging Library (fork)"
#AUTHOR = "Secret Labs AB (PythonWare)", "info@pythonware.com"
AUTHOR = "Alex Clark (fork author)", "aclark@aclark.net"
#HOMEPAGE = "http://www.pythonware.com/products/pil"
HOMEPAGE = "http://github.com/Pillow"
#DOWNLOAD_URL = "http://effbot.org/downloads/%s-%s.tar.gz" # name, version

# --------------------------------------------------------------------
# Core library

IMAGING = [
    "decode", "encode", "map", "display", "outline", "path",
    ]

LIBIMAGING = [
    "Access", "Antialias", "Bands", "BitDecode", "Blend", "Chops",
    "Convert", "ConvertYCbCr", "Copy", "Crc32", "Crop", "Dib", "Draw",
    "Effects", "EpsEncode", "File", "Fill", "Filter", "FliDecode",
    "Geometry", "GetBBox", "GifDecode", "GifEncode", "HexDecode",
    "Histo", "JpegDecode", "JpegEncode", "LzwDecode", "Matrix",
    "ModeFilter", "MspDecode", "Negative", "Offset", "Pack",
    "PackDecode", "Palette", "Paste", "Quant", "QuantHash",
    "QuantHeap", "PcdDecode", "PcxDecode", "PcxEncode", "Point",
    "RankFilter", "RawDecode", "RawEncode", "Storage", "SunRleDecode",
    "TgaRleDecode", "Unpack", "UnpackYCC", "UnsharpMask", "XbmDecode",
    "XbmEncode", "ZipDecode", "ZipEncode"
    ]

# --------------------------------------------------------------------

from distutils import sysconfig
from distutils.command.build_ext import build_ext
from setuptools import setup, find_packages, Extension

try:
    import _tkinter
except ImportError:
    _tkinter = None

def add_directory(path, dir, where=None):
    if dir and os.path.isdir(dir) and dir not in path:
        if where is None:
            path.append(dir)
        else:
            path.insert(where, dir)

def find_include_file(self, include):
    for directory in self.compiler.include_dirs:
        if os.path.isfile(os.path.join(directory, include)):
            return 1
    return 0

def find_library_file(self, library):
    return self.compiler.find_library_file(self.compiler.library_dirs, library)

def find_version(filename):
    for line in open(filename).readlines():
        m = re.search("VERSION\s*=\s*\"([^\"]+)\"", line)
        if m:
            return m.group(1)
    return None

#VERSION = find_version("PIL/Image.py")
VERSION = "1.2"

class pil_build_ext(build_ext):

    def build_extensions(self):

        global TCL_ROOT

        library_dirs = []
        include_dirs = []

        add_directory(include_dirs, "libImaging")

        #
        # add platform directories

        if sys.platform == "cygwin":
            # pythonX.Y.dll.a is in the /usr/lib/pythonX.Y/config directory
            add_directory(library_dirs, os.path.join(
                "/usr/lib", "python%s" % sys.version[:3], "config"
                ))

        elif sys.platform == "darwin":
            # attempt to make sure we pick freetype2 over other versions
            add_directory(include_dirs, "/sw/include/freetype2")
            add_directory(include_dirs, "/sw/lib/freetype2/include")
            # fink installation directories
            add_directory(library_dirs, "/sw/lib")
            add_directory(include_dirs, "/sw/include")
            # darwin ports installation directories
            add_directory(library_dirs, "/opt/local/lib")
            add_directory(include_dirs, "/opt/local/include")
            # freetype2 ships with X11
            add_directory(library_dirs, "/usr/x11/lib")
            add_directory(library_dirs, "/usr/x11/include")

        add_directory(library_dirs, "/usr/local/lib")
        # FIXME: check /opt/stuff directories here?

        prefix = sysconfig.get_config_var("prefix")
        if prefix:
            add_directory(library_dirs, os.path.join(prefix, "lib"))
            add_directory(include_dirs, os.path.join(prefix, "include"))

        #
        # locate tkinter libraries

        if _tkinter:
            TCL_VERSION = _tkinter.TCL_VERSION[:3]

        if _tkinter and not TCL_ROOT:
            # we have Tkinter but the TCL_ROOT variable was not set;
            # try to locate appropriate Tcl/Tk libraries
            PYVERSION = sys.version[0] + sys.version[2]
            TCLVERSION = TCL_VERSION[0] + TCL_VERSION[2]
            roots = [
                # common installation directories, mostly for Windows
                # (for Unix-style platforms, we'll check in well-known
                # locations later)
                os.path.join("/py" + PYVERSION, "Tcl"),
                os.path.join("/python" + PYVERSION, "Tcl"),
                "/Tcl", "/Tcl" + TCLVERSION, "/Tcl" + TCL_VERSION,
                os.path.join(os.environ.get("ProgramFiles", ""), "Tcl"),
                ]
            for TCL_ROOT in roots:
                TCL_ROOT = os.path.abspath(TCL_ROOT)
                if os.path.isfile(os.path.join(TCL_ROOT, "include", "tk.h")):
                    # FIXME: use distutils logging (?)
                    print "--- using Tcl/Tk libraries at", TCL_ROOT
                    print "--- using Tcl/Tk version", TCL_VERSION
                    TCL_ROOT = libinclude(TCL_ROOT)
                    break
            else:
                TCL_ROOT = None

        #
        # add configured kits

        for root in (TCL_ROOT, JPEG_ROOT, TCL_ROOT, TIFF_ROOT, ZLIB_ROOT,
                     FREETYPE_ROOT, LCMS_ROOT):
            if isinstance(root, type(())):
                lib_root, include_root = root
            else:
                lib_root = include_root = root
            add_directory(library_dirs, lib_root)
            add_directory(include_dirs, include_root)

        #
        # add standard directories

        # look for tcl specific subdirectory (e.g debian)
        if _tkinter:
            tcl_dir = "/usr/include/tcl" + TCL_VERSION
            if os.path.isfile(os.path.join(tcl_dir, "tk.h")):
                add_directory(include_dirs, tcl_dir)

        # standard locations
        add_directory(library_dirs, "/usr/local/lib")
        add_directory(include_dirs, "/usr/local/include")

        add_directory(library_dirs, "/usr/lib")
        add_directory(include_dirs, "/usr/include")

        #
        # insert new dirs *before* default libs, to avoid conflicts
        # between Python PYD stub libs and real libraries

        self.compiler.library_dirs = library_dirs + self.compiler.library_dirs
        self.compiler.include_dirs = include_dirs + self.compiler.include_dirs

        #
        # look for available libraries

        class feature:
            zlib = jpeg = tiff = freetype = tcl = tk = lcms = None
        feature = feature()

        if find_include_file(self, "zlib.h"):
            if find_library_file(self, "z"):
                feature.zlib = "z"
            elif sys.platform == "win32" and find_library_file(self, "zlib"):
                feature.zlib = "zlib" # alternative name

        if find_include_file(self, "jpeglib.h"):
            if find_library_file(self, "jpeg"):
                feature.jpeg = "jpeg"
            elif sys.platform == "win32" and find_library_file(self, "libjpeg"):
                feature.jpeg = "libjpeg" # alternative name

        if find_library_file(self, "tiff"):
            feature.tiff = "tiff"

        if find_library_file(self, "freetype"):
            # look for freetype2 include files
            freetype_version = 0
            for dir in self.compiler.include_dirs:
                if os.path.isfile(os.path.join(dir, "ft2build.h")):
                    freetype_version = 21
                    dir = os.path.join(dir, "freetype2")
                    break
                dir = os.path.join(dir, "freetype2")
                if os.path.isfile(os.path.join(dir, "ft2build.h")):
                    freetype_version = 21
                    break
                if os.path.isdir(os.path.join(dir, "freetype")):
                    freetype_version = 20
                    break
            if freetype_version:
                feature.freetype = "freetype"
                feature.freetype_version = freetype_version
                if dir:
                    add_directory(self.compiler.include_dirs, dir, 0)

        if find_include_file(self, "lcms.h"):
            if find_library_file(self, "lcms"):
                feature.lcms = "lcms"

        if _tkinter and find_include_file(self, "tk.h"):
            # the library names may vary somewhat (e.g. tcl84 or tcl8.4)
            version = TCL_VERSION[0] + TCL_VERSION[2]
            if find_library_file(self, "tcl" + version):
                feature.tcl = "tcl" + version
            elif find_library_file(self, "tcl" + TCL_VERSION):
                feature.tcl = "tcl" + TCL_VERSION
            if find_library_file(self, "tk" + version):
                feature.tk = "tk" + version
            elif find_library_file(self, "tk" + TCL_VERSION):
                feature.tk = "tk" + TCL_VERSION

        #
        # core library

        files = ["_imaging.c"]
        for file in IMAGING:
            files.append(file + ".c")
        for file in LIBIMAGING:
            files.append(os.path.join("libImaging", file + ".c"))

        libs = []
        defs = []
        if feature.jpeg:
            libs.append(feature.jpeg)
            defs.append(("HAVE_LIBJPEG", None))
        if feature.zlib:
            libs.append(feature.zlib)
            defs.append(("HAVE_LIBZ", None))
        if sys.platform == "win32":
            libs.extend(["kernel32", "user32", "gdi32"])
        if struct.unpack("h", "\0\1")[0] == 1:
            defs.append(("WORDS_BIGENDIAN", None))

        exts = [(Extension(
            "_imaging", files, libraries=libs, define_macros=defs
            ))]

        #
        # additional libraries

        if feature.freetype:
            defs = []
            if feature.freetype_version == 20:
                defs.append(("USE_FREETYPE_2_0", None))
            exts.append(Extension(
                "_imagingft", ["_imagingft.c"], libraries=["freetype"],
                define_macros=defs
                ))

        if os.path.isfile("_imagingtiff.c") and feature.tiff:
            exts.append(Extension(
                "_imagingtiff", ["_imagingtiff.c"], libraries=["tiff"]
                ))

        if os.path.isfile("_imagingcms.c") and feature.lcms:
            extra = []
            if sys.platform == "win32":
                extra.extend(["user32", "gdi32"])
            exts.append(Extension(
                "_imagingcms", ["_imagingcms.c"], libraries=["lcms"] + extra
                ))

        if sys.platform == "darwin":
            # locate Tcl/Tk frameworks
            frameworks = []
            framework_roots = [
                "/Library/Frameworks",
                "/System/Library/Frameworks"
                ]
            for root in framework_roots:
                if (os.path.exists(os.path.join(root, "Tcl.framework")) and
                    os.path.exists(os.path.join(root, "Tk.framework"))):
                    print "--- using frameworks at", root
                    frameworks = ["-framework", "Tcl", "-framework", "Tk"]
                    dir = os.path.join(root, "Tcl.framework", "Headers")
                    add_directory(self.compiler.include_dirs, dir, 0)
                    dir = os.path.join(root, "Tk.framework", "Headers")
                    add_directory(self.compiler.include_dirs, dir, 1)
                    break
            if frameworks:
                exts.append(Extension(
                    "_imagingtk", ["_imagingtk.c", "Tk/tkImaging.c"],
                    extra_compile_args=frameworks, extra_link_args=frameworks
                    ))
                feature.tcl = feature.tk = 1 # mark as present
        elif feature.tcl and feature.tk:
            exts.append(Extension(
                "_imagingtk", ["_imagingtk.c", "Tk/tkImaging.c"],
                libraries=[feature.tcl, feature.tk]
                ))

        if os.path.isfile("_imagingmath.c"):
            exts.append(Extension("_imagingmath", ["_imagingmath.c"]))

        self.extensions[:] = exts

        build_ext.build_extensions(self)

        #
        # sanity and security checks

        unsafe_zlib = None

        if feature.zlib:
            unsafe_zlib = self.check_zlib_version(self.compiler.include_dirs)

        self.summary_report(feature, unsafe_zlib)

    def summary_report(self, feature, unsafe_zlib):

        print "-" * 68
        print "Pillow (PIL fork)", VERSION, "SETUP SUMMARY"
        print "-" * 68
        print "version      ", VERSION
        v = string.split(sys.version, "[")
        print "platform     ", sys.platform, string.strip(v[0])
        for v in v[1:]:
            print "             ", string.strip("[" + v)
        print "-" * 68

        options = [
            (feature.tcl and feature.tk, "TKINTER"),
            (feature.jpeg, "JPEG"),
            (feature.zlib, "ZLIB (PNG/ZIP)"),
            # (feature.tiff, "experimental TIFF G3/G4 read"),
            (feature.freetype, "FREETYPE2"),
            (feature.lcms, "LITTLECMS"),
            ]

        all = 1
        for option in options:
            if option[0]:
                print "---", option[1], "support available"
            else:
                print "***", option[1], "support not available",
                if option[1] == "TKINTER" and _tkinter:
                    version = _tkinter.TCL_VERSION
                    print "(Tcl/Tk %s libraries needed)" % version,
                print
                all = 0

        if feature.zlib and unsafe_zlib:
            print
            print "*** Warning: zlib", unsafe_zlib,
            print "may contain a security vulnerability."
            print "*** Consider upgrading to zlib 1.2.3 or newer."
            print "*** See: http://www.kb.cert.org/vuls/id/238678"
            print "         http://www.kb.cert.org/vuls/id/680620"
            print "         http://www.gzip.org/zlib/advisory-2002-03-11.txt"
            print

        print "-" * 68

        if not all:
            print "To add a missing option, make sure you have the required"
            print "library, and set the corresponding ROOT variable in the"
            print "setup.py script."
            print

        print "To check the build, run the selftest.py script."

    def check_zlib_version(self, include_dirs):
        # look for unsafe versions of zlib
        for dir in include_dirs:
            zlibfile = os.path.join(dir, "zlib.h")
            if os.path.isfile(zlibfile):
                break
        else:
            return
        for line in open(zlibfile).readlines():
            m = re.match('#define\s+ZLIB_VERSION\s+"([^"]*)"', line)
            if not m:
                continue
            if m.group(1) < "1.2.3":
                return m.group(1)

#
# build!

if __name__ == "__main__":

    try:
        # add necessary to distutils (for backwards compatibility)
        from distutils.dist import DistributionMetadata
        DistributionMetadata.classifiers = None
        DistributionMetadata.download_url = None
        DistributionMetadata.platforms = None
    except:
        pass

    setup(
        author=AUTHOR[0], author_email=AUTHOR[1],
        classifiers=[
            "Development Status :: 6 - Mature",
            "Topic :: Multimedia :: Graphics",
            "Topic :: Multimedia :: Graphics :: Capture :: Digital Camera",
            "Topic :: Multimedia :: Graphics :: Capture :: Scanners",
            "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
            "Topic :: Multimedia :: Graphics :: Graphics Conversion",
            "Topic :: Multimedia :: Graphics :: Viewers",
            ],
        cmdclass = {"build_ext": pil_build_ext},
        description=DESCRIPTION,
#        download_url=DOWNLOAD_URL % (NAME, VERSION),
        ext_modules = [Extension("_imaging", ["_imaging.c"])], # dummy
        extra_path = "PIL",
        license="Python (MIT style)",
#        long_description=DESCRIPTION,
        long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "INSTALL.txt")).read() +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
        name=NAME,
        packages=find_packages(),
#        setup_requires=["setuptools_hg"],
        platforms="Python 1.5.2 and later.",
        scripts = glob.glob("Scripts/pil*.py"),
        url=HOMEPAGE,
        version=VERSION,
        )
