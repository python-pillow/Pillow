#!/usr/bin/env bash
# install raqm


archive=raqm-cmake-b517ba80

./download-and-extract.sh $archive https://raw.githubusercontent.com/python-pillow/pillow-depends/master/$archive.tar.gz

pushd $archive

mkdir build
cd build
cmake ..
make && sudo make install
cd ..

popd

