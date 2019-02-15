#!/bin/sh
# Usage: ./download-and-extract.sh something https://example.com/something.tar.gz

archive=$1
url=$2

if [ ! -f $archive.tar.gz ]; then
    wget -O $archive.tar.gz $url
fi

rm -r $archive
tar -xvzf $archive.tar.gz
