from helper import unittest, PillowTestCase, hopper

from PIL import ImageOps


class TestImageOps(PillowTestCase):

    class Deformer:
        def getmesh(self, im):
            x, y = im.size
            return [((0, 0, x, y), (0, 0, x, 0, x, y, y, 0))]

    deformer = Deformer()

    def test_sanity(self):

        ImageOps.autocontrast(hopper("L"))
        ImageOps.autocontrast(hopper("RGB"))

        ImageOps.autocontrast(hopper("L"), cutoff=10)
        ImageOps.autocontrast(hopper("L"), ignore=[0, 255])

        ImageOps.colorize(hopper("L"), (0, 0, 0), (255, 255, 255))
        ImageOps.colorize(hopper("L"), "black", "white")

        ImageOps.crop(hopper("L"), 1)
        ImageOps.crop(hopper("RGB"), 1)

        ImageOps.deform(hopper("L"), self.deformer)
        ImageOps.deform(hopper("RGB"), self.deformer)

        ImageOps.equalize(hopper("L"))
        ImageOps.equalize(hopper("RGB"))

        ImageOps.expand(hopper("L"), 1)
        ImageOps.expand(hopper("RGB"), 1)
        ImageOps.expand(hopper("L"), 2, "blue")
        ImageOps.expand(hopper("RGB"), 2, "blue")

        ImageOps.fit(hopper("L"), (128, 128))
        ImageOps.fit(hopper("RGB"), (128, 128))

        ImageOps.flip(hopper("L"))
        ImageOps.flip(hopper("RGB"))

        ImageOps.grayscale(hopper("L"))
        ImageOps.grayscale(hopper("RGB"))

        ImageOps.invert(hopper("L"))
        ImageOps.invert(hopper("RGB"))

        ImageOps.mirror(hopper("L"))
        ImageOps.mirror(hopper("RGB"))

        ImageOps.posterize(hopper("L"), 4)
        ImageOps.posterize(hopper("RGB"), 4)

        ImageOps.solarize(hopper("L"))
        ImageOps.solarize(hopper("RGB"))

    def test_1pxfit(self):
        # Division by zero in equalize if image is 1 pixel high
        newimg = ImageOps.fit(hopper("RGB").resize((1, 1)), (35, 35))
        self.assertEqual(newimg.size, (35, 35))

        newimg = ImageOps.fit(hopper("RGB").resize((1, 100)), (35, 35))
        self.assertEqual(newimg.size, (35, 35))

        newimg = ImageOps.fit(hopper("RGB").resize((100, 1)), (35, 35))
        self.assertEqual(newimg.size, (35, 35))

    def test_pil163(self):
        # Division by zero in equalize if < 255 pixels in image (@PIL163)

        i = hopper("RGB").resize((15, 16))

        ImageOps.equalize(i.convert("L"))
        ImageOps.equalize(i.convert("P"))
        ImageOps.equalize(i.convert("RGB"))


if __name__ == '__main__':
    unittest.main()

# End of file
