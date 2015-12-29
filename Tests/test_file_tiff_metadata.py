from __future__ import division

import io
import struct

from helper import unittest, PillowTestCase, hopper

from PIL import Image, TiffImagePlugin, TiffTags
from PIL.TiffImagePlugin import _limit_rational, IFDRational

tag_ids = dict((info.name, info.value) for info in TiffTags.TAGS_V2.values())


class TestFileTiffMetadata(PillowTestCase):

    def test_rt_metadata(self):
        """ Test writing arbitrary metadata into the tiff image directory
            Use case is ImageJ private tags, one numeric, one arbitrary
            data.  https://github.com/python-pillow/Pillow/issues/291
            """

        img = hopper()

        # Behaviour change: re #1416
        # Pre ifd rewrite, ImageJMetaData was being written as a string(2),
        # Post ifd rewrite, it's defined as arbitrary bytes(7). It should
        # roundtrip with the actual bytes, rather than stripped text
        # of the premerge tests.
        #
        # For text items, we still have to decode('ascii','replace') because
        # the tiff file format can't take 8 bit bytes in that field.

        basetextdata = "This is some arbitrary metadata for a text field"
        bindata = basetextdata.encode('ascii') + b" \xff"
        textdata = basetextdata + " " + chr(255)
        reloaded_textdata = basetextdata + " ?"
        floatdata = 12.345
        doubledata = 67.89
        info = TiffImagePlugin.ImageFileDirectory()

        ImageJMetaData = tag_ids['ImageJMetaData']
        ImageJMetaDataByteCounts = tag_ids['ImageJMetaDataByteCounts']
        ImageDescription = tag_ids['ImageDescription']

        info[ImageJMetaDataByteCounts] = len(bindata)
        info[ImageJMetaData] = bindata
        info[tag_ids['RollAngle']] = floatdata
        info.tagtype[tag_ids['RollAngle']] = 11
        info[tag_ids['YawAngle']] = doubledata
        info.tagtype[tag_ids['YawAngle']] = 12

        info[ImageDescription] = textdata

        f = self.tempfile("temp.tif")

        img.save(f, tiffinfo=info)

        loaded = Image.open(f)

        self.assertEqual(loaded.tag[ImageJMetaDataByteCounts], (len(bindata),))
        self.assertEqual(loaded.tag_v2[ImageJMetaDataByteCounts], len(bindata))

        self.assertEqual(loaded.tag[ImageJMetaData], bindata)
        self.assertEqual(loaded.tag_v2[ImageJMetaData], bindata)

        self.assertEqual(loaded.tag[ImageDescription], (reloaded_textdata,))
        self.assertEqual(loaded.tag_v2[ImageDescription], reloaded_textdata)

        loaded_float = loaded.tag[tag_ids['RollAngle']][0]
        self.assertAlmostEqual(loaded_float, floatdata, places=5)
        loaded_double = loaded.tag[tag_ids['YawAngle']][0]
        self.assertAlmostEqual(loaded_double, doubledata)

    def test_read_metadata(self):
        img = Image.open('Tests/images/hopper_g4.tif')

        self.assertEqual({'YResolution': IFDRational(4294967295, 113653537),
                          'PlanarConfiguration': 1,
                          'BitsPerSample': (1,),
                          'ImageLength': 128,
                          'Compression': 4,
                          'FillOrder': 1,
                          'RowsPerStrip': 128,
                          'ResolutionUnit': 3,
                          'PhotometricInterpretation': 0,
                          'PageNumber': (0, 1),
                          'XResolution': IFDRational(4294967295, 113653537),
                          'ImageWidth': 128,
                          'Orientation': 1,
                          'StripByteCounts': (1968,),
                          'SamplesPerPixel': 1,
                          'StripOffsets': (8,)
                          }, img.tag_v2.named())

        self.assertEqual({'YResolution': ((4294967295, 113653537),),
                          'PlanarConfiguration': (1,),
                          'BitsPerSample': (1,),
                          'ImageLength': (128,),
                          'Compression': (4,),
                          'FillOrder': (1,),
                          'RowsPerStrip': (128,),
                          'ResolutionUnit': (3,),
                          'PhotometricInterpretation': (0,),
                          'PageNumber': (0, 1),
                          'XResolution': ((4294967295, 113653537),),
                          'ImageWidth': (128,),
                          'Orientation': (1,),
                          'StripByteCounts': (1968,),
                          'SamplesPerPixel': (1,),
                          'StripOffsets': (8,)
                          }, img.tag.named())

    def test_write_metadata(self):
        """ Test metadata writing through the python code """
        img = Image.open('Tests/images/hopper.tif')

        f = self.tempfile('temp.tiff')
        img.save(f, tiffinfo=img.tag)

        loaded = Image.open(f)

        original = img.tag_v2.named()
        reloaded = loaded.tag_v2.named()

        for k,v in original.items():
            if type(v) == IFDRational:
                original[k] = IFDRational(*_limit_rational(v,2**31))
            if type(v) == tuple and \
                type(v[0]) == IFDRational:
                original[k] = tuple([IFDRational(
                                      *_limit_rational(elt, 2**31)) for elt in v])

        ignored = ['StripByteCounts', 'RowsPerStrip',
                   'PageNumber', 'StripOffsets']

        for tag, value in reloaded.items():
            if tag in ignored: continue
            if (type(original[tag]) == tuple
                and type(original[tag][0]) == IFDRational):
                # Need to compare element by element in the tuple,
                # not comparing tuples of object references
                self.assert_deep_equal(original[tag],
                                       value,
                                       "%s didn't roundtrip, %s, %s" %
                                       (tag, original[tag], value))
            else:
                self.assertEqual(original[tag],
                                 value,
                                 "%s didn't roundtrip, %s, %s" %
                                 (tag, original[tag], value))

        for tag, value in original.items():
            if tag not in ignored:
                self.assertEqual(
                    value, reloaded[tag], "%s didn't roundtrip" % tag)

    def test_no_duplicate_50741_tag(self):
        self.assertEqual(tag_ids['MakerNoteSafety'], 50741)
        self.assertEqual(tag_ids['BestQualityScale'], 50780)

    def test_empty_metadata(self):
        f = io.BytesIO(b'II*\x00\x08\x00\x00\x00')
        head = f.read(8)
        info = TiffImagePlugin.ImageFileDirectory(head)
        try:
            self.assert_warning(UserWarning, lambda: info.load(f))
        except struct.error:
            self.fail("Should not be struct errors there.")

    def test_iccprofile(self):
        # https://github.com/python-pillow/Pillow/issues/1462
        im = Image.open('Tests/images/hopper.iccprofile.tif')
        out = self.tempfile('temp.tiff')

        im.save(out)
        reloaded = Image.open(out)
        self.assert_(type(im.info['icc_profile']) is not type(tuple))
        self.assertEqual(im.info['icc_profile'], reloaded.info['icc_profile'])

    def test_iccprofile_binary(self):
        # https://github.com/python-pillow/Pillow/issues/1526
        # We should be able to load this, but probably won't be able to save it.

        im = Image.open('Tests/images/hopper.iccprofile_binary.tif')
        self.assertEqual(im.tag_v2.tagtype[34675], 1)
        self.assertTrue(im.info['icc_profile'])

    def test_exif_div_zero(self):
        im = hopper()
        info = TiffImagePlugin.ImageFileDirectory_v2()
        info[41988] = TiffImagePlugin.IFDRational(0,0)

        out = self.tempfile('temp.tiff')
        im.save(out, tiffinfo=info, compression='raw')

        reloaded = Image.open(out)
        self.assertEqual(0, reloaded.tag_v2[41988][0].numerator)
        self.assertEqual(0, reloaded.tag_v2[41988][0].denominator)




if __name__ == '__main__':
    unittest.main()

# End of file
