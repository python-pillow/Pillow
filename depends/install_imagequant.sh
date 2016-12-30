#!/bin/bash
# install libimagequant

archive=pngquant-2.8.2

./download-and-extract.sh $archive https://raw.githubusercontent.com/python-pillow/pillow-depends/master/$archive.tar.gz

pushd $archive

make -C lib shared
sudo cp lib/libimagequant.so* /usr/lib/
sudo cp lib/libimagequant.h /usr/include/

popd
