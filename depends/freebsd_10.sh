#!/bin/sh

#
# Installs all of the dependencies for Pillow for Freebsd 10.x
# for both system Pythons 2.7 and 3.4
#
sudo pkg install python2 python3 py27-pip py27-virtualenv wget cmake

# Openjpeg fails badly using the openjpeg package.
# I can't find a python3.4 version of tkinter
sudo pkg install jpeg-turbo tiff webp lcms2 freetype2 harfbuzz fribidi py27-tkinter

./install_raqm_cmake.sh
