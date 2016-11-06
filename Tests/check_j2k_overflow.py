from PIL import Image
from helper import unittest, PillowTestCase


class TestJ2kEncodeOverflow(PillowTestCase):
    def test_j2k_overflow(self):

        im = Image.new('RGBA', (1024, 131584))
        target = self.tempfile('temp.jpc')
        with self.assertRaises(IOError):
            im.save(target)

if __name__ == '__main__':
    unittest.main()
