from PIL import Image, ImageSequence, TiffImagePlugin

from .helper import PillowTestCase, hopper


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

        self.assertRaises(AttributeError, ImageSequence.Iterator, 0)

    def test_iterator(self):
        with Image.open("Tests/images/multipage.tiff") as im:
            i = ImageSequence.Iterator(im)
            for index in range(0, im.n_frames):
                self.assertEqual(i[index], next(i))
            self.assertRaises(IndexError, lambda: i[index + 1])
            self.assertRaises(StopIteration, next, i)

    def test_iterator_min_frame(self):
        with Image.open("Tests/images/hopper.psd") as im:
            i = ImageSequence.Iterator(im)
            for index in range(1, im.n_frames):
                self.assertEqual(i[index], next(i))

    def _test_multipage_tiff(self):
        with Image.open("Tests/images/multipage.tiff") as im:
            for index, frame in enumerate(ImageSequence.Iterator(im)):
                frame.load()
                self.assertEqual(index, im.tell())
                frame.convert("RGB")

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
        with Image.open("Tests/images/multipage.tiff") as im:
            firstFrame = None
            for frame in ImageSequence.Iterator(im):
                if firstFrame is None:
                    firstFrame = frame.copy()
            for frame in ImageSequence.Iterator(im):
                self.assert_image_equal(frame, firstFrame)
                break

    def test_palette_mmap(self):
        # Using mmap in ImageFile can require to reload the palette.
        with Image.open("Tests/images/multipage-mmap.tiff") as im:
            color1 = im.getpalette()[0:3]
            im.seek(0)
            color2 = im.getpalette()[0:3]
            self.assertEqual(color1, color2)

    def test_all_frames(self):
        # Test a single image
        with Image.open("Tests/images/iss634.gif") as im:
            ims = ImageSequence.all_frames(im)

            self.assertEqual(len(ims), 42)
            for i, im_frame in enumerate(ims):
                self.assertFalse(im_frame is im)

                im.seek(i)
                self.assert_image_equal(im, im_frame)

            # Test a series of images
            ims = ImageSequence.all_frames([im, hopper(), im])
            self.assertEqual(len(ims), 85)

            # Test an operation
            ims = ImageSequence.all_frames(im, lambda im_frame: im_frame.rotate(90))
            for i, im_frame in enumerate(ims):
                im.seek(i)
                self.assert_image_equal(im.rotate(90), im_frame)
