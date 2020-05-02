#!/bin/bash
# install extra test images

# Use SVN to just fetch a single Git subdirectory
svn_export()
{
    if [ ! -z $1 ]; then
        echo ""
        echo "Retrying svn export..."
        echo ""
    fi

    svn export --force https://github.com/python-pillow/pillow-depends/trunk/test_images ../Tests/images
}
svn_export || svn_export retry || svn_export retry || svn_export retry
