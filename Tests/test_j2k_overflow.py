from PIL import Image
from helper import unittest, PillowTestCase

class TestJ2kEncodeOverflow(PillowTestCase):
    def test_j2k_overflow(self):

        im = Image.new('RGBA', (1024, 131584))
        target = self.tempfile('temp.jpc')
        try:
            im.save(target)
            self.assertTrue(False, "Expected IOError, save succeeded?")
        except IOError as err:
            self.assertTrue(True, "IOError is expected")
        except Exception as err:
            self.assertTrue(False, "Expected IOError, got %s" %type(err))

if __name__ == '__main__':
    unittest.main()
