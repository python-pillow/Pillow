from helper import unittest, PillowTestCase
from PIL import Image


class TestFilePcd(PillowTestCase):

    def test_load_raw(self):
        im = Image.open('Tests/images/hopper.pcd')
        im.load()  # should not segfault.

        # Note that this image was created with a resized hopper
        # image, which was then converted to pcd with imagemagick
        # and the colors are wonky in Pillow.  It's unclear if this
        # is a pillow or a convert issue, as other images not generated
        # from convert look find on pillow and not imagemagick.

        # target = hopper().resize((768,512))
        # self.assert_image_similar(im, target, 10)


if __name__ == '__main__':
    unittest.main()
