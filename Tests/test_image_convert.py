from helper import unittest, PillowTestCase, hopper

from PIL import Image


class TestImageConvert(PillowTestCase):

    def test_sanity(self):

        def convert(im, mode):
            out = im.convert(mode)
            self.assertEqual(out.mode, mode)
            self.assertEqual(out.size, im.size)

        modes = "1", "L", "I", "F", "RGB", "RGBA", "RGBX", "CMYK", "YCbCr"

        for mode in modes:
            im = hopper(mode)
            for mode in modes:
                convert(im, mode)

            # Check 0
            im = Image.new(mode, (0,0))
            for mode in modes:
                convert(im, mode)
                  
    def test_default(self):

        im = hopper("P")
        self.assert_image(im, "P", im.size)
        im = im.convert()
        self.assert_image(im, "RGB", im.size)
        im = im.convert()
        self.assert_image(im, "RGB", im.size)

    # ref https://github.com/python-pillow/Pillow/issues/274

    def _test_float_conversion(self, im):
        orig = im.getpixel((5, 5))
        converted = im.convert('F').getpixel((5, 5))
        self.assertEqual(orig, converted)

    def test_8bit(self):
        im = Image.open('Tests/images/hopper.jpg')
        self._test_float_conversion(im.convert('L'))

    def test_16bit(self):
        im = Image.open('Tests/images/16bit.cropped.tif')
        self._test_float_conversion(im)

    def test_16bit_workaround(self):
        im = Image.open('Tests/images/16bit.cropped.tif')
        self._test_float_conversion(im.convert('I'))

    def test_rgba_p(self):
        im = hopper('RGBA')
        im.putalpha(hopper('L'))

        converted = im.convert('P')
        comparable = converted.convert('RGBA')

        self.assert_image_similar(im, comparable, 20)

    def test_trns_p(self):
        im = hopper('P')
        im.info['transparency'] = 0

        f = self.tempfile('temp.png')

        l = im.convert('L')
        self.assertEqual(l.info['transparency'], 0)  # undone
        l.save(f)

        rgb = im.convert('RGB')
        self.assertEqual(rgb.info['transparency'], (0, 0, 0))  # undone
        rgb.save(f)

    # ref https://github.com/python-pillow/Pillow/issues/664

    def test_trns_p_rgba(self):
        # Arrange
        im = hopper('P')
        im.info['transparency'] = 128

        # Act
        rgba = im.convert('RGBA')

        # Assert
        self.assertNotIn('transparency', rgba.info)

    def test_trns_l(self):
        im = hopper('L')
        im.info['transparency'] = 128

        f = self.tempfile('temp.png')

        rgb = im.convert('RGB')
        self.assertEqual(rgb.info['transparency'], (128, 128, 128))  # undone
        rgb.save(f)

        p = im.convert('P')
        self.assertIn('transparency', p.info)
        p.save(f)

        p = self.assert_warning(
            UserWarning,
            lambda: im.convert('P', palette=Image.ADAPTIVE))
        self.assertNotIn('transparency', p.info)
        p.save(f)

    def test_trns_RGB(self):
        im = hopper('RGB')
        im.info['transparency'] = im.getpixel((0, 0))

        f = self.tempfile('temp.png')

        l = im.convert('L')
        self.assertEqual(l.info['transparency'], l.getpixel((0, 0)))  # undone
        l.save(f)

        p = im.convert('P')
        self.assertIn('transparency', p.info)
        p.save(f)

        p = self.assert_warning(
            UserWarning,
            lambda: im.convert('P', palette=Image.ADAPTIVE))
        self.assertNotIn('transparency', p.info)
        p.save(f)

    def test_p_la(self):
        im = hopper('RGBA')
        alpha = hopper('L')
        im.putalpha(alpha)

        comparable = im.convert('P').convert('LA').split()[1]

        self.assert_image_similar(alpha, comparable, 5)


if __name__ == '__main__':
    unittest.main()
