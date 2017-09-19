import os

SF_MIRROR = 'http://iweb.dl.sourceforge.net'
PILLOW_DEPENDS_DIR = 'C:\\pillow-depends\\'

pythons = {  # '26': 7,
           '27': 7,
           'pypy2': 7,
           # '32': 7,
           '33': 7.1,
           '34': 7.1}

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
        'url': 'http://www.ijg.org/files/jpegsr9b.zip',
        'filename': PILLOW_DEPENDS_DIR + 'jpegsr9b.zip',
        'dir': 'jpeg-9b',
    },
    'tiff': {
        'url': 'ftp://download.osgeo.org/libtiff/tiff-4.0.8.zip',
        'filename': PILLOW_DEPENDS_DIR + 'tiff-4.0.8.zip',
        'dir': 'tiff-4.0.8',
    },
    'freetype': {
        'url': 'https://download.savannah.gnu.org/releases/freetype/freetype-2.8.1.tar.gz',
        'filename': PILLOW_DEPENDS_DIR + 'freetype-2.8.1.tar.gz',
        'dir': 'freetype-2.8.1',
    },
    'lcms': {
        'url': SF_MIRROR+'/project/lcms/lcms/2.7/lcms2-2.7.zip',
        'filename': PILLOW_DEPENDS_DIR + 'lcms2-2.7.zip',
        'dir': 'lcms2-2.7',
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
        'url': SF_MIRROR+'/project/tcl/Tcl/8.6.7/tcl867-src.zip',
        'filename': PILLOW_DEPENDS_DIR + 'tcl867-src.zip',
        'dir': '',
    },
    'tk-8.6': {
        'url': SF_MIRROR+'/project/tcl/Tcl/8.6.7/tk867-src.zip',
        'filename': PILLOW_DEPENDS_DIR + 'tk867-src.zip',
        'dir': '',
        'version': '8.6.7',
    },
    'webp': {
        'url': 'http://downloads.webmproject.org/releases/webp/libwebp-0.6.0.tar.gz',
        'filename': PILLOW_DEPENDS_DIR + 'libwebp-0.6.0.tar.gz',
        'dir': 'libwebp-0.6.0',
    },
    'openjpeg': {
        'url': SF_MIRROR+'/project/openjpeg/openjpeg/2.2.0/openjpeg-2.2.0.tar.gz',
        'filename': PILLOW_DEPENDS_DIR + 'openjpeg-2.2.0.tar.gz',
        'dir': 'openjpeg-2.2.0',
    },
}

compilers = {
    (7, 64): {
        'env_version': 'v7.0',
        'vc_version': '2008',
        'env_flags': '/x64 /xp',
        'inc_dir': 'msvcr90-x64',
        'platform': 'x64',
        'webp_platform': 'x64',
    },
    (7, 32): {
        'env_version': 'v7.0',
        'vc_version': '2008',
        'env_flags': '/x86 /xp',
        'inc_dir': 'msvcr90-x32',
        'platform': 'Win32',
        'webp_platform': 'x86',
    },
    (7.1, 64): {
        'env_version': 'v7.1',
        'vc_version': '2010',
        'env_flags': '/x64 /vista',
        'inc_dir': 'msvcr10-x64',
        'platform': 'x64',
        'webp_platform': 'x64',
    },
    (7.1, 32): {
        'env_version': 'v7.1',
        'vc_version': '2010',
        'env_flags': '/x86 /vista',
        'inc_dir': 'msvcr10-x32',
        'platform': 'Win32',
        'webp_platform': 'x86',
    },
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
            compiler_version = v
            break

    bit = 32
    if '64' in py:
        bit = 64

    return compilers[(compiler_version, bit)]
