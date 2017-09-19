#!/bin/sh

pacman -S --noconfirm mingw32/mingw-w64-i686-python3 \
	   mingw32/mingw-w64-i686-python3-pip \
	   mingw32/mingw-w64-i686-python3-setuptools \
	   mingw32/mingw-w64-i686-python2-pip \
	   mingw32/mingw-w64-i686-python2-setuptools \
	   mingw-w64-i686-libjpeg-turbo

/mingw32/bin/pip install nose olefile
/mingw32/bin/pip3 install nose olefile
