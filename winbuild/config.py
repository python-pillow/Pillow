import os

SF_MIRROR = 'http://iweb.dl.sourceforge.net'
PILLOW_DEPENDS_DIR = 'C:\\pillow-depends\\'

pythons = {'27': {'compiler': 7, 'vc': 2008},
           'pypy2': {'compiler': 7, 'vc': 2008},
           '35': {'compiler': 7.1, 'vc': 2015},
           '36': {'compiler': 7.1, 'vc': 2015},
           '37': {'compiler': 7.1, 'vc': 2015}}

VIRT_BASE = "c:/vp/"
X64_EXT = os.environ.get('X64_EXT', "x64")

libs = {
    # 'openjpeg': {
    #     'filename': 'openjpeg-2.0.0-win32-x86.zip',
    #     'version': '2.0'
    # },
    'zlib': {
        'url': 'http://zlib.net/zlib1211.zip',
        'filename': PILLOW_DEPENDS_DIR + 'zlib1211.zip',
        'dir': 'zlib-1.2.11',
    },
    'jpeg': {
        'url': 'http://www.ijg.org/files/jpegsr9c.zip',
        'filename': PILLOW_DEPENDS_DIR + 'jpegsr9c.zip',
        'dir': 'jpeg-9c',
    },
    'tiff': {
        'url': 'ftp://download.osgeo.org/libtiff/tiff-4.0.10.tar.gz',
        'filename': PILLOW_DEPENDS_DIR + 'tiff-4.0.10.tar.gz',
        'dir': 'tiff-4.0.10',
    },
    'freetype': {
        'url': 'https://download.savannah.gnu.org/releases/freetype/freetype-2.10.0.tar.gz',  # noqa: E501
        'filename': PILLOW_DEPENDS_DIR + 'freetype-2.10.0.tar.gz',
        'dir': 'freetype-2.10.0',
    },
    'lcms': {
        'url': SF_MIRROR+'/project/lcms/lcms/2.7/lcms2-2.7.zip',
        'filename': PILLOW_DEPENDS_DIR + 'lcms2-2.7.zip',
        'dir': 'lcms2-2.7',
    },
    'ghostscript': {
        'url': 'https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs926/ghostscript-9.26.tar.gz',  # noqa: E501
        'filename': PILLOW_DEPENDS_DIR + 'ghostscript-9.26.tar.gz',
        'dir': 'ghostscript-9.26',
    },
    'tcl-8.5': {
        'url': SF_MIRROR+'/project/tcl/Tcl/8.5.19/tcl8519-src.zip',
        'filename': PILLOW_DEPENDS_DIR + 'tcl8519-src.zip',
        'dir': '',
    },
    'tk-8.5': {
        'url': SF_MIRROR+'/project/tcl/Tcl/8.5.19/tk8519-src.zip',
        'filename': PILLOW_DEPENDS_DIR + 'tk8519-src.zip',
        'dir': '',
        'version': '8.5.19',
    },
    'tcl-8.6': {
        'url': SF_MIRROR+'/project/tcl/Tcl/8.6.9/tcl869-src.zip',
        'filename': PILLOW_DEPENDS_DIR + 'tcl869-src.zip',
        'dir': '',
    },
    'tk-8.6': {
        'url': SF_MIRROR+'/project/tcl/Tcl/8.6.9/tk869-src.zip',
        'filename': PILLOW_DEPENDS_DIR + 'tk869-src.zip',
        'dir': '',
        'version': '8.6.9',
    },
    'webp': {
        'url': 'http://downloads.webmproject.org/releases/webp/libwebp-1.0.2.tar.gz',
        'filename': PILLOW_DEPENDS_DIR + 'libwebp-1.0.2.tar.gz',
        'dir': 'libwebp-1.0.2',
    },
    'openjpeg': {
        'url': SF_MIRROR+'/project/openjpeg/openjpeg/2.3.0/openjpeg-2.3.0.tar.gz',
        'filename': PILLOW_DEPENDS_DIR + 'openjpeg-2.3.0.tar.gz',
        'dir': 'openjpeg-2.3.0',
    },
}

compilers = {
    7: {
        2008: {
            64: {
                'env_version': 'v7.0',
                'vc_version': '2008',
                'env_flags': '/x64 /xp',
                'inc_dir': 'msvcr90-x64',
                'platform': 'x64',
                'webp_platform': 'x64',
            },
            32: {
                'env_version': 'v7.0',
                'vc_version': '2008',
                'env_flags': '/x86 /xp',
                'inc_dir': 'msvcr90-x32',
                'platform': 'Win32',
                'webp_platform': 'x86',
            }
        }
    },
    7.1: {
        2015: {
            64: {
                'env_version': 'v7.1',
                'vc_version': '2015',
                'env_flags': '/x64 /vista',
                'inc_dir': 'msvcr10-x64',
                'platform': 'x64',
                'webp_platform': 'x64',
            },
            32: {
                'env_version': 'v7.1',
                'vc_version': '2015',
                'env_flags': '/x86 /vista',
                'inc_dir': 'msvcr10-x32',
                'platform': 'Win32',
                'webp_platform': 'x86',
            }
        }
    }
}


def pyversion_from_env():
    py = os.environ['PYTHON']

    py_version = '27'
    for k in pythons:
        if k in py:
            py_version = k
            break

    if '64' in py:
        py_version = '%s%s' % (py_version, X64_EXT)

    return py_version


def compiler_from_env():
    py = os.environ['PYTHON']

    for k, v in pythons.items():
        if k in py:
            py_info = v
            break

    bit = bit_from_env()
    return compilers[py_info['compiler']][py_info['vc']][bit]


def bit_from_env():
    py = os.environ['PYTHON']

    return 64 if '64' in py else 32


def all_compilers():
    all = []
    for vc_compilers in compilers.values():
        for bit_compilers in vc_compilers.values():
            all += bit_compilers.values()
    return all
