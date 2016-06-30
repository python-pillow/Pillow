# Script for building Pillow dependencies on OSX
source terryfy/library_installers.sh

# Compiler
export CC=clang
export CXX=clang++

# Package versions for fresh source builds
FT_VERSION=2.6.3
PNG_VERSION=1.6.23
ZLIB_VERSION=1.2.8
JPEG_VERSION=9b
OPENJPEG_VERSION=2.1.0
TIFF_VERSION=4.0.6
LCMS_VERSION=2.7
WEBP_VERSION=0.5.0

# Need cmake for openjpeg
brew install cmake
# Need pkg-config for freetype to find libpng
brew install pkg-config
# Set up build
clean_builds
clean_submodule Pillow
standard_install zlib $ZLIB_VERSION .tar.xz
standard_install jpeg $JPEG_VERSION .tar.gz jpegsrc.v
standard_install tiff $TIFF_VERSION
standard_install libpng $PNG_VERSION
standard_install lcms2 $LCMS_VERSION
WEBP_EXTRAS="--enable-libwebpmux --enable-libwebpdemux"
standard_install libwebp $WEBP_VERSION .tar.gz libwebp- "$WEBP_EXTRAS"
standard_install openjpeg $OPENJPEG_VERSION .tar.gz openjpeg- cmake
# Fix openjpeg library install id
# https://code.google.com/p/openjpeg/issues/detail?id=367
install_name_tool -id $PWD/build/lib/libopenjp2.7.dylib build/lib/libopenjp2.2.1.0.dylib
standard_install freetype $FT_VERSION .tar.gz freetype- "--with-harfbuzz=no"
