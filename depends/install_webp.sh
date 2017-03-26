#!/bin/bash
# install webp

archive=libwebp-0.6.0
checksum=19a6e926ab1721268df03161b84bb4a0

./download-and-extract.sh $archive https://raw.githubusercontent.com/python-pillow/pillow-depends/master/$archive.tar.gz $checksum

pushd $archive

./configure --prefix=/usr --enable-libwebpmux --enable-libwebpdemux && make -j4 && sudo make -j4 install

popd
