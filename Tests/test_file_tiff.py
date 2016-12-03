from __future__ import print_function
import logging
from io import BytesIO
import struct

from helper import unittest, PillowTestCase, hopper, py3

from PIL import Image, TiffImagePlugin

logger = logging.getLogger(__name__)


class TestFileTiff(PillowTestCase):

    def test_sanity(self):

        filename = self.tempfile("temp.tif")

        hopper("RGB").save(filename)

        im = Image.open(filename)
        im.load()
        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "TIFF")

        hopper("1").save(filename)
        im = Image.open(filename)

        hopper("L").save(filename)
        im = Image.open(filename)

        hopper("P").save(filename)
        im = Image.open(filename)

        hopper("RGB").save(filename)
        im = Image.open(filename)

        hopper("I").save(filename)
        im = Image.open(filename)

    def test_mac_tiff(self):
        # Read RGBa images from macOS [@PIL136]

        filename = "Tests/images/pil136.tiff"
        im = Image.open(filename)

        self.assertEqual(im.mode, "RGBA")
        self.assertEqual(im.size, (55, 43))
        self.assertEqual(im.tile, [('raw', (0, 0, 55, 43), 8, ('RGBa', 0, 1))])
        im.load()

    def test_gimp_tiff(self):
        # Read TIFF JPEG images from GIMP [@PIL168]

        codecs = dir(Image.core)
        if "jpeg_decoder" not in codecs:
            self.skipTest("jpeg support not available")

        filename = "Tests/images/pil168.tif"
        im = Image.open(filename)

        self.assertEqual(im.mode, "RGB")
        self.assertEqual(im.size, (256, 256))
        self.assertEqual(
            im.tile, [
                ('jpeg', (0, 0, 256, 64), 8, ('RGB', '')),
                ('jpeg', (0, 64, 256, 128), 1215, ('RGB', '')),
                ('jpeg', (0, 128, 256, 192), 2550, ('RGB', '')),
                ('jpeg', (0, 192, 256, 256), 3890, ('RGB', '')),
                ])
        im.load()

    def test_sampleformat(self):
        # https://github.com/python-pillow/Pillow/issues/1466
        im = Image.open("Tests/images/copyleft.tiff")
        self.assertEqual(im.mode, 'RGB')

    def test_xyres_tiff(self):
        from PIL.TiffImagePlugin import X_RESOLUTION, Y_RESOLUTION
        filename = "Tests/images/pil168.tif"
        im = Image.open(filename)

        # legacy api
        self.assertIsInstance(im.tag[X_RESOLUTION][0], tuple)
        self.assertIsInstance(im.tag[Y_RESOLUTION][0], tuple)

        # v2 api
        self.assertIsInstance(im.tag_v2[X_RESOLUTION],
                              TiffImagePlugin.IFDRational)
        self.assertIsInstance(im.tag_v2[Y_RESOLUTION],
                              TiffImagePlugin.IFDRational)

        self.assertEqual(im.info['dpi'], (72., 72.))

    def test_int_resolution(self):
        from PIL.TiffImagePlugin import X_RESOLUTION, Y_RESOLUTION
        filename = "Tests/images/pil168.tif"
        im = Image.open(filename)

        # Try to read a file where X,Y_RESOLUTION are ints
        im.tag_v2[X_RESOLUTION] = 71
        im.tag_v2[Y_RESOLUTION] = 71
        im._setup()
        self.assertEqual(im.info['dpi'], (71., 71.))

    def test_save_setting_missing_resolution(self):
        from PIL.TiffImagePlugin import X_RESOLUTION, Y_RESOLUTION
        b = BytesIO()
        Image.open("Tests/images/10ct_32bit_128.tiff").save(
            b, format="tiff", resolution=123.45)
        im = Image.open(b)
        self.assertEqual(float(im.tag_v2[X_RESOLUTION]), 123.45)
        self.assertEqual(float(im.tag_v2[Y_RESOLUTION]), 123.45)

    def test_invalid_file(self):
        invalid_file = "Tests/images/flower.jpg"

        self.assertRaises(SyntaxError,
                          lambda: TiffImagePlugin.TiffImageFile(invalid_file))

        TiffImagePlugin.PREFIXES.append(b"\xff\xd8\xff\xe0")
        self.assertRaises(SyntaxError,
                          lambda: TiffImagePlugin.TiffImageFile(invalid_file))
        TiffImagePlugin.PREFIXES.pop()

    def test_bad_exif(self):
        i = Image.open('Tests/images/hopper_bad_exif.jpg')
        try:
            self.assert_warning(UserWarning, i._getexif)
        except struct.error:
            self.fail(
                "Bad EXIF data passed incorrect values to _binary unpack")

    def test_save_rgba(self):
        im = hopper("RGBA")
        outfile = self.tempfile("temp.tif")
        im.save(outfile)

    def test_save_unsupported_mode(self):
        im = hopper("HSV")
        outfile = self.tempfile("temp.tif")
        self.assertRaises(IOError, lambda: im.save(outfile))

    def test_little_endian(self):
        im = Image.open('Tests/images/16bit.cropped.tif')
        self.assertEqual(im.getpixel((0, 0)), 480)
        self.assertEqual(im.mode, 'I;16')

        b = im.tobytes()
        # Bytes are in image native order (little endian)
        if py3:
            self.assertEqual(b[0], ord(b'\xe0'))
            self.assertEqual(b[1], ord(b'\x01'))
        else:
            self.assertEqual(b[0], b'\xe0')
            self.assertEqual(b[1], b'\x01')

    def test_big_endian(self):
        im = Image.open('Tests/images/16bit.MM.cropped.tif')
        self.assertEqual(im.getpixel((0, 0)), 480)
        self.assertEqual(im.mode, 'I;16B')

        b = im.tobytes()

        # Bytes are in image native order (big endian)
        if py3:
            self.assertEqual(b[0], ord(b'\x01'))
            self.assertEqual(b[1], ord(b'\xe0'))
        else:
            self.assertEqual(b[0], b'\x01')
            self.assertEqual(b[1], b'\xe0')

    def test_12bit_rawmode(self):
        """ Are we generating the same interpretation
        of the image as Imagemagick is? """

        im = Image.open('Tests/images/12bit.cropped.tif')

        # to make the target --
        # convert 12bit.cropped.tif -depth 16 tmp.tif
        # convert tmp.tif -evaluate RightShift 4 12in16bit2.tif
        # imagemagick will auto scale so that a 12bit FFF is 16bit FFF0,
        # so we need to unshift so that the integer values are the same.

        im2 = Image.open('Tests/images/12in16bit.tif')

        logger.debug("%s", [img.getpixel((0, idx))
                            for img in [im, im2] for idx in range(3)])

        self.assert_image_equal(im, im2)

    def test_32bit_float(self):
        # Issue 614, specific 32-bit float format
        path = 'Tests/images/10ct_32bit_128.tiff'
        im = Image.open(path)
        im.load()

        self.assertEqual(im.getpixel((0, 0)), -0.4526388943195343)
        self.assertEqual(
            im.getextrema(), (-3.140936851501465, 3.140684127807617))

    def test_n_frames(self):
        im = Image.open('Tests/images/multipage-lastframe.tif')
        self.assertEqual(im.n_frames, 1)
        self.assertFalse(im.is_animated)

        im = Image.open('Tests/images/multipage.tiff')
        self.assertEqual(im.n_frames, 3)
        self.assertTrue(im.is_animated)

    def test_eoferror(self):
        im = Image.open('Tests/images/multipage-lastframe.tif')

        n_frames = im.n_frames
        while True:
            n_frames -= 1
            try:
                im.seek(n_frames)
                break
            except EOFError:
                self.assertTrue(im.tell() < n_frames)

    def test_multipage(self):
        # issue #862
        im = Image.open('Tests/images/multipage.tiff')
        # file is a multipage tiff: 10x10 green, 10x10 red, 20x20 blue

        im.seek(0)
        self.assertEqual(im.size, (10, 10))
        self.assertEqual(im.convert('RGB').getpixel((0, 0)), (0, 128, 0))

        im.seek(1)
        im.load()
        self.assertEqual(im.size, (10, 10))
        self.assertEqual(im.convert('RGB').getpixel((0, 0)), (255, 0, 0))

        im.seek(2)
        im.load()
        self.assertEqual(im.size, (20, 20))
        self.assertEqual(im.convert('RGB').getpixel((0, 0)), (0, 0, 255))

    def test_multipage_last_frame(self):
        im = Image.open('Tests/images/multipage-lastframe.tif')
        im.load()
        self.assertEqual(im.size, (20, 20))
        self.assertEqual(im.convert('RGB').getpixel((0, 0)), (0, 0, 255))

    def test___str__(self):
        filename = "Tests/images/pil136.tiff"
        im = Image.open(filename)

        # Act
        ret = str(im.ifd)

        # Assert
        self.assertIsInstance(ret, str)

    def test_as_dict_deprecation(self):
        # Arrange
        filename = "Tests/images/pil136.tiff"
        im = Image.open(filename)

        self.assert_warning(DeprecationWarning, im.tag_v2.as_dict)
        self.assert_warning(DeprecationWarning, im.tag.as_dict)
        self.assertEqual(dict(im.tag_v2), im.tag_v2.as_dict())
        self.assertEqual(dict(im.tag), im.tag.as_dict())

    def test_dict(self):
        # Arrange
        filename = "Tests/images/pil136.tiff"
        im = Image.open(filename)

        # v2 interface
        v2_tags = {256: 55, 257: 43, 258: (8, 8, 8, 8), 259: 1,
                   262: 2, 296: 2, 273: (8,), 338: (1,), 277: 4,
                   279: (9460,), 282: 72.0, 283: 72.0, 284: 1}
        self.assertEqual(dict(im.tag_v2), v2_tags)

        # legacy interface
        legacy_tags = {256: (55,), 257: (43,), 258: (8, 8, 8, 8), 259: (1,),
                       262: (2,), 296: (2,), 273: (8,), 338: (1,), 277: (4,),
                       279: (9460,), 282: ((720000, 10000),),
                       283: ((720000, 10000),), 284: (1,)}
        self.assertEqual(dict(im.tag), legacy_tags)

    def test__delitem__(self):
        filename = "Tests/images/pil136.tiff"
        im = Image.open(filename)
        len_before = len(dict(im.ifd))
        del im.ifd[256]
        len_after = len(dict(im.ifd))
        self.assertEqual(len_before, len_after + 1)

    def test_load_byte(self):
        for legacy_api in [False, True]:
            ifd = TiffImagePlugin.ImageFileDirectory_v2()
            data = b"abc"
            ret = ifd.load_byte(data, legacy_api)
            self.assertEqual(ret, b"abc")

    def test_load_string(self):
        ifd = TiffImagePlugin.ImageFileDirectory_v2()
        data = b"abc\0"
        ret = ifd.load_string(data, False)
        self.assertEqual(ret, "abc")

    def test_load_float(self):
        ifd = TiffImagePlugin.ImageFileDirectory_v2()
        data = b"abcdabcd"
        ret = ifd.load_float(data, False)
        self.assertEqual(ret, (1.6777999408082104e+22, 1.6777999408082104e+22))

    def test_load_double(self):
        ifd = TiffImagePlugin.ImageFileDirectory_v2()
        data = b"abcdefghabcdefgh"
        ret = ifd.load_double(data, False)
        self.assertEqual(ret, (8.540883223036124e+194, 8.540883223036124e+194))

    def test_seek(self):
        filename = "Tests/images/pil136.tiff"
        im = Image.open(filename)
        im.seek(-1)
        self.assertEqual(im.tell(), 0)

    def test_seek_eof(self):
        filename = "Tests/images/pil136.tiff"
        im = Image.open(filename)
        self.assertEqual(im.tell(), 0)
        self.assertRaises(EOFError, lambda: im.seek(1))

    def test__limit_rational_int(self):
        from PIL.TiffImagePlugin import _limit_rational
        value = 34
        ret = _limit_rational(value, 65536)
        self.assertEqual(ret, (34, 1))

    def test__limit_rational_float(self):
        from PIL.TiffImagePlugin import _limit_rational
        value = 22.3
        ret = _limit_rational(value, 65536)
        self.assertEqual(ret, (223, 10))

    def test_4bit(self):
        test_file = "Tests/images/hopper_gray_4bpp.tif"
        original = hopper("L")
        im = Image.open(test_file)
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.mode, "L")
        self.assert_image_similar(im, original, 7.3)

    def test_gray_semibyte_per_pixel(self):
        test_files = (
            (
                24.8,  # epsilon
                (  # group
                    "Tests/images/tiff_gray_2_4_bpp/hopper2.tif",
                    "Tests/images/tiff_gray_2_4_bpp/hopper2I.tif",
                    "Tests/images/tiff_gray_2_4_bpp/hopper2R.tif",
                    "Tests/images/tiff_gray_2_4_bpp/hopper2IR.tif",
                )
            ),
            (
                7.3,  # epsilon
                (  # group
                    "Tests/images/tiff_gray_2_4_bpp/hopper4.tif",
                    "Tests/images/tiff_gray_2_4_bpp/hopper4I.tif",
                    "Tests/images/tiff_gray_2_4_bpp/hopper4R.tif",
                    "Tests/images/tiff_gray_2_4_bpp/hopper4IR.tif",
                )
            ),
        )
        original = hopper("L")
        for epsilon, group in test_files:
            im = Image.open(group[0])
            self.assertEqual(im.size, (128, 128))
            self.assertEqual(im.mode, "L")
            self.assert_image_similar(im, original, epsilon)
            for file in group[1:]:
                im2 = Image.open(file)
                self.assertEqual(im2.size, (128, 128))
                self.assertEqual(im2.mode, "L")
                self.assert_image_equal(im, im2)

    def test_with_underscores(self):
        kwargs = {'resolution_unit': 'inch',
                  'x_resolution': 72,
                  'y_resolution': 36}
        filename = self.tempfile("temp.tif")
        hopper("RGB").save(filename, **kwargs)
        from PIL.TiffImagePlugin import X_RESOLUTION, Y_RESOLUTION
        im = Image.open(filename)

        # legacy interface
        self.assertEqual(im.tag[X_RESOLUTION][0][0], 72)
        self.assertEqual(im.tag[Y_RESOLUTION][0][0], 36)

        # v2 interface
        self.assertEqual(im.tag_v2[X_RESOLUTION], 72)
        self.assertEqual(im.tag_v2[Y_RESOLUTION], 36)

    def test_deprecation_warning_with_spaces(self):
        kwargs = {'resolution unit': 'inch',
                  'x resolution': 36,
                  'y resolution': 72}
        filename = self.tempfile("temp.tif")
        self.assert_warning(DeprecationWarning,
                            lambda: hopper("RGB").save(filename, **kwargs))
        from PIL.TiffImagePlugin import X_RESOLUTION, Y_RESOLUTION

        im = Image.open(filename)

        # legacy interface
        self.assertEqual(im.tag[X_RESOLUTION][0][0], 36)
        self.assertEqual(im.tag[Y_RESOLUTION][0][0], 72)

        # v2 interface
        self.assertEqual(im.tag_v2[X_RESOLUTION], 36)
        self.assertEqual(im.tag_v2[Y_RESOLUTION], 72)

    def test_lzw(self):
        # Act
        im = Image.open("Tests/images/hopper_lzw.tif")

        # Assert
        self.assertEqual(im.mode, 'RGB')
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.format, "TIFF")
        im2 = hopper()
        self.assert_image_similar(im, im2, 5)

    def test_roundtrip_tiff_uint16(self):
        # Test an image of all '0' values
        pixel_value = 0x1234
        infile = "Tests/images/uint16_1_4660.tif"
        im = Image.open(infile)
        self.assertEqual(im.getpixel((0, 0)), pixel_value)

        tmpfile = self.tempfile("temp.tif")
        im.save(tmpfile)

        reloaded = Image.open(tmpfile)

        self.assert_image_equal(im, reloaded)

    def test_tiff_save_all(self):
        import io
        import os

        mp = io.BytesIO()
        with Image.open("Tests/images/multipage.tiff") as im:
            im.save(mp, format="tiff", save_all=True)

        mp.seek(0, os.SEEK_SET)
        with Image.open(mp) as im:
            self.assertEqual(im.n_frames, 3)

    def test_saving_icc_profile(self):
        # Tests saving TIFF with icc_profile set.
        # At the time of writing this will only work for non-compressed tiffs
        # as libtiff does not support embedded ICC profiles, ImageFile._save(..)
        # however does.
        im = Image.new('RGB', (1, 1))
        im.info['icc_profile'] = 'Dummy value'
        
        # Try save-load round trip to make sure both handle icc_profile.
        tmpfile = self.tempfile('temp.tif')
        im.save(tmpfile, 'TIFF', compression='raw')
        reloaded = Image.open(tmpfile)
        
        self.assertEqual(b'Dummy value', reloaded.info['icc_profile'])


if __name__ == '__main__':
    unittest.main()
