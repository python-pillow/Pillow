#!/bin/bash
# install openjpeg

archive=v2.5.4

./download-and-extract.sh $archive https://raw.githubusercontent.com/python-pillow/pillow-depends/main/$archive.tar.gz

pushd openjpeg-2.5.4

# Apply patches for OSV-2025-219 and CVE-2026-6192
# Pending release of https://github.com/uclouvain/openjpeg/pull/1621
# and https://github.com/uclouvain/openjpeg/pull/1628
patch -p0 < ../patches/$archive.tar.gz.patch

cmake -DCMAKE_INSTALL_PREFIX=/usr . && make -j4 && sudo make -j4 install

popd
