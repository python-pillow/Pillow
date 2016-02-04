from helper import unittest, PillowTestCase, hopper
from PIL import Image

class TestImagingCoreResize(PillowTestCase):
    #see https://github.com/python-pillow/Pillow/issues/1710
    def test_overflow(self):
        im = hopper('L')
        xsize = 0x100000008 // 4
        ysize = 1000 # unimportant
        try:
            im.im.resize((xsize, ysize), Image.LINEAR) # any resampling filter will do here
            self.fail("Resize should raise MemoryError on invalid xsize")
        except MemoryError:
            self.assertTrue(True, "Should raise MemoryError")


if __name__ == '__main__':
    unittest.main()
