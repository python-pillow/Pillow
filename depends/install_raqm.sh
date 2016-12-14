#!/bin/bash
# install raqm


if [ ! -f raqm-0.2.0.tar.gz ]; then
    wget -O 'raqm-0.2.0.tar.gz' 'https://github.com/HOST-Oman/libraqm/releases/download/v0.2.0/raqm-0.2.0.tar.gz?raw=true'

fi

rm -r raqm-0.2.0
tar -xvzf raqm-0.2.0.tar.gz


pushd raqm-0.2.0

./configure --prefix=/usr && make -j4 && sudo make -j4 install

popd

