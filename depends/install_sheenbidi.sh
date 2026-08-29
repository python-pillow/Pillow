#!/usr/bin/env bash
# install sheenbidi

version=3.0.0

archive=SheenBidi-$version

./download-and-extract.sh $archive https://github.com/Tehreer/SheenBidi/archive/refs/tags/v$version.tar.gz

pushd $archive

meson setup build --prefix=/usr && ninja -C build install

popd
