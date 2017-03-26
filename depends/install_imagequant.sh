#!/bin/bash
# install libimagequant

archive=libimagequant-2.9.0
checksum=00dfab880c76928a01c4b9524256bda5

./download-and-extract.sh $archive https://raw.githubusercontent.com/python-pillow/pillow-depends/master/$archive.tar.gz $checksum

pushd $archive

make shared
sudo cp libimagequant.so* /usr/lib/
sudo cp libimagequant.h /usr/include/

popd
