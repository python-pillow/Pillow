#!/bin/bash
# install extra test images

rm -rf test_images

# Use SVN to just fetch a single Git subdirectory
svn checkout https://github.com/python-pillow/pillow-depends/trunk/test_images

cp -r test_images/* ../Tests/images
