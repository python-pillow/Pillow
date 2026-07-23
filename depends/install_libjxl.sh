#!/bin/bash

version=0.11.2

./download-and-extract.sh highway-1.3.0 https://github.com/google/highway/archive/1.3.0.tar.gz

pushd highway-1.3.0
cmake .
make -j4 install
popd

./download-and-extract.sh libjxl-$version https://github.com/libjxl/libjxl/archive/v$version.tar.gz

pushd libjxl-$version
cmake -DCMAKE_INSTALL_PREFIX=/usr -DJPEGXL_ENABLE_SJPEG=OFF -DJPEGXL_ENABLE_SKCMS=OFF -DBUILD_TESTING=OFF .
make -j4 install
popd
