# Resources about PIL

PIL Handbook
http://www.pythonware.com/library/pil/handbook/index.htm

python 简单图像处理 series, ￥lan￥
http://www.cnblogs.com/xianglan/archive/2010/12/25/1916953.html

PIL 学习笔记 series, Neil Chen
http://www.cnblogs.com/RChen/archive/2007/03/31/pil_1.html


## Build it on Mac OS X 10.6.8

Build an egg for i386 with Python 2.5/Python 2.6

    export ARCHFLAGS="-arch i386"
    export CC="/usr/bin/gcc-4.0 -arch i386"

    python2.5 setup.py bdist_egg
    python2.6 setup.py bdist_egg

Build an egg for x86_64 with Python 2.7(install it via MacPorts)

    python setup.py bdist_egg

## Install it via Package Mangement System

HomeBrew is cool, you could use it instaed of MacPorts on OS X.
