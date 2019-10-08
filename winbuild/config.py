import os

SF_MIRROR = "https://iweb.dl.sourceforge.net"
PILLOW_DEPENDS_DIR = "C:\\pillow-depends\\"

pythons = {
    # for AppVeyor
    "27": {"compiler": 7, "vc": 2010},
    "pypy2": {"compiler": 7, "vc": 2010},
    "35": {"compiler": 7.1, "vc": 2015},
    "36": {"compiler": 7.1, "vc": 2015},
    "pypy3": {"compiler": 7.1, "vc": 2015},
    "37": {"compiler": 7.1, "vc": 2015},
    # for GitHub Actions
    "3.5": {"compiler": 7.1, "vc": 2015},
    "3.6": {"compiler": 7.1, "vc": 2015},
    "3.7": {"compiler": 7.1, "vc": 2015},
}

VIRT_BASE = "c:/vp/"
X64_EXT = os.environ.get("X64_EXT", "x64")

libs = {
    # 'openjpeg': {
    #     'filename': 'openjpeg-2.0.0-win32-x86.zip',
    #     'version': '2.0'
    # },
    "zlib": {
        "url": "http://zlib.net/zlib1211.zip",
        "filename": PILLOW_DEPENDS_DIR + "zlib1211.zip",
        "dir": "zlib-1.2.11",
    },
    "jpeg": {
        "url": "http://www.ijg.org/files/jpegsr9c.zip",
        "filename": PILLOW_DEPENDS_DIR + "jpegsr9c.zip",
        "dir": "jpeg-9c",
    },
    "tiff": {
        "url": "ftp://download.osgeo.org/libtiff/tiff-4.0.10.tar.gz",
        "filename": PILLOW_DEPENDS_DIR + "tiff-4.0.10.tar.gz",
        "dir": "tiff-4.0.10",
    },
    "freetype": {
        "url": "https://download.savannah.gnu.org/releases/freetype/freetype-2.10.1.tar.gz",  # noqa: E501
        "filename": PILLOW_DEPENDS_DIR + "freetype-2.10.1.tar.gz",
        "dir": "freetype-2.10.1",
    },
    "lcms-2.7": {
        "url": SF_MIRROR + "/project/lcms/lcms/2.7/lcms2-2.7.zip",
        "filename": PILLOW_DEPENDS_DIR + "lcms2-2.7.zip",
        "dir": "lcms2-2.7",
    },
    "lcms-2.8": {
        "url": SF_MIRROR + "/project/lcms/lcms/2.8/lcms2-2.8.zip",
        "filename": PILLOW_DEPENDS_DIR + "lcms2-2.8.zip",
        "dir": "lcms2-2.8",
    },
    "ghostscript": {
        "url": "https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs927/ghostscript-9.27.tar.gz",  # noqa: E501
        "filename": PILLOW_DEPENDS_DIR + "ghostscript-9.27.tar.gz",
        "dir": "ghostscript-9.27",
    },
    "tcl-8.5": {
        "url": SF_MIRROR + "/project/tcl/Tcl/8.5.19/tcl8519-src.zip",
        "filename": PILLOW_DEPENDS_DIR + "tcl8519-src.zip",
        "dir": "",
    },
    "tk-8.5": {
        "url": SF_MIRROR + "/project/tcl/Tcl/8.5.19/tk8519-src.zip",
        "filename": PILLOW_DEPENDS_DIR + "tk8519-src.zip",
        "dir": "",
        "version": "8.5.19",
    },
    "tcl-8.6": {
        "url": SF_MIRROR + "/project/tcl/Tcl/8.6.9/tcl869-src.zip",
        "filename": PILLOW_DEPENDS_DIR + "tcl869-src.zip",
        "dir": "",
    },
    "tk-8.6": {
        "url": SF_MIRROR + "/project/tcl/Tcl/8.6.9/tk869-src.zip",
        "filename": PILLOW_DEPENDS_DIR + "tk869-src.zip",
        "dir": "",
        "version": "8.6.9",
    },
    "webp": {
        "url": "http://downloads.webmproject.org/releases/webp/libwebp-1.0.3.tar.gz",
        "filename": PILLOW_DEPENDS_DIR + "libwebp-1.0.3.tar.gz",
        "dir": "libwebp-1.0.3",
    },
    "openjpeg": {
        "url": "https://github.com/uclouvain/openjpeg/archive/v2.3.1.tar.gz",
        "filename": PILLOW_DEPENDS_DIR + "openjpeg-2.3.1.tar.gz",
        "dir": "openjpeg-2.3.1",
    },
    "jpeg-turbo": {
        "url": SF_MIRROR + "/project/libjpeg-turbo/2.0.3/libjpeg-turbo-2.0.3.tar.gz",
        "filename": PILLOW_DEPENDS_DIR + "libjpeg-turbo-2.0.3.tar.gz",
        "dir": "libjpeg-turbo-2.0.3",
    },
    # ba653c8: Merge tag '2.12.5' into msvc
    "imagequant": {
        "url": "https://github.com/ImageOptim/libimagequant/archive/ba653c8ccb34dde4e21c6076d85a72d21ed9d971.zip",  # noqa: E501
        "filename": PILLOW_DEPENDS_DIR
        + "libimagequant-ba653c8ccb34dde4e21c6076d85a72d21ed9d971.zip",
        "dir": "libimagequant-ba653c8ccb34dde4e21c6076d85a72d21ed9d971",
    },
    "harfbuzz": {
        "url": "https://github.com/harfbuzz/harfbuzz/archive/2.6.1.zip",
        "filename": PILLOW_DEPENDS_DIR + "harfbuzz-2.6.1.zip",
        "dir": "harfbuzz-2.6.1",
    },
    "fribidi": {
        "url": "https://github.com/fribidi/fribidi/archive/v1.0.7.zip",
        "filename": PILLOW_DEPENDS_DIR + "fribidi-1.0.7.zip",
        "dir": "fribidi-1.0.7",
    },
    "libraqm": {
        "url": "https://github.com/HOST-Oman/libraqm/archive/v0.7.0.zip",
        "filename": PILLOW_DEPENDS_DIR + "libraqm-0.7.0.zip",
        "dir": "libraqm-0.7.0",
    },
}

compilers = {
    7: {
        2010: {
            64: {
                "env_version": "v7.0",
                "vc_version": "2010",
                "env_flags": "/x64 /xp",
                "inc_dir": "msvcr90-x64",
                "platform": "x64",
                "webp_platform": "x64",
            },
            32: {
                "env_version": "v7.0",
                "vc_version": "2010",
                "env_flags": "/x86 /xp",
                "inc_dir": "msvcr90-x32",
                "platform": "Win32",
                "webp_platform": "x86",
            },
        }
    },
    7.1: {
        2015: {
            64: {
                "env_version": "v7.1",
                "vc_version": "2015",
                "env_flags": "/x64 /vista",
                "inc_dir": "msvcr10-x64",
                "platform": "x64",
                "webp_platform": "x64",
            },
            32: {
                "env_version": "v7.1",
                "vc_version": "2015",
                "env_flags": "/x86 /vista",
                "inc_dir": "msvcr10-x32",
                "platform": "Win32",
                "webp_platform": "x86",
            },
        }
    },
}


def pyversion_from_env():
    py = os.environ["PYTHON"]

    py_version = "27"
    for k in pythons:
        if k in py:
            py_version = k
            break

    if "64" in py:
        py_version = "%s%s" % (py_version, X64_EXT)

    return py_version


def compiler_from_env():
    py = os.environ["PYTHON"]

    for k, v in pythons.items():
        if k in py:
            py_info = v
            break

    bit = bit_from_env()
    return compilers[py_info["compiler"]][py_info["vc"]][bit]


def bit_from_env():
    py = os.environ["PYTHON"]

    return 64 if "64" in py else 32


def all_compilers():
    all = []
    for vc_compilers in compilers.values():
        for bit_compilers in vc_compilers.values():
            all += bit_compilers.values()
    return all
