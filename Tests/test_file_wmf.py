from helper import unittest, PillowTestCase
from PIL import Image
from io import BytesIO


class TestFileWmf(PillowTestCase):

    def as_png(self, im):
        # Pass the image through PNG save/load
        out = BytesIO()
        im.save(out, "PNG")
        test_bytes = out.tell()
        out.seek(0)
        im = Image.open(out)
        im.bytes = test_bytes  # for testing only
        im.load()
        return im

    def test_load_raw(self):

        # Test basic EMF open and rendering
        im = Image.open('Tests/images/drawing.emf')
        if hasattr(Image.core, "drawwmf"):
            # Currently, support for WMF/EMF is Windows-only
            im.load()
            # Compare to reference rendering
            imref = Image.open('Tests/images/drawing_emf_ref.png')
            imref.load()
            self.assert_image_equal(self.as_png(im), imref)

        # Test basic WMF open and rendering
        im = Image.open('Tests/images/drawing.wmf')
        if hasattr(Image.core, "drawwmf"):
            # Currently, support for WMF/EMF is Windows-only
            im.load()
            # Compare to reference rendering
            imref = Image.open('Tests/images/drawing_wmf_ref.png')
            imref.load()
            self.assert_image_equal(self.as_png(im), imref)


if __name__ == '__main__':
    unittest.main()
