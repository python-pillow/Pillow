#!/bin/sh

#
# Installs all of the dependencies for Pillow for Fedora 23
# for both system Pythons 2.7 and 3.4
#

# this is a workaround for 
# "gcc: error: /usr/lib/rpm/redhat/redhat-hardened-cc1: No such file or directory"
# errors when compiling.
sudo yum install redhat-rpm-config

sudo yum install python-devel python3-devel python-virtualenv make gcc

# Note, I can't find a python2-tkinter package
sudo yum install libtiff-devel libjpeg-devel libzip-devel freetype-devel \
    lcms2-devel libwebp-devel openjpeg2-devel python3-tkinter tcl-devel tk-devel