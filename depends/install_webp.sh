#!/bin/bash
# install webp

if [ ! -f libwebp-0.4.3.tar.gz ]; then
    wget 'http://downloads.webmproject.org/releases/webp/libwebp-0.4.3.tar.gz'
fi

rm -r libwebp-0.4.3
tar -xvzf libwebp-0.4.3.tar.gz

pushd libwebp-0.4.3

./configure --prefix=/usr --enable-libwebpmux --enable-libwebpdemux && make -j4 && sudo make -j4 install

popd
