# Resources About PIL

PIL Handbook

 - http://www.pythonware.com/library/pil/handbook/index.htm


PIL Tutorial

 - http://www.pythonware.com/library/pil/handbook/introduction.htm
 - http://nadiana.com/category/pil


## Images used in These Demos


http://www.cs.cmu.edu/~chuck/lennapg/

    wget http://www.cs.cmu.edu/~chuck/lennapg/lena_std.tif -O image_resources/lena_std.tif
    wget http://www.cs.cmu.edu/~chuck/lennapg/len_std.jpg -O image_resources/len_std.jpg


## Build it on Mac OS X 10.6.8

Build an egg for i386 with Python 2.5/Python 2.6

    export ARCHFLAGS="-arch i386"
    export CC="/usr/bin/gcc-4.0 -arch i386"

    python2.5 setup.py bdist_egg
    python2.6 setup.py bdist_egg

Build an egg for x86_64 with Python 2.7(install it via MacPorts)

    python setup.py bdist_egg


## Install it via Package Management System

HomeBrew is cool, you could use it instead of MacPorts on OS X.
