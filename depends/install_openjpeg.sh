#!/bin/bash
# install openjpeg


if [ ! -f openjpeg-2.1.0.tar.gz ]; then
    wget 'http://iweb.dl.sourceforge.net/project/openjpeg.mirror/2.1.0/openjpeg-2.1.0.tar.gz'

fi

rm -r openjpeg-2.1.0
tar -xvzf openjpeg-2.1.0.tar.gz


pushd openjpeg-2.1.0

cmake -DCMAKE_INSTALL_PREFIX=/usr . && make -j4 && sudo make -j4 install

popd

