# Define custom utilities
# Test for OSX with [ -n "$IS_OSX" ]

ARCHIVE_SDIR=pillow-depends-master

# Package versions for fresh source builds
FREETYPE_VERSION=2.10.1
LIBPNG_VERSION=1.6.37
ZLIB_VERSION=1.2.11
JPEG_VERSION=9d
OPENJPEG_VERSION=2.3.1
XZ_VERSION=5.2.4
TIFF_VERSION=4.1.0
LCMS2_VERSION=2.9
GIFLIB_VERSION=5.1.4
LIBWEBP_VERSION=1.1.0
BZIP2_VERSION=1.0.8

function pre_build {
    # Any stuff that you need to do before you start building the wheels
    # Runs in the root directory of this repository.
    curl -fsSL -o pillow-depends-master.zip https://github.com/python-pillow/pillow-depends/archive/master.zip
    untar pillow-depends-master.zip
    if [ -n "$IS_OSX" ]; then
        # Update to latest zlib for OSX build
        build_new_zlib
    fi
    
    # Custom flags to include both multibuild and jpeg defaults
    ORIGINAL_CFLAGS=$CFLAGS
    CFLAGS="$CFLAGS -g -O2"
    build_jpeg
    CFLAGS=$ORIGINAL_CFLAGS
    
    build_tiff
    build_libpng
    build_openjpeg
    build_lcms2

    if [ -n "$IS_OSX" ]; then
        # Custom flags to allow building on OS X 10.10 and 10.11
        build_giflib
        
        ORIGINAL_CPPFLAGS=$CPPFLAGS
        CPPFLAGS=""
    fi
    CFLAGS="$CFLAGS -O3 -DNDEBUG"
    build_libwebp
    CFLAGS=$ORIGINAL_CFLAGS
    if [ -n "$IS_OSX" ]; then
        CPPFLAGS=$ORIGINAL_CPPFLAGS
    fi

    # freetype
    freetype_args=""
    if [ -n "$IS_OSX" ]; then
        freetype_args="--with-harfbuzz=no"
    else
        # bzip2
        fetch_unpack https://sourceware.org/pub/bzip2/bzip2-${BZIP2_VERSION}.tar.gz
        (cd bzip2-${BZIP2_VERSION} \
            && make -f Makefile-libbz2_so \
            && make install PREFIX=$BUILD_PREFIX)
    fi
    build_simple freetype $FREETYPE_VERSION https://download.savannah.gnu.org/releases/freetype tar.gz $freetype_args
}

function run_tests_in_repo {
    # Run Pillow tests from within source repo
    python selftest.py
    pytest
}

EXP_CODECS="jpg jpg_2000 libtiff zlib"
EXP_MODULES="freetype2 littlecms2 pil tkinter webp"

function run_tests {
    # Runs tests on installed distribution from an empty directory
    (cd ../Pillow && run_tests_in_repo)
    # Show supported codecs and modules
    local codecs=$(python -c 'from PIL.features import *; print(" ".join(sorted(get_supported_codecs())))')
    # Test against expected codecs and modules
    local ret=0
    if [ "$codecs" != "$EXP_CODECS" ]; then
        echo "Codecs should be: '$EXP_CODECS'; but are '$codecs'"
        ret=1
    fi
    local modules=$(python -c 'from PIL.features import *; print(" ".join(sorted(get_supported_modules())))')
    if [ "$modules" != "$EXP_MODULES" ]; then
        echo "Modules should be: '$EXP_MODULES'; but are '$modules'"
        ret=1
    fi
    return $ret
}
