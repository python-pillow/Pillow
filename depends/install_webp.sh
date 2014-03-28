#!/bin/bash
# install webp


if [ ! -f libwebp-0.4.0.tar.gz ]; then
    wget 'https://webp.googlecode.com/files/libwebp-0.4.0.tar.gz'
fi

rm -r libwebp-0.4.0
tar -xvzf libwebp-0.4.0.tar.gz


pushd libwebp-0.4.0 

./configure --prefix=/usr --enable-libwebpmux --enable-libwebpdemux && make && sudo make install

popd

