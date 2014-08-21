from helper import unittest, PillowTestCase

from PIL import Image, ImageSequence, TiffImagePlugin

TiffImagePlugin.READ_LIBTIFF = True

class TestFileTiff(PillowTestCase):

    def testSequence(self):
        try:
            im = Image.open('multi.tif')
            index = 0
            for frame in ImageSequence.Iterator(im):
                frame.load()
                self.assertEqual(index, im.tell())
                index = index+1
        except Exception as e:
            self.assertTrue(False, str(e))
            

