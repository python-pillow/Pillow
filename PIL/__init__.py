#
# The Python Imaging Library.
# $Id$
#
# package placeholder
#
# Copyright (c) 1999 by Secret Labs AB.
#
# See the README file for information on usage and redistribution.
#

# ;-)

VERSION = '1.1.7'  # PIL version
PILLOW_VERSION = '3.5.0.dev0'  # Pillow

__version__ = PILLOW_VERSION

_plugins = [
    #core
    'JpegImagePlugin',
    'PngImagePlugin',
    'GifImagePlugin',
    'BmpImagePlugin',
    'PpmImagePlugin',
    'TiffImagePlugin',
    'WebPImagePlugin',
    'Jpeg2KImagePlugin',

    #non-core
    'BufrStubImagePlugin',
    'CurImagePlugin',
    'DcxImagePlugin',
    'DdsImagePlugin',
    'EpsImagePlugin',
    'FitsStubImagePlugin',
    'FliImagePlugin',
    'FpxImagePlugin',
    'FtexImagePlugin',
    'GbrImagePlugin',
    'GribStubImagePlugin',
    'Hdf5StubImagePlugin',
    'IcnsImagePlugin',
    'IcoImagePlugin',
    'McIdasImagePlugin',
    'MicImagePlugin',
    'MpoImagePlugin',
    'MspImagePlugin',
    'PalmImagePlugin',
    'PcdImagePlugin',
    'PcxImagePlugin',
    'PdfImagePlugin',
    'PixarImagePlugin',
    'PsdImagePlugin',
    'SgiImagePlugin',
    'SunImagePlugin',
    'WmfImagePlugin',
    'XbmImagePlugin',
    'XpmImagePlugin',
    'XVThumbImagePlugin'
    #no _accept function
    'ImImagePlugin',
    'ImtImagePlugin',
    'IptcImagePlugin',
    'MpegImagePlugin',
    'SpiderImagePlugin',
    'TgaImagePlugin',
    ]
