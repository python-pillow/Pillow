#!/bin/bash
# install webp

archive=libwebp-1.6.0

if [[ "$GHA_LIBWEBP_CACHE_HIT" == "true" ]]; then

    # Copy cached files into place
    sudo cp ~/cache-libwebp/lib/* /usr/lib/
    sudo cp -r ~/cache-libwebp/include/webp /usr/include/

else

    ./download-and-extract.sh $archive https://raw.githubusercontent.com/python-pillow/pillow-depends/main/$archive.tar.gz

    pushd $archive

    ./configure --prefix=/usr --enable-libwebpmux --enable-libwebpdemux && make -j4 && sudo make -j4 install

    if [ -n "$GITHUB_ACTIONS" ]; then
        # Copy to cache
        rm -rf ~/cache-libwebp
        mkdir -p ~/cache-libwebp/lib
        mkdir -p ~/cache-libwebp/include
        mkdir -p ~/cache-libwebp/pkgconfig
        cp /usr/lib/libwebp*.so* /usr/lib/libwebp*.a ~/cache-libwebp/lib/
        cp /usr/lib/libsharpyuv*.so* /usr/lib/libsharpyuv*.a ~/cache-libwebp/lib/
        cp -r /usr/include/webp ~/cache-libwebp/include/
    fi

    popd

fi
