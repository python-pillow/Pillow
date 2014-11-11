from helper import unittest, PillowTestCase, hopper, tostring

from PIL import Image
from PIL import ImageFileIO


class TestImageFileIo(PillowTestCase):

    def test_fileio(self):

        class DumbFile:
            def __init__(self, data):
                self.data = data

            def read(self, bytes=None):
                assert(bytes is None)
                return self.data

            def close(self):
                pass

        im1 = hopper()

        io = ImageFileIO.ImageFileIO(DumbFile(tostring(im1, "PPM")))

        im2 = Image.open(io)
        self.assert_image_equal(im1, im2)


if __name__ == '__main__':
    unittest.main()

# End of file
