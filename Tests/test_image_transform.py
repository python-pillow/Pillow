from helper import unittest, PillowTestCase, hopper

from PIL import Image


class TestImageTransform(PillowTestCase):

    def test_sanity(self):
        from PIL import ImageTransform

        im = Image.new("L", (100, 100))

        seq = tuple(range(10))

        transform = ImageTransform.AffineTransform(seq[:6])
        im.transform((100, 100), transform)
        transform = ImageTransform.ExtentTransform(seq[:4])
        im.transform((100, 100), transform)
        transform = ImageTransform.QuadTransform(seq[:8])
        im.transform((100, 100), transform)
        transform = ImageTransform.MeshTransform([(seq[:4], seq[:8])])
        im.transform((100, 100), transform)

    def test_extent(self):
        im = hopper('RGB')
        (w, h) = im.size
        transformed = im.transform(im.size, Image.EXTENT,
                                   (0, 0,
                                    w//2, h//2),  # ul -> lr
                                   Image.BILINEAR)

        scaled = im.resize((w*2, h*2), Image.BILINEAR).crop((0, 0, w, h))

        # undone -- precision?
        self.assert_image_similar(transformed, scaled, 23)

    def test_quad(self):
        # one simple quad transform, equivalent to scale & crop upper left quad
        im = hopper('RGB')
        (w, h) = im.size
        transformed = im.transform(im.size, Image.QUAD,
                                   (0, 0, 0, h//2,
                                    # ul -> ccw around quad:
                                    w//2, h//2, w//2, 0),
                                   Image.BILINEAR)

        scaled = im.transform((w, h), Image.AFFINE,
                              (.5, 0, 0, 0, .5, 0),
                              Image.BILINEAR)

        self.assert_image_equal(transformed, scaled)

    def test_mesh(self):
        # this should be a checkerboard of halfsized hoppers in ul, lr
        im = hopper('RGBA')
        (w, h) = im.size
        transformed = im.transform(im.size, Image.MESH,
                                   [((0, 0, w//2, h//2),  # box
                                    (0, 0, 0, h,
                                     w, h, w, 0)),  # ul -> ccw around quad
                                    ((w//2, h//2, w, h),  # box
                                    (0, 0, 0, h,
                                     w, h, w, 0))],  # ul -> ccw around quad
                                   Image.BILINEAR)

        scaled = im.transform((w//2, h//2), Image.AFFINE,
                              (2, 0, 0, 0, 2, 0),
                              Image.BILINEAR)

        checker = Image.new('RGBA', im.size)
        checker.paste(scaled, (0, 0))
        checker.paste(scaled, (w//2, h//2))

        self.assert_image_equal(transformed, checker)

        # now, check to see that the extra area is (0, 0, 0, 0)
        blank = Image.new('RGBA', (w//2, h//2), (0, 0, 0, 0))

        self.assert_image_equal(blank, transformed.crop((w//2, 0, w, h//2)))
        self.assert_image_equal(blank, transformed.crop((0, h//2, w//2, h)))

    def _test_alpha_premult(self, op):
        # create image with half white, half black,
        # with the black half transparent.
        # do op,
        # there should be no darkness in the white section.
        im = Image.new('RGBA', (10, 10), (0, 0, 0, 0))
        im2 = Image.new('RGBA', (5, 10), (255, 255, 255, 255))
        im.paste(im2, (0, 0))

        im = op(im, (40, 10))
        im_background = Image.new('RGB', (40, 10), (255, 255, 255))
        im_background.paste(im, (0, 0), im)

        hist = im_background.histogram()
        self.assertEqual(40*10, hist[-1])

    def test_alpha_premult_resize(self):

        def op(im, sz):
            return im.resize(sz, Image.LINEAR)

        self._test_alpha_premult(op)

    def test_alpha_premult_transform(self):

        def op(im, sz):
            (w, h) = im.size
            return im.transform(sz, Image.EXTENT,
                                (0, 0,
                                 w, h),
                                Image.BILINEAR)

        self._test_alpha_premult(op)

    def test_blank_fill(self):
        # attempting to hit
        # https://github.com/python-pillow/Pillow/issues/254 reported
        #
        # issue is that transforms with transparent overflow area
        # contained junk from previous images, especially on systems with
        # constrained memory. So, attempt to fill up memory with a
        # pattern, free it, and then run the mesh test again. Using a 1Mp
        # image with 4 bands, for 4 megs of data allocated, x 64. OMM (64
        # bit 12.04 VM with 512 megs available, this fails with Pillow <
        # a0eaf06cc5f62a6fb6de556989ac1014ff3348ea
        #
        # Running by default, but I'd totally understand not doing it in
        # the future

        pattern = [
            Image.new('RGBA', (1024, 1024), (a, a, a, a))
            for a in range(1, 65)
        ]

        # Yeah. Watch some JIT optimize this out.
        pattern = None

        self.test_mesh()


if __name__ == '__main__':
    unittest.main()

# End of file
