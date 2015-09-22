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
#
#  id: (Name, Type, Length, enum_values)
#
TAGS_V2 = {

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

    # MPInfo
    45056: ("MPFVersion", 7, 1),
    45057: ("NumberOfImages", 4, 1),
    45058: ("MPEntry", 7, 1),
    45059: ("ImageUIDList", 7, 0),
    45060: ("TotalFrames", 4, 1),
    45313: ("MPIndividualNum", 4, 1),
    45569: ("PanOrientation", 4, 1),
    45570: ("PanOverlap_H", 5, 1),
    45571: ("PanOverlap_V", 5, 1),
    45572: ("BaseViewpointNum", 4, 1),
    45573: ("ConvergenceAngle", 10, 1),
    45574: ("BaselineLength", 5, 1),
    45575: ("VerticalDivergence", 10, 1),
    45576: ("AxisDistance_X", 10, 1),
    45577: ("AxisDistance_Y", 10, 1),
    45578: ("AxisDistance_Z", 10, 1),
    45579: ("YawAngle", 10, 1),
    45580: ("PitchAngle", 10, 1),
    45581: ("RollAngle", 10, 1),

    50741: ("MakerNoteSafety", 3, 1, {"Unsafe": 0, "Safe": 1}),
    50780: ("BestQualityScale", 5, 1),
    50838: ("ImageJMetaDataByteCounts", 4, 1),
    50839: ("ImageJMetaData", 7, 1)
}

# Legacy Tags structure
# these tags aren't included above, but were in the previous versions
TAGS = {347: 'JPEGTables',
        700: 'XMP',

        # Additional Exif Info
        33434: 'ExposureTime',
        33437: 'FNumber',
        33723: 'IptcNaaInfo',
        34377: 'PhotoshopInfo',
        34675: 'ICCProfile',
        34850: 'ExposureProgram',
        34852: 'SpectralSensitivity',
        34853: 'GPSInfoIFD',
        34855: 'ISOSpeedRatings',
        34856: 'OECF',
        34864: 'SensitivityType',
        34865: 'StandardOutputSensitivity',
        34866: 'RecommendedExposureIndex',
        34867: 'ISOSpeed',
        34868: 'ISOSpeedLatitudeyyy',
        34869: 'ISOSpeedLatitudezzz',
        36864: 'ExifVersion',
        36867: 'DateTimeOriginal',
        36868: 'DateTImeDigitized',
        37121: 'ComponentsConfiguration',
        37122: 'CompressedBitsPerPixel',
        37377: 'ShutterSpeedValue',
        37378: 'ApertureValue',
        37379: 'BrightnessValue',
        37380: 'ExposureBiasValue',
        37381: 'MaxApertureValue',
        37382: 'SubjectDistance',
        37383: 'MeteringMode',
        37384: 'LightSource',
        37385: 'Flash',
        37386: 'FocalLength',
        37396: 'SubjectArea',
        37500: 'MakerNote',
        37510: 'UserComment',
        37520: 'SubSec',
        37521: 'SubSecTimeOriginal',
        37522: 'SubsecTimeDigitized',
        40960: 'FlashPixVersion',
        40961: 'ColorSpace',
        40962: 'PixelXDimension',
        40963: 'PixelYDimension',
        40964: 'RelatedSoundFile',
        40965: 'InteroperabilityIFD',
        41483: 'FlashEnergy',
        41484: 'SpatialFrequencyResponse',
        41486: 'FocalPlaneXResolution',
        41487: 'FocalPlaneYResolution',
        41488: 'FocalPlaneResolutionUnit',
        41492: 'SubjectLocation',
        41493: 'ExposureIndex',
        41495: 'SensingMethod',
        41728: 'FileSource',
        41729: 'SceneType',
        41730: 'CFAPattern',
        41985: 'CustomRendered',
        41986: 'ExposureMode',
        41987: 'WhiteBalance',
        41988: 'DigitalZoomRatio',
        41989: 'FocalLengthIn35mmFilm',
        41990: 'SceneCaptureType',
        41991: 'GainControl',
        41992: 'Contrast',
        41993: 'Saturation',
        41994: 'Sharpness',
        41995: 'DeviceSettingDescription',
        41996: 'SubjectDistanceRange',
        42016: 'ImageUniqueID',
        42032: 'CameraOwnerName',
        42033: 'BodySerialNumber',
        42034: 'LensSpecification',
        42035: 'LensMake',
        42036: 'LensModel',
        42037: 'LensSerialNumber',
        42240: 'Gamma',

        # Adobe DNG
        50706: 'DNGVersion',
        50707: 'DNGBackwardVersion',
        50708: 'UniqueCameraModel',
        50709: 'LocalizedCameraModel',
        50710: 'CFAPlaneColor',
        50711: 'CFALayout',
        50712: 'LinearizationTable',
        50713: 'BlackLevelRepeatDim',
        50714: 'BlackLevel',
        50715: 'BlackLevelDeltaH',
        50716: 'BlackLevelDeltaV',
        50717: 'WhiteLevel',
        50718: 'DefaultScale',
        50719: 'DefaultCropOrigin',
        50720: 'DefaultCropSize',
        50721: 'ColorMatrix1',
        50722: 'ColorMatrix2',
        50723: 'CameraCalibration1',
        50724: 'CameraCalibration2',
        50725: 'ReductionMatrix1',
        50726: 'ReductionMatrix2',
        50727: 'AnalogBalance',
        50728: 'AsShotNeutral',
        50729: 'AsShotWhiteXY',
        50730: 'BaselineExposure',
        50731: 'BaselineNoise',
        50732: 'BaselineSharpness',
        50733: 'BayerGreenSplit',
        50734: 'LinearResponseLimit',
        50735: 'CameraSerialNumber',
        50736: 'LensInfo',
        50737: 'ChromaBlurRadius',
        50738: 'AntiAliasStrength',
        50740: 'DNGPrivateData',
        50778: 'CalibrationIlluminant1',
        50779: 'CalibrationIlluminant2',
        }


def _populate():
    for k, v in TAGS_V2.items():
        # Populate legacy structure.
        TAGS[k] = v[0]
        if len(v) == 4:
            for sk, sv in v[3].items():
                TAGS[(k, sv)] = sk

        TAGS_V2[k] = TagInfo(k, *v)

_populate()
##
# Map type numbers to type names -- defined in ImageFileDirectory.

TYPES = {}

# was:
# TYPES = {
#     1: "byte",
#     2: "ascii",
#     3: "short",
#     4: "long",
#     5: "rational",
#     6: "signed byte",
#     7: "undefined",
#     8: "signed short",
#     9: "signed long",
#     10: "signed rational",
#     11: "float",
#     12: "double",
# }
