#!/usr/bin/env bash
# install raqm


archive=raqm-0.2.0

./download-and-extract.sh $archive https://raw.githubusercontent.com/python-pillow/pillow-depends/master/$archive.tar.gz

pushd $archive

./configure --prefix=/usr && make -j4 && sudo make -j4 install

popd

