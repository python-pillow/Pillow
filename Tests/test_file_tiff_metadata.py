from helper import unittest, PillowTestCase, hopper

from PIL import Image, TiffImagePlugin, TiffTags

tag_ids = dict(zip(TiffTags.TAGS.values(), TiffTags.TAGS.keys()))


class TestFileTiffMetadata(PillowTestCase):

    def test_rt_metadata(self):
        """ Test writing arbitrary metadata into the tiff image directory
            Use case is ImageJ private tags, one numeric, one arbitrary
            data.  https://github.com/python-pillow/Pillow/issues/291
            """

        img = hopper()

        textdata = "This is some arbitrary metadata for a text field"
        info = TiffImagePlugin.ImageFileDirectory()

        info[tag_ids['ImageJMetaDataByteCounts']] = len(textdata)
        info[tag_ids['ImageJMetaData']] = textdata

        f = self.tempfile("temp.tif")

        img.save(f, tiffinfo=info)

        loaded = Image.open(f)

        self.assertEqual(loaded.tag[50838], (len(textdata),))
        self.assertEqual(loaded.tag[50839], textdata)

    def test_read_metadata(self):
        img = Image.open('Tests/images/hopper_g4.tif')

        known = {'YResolution': ((4294967295, 113653537),),
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
                 'StripOffsets': (8,),
                 }

        # self.assertEqual is equivalent,
        # but less helpful in telling what's wrong.
        named = img.tag.named()
        for tag, value in named.items():
            self.assertEqual(known[tag], value)

        for tag, value in known.items():
            self.assertEqual(value, named[tag])

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
