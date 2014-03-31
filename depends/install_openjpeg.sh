#!/bin/bash
# install openjpeg


if [ ! -f openjpeg-2.0.0.tar.gz ]; then
    wget 'https://openjpeg.googlecode.com/files/openjpeg-2.0.0.tar.gz' 
fi

rm -r openjpeg-2.0.0
tar -xvzf openjpeg-2.0.0.tar.gz


pushd openjpeg-2.0.0 

cmake -DCMAKE_INSTALL_PREFIX=/usr . && make && sudo make install

popd

