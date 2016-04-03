#!/bin/sh

#
# Installs all of the dependencies for Pillow for Fedora 23
# for both system Pythons 2.7 and 3.4
#
# note that Fedora does ship packages for Pillow as python-pillow

# this is a workaround for 
# "gcc: error: /usr/lib/rpm/redhat/redhat-hardened-cc1: No such file or directory"
# errors when compiling.
sudo dnf install redhat-rpm-config

sudo dnf install python-devel python3-devel python-virtualenv make gcc

sudo dnf install libtiff-devel libjpeg-devel libzip-devel freetype-devel \
    lcms2-devel libwebp-devel openjpeg2-devel tkinter python3-tkinter \ 
    tcl-devel tk-devel