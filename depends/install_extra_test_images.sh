#!/bin/bash
# install extra test images

rm -rf test_images

# Use SVN to just fetch a single Git subdirectory
svn_checkout()
{
	if [ ! -z $1 ]; then
		echo ""
		echo "Retrying svn checkout..."
		echo ""
	fi

	svn checkout https://github.com/python-pillow/pillow-depends/trunk/test_images
}
svn_checkout || svn_checkout retry || svn_checkout retry || svn_checkout retry

cp -r test_images/* ../Tests/images
