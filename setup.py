# > pyroma .
# ------------------------------
# Checking .
# Found Pillow
# ------------------------------
# Final rating: 10/10
# Your cheese is so fresh most people think it's a cream: Mascarpone
# ------------------------------
from __future__ import annotations

import os
import re
import shutil
import struct
import subprocess
import sys
import warnings
from collections.abc import Iterator

from pybind11.setup_helpers import ParallelCompile
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

TYPE_CHECKING = False
if TYPE_CHECKING:
    from setuptools import _BuildInfo

configuration: dict[str, list[str]] = {}

# parse configuration from _custom_build/backend.py
while sys.argv[-1].startswith("--pillow-configuration="):
    _, key, value = sys.argv.pop().split("=", 2)
    configuration.setdefault(key, []).append(value)

default = int(configuration.get("parallel", ["0"])[-1])
ParallelCompile("MAX_CONCURRENCY", default).install()


def get_version() -> str:
    version_file = "src/PIL/_version.py"
    with open(version_file, encoding="utf-8") as f:
        return f.read().split('"')[1]


PILLOW_VERSION = get_version()
AVIF_ROOT = None
FREETYPE_ROOT = None
HARFBUZZ_ROOT = None
FRIBIDI_ROOT = None
IMAGEQUANT_ROOT = None
JPEG2K_ROOT = None
JPEG_ROOT = None
LCMS_ROOT = None
RAQM_ROOT = None
TIFF_ROOT = None
WEBP_ROOT = None
ZLIB_ROOT = None
FUZZING_BUILD = "LIB_FUZZING_ENGINE" in os.environ

if sys.platform == "win32" and sys.version_info >= (3, 15):
    import atexit

    atexit.register(
        lambda: warnings.warn(
            f"Pillow {PILLOW_VERSION} does not support Python "
            f"{sys.version_info.major}.{sys.version_info.minor} and does not provide "
            "prebuilt Windows binaries. We do not recommend building from source on "
            "Windows.",
            RuntimeWarning,
        )
    )


_IMAGING = ("decode", "encode", "map", "display", "outline", "path")

_LIB_IMAGING = (
    "Access",
    "AlphaComposite",
    "Arrow",
    "Resample",
    "Reduce",
    "Bands",
    "BcnDecode",
    "BcnEncode",
    "BitDecode",
    "Blend",
    "Chops",
    "ColorLUT",
    "Convert",
    "ConvertYCbCr",
    "Copy",
    "Crop",
    "Dib",
    "Draw",
    "Effects",
    "EpsEncode",
    "File",
    "Fill",
    "Filter",
    "FliDecode",
    "Geometry",
    "GetBBox",
    "GifDecode",
    "GifEncode",
    "HexDecode",
    "Histo",
    "JpegDecode",
    "JpegEncode",
    "Matrix",
    "ModeFilter",
    "Negative",
    "Offset",
    "Pack",
    "PackDecode",
    "Palette",
    "Paste",
    "Quant",
    "QuantOctree",
    "QuantHash",
    "QuantHeap",
    "PcdDecode",
    "PcxDecode",
    "PcxEncode",
    "Point",
    "RankFilter",
    "RawDecode",
    "RawEncode",
    "Storage",
    "SgiRleDecode",
    "SunRleDecode",
    "TgaRleDecode",
    "TgaRleEncode",
    "Unpack",
    "UnpackYCC",
    "UnsharpMask",
    "XbmDecode",
    "XbmEncode",
    "ZipDecode",
    "ZipEncode",
    "TiffDecode",
    "Jpeg2KDecode",
    "Jpeg2KEncode",
    "BoxBlur",
    "QuantPngQuant",
    "codec_fd",
)

DEBUG = False


class DependencyException(Exception):
    pass


class RequiredDependencyException(Exception):
    pass


PLATFORM_MINGW = os.name == "nt" and "GCC" in sys.version


def _dbg(s: str, tp: str | tuple[str, ...] | None = None) -> None:
    if DEBUG:
        if tp:
            print(s % tp)
            return
        print(s)


def _find_library_dirs_ldconfig() -> list[str]:
    # Based on ctypes.util from Python 2

    ldconfig = "ldconfig" if shutil.which("ldconfig") else "/sbin/ldconfig"
    args: list[str]
    env: dict[str, str]
    expr: str
    if sys.platform.startswith(("linux", "gnu")):
        if struct.calcsize("l") == 4:
            machine = os.uname()[4] + "-32"
        else:
            machine = os.uname()[4] + "-64"
        mach_map = {
            "x86_64-64": "libc6,x86-64",
            "ppc64-64": "libc6,64bit",
            "sparc64-64": "libc6,64bit",
            "s390x-64": "libc6,64bit",
            "ia64-64": "libc6,IA-64",
        }
        abi_type = mach_map.get(machine, "libc6")

        # Assuming GLIBC's ldconfig (with option -p)
        # Alpine Linux uses musl that can't print cache
        args = [ldconfig, "-p"]
        expr = rf".*\({abi_type}.*\) => (.*)"
        env = dict(os.environ)
        env["LC_ALL"] = "C"
        env["LANG"] = "C"

    elif sys.platform.startswith("freebsd"):
        args = [ldconfig, "-r"]
        expr = r".* => (.*)"
        env = {}

    try:
        p = subprocess.Popen(
            args, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE, env=env, text=True
        )
    except OSError:  # E.g. command not found
        return []
    data = p.communicate()[0]

    dirs = []
    for dll in re.findall(expr, data):
        dir = os.path.dirname(dll)
        if dir not in dirs:
            dirs.append(dir)
    return dirs


def _add_directory(
    path: list[str], subdir: str | None, where: int | None = None
) -> None:
    if subdir is None:
        return
    subdir = os.path.realpath(subdir)
    if os.path.isdir(subdir) and subdir not in path:
        if where is None:
            _dbg("Appending path %s", subdir)
            path.append(subdir)
        else:
            _dbg("Inserting path %s", subdir)
            path.insert(where, subdir)
    elif subdir in path and where is not None:
        path.remove(subdir)
        path.insert(where, subdir)


def _find_include_file(self: pil_build_ext, include: str) -> str | None:
    for directory in self.compiler.include_dirs:
        _dbg("Checking for include file %s in %s", (include, directory))
        path = os.path.join(directory, include)
        if os.path.isfile(path):
            _dbg("Found %s", include)
            return path
    return None


def _find_library_file(self: pil_build_ext, library: str) -> str | None:
    ret = self.compiler.find_library_file(self.compiler.library_dirs, library)
    if ret:
        _dbg("Found library %s at %s", (library, ret))
    else:
        _dbg("Couldn't find library %s in %s", (library, self.compiler.library_dirs))
    return ret


def _find_include_dir(self: pil_build_ext, dirname: str, include: str) -> bool | str:
    for directory in self.compiler.include_dirs:
        _dbg("Checking for include file %s in %s", (include, directory))
        if os.path.isfile(os.path.join(directory, include)):
            _dbg("Found %s in %s", (include, directory))
            return True
        subdir = os.path.join(directory, dirname)
        _dbg("Checking for include file %s in %s", (include, subdir))
        if os.path.isfile(os.path.join(subdir, include)):
            _dbg("Found %s in %s", (include, subdir))
            return subdir
    return False


def _cmd_exists(cmd: str) -> bool:
    if "PATH" not in os.environ:
        return False
    return any(
        os.access(os.path.join(path, cmd), os.X_OK)
        for path in os.environ["PATH"].split(os.pathsep)
    )


def _pkg_config(name: str) -> tuple[list[str], list[str]] | None:
    command = os.environ.get("PKG_CONFIG", "pkg-config")
    for keep_system in (True, False):
        try:
            command_libs = [command, "--libs-only-L", name]
            command_cflags = [command, "--cflags-only-I", name]
            stderr = None
            if keep_system:
                command_libs.append("--keep-system-libs")
                command_cflags.append("--keep-system-cflags")
                stderr = subprocess.DEVNULL
            if not DEBUG:
                command_libs.append("--silence-errors")
                command_cflags.append("--silence-errors")
            libs = re.split(
                r"(^|\s+)-L",
                subprocess.check_output(command_libs, stderr=stderr)
                .decode("utf8")
                .strip(),
            )[::2][1:]
            cflags = re.split(
                r"(^|\s+)-I",
                subprocess.check_output(command_cflags).decode("utf8").strip(),
            )[::2][1:]
            return libs, cflags
        except Exception:
            pass
    return None


class pil_build_ext(build_ext):
    class ext_feature:
        features = [
            "zlib",
            "jpeg",
            "tiff",
            "freetype",
            "raqm",
            "lcms",
            "webp",
            "jpeg2000",
            "imagequant",
            "xcb",
            "avif",
        ]

        required = {"jpeg", "zlib"}
        vendor: set[str] = set()

        def __init__(self) -> None:
            self._settings: dict[str, str | bool | None] = {}
            for f in self.features:
                self.set(f, None)

        def require(self, feat: str) -> bool:
            return feat in self.required

        def get(self, feat: str) -> str | bool | None:
            return self._settings[feat]

        def set(self, feat: str, value: str | bool | None) -> None:
            self._settings[feat] = value

        def want(self, feat: str) -> bool:
            return self._settings[feat] is None

        def want_vendor(self, feat: str) -> bool:
            return feat in self.vendor

        def __iter__(self) -> Iterator[str]:
            yield from self.features

    feature = ext_feature()

    user_options = (
        build_ext.user_options
        + [(f"disable-{x}", None, f"Disable support for {x}") for x in feature]
        + [(f"enable-{x}", None, f"Enable support for {x}") for x in feature]
        + [
            (f"vendor-{x}", None, f"Use vendored version of {x}")
            for x in ("raqm", "fribidi")
        ]
        + [
            ("disable-platform-guessing", None, "Disable platform guessing"),
            ("debug", None, "Debug logging"),
        ]
        + [("add-imaging-libs=", None, "Add libs to _imaging build")]
    )

    @staticmethod
    def check_configuration(option: str, value: str) -> bool | None:
        return True if value in configuration.get(option, []) else None

    def initialize_options(self) -> None:
        self.disable_platform_guessing = self.check_configuration(
            "platform-guessing", "disable"
        )
        self.add_imaging_libs = ""
        build_ext.initialize_options(self)
        for x in self.feature:
            setattr(self, f"disable_{x}", self.check_configuration(x, "disable"))
            setattr(self, f"enable_{x}", self.check_configuration(x, "enable"))
        for x in ("raqm", "fribidi"):
            setattr(self, f"vendor_{x}", self.check_configuration(x, "vendor"))
        if self.check_configuration("debug", "true"):
            self.debug = True
        self.parallel = configuration.get("parallel", [None])[-1]

    def finalize_options(self) -> None:
        build_ext.finalize_options(self)
        if self.debug:
            global DEBUG
            DEBUG = True
        if not self.parallel:
            # If --parallel (or -j) wasn't specified, we want to reproduce the same
            # behavior as before, that is, auto-detect the number of jobs.
            self.parallel = None

            cpu_count = os.cpu_count()
            if cpu_count is not None:
                try:
                    self.parallel = int(os.environ.get("MAX_CONCURRENCY", cpu_count))
                except TypeError:
                    pass
        for x in self.feature:
            if getattr(self, f"disable_{x}"):
                self.feature.set(x, False)
                self.feature.required.discard(x)
                _dbg("Disabling %s", x)
                if getattr(self, f"enable_{x}"):
                    msg = f"Conflicting options: '-C {x}=enable' and '-C {x}=disable'"
                    raise ValueError(msg)
                if x == "freetype":
                    _dbg("'-C freetype=disable' implies '-C raqm=disable'")
                    if getattr(self, "enable_raqm"):
                        msg = (
                            "Conflicting options: "
                            "'-C raqm=enable' and '-C freetype=disable'"
                        )
                        raise ValueError(msg)
                    setattr(self, "disable_raqm", True)
            if getattr(self, f"enable_{x}"):
                _dbg("Requiring %s", x)
                self.feature.required.add(x)
                if x == "raqm":
                    _dbg("'-C raqm=enable' implies '-C freetype=enable'")
                    self.feature.required.add("freetype")
        for x in ("raqm", "fribidi"):
            if getattr(self, f"vendor_{x}"):
                if getattr(self, "disable_raqm"):
                    msg = f"Conflicting options: '-C {x}=vendor' and '-C raqm=disable'"
                    raise ValueError(msg)
                if x == "fribidi" and not getattr(self, "vendor_raqm"):
                    msg = (
                        f"Conflicting options: '-C {x}=vendor' and not '-C raqm=vendor'"
                    )
                    raise ValueError(msg)
                _dbg("Using vendored version of %s", x)
                self.feature.vendor.add(x)

    def _update_extension(
        self,
        name: str,
        libraries: list[str] | list[str | bool | None],
        define_macros: list[tuple[str, str | None]] | None = None,
        sources: list[str] | None = None,
    ) -> None:
        for extension in self.extensions:
            if extension.name == name:
                extension.libraries += libraries
                if define_macros is not None:
                    extension.define_macros += define_macros
                if sources is not None:
                    extension.sources += sources
                if FUZZING_BUILD:
                    extension.language = "c++"
                    extension.extra_link_args = ["--stdlib=libc++"]
                break

    def _remove_extension(self, name: str) -> None:
        for extension in self.extensions:
            if extension.name == name:
                self.extensions.remove(extension)
                break

    def get_macos_sdk_path(self) -> str | None:
        try:
            sdk_path = (
                subprocess.check_output(["xcrun", "--show-sdk-path", "--sdk", "macosx"])
                .strip()
                .decode("latin1")
            )
        except Exception:
            sdk_path = None
        if (
            not sdk_path
            or sdk_path == "/Applications/Xcode.app/Contents/Developer"
            "/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk"
        ):
            commandlinetools_sdk_path = (
                "/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"
            )
            if os.path.exists(commandlinetools_sdk_path):
                sdk_path = commandlinetools_sdk_path
        return sdk_path

    def get_ios_sdk_path(self) -> str:
        try:
            sdk = sys.implementation._multiarch.split("-")[-1]
            _dbg("Using %s SDK", sdk)
            return (
                subprocess.check_output(["xcrun", "--show-sdk-path", "--sdk", sdk])
                .strip()
                .decode("latin1")
            )
        except Exception:
            msg = "Unable to identify location of iOS SDK."
            raise ValueError(msg)

    def build_extensions(self) -> None:
        library_dirs: list[str] = []
        include_dirs: list[str] = []

        pkg_config = None
        if _cmd_exists(os.environ.get("PKG_CONFIG", "pkg-config")):
            pkg_config = _pkg_config

        #
        # add configured kits
        for root_name, lib_name in {
            "AVIF_ROOT": "avif",
            "JPEG_ROOT": "libjpeg",
            "JPEG2K_ROOT": "libopenjp2",
            "TIFF_ROOT": ("libtiff-5", "libtiff-4"),
            "ZLIB_ROOT": "zlib",
            "FREETYPE_ROOT": "freetype2",
            "HARFBUZZ_ROOT": "harfbuzz",
            "FRIBIDI_ROOT": "fribidi",
            "RAQM_ROOT": "raqm",
            "WEBP_ROOT": "libwebp",
            "LCMS_ROOT": "lcms2",
            "IMAGEQUANT_ROOT": "libimagequant",
        }.items():
            root = globals()[root_name]

            if root is None and root_name in os.environ:
                root_prefix = os.environ[root_name]
                root = (
                    os.path.join(root_prefix, "lib"),
                    os.path.join(root_prefix, "include"),
                )

            if root is None and pkg_config:
                if isinstance(lib_name, str):
                    _dbg("Looking for `%s` using pkg-config.", lib_name)
                    root = pkg_config(lib_name)
                else:
                    for lib_name2 in lib_name:
                        _dbg("Looking for `%s` using pkg-config.", lib_name2)
                        root = pkg_config(lib_name2)
                        if root:
                            break

            if isinstance(root, tuple):
                lib_root, include_root = root
            else:
                lib_root = include_root = root

            if lib_root is not None:
                if not isinstance(lib_root, (tuple, list)):
                    lib_root = (lib_root,)
                for lib_dir in lib_root:
                    _add_directory(library_dirs, lib_dir)
            if include_root is not None:
                if not isinstance(include_root, (tuple, list)):
                    include_root = (include_root,)
                for include_dir in include_root:
                    _add_directory(include_dirs, include_dir)

        # respect CFLAGS/CPPFLAGS/LDFLAGS
        for k in ("CFLAGS", "CPPFLAGS", "LDFLAGS"):
            if k in os.environ:
                for match in re.finditer(r"-I([^\s]+)", os.environ[k]):
                    _add_directory(include_dirs, match.group(1))
                for match in re.finditer(r"-L([^\s]+)", os.environ[k]):
                    _add_directory(library_dirs, match.group(1))

        # include, rpath, if set as environment variables:
        for k in ("C_INCLUDE_PATH", "CPATH", "INCLUDE"):
            if k in os.environ:
                for d in os.environ[k].split(os.path.pathsep):
                    _add_directory(include_dirs, d)

        for k in ("LD_RUN_PATH", "LIBRARY_PATH", "LIB"):
            if k in os.environ:
                for d in os.environ[k].split(os.path.pathsep):
                    _add_directory(library_dirs, d)

        _add_directory(library_dirs, os.path.join(sys.prefix, "lib"))
        _add_directory(include_dirs, os.path.join(sys.prefix, "include"))

        #
        # add platform directories

        if self.disable_platform_guessing:
            pass

        elif sys.platform == "cygwin":
            # pythonX.Y.dll.a is in the /usr/lib/pythonX.Y/config directory
            self.compiler.shared_lib_extension = ".dll.a"
            _add_directory(
                library_dirs,
                os.path.join(
                    "/usr/lib", "python{}.{}".format(*sys.version_info), "config"
                ),
            )

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
            try:
                prefix = (
                    subprocess.check_output(["brew", "--prefix"])
                    .strip()
                    .decode("latin1")
                )
            except Exception:
                # Homebrew not installed
                prefix = None

            ft_prefix = None

            if prefix:
                # add Homebrew's include and lib directories
                _add_directory(library_dirs, os.path.join(prefix, "lib"))
                _add_directory(include_dirs, os.path.join(prefix, "include"))
                _add_directory(
                    include_dirs, os.path.join(prefix, "opt", "zlib", "include")
                )
                ft_prefix = os.path.join(prefix, "opt", "freetype")

            if ft_prefix and os.path.isdir(ft_prefix):
                # freetype might not be linked into Homebrew's prefix
                _add_directory(library_dirs, os.path.join(ft_prefix, "lib"))
                _add_directory(include_dirs, os.path.join(ft_prefix, "include"))
            else:
                # fall back to freetype from XQuartz if
                # Homebrew's freetype is missing
                _add_directory(library_dirs, "/usr/X11/lib")
                _add_directory(include_dirs, "/usr/X11/include")

            # Add the macOS SDK path.
            sdk_path = self.get_macos_sdk_path()
            if sdk_path:
                _add_directory(library_dirs, os.path.join(sdk_path, "usr", "lib"))
                _add_directory(include_dirs, os.path.join(sdk_path, "usr", "include"))

                for extension in self.extensions:
                    extension.extra_compile_args = ["-Wno-nullability-completeness"]

        elif sys.platform == "ios":
            # Add the iOS SDK path.
            sdk_path = self.get_ios_sdk_path()

            # Add the iOS SDK path.
            _add_directory(library_dirs, os.path.join(sdk_path, "usr", "lib"))
            _add_directory(include_dirs, os.path.join(sdk_path, "usr", "include"))

            for extension in self.extensions:
                extension.extra_compile_args = ["-Wno-nullability-completeness"]

        elif sys.platform.startswith(("linux", "gnu", "freebsd")):
            for dirname in _find_library_dirs_ldconfig():
                _add_directory(library_dirs, dirname)
            if sys.platform.startswith("linux") and os.environ.get("ANDROID_ROOT"):
                # termux support for android.
                # system libraries (zlib) are installed in /system/lib
                # headers are at $PREFIX/include
                # user libs are at $PREFIX/lib
                _add_directory(
                    library_dirs,
                    os.path.join(
                        os.environ["ANDROID_ROOT"],
                        "lib" if struct.calcsize("l") == 4 else "lib64",
                    ),
                )

        elif sys.platform.startswith("netbsd"):
            _add_directory(library_dirs, "/usr/pkg/lib")
            _add_directory(include_dirs, "/usr/pkg/include")

        elif sys.platform.startswith("sunos5"):
            _add_directory(library_dirs, "/opt/local/lib")
            _add_directory(include_dirs, "/opt/local/include")

        # FIXME: check /opt/stuff directories here?

        # standard locations
        if not self.disable_platform_guessing:
            _add_directory(library_dirs, "/usr/local/lib")
            _add_directory(include_dirs, "/usr/local/include")

            _add_directory(library_dirs, "/usr/lib")
            _add_directory(include_dirs, "/usr/include")
            # alpine, at least
            _add_directory(library_dirs, "/lib")

        if sys.platform == "win32":
            # on Windows, look for the OpenJPEG libraries in the location that
            # the official installer puts them
            program_files = os.environ.get("ProgramFiles", "")
            best_version = (0, 0)
            best_path = None
            for name in os.listdir(program_files):
                if name.startswith("OpenJPEG "):
                    version = tuple(int(x) for x in name[9:].strip().split("."))
                    if version > best_version:
                        best_version = version
                        best_path = os.path.join(program_files, name)

            if best_path:
                _dbg("Adding %s to search list", best_path)
                _add_directory(library_dirs, os.path.join(best_path, "lib"))
                _add_directory(include_dirs, os.path.join(best_path, "include"))

        #
        # insert new dirs *before* default libs, to avoid conflicts
        # between Python PYD stub libs and real libraries

        self.compiler.library_dirs = library_dirs + self.compiler.library_dirs
        self.compiler.include_dirs = include_dirs + self.compiler.include_dirs

        #
        # look for available libraries

        feature = self.feature

        if feature.want("zlib"):
            _dbg("Looking for zlib")
            if _find_include_file(self, "zlib.h"):
                if _find_library_file(self, "z"):
                    feature.set("zlib", "z")
                elif sys.platform == "win32" and _find_library_file(self, "zlib"):
                    feature.set("zlib", "zlib")  # alternative name
                elif sys.platform == "win32" and _find_library_file(self, "zdll"):
                    feature.set("zlib", "zdll")  # dll import library

        if feature.want("jpeg"):
            _dbg("Looking for jpeg")
            if _find_include_file(self, "jpeglib.h"):
                if _find_library_file(self, "jpeg"):
                    feature.set("jpeg", "jpeg")
                elif sys.platform == "win32" and _find_library_file(self, "libjpeg"):
                    feature.set("jpeg", "libjpeg")  # alternative name

        feature.set("openjpeg_version", None)
        if feature.want("jpeg2000"):
            _dbg("Looking for jpeg2000")
            best_version: tuple[int, ...] | None = None
            best_path = None

            # Find the best version
            for directory in self.compiler.include_dirs:
                _dbg("Checking for openjpeg-#.# in %s", directory)
                try:
                    listdir = os.listdir(directory)
                except Exception:
                    # OSError, FileNotFoundError
                    continue
                for name in listdir:
                    if name.startswith("openjpeg-") and os.path.isfile(
                        os.path.join(directory, name, "openjpeg.h")
                    ):
                        _dbg("Found openjpeg.h in %s/%s", (directory, name))
                        version = tuple(int(x) for x in name[9:].split("."))
                        if best_version is None or version > best_version:
                            best_version = version
                            best_path = os.path.join(directory, name)
                            _dbg(
                                "Best openjpeg version %s so far in %s",
                                (str(best_version), best_path),
                            )

            if best_version and _find_library_file(self, "openjp2"):
                # Add the directory to the include path so we can include
                # <openjpeg.h> rather than having to cope with the versioned
                # include path
                _add_directory(self.compiler.include_dirs, best_path, 0)
                feature.set("jpeg2000", "openjp2")
                feature.set("openjpeg_version", ".".join(str(x) for x in best_version))

        if feature.want("imagequant"):
            _dbg("Looking for imagequant")
            if _find_include_file(self, "libimagequant.h"):
                if _find_library_file(self, "imagequant"):
                    feature.set("imagequant", "imagequant")
                elif _find_library_file(self, "libimagequant"):
                    feature.set("imagequant", "libimagequant")

        if feature.want("tiff"):
            _dbg("Looking for tiff")
            if _find_include_file(self, "tiff.h"):
                if sys.platform in ["win32", "darwin"] and _find_library_file(
                    self, "libtiff"
                ):
                    feature.set("tiff", "libtiff")
                elif _find_library_file(self, "tiff"):
                    feature.set("tiff", "tiff")

        if feature.want("freetype"):
            _dbg("Looking for freetype")
            if _find_library_file(self, "freetype"):
                # look for freetype2 include files
                freetype_version = 0
                for subdir in self.compiler.include_dirs:
                    _dbg("Checking for include file %s in %s", ("ft2build.h", subdir))
                    if os.path.isfile(os.path.join(subdir, "ft2build.h")):
                        _dbg("Found %s in %s", ("ft2build.h", subdir))
                        freetype_version = 21
                        subdir = os.path.join(subdir, "freetype2")
                        break
                    subdir = os.path.join(subdir, "freetype2")
                    _dbg("Checking for include file %s in %s", ("ft2build.h", subdir))
                    if os.path.isfile(os.path.join(subdir, "ft2build.h")):
                        _dbg("Found %s in %s", ("ft2build.h", subdir))
                        freetype_version = 21
                        break
                if freetype_version:
                    feature.set("freetype", "freetype")
                    if subdir:
                        _add_directory(self.compiler.include_dirs, subdir, 0)

        if feature.get("freetype") and feature.want("raqm"):
            if not feature.want_vendor("raqm"):  # want system Raqm
                _dbg("Looking for Raqm")
                if _find_include_file(self, "raqm.h"):
                    if _find_library_file(self, "raqm"):
                        feature.set("raqm", "raqm")
                    elif _find_library_file(self, "libraqm"):
                        feature.set("raqm", "libraqm")
            else:  # want to build Raqm from src/thirdparty
                _dbg("Looking for HarfBuzz")
                feature.set("harfbuzz", None)
                hb_dir = _find_include_dir(self, "harfbuzz", "hb.h")
                if hb_dir:
                    if isinstance(hb_dir, str):
                        _add_directory(self.compiler.include_dirs, hb_dir, 0)
                    if _find_library_file(self, "harfbuzz"):
                        feature.set("harfbuzz", "harfbuzz")
                if feature.get("harfbuzz"):
                    if not feature.want_vendor("fribidi"):  # want system FriBiDi
                        _dbg("Looking for FriBiDi")
                        feature.set("fribidi", None)
                        fribidi_dir = _find_include_dir(self, "fribidi", "fribidi.h")
                        if fribidi_dir:
                            if isinstance(fribidi_dir, str):
                                _add_directory(
                                    self.compiler.include_dirs, fribidi_dir, 0
                                )
                            if _find_library_file(self, "fribidi"):
                                feature.set("fribidi", "fribidi")
                                feature.set("raqm", True)
                    else:  # want to build FriBiDi shim from src/thirdparty
                        feature.set("raqm", True)

        if feature.want("lcms"):
            _dbg("Looking for lcms")
            if _find_include_file(self, "lcms2.h"):
                if _find_library_file(self, "lcms2"):
                    feature.set("lcms", "lcms2")
                elif _find_library_file(self, "lcms2_static"):
                    # alternate Windows name.
                    feature.set("lcms", "lcms2_static")

        if feature.want("webp"):
            _dbg("Looking for webp")
            if all(
                _find_include_file(self, "webp/" + include)
                for include in ("encode.h", "decode.h", "mux.h", "demux.h")
            ):
                # In Google's precompiled zip it is called "libwebp"
                for prefix in ("", "lib"):
                    if all(
                        _find_library_file(self, prefix + library)
                        for library in ("webp", "webpmux", "webpdemux")
                    ):
                        feature.set("webp", prefix + "webp")
                        break

        if feature.want("xcb"):
            _dbg("Looking for xcb")
            if _find_include_file(self, "xcb/xcb.h"):
                if _find_library_file(self, "xcb"):
                    feature.set("xcb", "xcb")

        if feature.want("avif"):
            _dbg("Looking for avif")
            if avif_h := _find_include_file(self, "avif/avif.h"):
                with open(avif_h, "rb") as fp:
                    major_version = int(
                        fp.read().split(b"#define AVIF_VERSION_MAJOR ")[1].split()[0]
                    )
                    if major_version >= 1 and _find_library_file(self, "avif"):
                        feature.set("avif", "avif")

        for f in feature:
            if not feature.get(f) and feature.require(f):
                if f in ("jpeg", "zlib"):
                    raise RequiredDependencyException(f)
                raise DependencyException(f)

        #
        # core library

        libs: list[str | bool | None] = []
        libs.extend(self.add_imaging_libs.split())
        defs: list[tuple[str, str | None]] = []
        if feature.get("tiff"):
            libs.append(feature.get("tiff"))
            defs.append(("HAVE_LIBTIFF", None))
            if sys.platform == "win32":
                # This define needs to be defined if-and-only-if it was defined
                # when compiling LibTIFF. LibTIFF doesn't expose it in `tiffconf.h`,
                # so we have to guess; by default it is defined in all Windows builds.
                # See #4237, #5243, #5359 for more information.
                defs.append(("USE_WIN32_FILEIO", None))
            elif sys.platform == "ios":
                # Ensure transitive dependencies are linked.
                libs.append("lzma")
        if feature.get("jpeg"):
            libs.append(feature.get("jpeg"))
            defs.append(("HAVE_LIBJPEG", None))
        if feature.get("jpeg2000"):
            libs.append(feature.get("jpeg2000"))
            defs.append(("HAVE_OPENJPEG", None))
            if sys.platform == "win32" and not PLATFORM_MINGW:
                defs.append(("OPJ_STATIC", None))
        if feature.get("zlib"):
            libs.append(feature.get("zlib"))
            defs.append(("HAVE_LIBZ", None))
        if feature.get("imagequant"):
            libs.append(feature.get("imagequant"))
            defs.append(("HAVE_LIBIMAGEQUANT", None))
        if feature.get("xcb"):
            libs.append(feature.get("xcb"))
            if sys.platform == "ios":
                # Ensure transitive dependencies are linked.
                libs.append("Xau")
            defs.append(("HAVE_XCB", None))
        if sys.platform == "win32":
            libs.extend(["kernel32", "user32", "gdi32"])
        if struct.unpack("h", b"\0\1")[0] == 1:
            defs.append(("WORDS_BIGENDIAN", None))

        defs.append(("PILLOW_VERSION", f'"{PILLOW_VERSION}"'))

        self._update_extension("PIL._imaging", libs, defs)

        #
        # additional libraries

        if feature.get("freetype"):
            srcs = []
            libs = ["freetype"]
            defs = []
            if feature.get("raqm"):
                if not feature.want_vendor("raqm"):  # using system Raqm
                    defs.append(("HAVE_RAQM", None))
                    defs.append(("HAVE_RAQM_SYSTEM", None))
                    libs.append(feature.get("raqm"))
                else:  # building Raqm from src/thirdparty
                    defs.append(("HAVE_RAQM", None))
                    srcs.append("src/thirdparty/raqm/raqm.c")
                    libs.append(feature.get("harfbuzz"))
                    if not feature.want_vendor("fribidi"):  # using system FriBiDi
                        defs.append(("HAVE_FRIBIDI_SYSTEM", None))
                        libs.append(feature.get("fribidi"))
                    else:  # building FriBiDi shim from src/thirdparty
                        srcs.append("src/thirdparty/fribidi-shim/fribidi.c")

            if sys.platform == "ios":
                # Ensure transitive dependencies are linked.
                libs.extend(["z", "bz2", "brotlicommon", "brotlidec", "png"])

            self._update_extension("PIL._imagingft", libs, defs, srcs)

        else:
            self._remove_extension("PIL._imagingft")

        if feature.get("lcms"):
            libs = [feature.get("lcms")]
            if sys.platform == "win32":
                libs.extend(["user32", "gdi32"])
            self._update_extension("PIL._imagingcms", libs)
        else:
            self._remove_extension("PIL._imagingcms")

        webp = feature.get("webp")
        if isinstance(webp, str):
            libs = [webp, webp + "mux", webp + "demux"]
            if sys.platform == "ios":
                # Ensure transitive dependencies are linked.
                libs.append("sharpyuv")
            self._update_extension("PIL._webp", libs)
        else:
            self._remove_extension("PIL._webp")

        if feature.get("avif"):
            libs = [feature.get("avif")]
            if sys.platform == "win32":
                libs.extend(["ntdll", "userenv", "ws2_32", "bcrypt"])
            self._update_extension("PIL._avif", libs)
        else:
            self._remove_extension("PIL._avif")

        tk_libs = ["psapi"] if sys.platform in ("win32", "cygwin") else []
        self._update_extension("PIL._imagingtk", tk_libs)

        build_ext.build_extensions(self)

        #
        # sanity checks

        self.summary_report(feature)

    def summary_report(self, feature: ext_feature) -> None:
        print("-" * 68)
        print("PIL SETUP SUMMARY")
        print("-" * 68)
        print(f"version      Pillow {PILLOW_VERSION}")
        version = sys.version.split("[")
        print(f"platform     {sys.platform} {version[0].strip()}")
        for v in version[1:]:
            print(f"             [{v.strip()}")
        print("-" * 68)

        raqm_extra_info = ""
        if feature.want_vendor("raqm"):
            raqm_extra_info += "bundled"
            if feature.want_vendor("fribidi"):
                raqm_extra_info += ", FriBiDi shim"

        options = [
            (feature.get("jpeg"), "JPEG"),
            (
                feature.get("jpeg2000"),
                "OPENJPEG (JPEG2000)",
                feature.get("openjpeg_version"),
            ),
            (feature.get("zlib"), "ZLIB (PNG/ZIP)"),
            (feature.get("imagequant"), "LIBIMAGEQUANT"),
            (feature.get("tiff"), "LIBTIFF"),
            (feature.get("freetype"), "FREETYPE2"),
            (feature.get("raqm"), "RAQM (Text shaping)", raqm_extra_info),
            (feature.get("lcms"), "LITTLECMS2"),
            (feature.get("webp"), "WEBP"),
            (feature.get("xcb"), "XCB (X protocol)"),
            (feature.get("avif"), "LIBAVIF"),
        ]

        all = 1
        for option in options:
            if option[0]:
                extra_info = ""
                if len(option) >= 3 and option[2]:
                    extra_info = f" ({option[2]})"
                print(f"--- {option[1]} support available{extra_info}")
            else:
                print(f"*** {option[1]} support not available")
                all = 0

        print("-" * 68)

        if not all:
            print("To add a missing option, make sure you have the required")
            print("library and headers.")
            print(
                "See https://pillow.readthedocs.io/en/latest/installation."
                "html#building-from-source"
            )
            print("")

        print("To check the build, run the selftest.py script.")
        print("")


def debug_build() -> bool:
    return hasattr(sys, "gettotalrefcount") or FUZZING_BUILD


libraries: list[tuple[str, _BuildInfo]] = [
    ("pil_imaging_mode", {"sources": ["src/libImaging/Mode.c"]}),
]

files: list[str | os.PathLike[str]] = ["src/_imaging.c"]
for src_file in _IMAGING:
    files.append("src/" + src_file + ".c")
for src_file in _LIB_IMAGING:
    files.append(os.path.join("src/libImaging", src_file + ".c"))
ext_modules = [
    Extension("PIL._imaging", files),
    Extension("PIL._imagingft", ["src/_imagingft.c"]),
    Extension("PIL._imagingcms", ["src/_imagingcms.c"]),
    Extension("PIL._webp", ["src/_webp.c"]),
    Extension("PIL._avif", ["src/_avif.c"]),
    Extension("PIL._imagingtk", ["src/_imagingtk.c", "src/Tk/tkImaging.c"]),
    Extension("PIL._imagingmath", ["src/_imagingmath.c"]),
    Extension("PIL._imagingmorph", ["src/_imagingmorph.c"]),
]


try:
    setup(
        cmdclass={"build_ext": pil_build_ext},
        ext_modules=ext_modules,
        libraries=libraries,
        zip_safe=not (debug_build() or PLATFORM_MINGW),
    )
except RequiredDependencyException as err:
    msg = f"""

The headers or library files could not be found for {str(err)},
a required dependency when compiling Pillow from source.

Please see the install instructions at:
   https://pillow.readthedocs.io/en/latest/installation/basic-installation.html

"""
    sys.stderr.write(msg)
    raise RequiredDependencyException(msg)
except DependencyException as err:
    msg = f"""

The headers or library files could not be found for {str(err)},
which was requested by the option flag '-C {str(err)}=enable'

"""
    sys.stderr.write(msg)
    raise DependencyException(msg)
