from helper import unittest, PillowTestCase

from PIL import Image, PSDraw
import os
import sys


class TestPsDraw(PillowTestCase):

    def _create_document(self, ps):
        im = Image.open("Tests/images/hopper.ppm")
        title = "hopper"
        box = (1*72, 2*72, 7*72, 10*72)  # in points

        ps.begin_document(title)

        # draw diagonal lines in a cross
        ps.line((1*72, 2*72), (7*72, 10*72))
        ps.line((7*72, 2*72), (1*72, 10*72))

        # draw the image (75 dpi)
        ps.image(box, im, 75)
        ps.rectangle(box)

        # draw title
        ps.setfont("Courier", 36)
        ps.text((3*72, 4*72), title)

        ps.end_document()

    def test_draw_postscript(self):

        # Based on Pillow tutorial, but there is no textsize:
        # https://pillow.readthedocs.io/en/latest/handbook/tutorial.html

        # Arrange
        tempfile = self.tempfile('temp.ps')
        fp = open(tempfile, "wb")

        # Act
        ps = PSDraw.PSDraw(fp)
        self._create_document(ps)
        fp.close()

        # Assert
        # Check non-zero file was created
        self.assertTrue(os.path.isfile(tempfile))
        self.assertGreater(os.path.getsize(tempfile), 0)

    def test_stdout(self):
        # Temporarily redirect stdout
        try:
            from cStringIO import StringIO
        except ImportError:
            from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        ps = PSDraw.PSDraw()
        self._create_document(ps)

        # Reset stdout
        sys.stdout = old_stdout

        self.assertNotEqual(mystdout.getvalue(), "")


if __name__ == '__main__':
    unittest.main()
