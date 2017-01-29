#!/bin/bash
# install webp

archive=libwebp-0.5.2

./download-and-extract.sh $archive https://raw.githubusercontent.com/python-pillow/pillow-depends/master/$archive.tar.gz

pushd $archive

./configure --prefix=/usr --enable-libwebpmux --enable-libwebpdemux && make -j4 && sudo make -j4 install

popd
