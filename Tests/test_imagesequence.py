from helper import unittest, PillowTestCase, hopper

from PIL import Image, ImageSequence, TiffImagePlugin


class TestImageSequence(PillowTestCase):

    def test_sanity(self):

        test_file = self.tempfile("temp.im")

        im = hopper("RGB")
        im.save(test_file)

        seq = ImageSequence.Iterator(im)

        index = 0
        for frame in seq:
            self.assert_image_equal(im, frame)
            self.assertEqual(im.tell(), index)
            index += 1

        self.assertEqual(index, 1)

        self.assertRaises(AttributeError, lambda: ImageSequence.Iterator(0))

    def test_iterator(self):
        im = Image.open('Tests/images/multipage.tiff')
        i = ImageSequence.Iterator(im)
        for index in range(0, im.n_frames):
            self.assertEqual(i[index], next(i))
        self.assertRaises(IndexError, lambda: i[index+1])
        self.assertRaises(StopIteration, lambda: next(i))

    def _test_multipage_tiff(self):
        im = Image.open('Tests/images/multipage.tiff')
        for index, frame in enumerate(ImageSequence.Iterator(im)):
            frame.load()
            self.assertEqual(index, im.tell())
            frame.convert('RGB')

    def test_tiff(self):
        self._test_multipage_tiff()

    def test_libtiff(self):
        codecs = dir(Image.core)

        if "libtiff_encoder" not in codecs or "libtiff_decoder" not in codecs:
            self.skipTest("tiff support not available")

        TiffImagePlugin.READ_LIBTIFF = True
        self._test_multipage_tiff()
        TiffImagePlugin.READ_LIBTIFF = False

    def test_consecutive(self):
        im = Image.open('Tests/images/multipage.tiff')
        firstFrame = None
        for frame in ImageSequence.Iterator(im):
            if firstFrame is None:
                firstFrame = frame.copy()
            pass
        for frame in ImageSequence.Iterator(im):
            self.assert_image_equal(frame, firstFrame)
            break


    def test_palette_mmap(self):
        # Using mmap in ImageFile can require to reload the palette.
        im = Image.open('Tests/images/multipage-mmap.tiff')
        color1 = im.getpalette()[0:3]
        im.seek(0)
        color2 = im.getpalette()[0:3]
        self.assertEqual(color1, color2)

if __name__ == '__main__':
    unittest.main()
