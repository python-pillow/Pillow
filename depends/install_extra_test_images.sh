#!/bin/bash
# install extra test images

if [ ! -f test_images.tar.gz ]; then
    wget -O 'test_images.tar.gz' 'https://github.com/python-pillow/pillow-depends/blob/master/test_images.tar.gz?raw=true'
fi

rm -r test_images
tar -xvzf test_images.tar.gz

cp -r test_images/* ../Tests/images
