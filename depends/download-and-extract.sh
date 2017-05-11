#!/bin/bash
# Usage: ./download-and-extract.sh something.tar.gz https://example.com/something.tar.gz

archive=$1
url=$2
checksum=$3

if [ ! -f $archive.tar.gz ]; then
    wget -O $archive.tar.gz $url
fi

if ! verify=$(echo "$checksum  $archive.tar.gz" | md5sum -c -); then
    echo $archive "checksum failed to verify"
    exit 1
fi

rm -r $archive
tar -xvzf $archive.tar.gz
