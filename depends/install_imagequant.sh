#!/bin/bash
# install libimagequant

archive=pngquant-2.6.0

./download-and-extract.sh $archive https://github.com/python-pillow/pillow-depends/blob/master/$archive.tar.gz?raw=true

pushd $archive

make -C lib shared
sudo cp lib/libimagequant.so* /usr/lib/
sudo cp lib/libimagequant.h /usr/include/

popd
