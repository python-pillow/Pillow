#!/bin/bash
# install webp

archive=libwebp-0.5.2

./download-and-extract.sh $archive https://github.com/python-pillow/pillow-depends/blob/master/$archive.tar.gz?raw=true

pushd $archive

./configure --prefix=/usr --enable-libwebpmux --enable-libwebpdemux && make -j4 && sudo make -j4 install

popd
