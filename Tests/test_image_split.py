from helper import unittest, PillowTestCase, hopper

from PIL import Image


class TestImageSplit(PillowTestCase):

    def test_split(self):
        def split(mode):
            layers = hopper(mode).split()
            return [(i.mode, i.size[0], i.size[1]) for i in layers]
        self.assertEqual(split("1"), [('1', 128, 128)])
        self.assertEqual(split("L"), [('L', 128, 128)])
        self.assertEqual(split("I"), [('I', 128, 128)])
        self.assertEqual(split("F"), [('F', 128, 128)])
        self.assertEqual(split("P"), [('P', 128, 128)])
        self.assertEqual(
            split("RGB"), [('L', 128, 128), ('L', 128, 128), ('L', 128, 128)])
        self.assertEqual(
            split("RGBA"),
            [('L', 128, 128), ('L', 128, 128),
                ('L', 128, 128), ('L', 128, 128)])
        self.assertEqual(
            split("CMYK"),
            [('L', 128, 128), ('L', 128, 128),
                ('L', 128, 128), ('L', 128, 128)])
        self.assertEqual(
            split("YCbCr"),
            [('L', 128, 128), ('L', 128, 128), ('L', 128, 128)])

    def test_split_merge(self):
        def split_merge(mode):
            return Image.merge(mode, hopper(mode).split())
        self.assert_image_equal(hopper("1"), split_merge("1"))
        self.assert_image_equal(hopper("L"), split_merge("L"))
        self.assert_image_equal(hopper("I"), split_merge("I"))
        self.assert_image_equal(hopper("F"), split_merge("F"))
        self.assert_image_equal(hopper("P"), split_merge("P"))
        self.assert_image_equal(hopper("RGB"), split_merge("RGB"))
        self.assert_image_equal(hopper("RGBA"), split_merge("RGBA"))
        self.assert_image_equal(hopper("CMYK"), split_merge("CMYK"))
        self.assert_image_equal(hopper("YCbCr"), split_merge("YCbCr"))

    def test_split_open(self):
        codecs = dir(Image.core)

        if 'zip_encoder' in codecs:
            file = self.tempfile("temp.png")
        else:
            file = self.tempfile("temp.pcx")

        def split_open(mode):
            hopper(mode).save(file)
            im = Image.open(file)
            return len(im.split())
        self.assertEqual(split_open("1"), 1)
        self.assertEqual(split_open("L"), 1)
        self.assertEqual(split_open("P"), 1)
        self.assertEqual(split_open("RGB"), 3)
        if 'zip_encoder' in codecs:
            self.assertEqual(split_open("RGBA"), 4)


if __name__ == '__main__':
    unittest.main()

# End of file
