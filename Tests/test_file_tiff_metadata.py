from __future__ import division

from helper import unittest, PillowTestCase, hopper

from PIL import Image, TiffImagePlugin, TiffTags

tag_ids = dict((info.name, info.value) for info in TiffTags.TAGS.values())


class TestFileTiffMetadata(PillowTestCase):

    def test_rt_metadata(self):
        """ Test writing arbitrary metadata into the tiff image directory
            Use case is ImageJ private tags, one numeric, one arbitrary
            data.  https://github.com/python-pillow/Pillow/issues/291
            """

        img = hopper()

        basetextdata = "This is some arbitrary metadata for a text field"
        textdata = basetextdata + " \xff" 
        reloaded_textdata = basetextdata.encode('ascii') + b" ?"
        floatdata = 12.345
        doubledata = 67.89
        info = TiffImagePlugin.ImageFileDirectory()

        info[tag_ids['ImageJMetaDataByteCounts']] = len(reloaded_textdata)
        info[tag_ids['ImageJMetaData']] = textdata
        info[tag_ids['RollAngle']] = floatdata
        info.tagtype[tag_ids['RollAngle']] = 11
        info[tag_ids['YawAngle']] = doubledata
        info.tagtype[tag_ids['YawAngle']] = 12

        print(info.tagtype)

        f = self.tempfile("temp.tif")

        img.save(f, tiffinfo=info)

        loaded = Image.open(f)

        self.assertEqual(loaded.tag[50838], (len(reloaded_textdata),))
        self.assertEqual(loaded.tag_v2[50838], len(reloaded_textdata))

        self.assertEqual(loaded.tag[50839], reloaded_textdata)
        self.assertEqual(loaded.tag_v2[50839], reloaded_textdata)


        loaded_float = loaded.tag[tag_ids['RollAngle']][0]
        self.assertAlmostEqual(loaded_float, floatdata, places=5)
        loaded_double = loaded.tag[tag_ids['YawAngle']][0]
        self.assertAlmostEqual(loaded_double, doubledata)


    def test_read_metadata(self):
        img = Image.open('Tests/images/hopper_g4.tif')

        self.assertEqual({'YResolution': 4294967295 / 113653537,
                          'PlanarConfiguration': 1,
                          'BitsPerSample': (1,),
                          'ImageLength': 128,
                          'Compression': 4,
                          'FillOrder': 1,
                          'RowsPerStrip': 128,
                          'ResolutionUnit': 3,
                          'PhotometricInterpretation': 0,
                          'PageNumber': (0, 1),
                          'XResolution': 4294967295 / 113653537,
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

        original = img.tag.named()
        reloaded = loaded.tag.named()

        ignored = [
            'StripByteCounts', 'RowsPerStrip', 'PageNumber', 'StripOffsets']

        for tag, value in reloaded.items():
            if tag not in ignored:
                self.assertEqual(
                    original[tag], value, "%s didn't roundtrip" % tag)

        for tag, value in original.items():
            if tag not in ignored:
                self.assertEqual(
                    value, reloaded[tag], "%s didn't roundtrip" % tag)

    def test_no_duplicate_50741_tag(self):
        self.assertEqual(tag_ids['MakerNoteSafety'], 50741)
        self.assertEqual(tag_ids['BestQualityScale'], 50780)


if __name__ == '__main__':
    unittest.main()

# End of file
