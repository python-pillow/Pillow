from helper import unittest, PillowTestCase


class TestPsDraw(PillowTestCase):

    def test_draw_postscript(self):

        # Based on Pillow tutorial, but there is no textsize:
        # http://pillow.readthedocs.org/en/latest/handbook/tutorial.html

        # Arrange
        from PIL import Image
        from PIL import PSDraw
        tempfile = self.tempfile('temp.ps')
        fp = open(tempfile, "wb")

        im = Image.open("Tests/images/hopper.ppm")
        title = "hopper"
        box = (1*72, 2*72, 7*72, 10*72)  # in points

        # Act
        ps = PSDraw.PSDraw(fp)
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
        fp.close()

        # Assert
        # Check non-zero file was created
        import os
        self.assertTrue(os.path.isfile(tempfile))
        self.assertGreater(os.path.getsize(tempfile), 0)


if __name__ == '__main__':
    unittest.main()

# End of file
