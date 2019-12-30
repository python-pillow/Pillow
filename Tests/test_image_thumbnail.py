from PIL import Image

from .helper import PillowTestCase, fromstring, hopper, tostring


class TestImageThumbnail(PillowTestCase):
    def test_sanity(self):
        im = hopper()
        self.assertIsNone(im.thumbnail((100, 100)))

        self.assertEqual(im.size, (100, 100))

    def test_aspect(self):
        im = Image.new("L", (128, 128))
        im.thumbnail((100, 100))
        self.assertEqual(im.size, (100, 100))

        im = Image.new("L", (128, 256))
        im.thumbnail((100, 100))
        self.assertEqual(im.size, (50, 100))

        im = Image.new("L", (128, 256))
        im.thumbnail((50, 100))
        self.assertEqual(im.size, (50, 100))

        im = Image.new("L", (256, 128))
        im.thumbnail((100, 100))
        self.assertEqual(im.size, (100, 50))

        im = Image.new("L", (256, 128))
        im.thumbnail((100, 50))
        self.assertEqual(im.size, (100, 50))

        im = Image.new("L", (128, 128))
        im.thumbnail((100, 100))
        self.assertEqual(im.size, (100, 100))

        im = Image.new("L", (256, 162))  # ratio is 1.5802469136
        im.thumbnail((33, 33))
        self.assertEqual(im.size, (33, 21))  # ratio is 1.5714285714

        im = Image.new("L", (162, 256))  # ratio is 0.6328125
        im.thumbnail((33, 33))
        self.assertEqual(im.size, (21, 33))  # ratio is 0.6363636364

    def test_float(self):
        im = Image.new("L", (128, 128))
        im.thumbnail((99.9, 99.9))
        self.assertEqual(im.size, (100, 100))

    def test_no_resize(self):
        # Check that draft() can resize the image to the destination size
        with Image.open("Tests/images/hopper.jpg") as im:
            im.draft(None, (64, 64))
            self.assertEqual(im.size, (64, 64))

        # Test thumbnail(), where only draft() is necessary to resize the image
        with Image.open("Tests/images/hopper.jpg") as im:
            im.thumbnail((64, 64))
            self.assertEqual(im.size, (64, 64))

    def test_DCT_scaling_edges(self):
        # Make an image with red borders and size (N * 8) + 1 to cross DCT grid
        im = Image.new("RGB", (257, 257), "red")
        im.paste(Image.new("RGB", (235, 235)), (11, 11))

        thumb = fromstring(tostring(im, "JPEG", quality=99, subsampling=0))
        # small reducing_gap to amplify the effect
        thumb.thumbnail((32, 32), Image.BICUBIC, reducing_gap=1.0)

        ref = im.resize((32, 32), Image.BICUBIC)
        # This is still JPEG, some error is present. Without the fix it is 11.5
        self.assert_image_similar(thumb, ref, 1.5)

    def test_reducing_gap_values(self):
        im = hopper()
        im.thumbnail((18, 18), Image.BICUBIC)

        ref = hopper()
        ref.thumbnail((18, 18), Image.BICUBIC, reducing_gap=2.0)
        # reducing_gap=2.0 should be the default
        self.assert_image_equal(ref, im)

        ref = hopper()
        ref.thumbnail((18, 18), Image.BICUBIC, reducing_gap=None)
        with self.assertRaises(AssertionError):
            self.assert_image_equal(ref, im)

        self.assert_image_similar(ref, im, 3.5)

    def test_reducing_gap_for_DCT_scaling(self):
        with Image.open("Tests/images/hopper.jpg") as ref:
            # thumbnail should call draft with reducing_gap scale
            ref.draft(None, (18 * 3, 18 * 3))
            ref = ref.resize((18, 18), Image.BICUBIC)

            with Image.open("Tests/images/hopper.jpg") as im:
                im.thumbnail((18, 18), Image.BICUBIC, reducing_gap=3.0)

                self.assert_image_equal(ref, im)
