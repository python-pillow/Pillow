#!/bin/sh

#
# Installs all of the dependencies for Pillow for Freebsd 10.x
# for both system Pythons 2.7 and 3.4
#
sudo pkg install python2 python3 py27-pip py27-virtualenv py27-setuptools27

# Openjpeg fails badly using the openjpeg package.
# I can't find a python3.4 version of tkinter
sudo pkg install jpeg-turbo tiff webp lcms2 freetype2 py27-tkinter
