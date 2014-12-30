#
# The Python Imaging Library.
# $Id$
#
# TIFF tags
#
# This module provides clear-text names for various well-known
# TIFF tags.  the TIFF codec works just fine without it.
#
# Copyright (c) Secret Labs AB 1999.
#
# See the README file for information on usage and redistribution.
#

##
# This module provides constants and clear-text names for various
# well-known TIFF tags.
##

from collections import namedtuple

class TagInfo(namedtuple("_TagInfo", "value name type length enum")):
    __slots__ = []

    def __new__(cls, value=None, name="unknown", type=4, length=0, enum=None):
        return super(TagInfo, cls).__new__(
            cls, value, name, type, length, enum or {})

    def cvt_enum(self, value):
        return self.enum.get(value, value)

##
# Map tag numbers to tag info.

TAGS = {

    254: ("NewSubfileType", 4, 1),
    255: ("SubfileType", 3, 1),
    256: ("ImageWidth", 4, 1),
    257: ("ImageLength", 4, 1),
    258: ("BitsPerSample", 3, 0),
    259: ("Compression", 3, 1,
          {"Uncompressed": 1, "CCITT 1d": 2, "Group 3 Fax": 3, "Group 4 Fax": 4,
           "LZW": 5, "JPEG": 6, "PackBits": 32773}),

    262: ("PhotometricInterpretation", 3, 1,
          {"WhiteIsZero": 0, "BlackIsZero": 1, "RGB": 2, "RBG Palette": 3,
           "Transparency Mask": 4, "CMYK": 5, "YCbCr": 6, "CieLAB": 8,
           "CFA": 32803,  # TIFF/EP, Adobe DNG
           "LinearRaw": 32892}),  # Adobe DNG
    263: ("Thresholding", 3, 1),
    264: ("CellWidth", 3, 1),
    265: ("CellHeight", 3, 1),
    266: ("FillOrder", 3, 1),
    269: ("DocumentName", 2, 1),

    270: ("ImageDescription", 2, 1),
    271: ("Make", 2, 1),
    272: ("Model", 2, 1),
    273: ("StripOffsets", 4, 0),
    274: ("Orientation", 3, 1),
    277: ("SamplesPerPixel", 3, 1),
    278: ("RowsPerStrip", 4, 1),
    279: ("StripByteCounts", 4, 0),

    280: ("MinSampleValue", 4, 0),
    281: ("MaxSampleValue", 3, 0),
    282: ("XResolution", 5, 1),
    283: ("YResolution", 5, 1),
    284: ("PlanarConfiguration", 3, 1, {"Contigous": 1, "Separate": 2}),
    285: ("PageName", 2, 1),
    286: ("XPosition", 5, 1),
    287: ("YPosition", 5, 1),
    288: ("FreeOffsets", 4, 1),
    289: ("FreeByteCounts", 4, 1),

    290: ("GrayResponseUnit", 3, 1),
    291: ("GrayResponseCurve", 3, 0),
    292: ("T4Options", 4, 1),
    293: ("T6Options", 4, 1),
    296: ("ResolutionUnit", 3, 1, {"inch": 1, "cm": 2}),
    297: ("PageNumber", 3, 2),

    301: ("TransferFunction", 3, 0),
    305: ("Software", 2, 1),
    306: ("DateTime", 2, 1),

    315: ("Artist", 2, 1),
    316: ("HostComputer", 2, 1),
    317: ("Predictor", 3, 1),
    318: ("WhitePoint", 5, 2),
    319: ("PrimaryChromaticies", 3, 6),

    320: ("ColorMap", 3, 0),
    321: ("HalftoneHints", 3, 2),
    322: ("TileWidth", 4, 1),
    323: ("TileLength", 4, 1),
    324: ("TileOffsets", 4, 0),
    325: ("TileByteCounts", 4, 0),

    332: ("InkSet", 3, 1),
    333: ("InkNames", 2, 1),
    334: ("NumberOfInks", 3, 1),
    336: ("DotRange", 3, 0),
    337: ("TargetPrinter", 2, 1),
    338: ("ExtraSamples", 1, 0),
    339: ("SampleFormat", 3, 0),

    340: ("SMinSampleValue", 12, 0),
    341: ("SMaxSampleValue", 12, 0),
    342: ("TransferRange", 3, 6),

    # obsolete JPEG tags
    512: ("JPEGProc", 3, 1),
    513: ("JPEGInterchangeFormat", 4, 1),
    514: ("JPEGInterchangeFormatLength", 4, 1),
    515: ("JPEGRestartInterval", 3, 1),
    517: ("JPEGLosslessPredictors", 3, 0),
    518: ("JPEGPointTransforms", 3, 0),
    519: ("JPEGQTables", 4, 0),
    520: ("JPEGDCTables", 4, 0),
    521: ("JPEGACTables", 4, 0),

    529: ("YCbCrCoefficients", 5, 3),
    530: ("YCbCrSubSampling", 3, 2),
    531: ("YCbCrPositioning", 3, 1),
    532: ("ReferenceBlackWhite", 4, 0),

    33432: ("Copyright", 2, 1),

    # FIXME add more tags here
    34665: ("ExifIFD", 3, 1),
    50741: ("MakerNoteSafety", 3, 1, {0: "Unsafe", 1: "Safe"}),
    50780: ("BestQualityScale", 5, 1),
    50838: ("ImageJMetaDataByteCounts", 4, 1),
    50839: ("ImageJMetaData", 7, 1)
}


for k, v in TAGS.items():
    TAGS[k] = TagInfo(k, *v)
del k, v


##
# Map type numbers to type names -- defined in ImageFileDirectory.

TYPES = {}
