#!/bin/bash
# install openjpeg

archive=openjpeg-2.1.2

./download-and-extract.sh $archive https://github.com/python-pillow/pillow-depends/blob/master/$archive.tar.gz?raw=true

pushd $archive

cmake -DCMAKE_INSTALL_PREFIX=/usr . && make -j4 && sudo make -j4 install

popd
