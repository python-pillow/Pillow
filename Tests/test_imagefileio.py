from tester import *

from PIL import Image
from PIL import ImageFileIO

def test_fileio():

    class DumbFile:
        def __init__(self, data):
            self.data = data
        def read(self, bytes=None):
            assert_equal(bytes, None)
            return self.data
        def close(self):
            pass

    im1 = lena()

    io = ImageFileIO.ImageFileIO(DumbFile(tostring(im1, "PPM")))

    im2 = Image.open(io)
    assert_image_equal(im1, im2)


