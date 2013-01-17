# About

Some simple Pillow demos

how to run

    [ -d image_resources ] || mkdir image_resources
    wget http://upload.wikimedia.org/wikipedia/commons/6/69/Captcha.jpg -O image_resources/captcha.jpg
    python crop/crop.py


## Build pillow on Ubuntu 12.04

    sudo apt-get install zlib1g-dev
    sudo apt-get install libjpeg8-dev
    sudo apt-get install libpng12-dev
    sudo apt-get install libfreetype6-dev
    sudo apt-get install liblcms1-dev
    sudo apt-get install python-setuptools
    python setup.py build


## Build it on Mac OS X 10.6.*

Build an egg for i386 with Python 2.5/Python 2.6

    export ARCHFLAGS="-arch i386"
    export CC="/usr/bin/gcc-4.0 -arch i386"

    python2.5 setup.py bdist_egg
    python2.6 setup.py bdist_egg

Build an egg for x86_64 with Python 2.7(install it via MacPorts)

    python setup.py bdist_egg


## Install it via package management system

HomeBrew is cool, you could use it instead of MacPorts on OS X.


## See also

PIL Handbook

 - http://www.pythonware.com/library/pil/handbook/index.htm


PIL Tutorial

 - http://www.pythonware.com/library/pil/handbook/introduction.htm
 - http://nadiana.com/category/pil
