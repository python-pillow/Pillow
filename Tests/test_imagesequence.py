from helper import unittest, PillowTestCase, tearDownModule, lena

from PIL import ImageSequence


class TestImageSequence(PillowTestCase):

    def test_sanity(self):

        file = self.tempfile("temp.im")

        im = lena("RGB")
        im.save(file)

        seq = ImageSequence.Iterator(im)

        index = 0
        for frame in seq:
            self.assert_image_equal(im, frame)
            self.assertEqual(im.tell(), index)
            index += 1

        self.assertEqual(index, 1)


if __name__ == '__main__':
    unittest.main()

# End of file
