#!/bin/sh
# Usage: ./download-and-extract.sh something https://example.com/something.tar.gz

archive=$1
url=$2

if [ ! -f $archive.tar.gz ]; then
    wget -O $archive.tar.gz $url \
        --no-verbose \
        --retry-connrefused \
        --retry-on-http-error=429,503,504
fi

rmdir $archive
tar -xvzf $archive.tar.gz
