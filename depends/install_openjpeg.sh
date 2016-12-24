#!/bin/bash
# install openjpeg

archive=openjpeg-2.1.2

./download-and-extract.sh $archive https://raw.githubusercontent.com/python-pillow/pillow-depends/master/$archive.tar.gz

pushd $archive

cmake -DCMAKE_INSTALL_PREFIX=/usr . && make -j4 && sudo make -j4 install

popd
