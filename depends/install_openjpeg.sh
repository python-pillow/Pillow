#!/bin/bash
# install openjpeg

archive=openjpeg-2.1.2
checksum=40a7bfdcc66280b3c1402a0eb1a27624

./download-and-extract.sh $archive https://raw.githubusercontent.com/python-pillow/pillow-depends/master/$archive.tar.gz $checksum

pushd $archive

cmake -DCMAKE_INSTALL_PREFIX=/usr . && make -j4 && sudo make -j4 install

popd
