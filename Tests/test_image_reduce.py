from PIL import Image

from .helper import PillowTestCase, hopper


class TestImageReduce(PillowTestCase):
    # There are several internal implementations
    remarkable_factors = [
        1, 2, 3, 4, 5, 6,  # special implementations
        (1, 2), (1, 3), (1, 4),  # 1xN implementation
        (2, 1), (3, 1), (4, 1),  # Nx1 implementation
        # general implementation with different paths
        (4, 6), (5, 6), (4, 7), (5, 7),
    ]

    def test_args(self):
        im = Image.new('L', (10, 10))
        
        self.assertEqual((4, 4), im.reduce(3).size)
        self.assertEqual((4, 10), im.reduce((3, 1)).size)
        self.assertEqual((10, 4), im.reduce((1, 3)).size)

        with self.assertRaises(ValueError):
            im.reduce(0)
        with self.assertRaises(TypeError):
            im.reduce(2.0)
        with self.assertRaises(ValueError):
            im.reduce((0, 10))

    def check_correctness(self, im, factor):
        if not isinstance(factor, (list, tuple)):
            factor = (factor, factor)

        # Image.reduce() should works very similar to Image.resize(BOX)
        # when image size is dividable by the factor.
        desired_size = (im.width // factor[0], im.height // factor[1])
        im = im.crop((0, 0, desired_size[0] * factor[0], desired_size[1] * factor[1]))

        reduced = im.reduce(factor)
        resized = im.resize(desired_size, Image.BOX)

        epsilon = 0.5 * len(reduced.getbands())
        self.assert_image_similar(reduced, resized, epsilon)

    def test_mode_RGB(self):
        im = hopper('RGB')
        for factor in self.remarkable_factors:
            self.check_correctness(im, factor)

    def test_mode_LA(self):
        im = Image.open("Tests/images/transparent.png").convert('LA')
        for factor in self.remarkable_factors:
            print(factor)
            self.check_correctness(im, factor)

    def test_mode_RGBA(self):
        im = Image.open("Tests/images/transparent.png").convert('RGBA')
        for factor in self.remarkable_factors:
            print(factor)
            self.check_correctness(im, factor)

