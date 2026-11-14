#!/usr/bin/env bash
set -eo pipefail

version=1.4.2

PREFIX=/usr
if [ $(uname) == "Darwin" ]; then
    if [ -x "$(command -v brew)" ]; then
        PREFIX=$(brew --prefix)
    fi
    LIBDIR=$PREFIX/lib
    LIBGLOB="libavif*.dylib"
else
    LIBDIR=/usr/lib/x86_64-linux-gnu
    LIBGLOB="libavif.so*"
fi

if [[ "$GHA_LIBAVIF_CACHE_HIT" == "true" ]]; then

    # Copy cached files into place
    sudo cp ~/cache-libavif/lib/* $LIBDIR/
    sudo mkdir -p $PREFIX/include/avif
    sudo cp ~/cache-libavif/include/avif/* $PREFIX/include/avif/

else

    ./download-and-extract.sh libavif-$version https://github.com/AOMediaCodec/libavif/archive/refs/tags/v$version.tar.gz

    pushd libavif-$version

    PKGCONFIG=${PKGCONFIG:-pkg-config}

    LIBAVIF_CMAKE_FLAGS=()
    HAS_DECODER=0
    HAS_ENCODER=0

    if $PKGCONFIG --exists aom; then
        LIBAVIF_CMAKE_FLAGS+=(-DAVIF_CODEC_AOM=SYSTEM)
        HAS_ENCODER=1
        HAS_DECODER=1
    fi

    if $PKGCONFIG --exists dav1d; then
        LIBAVIF_CMAKE_FLAGS+=(-DAVIF_CODEC_DAV1D=SYSTEM)
        HAS_DECODER=1
    fi

    if $PKGCONFIG --exists libgav1; then
        LIBAVIF_CMAKE_FLAGS+=(-DAVIF_CODEC_LIBGAV1=SYSTEM)
        HAS_DECODER=1
    fi

    if $PKGCONFIG --exists rav1e; then
        LIBAVIF_CMAKE_FLAGS+=(-DAVIF_CODEC_RAV1E=SYSTEM)
        HAS_ENCODER=1
    fi

    if $PKGCONFIG --exists SvtAv1Enc; then
        LIBAVIF_CMAKE_FLAGS+=(-DAVIF_CODEC_SVT=SYSTEM)
        HAS_ENCODER=1
    fi

    if [ "$HAS_ENCODER" != 1 ] || [ "$HAS_DECODER" != 1 ]; then
        LIBAVIF_CMAKE_FLAGS+=(-DAVIF_CODEC_AOM=LOCAL)
    fi

    cmake \
        -DCMAKE_INSTALL_PREFIX=$PREFIX \
        -DCMAKE_INSTALL_NAME_DIR=$PREFIX/lib \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_MACOSX_RPATH=OFF \
        -DAVIF_LIBSHARPYUV=LOCAL \
        -DAVIF_LIBYUV=LOCAL \
        "${LIBAVIF_CMAKE_FLAGS[@]}" \
        .

    sudo make install

    if [ -n "$GITHUB_ACTIONS" ]; then
        # Copy to cache
        rm -rf ~/cache-libavif
        mkdir -p ~/cache-libavif/lib
        mkdir -p ~/cache-libavif/include
        cp $LIBDIR/$LIBGLOB ~/cache-libavif/lib/
        cp -r $PREFIX/include/avif ~/cache-libavif/include/
    fi

    popd

fi
