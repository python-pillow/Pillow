# > pyroma .
# ------------------------------
# Checking .
# Found Pillow
# ------------------------------
# Final rating: 10/10
# Your cheese is so fresh most people think it's a cream: Mascarpone
# ------------------------------
from __future__ import print_function
import glob
import os
import platform as plat
import re
import struct
import sys

from distutils.command.build_ext import build_ext
from distutils import sysconfig
from setuptools import Extension, setup, find_packages

# monkey patch import hook. Even though flake8 says it's not used, it is.
# comment this out to disable multi threaded builds.
import mp_compile

_IMAGING = (
    "decode", "encode", "map", "display", "outline", "path")

_LIB_IMAGING = (
    "Access", "AlphaComposite", "Resample", "Bands", "BitDecode", "Blend",
    "Chops", "Convert", "ConvertYCbCr", "Copy", "Crc32", "Crop", "Dib", "Draw",
    "Effects", "EpsEncode", "File", "Fill", "Filter", "FliDecode",
    "Geometry", "GetBBox", "GifDecode", "GifEncode", "HexDecode",
    "Histo", "JpegDecode", "JpegEncode", "LzwDecode", "Matrix",
    "ModeFilter", "MspDecode", "Negative", "Offset", "Pack",
    "PackDecode", "Palette", "Paste", "Quant", "QuantOctree", "QuantHash",
    "QuantHeap", "PcdDecode", "PcxDecode", "PcxEncode", "Point",
    "RankFilter", "RawDecode", "RawEncode", "Storage", "SunRleDecode",
    "TgaRleDecode", "Unpack", "UnpackYCC", "UnsharpMask", "XbmDecode",
    "XbmEncode", "ZipDecode", "ZipEncode", "TiffDecode", "Incremental",
    "Jpeg2KDecode", "Jpeg2KEncode", "BoxBlur")


def _add_directory(path, dir, where=None):
    if dir is None:
        return
    dir = os.path.realpath(dir)
    if os.path.isdir(dir) and dir not in path:
        if where is None:
            path.append(dir)
        else:
            path.insert(where, dir)


def _find_include_file(self, include):
    for directory in self.compiler.include_dirs:
        if os.path.isfile(os.path.join(directory, include)):
            return 1
    return 0


def _find_library_file(self, library):
    # Fix for 3.2.x <3.2.4, 3.3.0, shared lib extension is the python shared
    # lib extension, not the system shared lib extension: e.g. .cpython-33.so
    # vs .so. See Python bug http://bugs.python.org/16754
    if 'cpython' in self.compiler.shared_lib_extension:
        existing = self.compiler.shared_lib_extension
        self.compiler.shared_lib_extension = "." + existing.split('.')[-1]
        ret = self.compiler.find_library_file(
            self.compiler.library_dirs, library)
        self.compiler.shared_lib_extension = existing
        return ret
    else:
        return self.compiler.find_library_file(
            self.compiler.library_dirs, library)


def _lib_include(root):
    # map root to (root/lib, root/include)
    return os.path.join(root, "lib"), os.path.join(root, "include")


def _read(file):
    return open(file, 'rb').read()

try:
    import _tkinter
except (ImportError, OSError):
    # pypy emits an oserror
    _tkinter = None


NAME = 'Pillow'
PILLOW_VERSION = '2.7.0'
TCL_ROOT = None
JPEG_ROOT = None
JPEG2K_ROOT = None
ZLIB_ROOT = None
TIFF_ROOT = None
FREETYPE_ROOT = None
LCMS_ROOT = None


class pil_build_ext(build_ext):

    class feature:
        zlib = jpeg = tiff = freetype = tcl = tk = lcms = webp = webpmux = None
        jpeg2000 = None
        required = []

        def require(self, feat):
            return feat in self.required

        def want(self, feat):
            return getattr(self, feat) is None

        def __iter__(self):
            for x in dir(self):
                if x[1] != '_':
                    yield x

    feature = feature()

    user_options = build_ext.user_options + [
        ('disable-%s' % x, None, 'Disable support for %s' % x)
        for x in feature
    ] + [
        ('enable-%s' % x, None, 'Enable support for %s' % x)
        for x in feature
    ]

    def initialize_options(self):
        build_ext.initialize_options(self)
        for x in self.feature:
            setattr(self, 'disable_%s' % x, None)
            setattr(self, 'enable_%s' % x, None)

    def finalize_options(self):
        build_ext.finalize_options(self)
        for x in self.feature:
            if getattr(self, 'disable_%s' % x):
                setattr(self.feature, x, False)
                if getattr(self, 'enable_%s' % x):
                    raise ValueError(
                        'Conflicting options: --enable-%s and --disable-%s'
                        % (x, x))
            if getattr(self, 'enable_%s' % x):
                self.feature.required.append(x)

    def build_extensions(self):

        global TCL_ROOT

        library_dirs = []
        include_dirs = []

        _add_directory(include_dirs, "libImaging")

        #
        # add configured kits

        for root in (TCL_ROOT, JPEG_ROOT, JPEG2K_ROOT, TIFF_ROOT, ZLIB_ROOT,
                     FREETYPE_ROOT, LCMS_ROOT):
            if isinstance(root, type(())):
                lib_root, include_root = root
            else:
                lib_root = include_root = root
            _add_directory(library_dirs, lib_root)
            _add_directory(include_dirs, include_root)

        # respect CFLAGS/LDFLAGS
        for k in ('CFLAGS', 'LDFLAGS'):
            if k in os.environ:
                for match in re.finditer(r'-I([^\s]+)', os.environ[k]):
                    _add_directory(include_dirs, match.group(1))
                for match in re.finditer(r'-L([^\s]+)', os.environ[k]):
                    _add_directory(library_dirs, match.group(1))

        # include, rpath, if set as environment variables:
        for k in ('C_INCLUDE_PATH', 'CPATH', 'INCLUDE'):
            if k in os.environ:
                for d in os.environ[k].split(os.path.pathsep):
                    _add_directory(include_dirs, d)

        for k in ('LD_RUN_PATH', 'LIBRARY_PATH', 'LIB'):
            if k in os.environ:
                for d in os.environ[k].split(os.path.pathsep):
                    _add_directory(library_dirs, d)

        prefix = sysconfig.get_config_var("prefix")
        if prefix:
            _add_directory(library_dirs, os.path.join(prefix, "lib"))
            _add_directory(include_dirs, os.path.join(prefix, "include"))

        #
        # add platform directories

        if sys.platform == "cygwin":
            # pythonX.Y.dll.a is in the /usr/lib/pythonX.Y/config directory
            _add_directory(library_dirs, os.path.join(
                "/usr/lib", "python%s" % sys.version[:3], "config"))

        elif sys.platform == "darwin":
            # attempt to make sure we pick freetype2 over other versions
            _add_directory(include_dirs, "/sw/include/freetype2")
            _add_directory(include_dirs, "/sw/lib/freetype2/include")
            # fink installation directories
            _add_directory(library_dirs, "/sw/lib")
            _add_directory(include_dirs, "/sw/include")
            # darwin ports installation directories
            _add_directory(library_dirs, "/opt/local/lib")
            _add_directory(include_dirs, "/opt/local/include")

            # if Homebrew is installed, use its lib and include directories
            import subprocess
            try:
                prefix = subprocess.check_output(
                    ['brew', '--prefix']
                ).strip().decode('latin1')
            except:
                # Homebrew not installed
                prefix = None

            ft_prefix = None

            if prefix:
                # add Homebrew's include and lib directories
                _add_directory(library_dirs, os.path.join(prefix, 'lib'))
                _add_directory(include_dirs, os.path.join(prefix, 'include'))
                ft_prefix = os.path.join(prefix, 'opt', 'freetype')

            if ft_prefix and os.path.isdir(ft_prefix):
                # freetype might not be linked into Homebrew's prefix
                _add_directory(library_dirs, os.path.join(ft_prefix, 'lib'))
                _add_directory(
                    include_dirs, os.path.join(ft_prefix, 'include'))
            else:
                # fall back to freetype from XQuartz if
                # Homebrew's freetype is missing
                _add_directory(library_dirs, "/usr/X11/lib")
                _add_directory(include_dirs, "/usr/X11/include")

        elif sys.platform.startswith("linux"):
            arch_tp = (plat.processor(), plat.architecture()[0])
            if arch_tp == ("x86_64", "32bit"):
                # 32 bit build on 64 bit machine.
                _add_directory(library_dirs, "/usr/lib/i386-linux-gnu")
            else:
                for platform_ in arch_tp:

                    if not platform_:
                        continue

                    if platform_ in ["x86_64", "64bit"]:
                        _add_directory(library_dirs, "/lib64")
                        _add_directory(library_dirs, "/usr/lib64")
                        _add_directory(
                            library_dirs, "/usr/lib/x86_64-linux-gnu")
                        break
                    elif platform_ in ["i386", "i686", "32bit"]:
                        _add_directory(
                            library_dirs, "/usr/lib/i386-linux-gnu")
                        break
                    elif platform_ in ["aarch64"]:
                        _add_directory(library_dirs, "/usr/lib64")
                        _add_directory(
                            library_dirs, "/usr/lib/aarch64-linux-gnu")
                        break
                    elif platform_ in ["arm", "armv7l"]:
                        _add_directory(
                            library_dirs, "/usr/lib/arm-linux-gnueabi")
                        break
                    elif platform_ in ["ppc64"]:
                        _add_directory(library_dirs, "/usr/lib64")
                        _add_directory(
                            library_dirs, "/usr/lib/ppc64-linux-gnu")
                        _add_directory(
                            library_dirs, "/usr/lib/powerpc64-linux-gnu")
                        break
                    elif platform_ in ["ppc"]:
                        _add_directory(library_dirs, "/usr/lib/ppc-linux-gnu")
                        _add_directory(
                            library_dirs, "/usr/lib/powerpc-linux-gnu")
                        break
                    elif platform_ in ["s390x"]:
                        _add_directory(library_dirs, "/usr/lib64")
                        _add_directory(
                            library_dirs, "/usr/lib/s390x-linux-gnu")
                        break
                    elif platform_ in ["s390"]:
                        _add_directory(library_dirs, "/usr/lib/s390-linux-gnu")
                        break
                else:
                    raise ValueError(
                        "Unable to identify Linux platform: `%s`" % platform_)

            # XXX Kludge. Above /\ we brute force support multiarch. Here we
            # try Barry's more general approach. Afterward, something should
            # work ;-)
            self.add_multiarch_paths()

        elif sys.platform.startswith("gnu"):
            self.add_multiarch_paths()

        elif sys.platform.startswith("netbsd"):
                    _add_directory(library_dirs, "/usr/pkg/lib")
                    _add_directory(include_dirs, "/usr/pkg/include")

        # FIXME: check /opt/stuff directories here?

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
                os.path.join(os.environ.get("ProgramFiles", ""), "Tcl"), ]
            for TCL_ROOT in roots:
                TCL_ROOT = os.path.abspath(TCL_ROOT)
                if os.path.isfile(os.path.join(TCL_ROOT, "include", "tk.h")):
                    # FIXME: use distutils logging (?)
                    print("--- using Tcl/Tk libraries at", TCL_ROOT)
                    print("--- using Tcl/Tk version", TCL_VERSION)
                    TCL_ROOT = _lib_include(TCL_ROOT)
                    break
            else:
                TCL_ROOT = None

        # add standard directories

        # look for tcl specific subdirectory (e.g debian)
        if _tkinter:
            tcl_dir = "/usr/include/tcl" + TCL_VERSION
            if os.path.isfile(os.path.join(tcl_dir, "tk.h")):
                _add_directory(include_dirs, tcl_dir)

        # standard locations
        _add_directory(library_dirs, "/usr/local/lib")
        _add_directory(include_dirs, "/usr/local/include")

        _add_directory(library_dirs, "/usr/lib")
        _add_directory(include_dirs, "/usr/include")

        # on Windows, look for the OpenJPEG libraries in the location that
        # the official installer puts them
        if sys.platform == "win32":
            program_files = os.environ.get('ProgramFiles', '')
            best_version = (0, 0)
            best_path = None
            for name in os.listdir(program_files):
                if name.startswith('OpenJPEG '):
                    version = tuple(
                        [int(x) for x in name[9:].strip().split('.')])
                    if version > best_version:
                        best_version = version
                        best_path = os.path.join(program_files, name)

            if best_path:
                _add_directory(library_dirs,
                               os.path.join(best_path, 'lib'))
                _add_directory(include_dirs,
                               os.path.join(best_path, 'include'))

        #
        # insert new dirs *before* default libs, to avoid conflicts
        # between Python PYD stub libs and real libraries

        self.compiler.library_dirs = library_dirs + self.compiler.library_dirs
        self.compiler.include_dirs = include_dirs + self.compiler.include_dirs

        #
        # look for available libraries

        feature = self.feature

        if feature.want('zlib'):
            if _find_include_file(self, "zlib.h"):
                if _find_library_file(self, "z"):
                    feature.zlib = "z"
                elif (sys.platform == "win32" and
                        _find_library_file(self, "zlib")):
                    feature.zlib = "zlib"  # alternative name

        if feature.want('jpeg'):
            if _find_include_file(self, "jpeglib.h"):
                if _find_library_file(self, "jpeg"):
                    feature.jpeg = "jpeg"
                elif (
                        sys.platform == "win32" and
                        _find_library_file(self, "libjpeg")):
                    feature.jpeg = "libjpeg"  # alternative name

        feature.openjpeg_version = None
        if feature.want('jpeg2000'):
            best_version = None
            best_path = None

            # Find the best version
            for directory in self.compiler.include_dirs:
                try:
                    listdir = os.listdir(directory)
                except Exception:
                    # WindowsError, FileNotFoundError
                    continue
                for name in listdir:
                    if name.startswith('openjpeg-') and \
                        os.path.isfile(os.path.join(directory, name,
                                                    'openjpeg.h')):
                        version = tuple([int(x) for x in name[9:].split('.')])
                        if best_version is None or version > best_version:
                            best_version = version
                            best_path = os.path.join(directory, name)

            if best_version and _find_library_file(self, 'openjp2'):
                # Add the directory to the include path so we can include
                # <openjpeg.h> rather than having to cope with the versioned
                # include path
                _add_directory(self.compiler.include_dirs, best_path, 0)
                feature.jpeg2000 = 'openjp2'
                feature.openjpeg_version = '.'.join(
                    [str(x) for x in best_version])

        if feature.want('tiff'):
            if _find_library_file(self, "tiff"):
                feature.tiff = "tiff"
            if sys.platform == "win32" and _find_library_file(self, "libtiff"):
                feature.tiff = "libtiff"
            if (sys.platform == "darwin" and
                    _find_library_file(self, "libtiff")):
                feature.tiff = "libtiff"

        if feature.want('freetype'):
            if _find_library_file(self, "freetype"):
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
                        _add_directory(self.compiler.include_dirs, dir, 0)

        if feature.want('lcms'):
            if _find_include_file(self, "lcms2.h"):
                if _find_library_file(self, "lcms2"):
                    feature.lcms = "lcms"

        if _tkinter and _find_include_file(self, "tk.h"):
            # the library names may vary somewhat (e.g. tcl84 or tcl8.4)
            version = TCL_VERSION[0] + TCL_VERSION[2]
            if feature.want('tcl'):
                if _find_library_file(self, "tcl" + version):
                    feature.tcl = "tcl" + version
                elif _find_library_file(self, "tcl" + TCL_VERSION):
                    feature.tcl = "tcl" + TCL_VERSION
            if feature.want('tk'):
                if _find_library_file(self, "tk" + version):
                    feature.tk = "tk" + version
                elif _find_library_file(self, "tk" + TCL_VERSION):
                    feature.tk = "tk" + TCL_VERSION

        if feature.want('webp'):
            if (_find_include_file(self, "webp/encode.h") and
                    _find_include_file(self, "webp/decode.h")):
                # In Google's precompiled zip it is call "libwebp":
                if _find_library_file(self, "webp"):
                    feature.webp = "webp"
                elif _find_library_file(self, "libwebp"):
                    feature.webp = "libwebp"

        if feature.want('webpmux'):
            if (_find_include_file(self, "webp/mux.h") and
                    _find_include_file(self, "webp/demux.h")):
                if (_find_library_file(self, "webpmux") and
                        _find_library_file(self, "webpdemux")):
                    feature.webpmux = "webpmux"
                if (_find_library_file(self, "libwebpmux") and
                        _find_library_file(self, "libwebpdemux")):
                    feature.webpmux = "libwebpmux"

        for f in feature:
            if not getattr(feature, f) and feature.require(f):
                raise ValueError(
                    '--enable-%s requested but %s not found, aborting.'
                    % (f, f))

        #
        # core library

        files = ["_imaging.c"]
        for file in _IMAGING:
            files.append(file + ".c")
        for file in _LIB_IMAGING:
            files.append(os.path.join("libImaging", file + ".c"))

        libs = []
        defs = []
        if feature.jpeg:
            libs.append(feature.jpeg)
            defs.append(("HAVE_LIBJPEG", None))
        if feature.jpeg2000:
            libs.append(feature.jpeg2000)
            defs.append(("HAVE_OPENJPEG", None))
            if sys.platform == "win32":
                defs.append(("OPJ_STATIC", None))
        if feature.zlib:
            libs.append(feature.zlib)
            defs.append(("HAVE_LIBZ", None))
        if feature.tiff:
            libs.append(feature.tiff)
            defs.append(("HAVE_LIBTIFF", None))
        if sys.platform == "win32":
            libs.extend(["kernel32", "user32", "gdi32"])
        if struct.unpack("h", "\0\1".encode('ascii'))[0] == 1:
            defs.append(("WORDS_BIGENDIAN", None))

        exts = [(Extension(
            "PIL._imaging", files, libraries=libs, define_macros=defs))]

        #
        # additional libraries

        if feature.freetype:
            defs = []
            if feature.freetype_version == 20:
                defs.append(("USE_FREETYPE_2_0", None))
            exts.append(Extension(
                "PIL._imagingft", ["_imagingft.c"], libraries=["freetype"],
                define_macros=defs))

        if os.path.isfile("_imagingtiff.c") and feature.tiff:
            exts.append(Extension(
                "PIL._imagingtiff", ["_imagingtiff.c"], libraries=["tiff"]))

        if os.path.isfile("_imagingcms.c") and feature.lcms:
            extra = []
            if sys.platform == "win32":
                extra.extend(["user32", "gdi32"])
            exts.append(Extension(
                "PIL._imagingcms",
                ["_imagingcms.c"],
                libraries=["lcms2"] + extra))

        if os.path.isfile("_webp.c") and feature.webp:
            libs = [feature.webp]
            defs = []

            if feature.webpmux:
                defs.append(("HAVE_WEBPMUX", None))
                libs.append(feature.webpmux)
                libs.append(feature.webpmux.replace('pmux','pdemux'))

            exts.append(Extension(
                "PIL._webp", ["_webp.c"], libraries=libs, define_macros=defs))

        if sys.platform == "darwin":
            # locate Tcl/Tk frameworks
            frameworks = []
            framework_roots = [
                "/Library/Frameworks",
                "/System/Library/Frameworks"]
            for root in framework_roots:
                if (
                        os.path.exists(os.path.join(root, "Tcl.framework")) and
                        os.path.exists(os.path.join(root, "Tk.framework"))):
                    print("--- using frameworks at %s" % root)
                    frameworks = ["-framework", "Tcl", "-framework", "Tk"]
                    dir = os.path.join(root, "Tcl.framework", "Headers")
                    _add_directory(self.compiler.include_dirs, dir, 0)
                    dir = os.path.join(root, "Tk.framework", "Headers")
                    _add_directory(self.compiler.include_dirs, dir, 1)
                    break
            if frameworks:
                exts.append(Extension(
                    "PIL._imagingtk", ["_imagingtk.c", "Tk/tkImaging.c"],
                    extra_compile_args=frameworks, extra_link_args=frameworks))
                feature.tcl = feature.tk = 1  # mark as present
        elif feature.tcl and feature.tk:
            exts.append(Extension(
                "PIL._imagingtk", ["_imagingtk.c", "Tk/tkImaging.c"],
                libraries=[feature.tcl, feature.tk]))

        if os.path.isfile("_imagingmath.c"):
            exts.append(Extension("PIL._imagingmath", ["_imagingmath.c"]))

        if os.path.isfile("_imagingmorph.c"):
            exts.append(Extension("PIL._imagingmorph", ["_imagingmorph.c"]))

        self.extensions[:] = exts

        build_ext.build_extensions(self)

        #
        # sanity and security checks

        unsafe_zlib = None

        if feature.zlib:
            unsafe_zlib = self.check_zlib_version(self.compiler.include_dirs)

        self.summary_report(feature, unsafe_zlib)

    def summary_report(self, feature, unsafe_zlib):

        print("-" * 68)
        print("PIL SETUP SUMMARY")
        print("-" * 68)
        print("version      Pillow %s" % PILLOW_VERSION)
        v = sys.version.split("[")
        print("platform     %s %s" % (sys.platform, v[0].strip()))
        for v in v[1:]:
            print("             [%s" % v.strip())
        print("-" * 68)

        options = [
            (feature.tcl and feature.tk, "TKINTER"),
            (feature.jpeg, "JPEG"),
            (feature.jpeg2000, "OPENJPEG (JPEG2000)",
                feature.openjpeg_version),
            (feature.zlib, "ZLIB (PNG/ZIP)"),
            (feature.tiff, "LIBTIFF"),
            (feature.freetype, "FREETYPE2"),
            (feature.lcms, "LITTLECMS2"),
            (feature.webp, "WEBP"),
            (feature.webpmux, "WEBPMUX"), ]

        all = 1
        for option in options:
            if option[0]:
                version = ''
                if len(option) >= 3 and option[2]:
                    version = ' (%s)' % option[2]
                print("--- %s support available%s" % (option[1], version))
            else:
                print("*** %s support not available" % option[1])
                if option[1] == "TKINTER" and _tkinter:
                    version = _tkinter.TCL_VERSION
                    print("(Tcl/Tk %s libraries needed)" % version)
                all = 0

        if feature.zlib and unsafe_zlib:
            print("")
            print("*** Warning: zlib", unsafe_zlib)
            print("may contain a security vulnerability.")
            print("*** Consider upgrading to zlib 1.2.3 or newer.")
            print("*** See: http://www.kb.cert.org/vuls/id/238678")
            print(" http://www.kb.cert.org/vuls/id/680620")
            print(" http://www.gzip.org/zlib/advisory-2002-03-11.txt")
            print("")

        print("-" * 68)

        if not all:
            print("To add a missing option, make sure you have the required")
            print("library, and set the corresponding ROOT variable in the")
            print("setup.py script.")
            print("")

        print("To check the build, run the selftest.py script.")
        print("")

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

    # http://hg.python.org/users/barry/rev/7e8deab93d5a
    def add_multiarch_paths(self):
        # Debian/Ubuntu multiarch support.
        # https://wiki.ubuntu.com/MultiarchSpec
        # self.build_temp
        tmpfile = os.path.join(self.build_temp, 'multiarch')
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        ret = os.system(
            'dpkg-architecture -qDEB_HOST_MULTIARCH > %s 2> /dev/null' %
            tmpfile)
        try:
            if ret >> 8 == 0:
                fp = open(tmpfile, 'r')
                multiarch_path_component = fp.readline().strip()
                fp.close()
                _add_directory(
                    self.compiler.library_dirs,
                    '/usr/lib/' + multiarch_path_component)
                _add_directory(
                    self.compiler.include_dirs,
                    '/usr/include/' + multiarch_path_component)
        finally:
            os.unlink(tmpfile)


setup(
    name=NAME,
    version=PILLOW_VERSION,
    description='Python Imaging Library (Fork)',
    long_description=_read('README.rst').decode('utf-8'),
    author='Alex Clark (fork author)',
    author_email='aclark@aclark.net',
    url='http://python-pillow.github.io/',
    classifiers=[
        "Development Status :: 6 - Mature",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Graphics :: Capture :: Digital Camera",
        "Topic :: Multimedia :: Graphics :: Capture :: Scanners",
        "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Multimedia :: Graphics :: Viewers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        ],
    cmdclass={"build_ext": pil_build_ext},
    ext_modules=[Extension("PIL._imaging", ["_imaging.c"])],
    include_package_data=True,
    packages=find_packages(),
    scripts=glob.glob("Scripts/pil*.py"),
    test_suite='PIL.tests',
    keywords=["Imaging", ],
    license='Standard PIL License',
    zip_safe=True,
)
# End of file
