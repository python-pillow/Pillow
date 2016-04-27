from helper import unittest, PillowTestCase

from PIL import Image

try:
    import site
    import numpy
except ImportError:
    # Skip via setUp()
    pass

class TestImageFromArrayLA(PillowTestCase):

    def setUp(self):
        try:
            import site
            import numpy
        except ImportError:
            self.skipTest("ImportError")

    def test_sanity(self):
        ar1 = (numpy.random.random((40,40,2))*255).astype('uint8')
        im1 = Image.fromarray(ar1)
        arr = numpy.array(im1.getdata(), 'uint8')
        ar2 = arr.reshape(im1.size[1], im1.size[0], arr.shape[1])
        self.assertTrue(numpy.array_equal(ar1, ar2))


if __name__ == '__main__':
    unittest.main()

# End of file
