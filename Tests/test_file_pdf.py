from helper import unittest, PillowTestCase, hopper
from PIL import Image, pdfParser
import io
import os
import os.path
import tempfile


class TestFilePdf(PillowTestCase):

    def helper_save_as_pdf(self, mode, **kwargs):
        # Arrange
        im = hopper(mode)
        outfile = self.tempfile("temp_" + mode + ".pdf")

        # Act
        im.save(outfile, **kwargs)

        # Assert
        self.assertTrue(os.path.isfile(outfile))
        self.assertGreater(os.path.getsize(outfile), 0)

        return outfile

    def test_monochrome(self):
        # Arrange
        mode = "1"

        # Act / Assert
        self.helper_save_as_pdf(mode)

    def test_greyscale(self):
        # Arrange
        mode = "L"

        # Act / Assert
        self.helper_save_as_pdf(mode)

    def test_rgb(self):
        # Arrange
        mode = "RGB"

        # Act / Assert
        self.helper_save_as_pdf(mode)

    def test_p_mode(self):
        # Arrange
        mode = "P"

        # Act / Assert
        self.helper_save_as_pdf(mode)

    def test_cmyk_mode(self):
        # Arrange
        mode = "CMYK"

        # Act / Assert
        self.helper_save_as_pdf(mode)

    def test_unsupported_mode(self):
        im = hopper("LA")
        outfile = self.tempfile("temp_LA.pdf")

        self.assertRaises(ValueError, im.save, outfile)

    def test_save_all(self):
        # Single frame image
        self.helper_save_as_pdf("RGB", save_all=True)

        # Multiframe image
        im = Image.open("Tests/images/dispose_bgnd.gif")

        outfile = self.tempfile('temp.pdf')
        im.save(outfile, save_all=True)

        self.assertTrue(os.path.isfile(outfile))
        self.assertGreater(os.path.getsize(outfile), 0)

        # Append images
        ims = [hopper()]
        im.copy().save(outfile, save_all=True, append_images=ims)

        self.assertTrue(os.path.isfile(outfile))
        self.assertGreater(os.path.getsize(outfile), 0)

        # Test appending using a generator
        def imGenerator(ims):
            for im in ims:
                yield im
        im.save(outfile, save_all=True, append_images=imGenerator(ims))

        self.assertTrue(os.path.isfile(outfile))
        self.assertGreater(os.path.getsize(outfile), 0)

        # Append JPEG images
        jpeg = Image.open("Tests/images/flower.jpg")
        jpeg.save(outfile, save_all=True, append_images=[jpeg.copy()])

        self.assertTrue(os.path.isfile(outfile))
        self.assertGreater(os.path.getsize(outfile), 0)

    def test_pdf_open(self):
        # fail on empty buffer
        self.assertRaises(pdfParser.PdfFormatError, pdfParser.PdfParser, buf=bytearray())
        # fail on a buffer full of null bytes
        self.assertRaises(pdfParser.PdfFormatError, pdfParser.PdfParser, buf=bytearray(65536))
        # make an empty PDF object
        empty_pdf = pdfParser.PdfParser()
        self.assertEqual(len(empty_pdf.pages), 0)
        # make a PDF file
        pdf_filename = self.helper_save_as_pdf("RGB")
        # open the PDF file
        hopper_pdf = pdfParser.PdfParser(filename=pdf_filename)
        self.assertEqual(len(hopper_pdf.pages), 1)
        # read a PDF file from a buffer with a non-zero offset
        with open(pdf_filename, "rb") as f:
            content = b"xyzzy" + f.read()
        hopper_pdf = pdfParser.PdfParser(buf=content, start_offset=5)
        self.assertEqual(len(hopper_pdf.pages), 1)
        # read a PDF file from an already open file
        with open(pdf_filename, "rb") as f:
            hopper_pdf = pdfParser.PdfParser(f=f)
        self.assertEqual(len(hopper_pdf.pages), 1)

    def test_pdf_append_fails_on_nonexistent_file(self):
        im = hopper("RGB")
        temp_dir = tempfile.mkdtemp()
        try:
            self.assertRaises(IOError, im.save, os.path.join(temp_dir, "nonexistent.pdf"), append=True)
        finally:
            os.rmdir(temp_dir)

    def test_pdf_append(self):
        # make a PDF file
        pdf_filename = self.helper_save_as_pdf("RGB", producer="pdfParser")
        # open it, check pages and info
        pdf = pdfParser.PdfParser(pdf_filename)
        self.assertEqual(len(pdf.pages), 1)
        self.assertEqual(len(pdf.info), 1)
        self.assertEqual(pdfParser.decode_text(pdf.info[b"Producer"]), "pdfParser")
        # append some info
        pdf.info[b"Title"] = pdfParser.encode_text("abc")
        pdf.info[b"Author"] = pdfParser.encode_text("def")
        pdf.info[b"Subject"] = pdfParser.encode_text("ghi")
        pdf.info[b"Keywords"] = pdfParser.encode_text("jkl")
        pdf.info[b"Creator"] = pdfParser.encode_text("hopper()")
        with open(pdf_filename, "r+b") as f:
            f.seek(0, os.SEEK_END)
            pdf.write_xref_and_trailer(f)
        # open it again, check pages and info again
        pdf = pdfParser.PdfParser(pdf_filename)
        self.assertEqual(len(pdf.pages), 1)
        self.assertEqual(len(pdf.info), 6)
        self.assertEqual(pdfParser.decode_text(pdf.info[b"Title"]), "abc")
        # append two images
        mode_CMYK = hopper("CMYK")
        mode_P = hopper("P")
        mode_CMYK.save(pdf_filename, append=True, save_all=True, append_images=[mode_P])
        # open the PDF again, check pages and info again
        pdf = pdfParser.PdfParser(pdf_filename)
        self.assertEqual(len(pdf.pages), 3)
        self.assertEqual(len(pdf.info), 6)
        self.assertEqual(pdfParser.decode_text(pdf.info[b"Title"]), "abc")
        self.assertEqual(pdfParser.decode_text(pdf.info[b"Producer"]), "pdfParser")

    def test_pdf_append_to_bytesio(self):
        im = hopper("RGB")
        f = io.BytesIO()
        im.save(f, format="PDF")
        initial_size = len(f.getvalue())
        self.assertGreater(initial_size, 0)
        im = hopper("P")
        f = io.BytesIO(f.getvalue())
        im.save(f, format="PDF", append=True)
        self.assertGreater(len(f.getvalue()), initial_size)


if __name__ == '__main__':
    unittest.main()
