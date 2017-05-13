from helper import unittest, PillowTestCase, hopper
from PIL import Image


class TestFileWmf(PillowTestCase):

    def test_load_raw(self):

        # Test basic EMF open and rendering
        im = Image.open('Tests/images/drawing.emf')
        if hasattr(Image.core, "drawwmf"):
            # Currently, support for WMF/EMF is Windows-only
            im.load()
            # Compare to reference rendering
            imref = Image.open('Tests/images/drawing_emf_ref.png')
            imref.load()
            self.assert_image_similar(im, imref, 0)

        # Test basic WMF open and rendering
        im = Image.open('Tests/images/drawing.wmf')
        if hasattr(Image.core, "drawwmf"):
            # Currently, support for WMF/EMF is Windows-only
            im.load()
            # Compare to reference rendering
            imref = Image.open('Tests/images/drawing_wmf_ref.png')
            imref.load()
            self.assert_image_similar(im, imref, 2.0)

    def test_save(self):
        im = hopper()

        for ext in [".wmf", ".emf"]:
            tmpfile = self.tempfile("temp"+ext)
            self.assertRaises(IOError, lambda: im.save(tmpfile))


if __name__ == '__main__':
    unittest.main()
