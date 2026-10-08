#!/bin/bash
# install openjpeg

archive=openjpeg-2.5.4

./download-and-extract.sh $archive https://raw.githubusercontent.com/python-pillow/pillow-depends/main/$archive.tar.gz

pushd $archive

# Apply patch for OSV-2025-219
# Pending release of https://github.com/uclouvain/openjpeg/pull/1621
patch -p1 < ../patches/openjpeg-2.5.4.tar.gz.patch

cmake -DCMAKE_INSTALL_PREFIX=/usr . && make -j4 && sudo make -j4 install

popd
