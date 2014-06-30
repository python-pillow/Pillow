# Travis install
# source this script to run the install on travis OSX workers

# Get needed utilities
source terryfy/travis_tools.sh

# Package versions for fresh source builds
FT_VERSION="2.5.3"
PNG_VERSION="1.6.12"
JPEG_VERSION=9a
OPENJPEG_VERSION=2.0.0
TIFF_VERSION=4.0.3
LCMS_VERSION=2.6
WEBP_VERSION=0.4.0

# Compiler defaults
SYS_CC=clang
SYS_CXX=clang++
ARCH_FLAGS="-arch i386 -arch x86_64"
MACOSX_DEPLOYMENT_TARGET='10.6'


function check_version {
    if [ -z "$version" ]; then
        echo "Need version"
        exit 1
    fi
}


function check_var {
    if [ -z "$1" ]; then
        echo "Undefined required variable"
        exit 1
    fi
}


function init_vars {
    SRC_PREFIX=$PWD/working
    BUILD_PREFIX=$PWD/build
    export PATH=$BUILD_PREFIX/bin:$PATH
    export CPATH=$BUILD_PREFIX/include
    export LIBRARY_PATH=$BUILD_PREFIX/lib
    export PKG_CONFIG_PATH=$BUILD_PREFIX/lib/pkgconfig
}


function clean_builds {
    check_var $SRC_PREFIX
    check_var $BUILD_PREFIX
    rm -rf $SRC_PREFIX
    mkdir $SRC_PREFIX
    rm -rf $BUILD_PREFIX
    mkdir $BUILD_PREFIX
    cd Pillow
    git clean -fxd
    git reset --hard
    cd ..
}


function install_jpeg {
    check_var $JPEG_VERSION
    check_var $SRC_PREFIX
    check_var $BUILD_PREFIX
    local archive_path="archives/jpegsrc.v${JPEG_VERSION}.tar.gz"
    tar zxvf $archive_path -C $SRC_PREFIX
    cd $SRC_PREFIX/jpeg-$JPEG_VERSION
    require_success "Failed to cd to jpeg directory"
    CC=${SYS_CC} CXX=${SYS_CXX} CFLAGS=$ARCH_FLAGS ./configure --prefix=$BUILD_PREFIX
    make
    make install
    require_success "Failed to install jpeg $version"
    cd ../..
}


function install_openjpeg {
    check_var $OPENJPEG_VERSION
    check_var $SRC_PREFIX
    check_var $BUILD_PREFIX
    local archive_path="archives/openjpeg-${OPENJPEG_VERSION}.tar.gz"
    tar zxvf $archive_path -C $SRC_PREFIX
    cd $SRC_PREFIX/openjpeg-$OPENJPEG_VERSION
    require_success "Failed to cd to openjpeg directory"
    CC=${SYS_CC} CXX=${SYS_CXX} CFLAGS=$ARCH_FLAGS \
        CMAKE_INCLUDE_PATH=$CPATH \
        CMAKE_LIBRARY_PATH=$LIBRARY_PATH \
        cmake -DCMAKE_INSTALL_PREFIX:PATH=$BUILD_PREFIX .
    make
    make install
    require_success "Failed to install openjpeg $version"
    cd ../..
}


function install_tiff {
    check_var $TIFF_VERSION
    check_var $SRC_PREFIX
    check_var $BUILD_PREFIX
    local archive_path="archives/tiff-${TIFF_VERSION}.tar.gz"
    tar zxvf $archive_path -C $SRC_PREFIX
    cd $SRC_PREFIX/tiff-$TIFF_VERSION
    require_success "Failed to cd to tiff directory"
    CC=${SYS_CC} CXX=${SYS_CXX} CFLAGS=$ARCH_FLAGS ./configure --prefix=$BUILD_PREFIX
    make
    make install
    require_success "Failed to install tiff $version"
    cd ../..
}


function install_libpng {
    check_var $PNG_VERSION
    check_var $SRC_PREFIX
    check_var $BUILD_PREFIX
    local archive_path="archives/libpng-${PNG_VERSION}.tar.gz"
    tar zxvf $archive_path -C $SRC_PREFIX
    cd $SRC_PREFIX/libpng-$PNG_VERSION
    require_success "Failed to cd to png directory"
    CC=${SYS_CC} CXX=${SYS_CXX} CFLAGS=$ARCH_FLAGS ./configure --prefix=$BUILD_PREFIX
    make
    make install
    require_success "Failed to install png $version"
    cd ../..
}


function install_freetype {
    check_var $FT_VERSION
    check_var $SRC_PREFIX
    check_var $BUILD_PREFIX
    local archive_path="archives/freetype-${FT_VERSION}.tar.gz"
    tar zxvf $archive_path -C $SRC_PREFIX
    cd $SRC_PREFIX/freetype-$FT_VERSION
    require_success "Failed to cd to freetype directory"
    CC=${SYS_CC} CXX=${SYS_CXX} CFLAGS=$ARCH_FLAGS ./configure --prefix=$BUILD_PREFIX
    make
    make install
    require_success "Failed to install freetype $version"
    cd ../..
}


function install_lcms2 {
    check_var $LCMS_VERSION
    check_var $SRC_PREFIX
    check_var $BUILD_PREFIX
    local archive_path="archives/lcms2-${LCMS_VERSION}.tar.gz"
    tar zxvf $archive_path -C $SRC_PREFIX
    cd $SRC_PREFIX/lcms2-$LCMS_VERSION
    require_success "Failed to cd to lcms2 directory"
    CC=${SYS_CC} CXX=${SYS_CXX} CFLAGS=$ARCH_FLAGS ./configure --prefix=$BUILD_PREFIX
    make
    make install
    require_success "Failed to install lcms $version"
    cd ../..
}


function install_webp {
    check_var $WEBP_VERSION
    check_var $SRC_PREFIX
    check_var $BUILD_PREFIX
    local archive_path="archives/libwebp-${WEBP_VERSION}.tar.gz"
    tar zxvf $archive_path -C $SRC_PREFIX
    cd $SRC_PREFIX/libwebp-$WEBP_VERSION
    require_success "Failed to cd to libwebp directory"
    CC=${SYS_CC} CXX=${SYS_CXX} CFLAGS=$ARCH_FLAGS ./configure \
        --enable-libwebpmux \
        --enable-libwebpdemux \
        --prefix=$BUILD_PREFIX
    make
    make install
    require_success "Failed to install webp $version"
    cd ../..
}
