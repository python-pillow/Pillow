from helper import unittest, PillowTestCase, hopper, py3

from PIL import Image, TiffImagePlugin


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
        # Read RGBa images from Mac OS X [@PIL136]

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

    def test_xyres_tiff(self):
        from PIL.TiffImagePlugin import X_RESOLUTION, Y_RESOLUTION
        filename = "Tests/images/pil168.tif"
        im = Image.open(filename)
        assert isinstance(im.tag.tags[X_RESOLUTION][0], tuple)
        assert isinstance(im.tag.tags[Y_RESOLUTION][0], tuple)
        # Try to read a file where X,Y_RESOLUTION are ints
        im.tag.tags[X_RESOLUTION] = (72,)
        im.tag.tags[Y_RESOLUTION] = (72,)
        im._setup()
        self.assertEqual(im.info['dpi'], (72., 72.))

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

        # Image.DEBUG = True
        im = Image.open('Tests/images/12bit.cropped.tif')

        # to make the target --
        # convert 12bit.cropped.tif -depth 16 tmp.tif
        # convert tmp.tif -evaluate RightShift 4 12in16bit2.tif
        # imagemagick will auto scale so that a 12bit FFF is 16bit FFF0,
        # so we need to unshift so that the integer values are the same.

        im2 = Image.open('Tests/images/12in16bit.tif')

        if Image.DEBUG:
            print (im.getpixel((0, 0)))
            print (im.getpixel((0, 1)))
            print (im.getpixel((0, 2)))

            print (im2.getpixel((0, 0)))
            print (im2.getpixel((0, 1)))
            print (im2.getpixel((0, 2)))

        self.assert_image_equal(im, im2)

    def test_32bit_float(self):
        # Issue 614, specific 32 bit float format
        path = 'Tests/images/10ct_32bit_128.tiff'
        im = Image.open(path)
        im.load()

        self.assertEqual(im.getpixel((0, 0)), -0.4526388943195343)
        self.assertEqual(
            im.getextrema(), (-3.140936851501465, 3.140684127807617))

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
        # Arrange
        filename = "Tests/images/pil136.tiff"
        im = Image.open(filename)

        # Act
        ret = str(im.ifd)

        # Assert
        self.assertIsInstance(ret, str)
        self.assertEqual(
            ret,
            '{256: (55,), 257: (43,), 258: (8, 8, 8, 8), 259: (1,), '
            '262: (2,), 296: (2,), 273: (8,), 338: (1,), 277: (4,), '
            '279: (9460,), 282: ((720000, 10000),), '
            '283: ((720000, 10000),), 284: (1,)}')

    def test__delitem__(self):
        # Arrange
        filename = "Tests/images/pil136.tiff"
        im = Image.open(filename)
        len_before = len(im.ifd.as_dict())

        # Act
        del im.ifd[256]

        # Assert
        len_after = len(im.ifd.as_dict())
        self.assertEqual(len_before, len_after + 1)

    def test_load_byte(self):
        # Arrange
        ifd = TiffImagePlugin.ImageFileDirectory()
        data = b"abc"

        # Act
        ret = ifd.load_byte(data)

        # Assert
        self.assertEqual(ret, b"abc")

    def test_load_string(self):
        # Arrange
        ifd = TiffImagePlugin.ImageFileDirectory()
        data = b"abc\0"

        # Act
        ret = ifd.load_string(data)

        # Assert
        self.assertEqual(ret, "abc")

    def test_load_float(self):
        # Arrange
        ifd = TiffImagePlugin.ImageFileDirectory()
        data = b"abcdabcd"

        # Act
        ret = ifd.load_float(data)

        # Assert
        self.assertEqual(ret, (1.6777999408082104e+22, 1.6777999408082104e+22))

    def test_load_double(self):
        # Arrange
        ifd = TiffImagePlugin.ImageFileDirectory()
        data = b"abcdefghabcdefgh"

        # Act
        ret = ifd.load_double(data)

        # Assert
        self.assertEqual(ret, (8.540883223036124e+194, 8.540883223036124e+194))

    def test_seek(self):
        # Arrange
        filename = "Tests/images/pil136.tiff"
        im = Image.open(filename)

        # Act
        im.seek(-1)

        # Assert
        self.assertEqual(im.tell(), 0)

    def test_seek_eof(self):
        # Arrange
        filename = "Tests/images/pil136.tiff"
        im = Image.open(filename)
        self.assertEqual(im.tell(), 0)

        # Act / Assert
        self.assertRaises(EOFError, lambda: im.seek(1))

    def test__cvt_res_int(self):
        # Arrange
        from PIL.TiffImagePlugin import _cvt_res
        value = 34

        # Act
        ret = _cvt_res(value)

        # Assert
        self.assertEqual(ret, (34, 1))

    def test__cvt_res_float(self):
        # Arrange
        from PIL.TiffImagePlugin import _cvt_res
        value = 22.3

        # Act
        ret = _cvt_res(value)

        # Assert
        self.assertEqual(ret, (1461452, 65536))

    def test__cvt_res_sequence(self):
        # Arrange
        from PIL.TiffImagePlugin import _cvt_res
        value = [0, 1]

        # Act
        ret = _cvt_res(value)

        # Assert
        self.assertEqual(ret, [0, 1])

    def test_4bit(self):
        # Arrange
        test_file = "Tests/images/hopper_gray_4bpp.tif"
        original = hopper("L")

        # Act
        im = Image.open(test_file)

        # Assert
        self.assertEqual(im.size, (128, 128))
        self.assertEqual(im.mode, "L")
        self.assert_image_similar(im, original, 7.3)

    def test_page_number_x_0(self):
        # Issue 973
        # Test TIFF with tag 297 (Page Number) having value of 0 0.
        # The first number is the current page number.
        # The second is the total number of pages, zero means not available.

        # Arrange
        outfile = self.tempfile("temp.tif")

        # Created by printing a page in Chrome to PDF, then:
        # /usr/bin/gs -q -sDEVICE=tiffg3 -sOutputFile=total-pages-zero.tif
        # -dNOPAUSE /tmp/test.pdf -c quit
        infile = "Tests/images/total-pages-zero.tif"
        im = Image.open(infile)

        # Act / Assert
        # Should not divide by zero
        im.save(outfile)

    def test_with_underscores(self):
        # Arrange: use underscores
        kwargs = {'resolution_unit': 'inch',
                  'x_resolution': 72,
                  'y_resolution': 36}
        filename = self.tempfile("temp.tif")

        # Act
        hopper("RGB").save(filename, **kwargs)

        # Assert
        from PIL.TiffImagePlugin import X_RESOLUTION, Y_RESOLUTION
        im = Image.open(filename)
        self.assertEqual(im.tag.tags[X_RESOLUTION][0][0], 72)
        self.assertEqual(im.tag.tags[Y_RESOLUTION][0][0], 36)

    def test_deprecation_warning_with_spaces(self):
        # Arrange: use spaces
        kwargs = {'resolution unit': 'inch',
                  'x resolution': 36,
                  'y resolution': 72}
        filename = self.tempfile("temp.tif")

        # Act
        self.assert_warning(DeprecationWarning,
                            lambda: hopper("RGB").save(filename, **kwargs))

        # Assert
        from PIL.TiffImagePlugin import X_RESOLUTION, Y_RESOLUTION
        im = Image.open(filename)
        self.assertEqual(im.tag.tags[X_RESOLUTION][0][0], 36)
        self.assertEqual(im.tag.tags[Y_RESOLUTION][0][0], 72)


if __name__ == '__main__':
    unittest.main()

# End of file
