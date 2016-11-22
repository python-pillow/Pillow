#!/bin/bash
# install openjpeg


if [ ! -f openjpeg-2.1.2.tar.gz ]; then
    wget -O 'openjpeg-2.1.2.tar.gz' 'https://github.com/python-pillow/pillow-depends/blob/master/openjpeg-2.1.2.tar.gz?raw=true'

fi

rm -r openjpeg-2.1.2
tar -xvzf openjpeg-2.1.2.tar.gz


pushd openjpeg-2.1.2

cmake -DCMAKE_INSTALL_PREFIX=/usr . && make -j4 && sudo make -j4 install

popd

