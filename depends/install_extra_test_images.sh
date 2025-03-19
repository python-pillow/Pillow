#!/usr/bin/env bash
# install extra test images

archive=test-images-main

./download-and-extract.sh $archive https://github.com/python-pillow/test-images/archive/main.tar.gz

mv $archive/* ../Tests/images/

# Cleanup old tarball and empty directory
rm $archive.tar.gz
rmdir $archive
