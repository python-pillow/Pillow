#!/usr/bin/env python

#
# Shows how to scan a color image into a PIL rgb-image
#

# Get the path set up to find PIL modules if not installed yet:
import sys ; sys.path.append('../PIL')

import sane
print 'SANE version:', sane.init()
print 'Available devices=', sane.get_devices()

s = sane.open(sane.get_devices()[0][0])

s.mode = 'color'
s.br_x=320. ; s.br_y=240.

print 'Device parameters:', s.get_parameters()

# Initiate the scan
s.start()

# Get an Image object
# (For my B&W QuickCam, this is a grey-scale image.  Other scanning devices
#  may return a
im=s.snap()

# Write the image out as a GIF file
#im.save('foo.gif')

# The show method() simply saves the image to a temporary file and calls "xv".
im.show()
