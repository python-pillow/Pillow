from helper import PillowTestCase

try:
    import numpy as np
    from numpy.testing import assert_equal

    from scipy import misc
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


class Test_scipy_resize(PillowTestCase):
    """ Tests for scipy regression in Pillow 2.6.0

    Tests from https://github.com/scipy/scipy/blob/master/scipy/misc/pilutil.py
    """

    def setUp(self):
        if not HAS_SCIPY:
            self.skipTest("Scipy Required")

    def test_imresize(self):
        im = np.random.random((10, 20))
        for T in np.sctypes['float'] + [float]:
            # 1.1 rounds to below 1.1 for float16, 1.101 works
            im1 = misc.imresize(im, T(1.101))
            self.assertEqual(im1.shape, (11, 22))

    def test_imresize4(self):
        im = np.array([[1, 2],
                       [3, 4]])
        res = np.array([[1.,   1.25,  1.75,  2.],
                        [1.5,  1.75,  2.25,  2.5],
                        [2.5,  2.75,  3.25,  3.5],
                        [3.,   3.25,  3.75,  4.]], dtype=np.float32)
        # Check that resizing by target size, float and int are the same
        im2 = misc.imresize(im, (4, 4), mode='F')  # output size
        im3 = misc.imresize(im, 2., mode='F')  # fraction
        im4 = misc.imresize(im, 200, mode='F')  # percentage
        assert_equal(im2, res)
        assert_equal(im3, res)
        assert_equal(im4, res)
