# Define custom utilities
# Test for OSX with [ -n "$IS_OSX" ]

# Package versions for fresh source builds
FREETYPE_VERSION=2.6.4
LIBPNG_VERSION=1.6.23
ZLIB_VERSION=1.2.8
JPEG_VERSION=9b
OPENJPEG_VERSION=2.1
TIFF_VERSION=4.0.6
LCMS2_VERSION=2.8
LIBWEBP_VERSION=0.5.1

function pre_build {
    # Any stuff that you need to do before you start building the wheels
    # Runs in the root directory of this repository.
    if [ -n "$IS_OSX" ]; then
        # Update to latest zlib for OSX build
        build_new_zlib
    else  # Linux tests may depend on specific versions
        FREETYPE_VERSION=2.6.3
    fi
    build_jpeg
    build_tiff
    build_libpng
    build_openjpeg
    if [ -n "$IS_OSX" ]; then
        # Fix openjpeg library install id
        # https://code.google.com/p/openjpeg/issues/detail?id=367
        install_name_tool -id $BUILD_PREFIX/lib/libopenjp2.7.dylib $BUILD_PREFIX/lib/libopenjp2.2.1.0.dylib
    fi
    build_lcms2
    build_libwebp
    if [ -n "$IS_OSX" ]; then
        # Custom freetype build
        local ft_name_ver=freetype-${FREETYPE_VERSION}
        fetch_unpack http://download.savannah.gnu.org/releases/freetype/${ft_name_ver}.tar.gz
        (cd $ft_name_ver \
            && ./configure --prefix=$BUILD_PREFIX "--with-harfbuzz=no" \
            && make && make install)
    else
        build_freetype
    fi
}

function run_tests_in_repo {
    # Run Pillow tests from within source repo
    if [ -f test-installed.py ]; then
        python test-installed.py -s -v Tests/test_*.py
    else
        python Tests/run.py --installed
    fi
}

EXP_CODECS="jpg jpg_2000 libtiff zlib"
EXP_MODULES="freetype2 littlecms2 pil tkinter webp"

function run_tests {
    # Runs tests on installed distribution from an empty directory
    export NOSE_PROCESS_TIMEOUT=600
    export NOSE_PROCESSES=0
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
