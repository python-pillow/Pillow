from helper import unittest, PillowTestCase, hopper


class TestPsDraw(PillowTestCase):

    def test_draw_postscript(self):

        # Taken from Pillow tutorial:
        # http://pillow.readthedocs.org/en/latest/handbook/tutorial.html

        # Arrange
        from PIL import Image
        from PIL import PSDraw
        tempfile = self.tempfile('temp.ps')
        fp = open(tempfile, "wb")

        im = Image.open("Tests/images/hopper.ppm")
        title = "hopper"
        box = (1*72, 2*72, 7*72, 10*72) # in points

        # Act
        ps = PSDraw.PSDraw(fp)
        ps.begin_document(title)

        # draw the image (75 dpi)
        ps.image(box, im, 75)
        ps.rectangle(box)

        # draw centered title
        ps.setfont("HelveticaNarrow-Bold", 36)
        w, h, b = ps.textsize(title)
        ps.text((4*72-w/2, 1*72-h), title)

        ps.end_document()
        fp.close()

        # Assert
        # TODO


if __name__ == '__main__':
    unittest.main()

# End of file
