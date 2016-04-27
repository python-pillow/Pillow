from helper import unittest, PillowTestCase

from PIL import Image

import numpy as np

class TestImageFromArrayLA(PillowTestCase):

    def test_sanity(self):
        ar1 = (np.random.random((40,40,2))*255).astype('uint8')
        im1 = Image.fromarray(ar1)
        arr = np.array(im1.getdata(), 'uint8')
        ar2 = arr.reshape(im1.size[1], im1.size[0], arr.shape[1])
        im2 = Image.fromarray(ar2)

        self.assert_image_equal(im1, im2)


if __name__ == '__main__':
    unittest.main()

# End of file
