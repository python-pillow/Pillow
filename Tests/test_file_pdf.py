import io
import os
import os.path
import tempfile
import time

from PIL import Image, PdfParser

from .helper import PillowTestCase, hopper


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
        with PdfParser.PdfParser(outfile) as pdf:
            if kwargs.get("append_images", False) or kwargs.get("append", False):
                self.assertGreater(len(pdf.pages), 1)
            else:
                self.assertGreater(len(pdf.pages), 0)
        with open(outfile, "rb") as fp:
            contents = fp.read()
        size = tuple(
            int(d)
            for d in contents.split(b"/MediaBox [ 0 0 ")[1].split(b"]")[0].split()
        )
        self.assertEqual(im.size, size)

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
        with Image.open("Tests/images/dispose_bgnd.gif") as im:

            outfile = self.tempfile("temp.pdf")
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
                yield from ims

            im.save(outfile, save_all=True, append_images=imGenerator(ims))

        self.assertTrue(os.path.isfile(outfile))
        self.assertGreater(os.path.getsize(outfile), 0)

        # Append JPEG images
        with Image.open("Tests/images/flower.jpg") as jpeg:
            jpeg.save(outfile, save_all=True, append_images=[jpeg.copy()])

        self.assertTrue(os.path.isfile(outfile))
        self.assertGreater(os.path.getsize(outfile), 0)

    def test_multiframe_normal_save(self):
        # Test saving a multiframe image without save_all
        with Image.open("Tests/images/dispose_bgnd.gif") as im:

            outfile = self.tempfile("temp.pdf")
            im.save(outfile)

        self.assertTrue(os.path.isfile(outfile))
        self.assertGreater(os.path.getsize(outfile), 0)

    def test_pdf_open(self):
        # fail on a buffer full of null bytes
        self.assertRaises(
            PdfParser.PdfFormatError, PdfParser.PdfParser, buf=bytearray(65536)
        )

        # make an empty PDF object
        with PdfParser.PdfParser() as empty_pdf:
            self.assertEqual(len(empty_pdf.pages), 0)
            self.assertEqual(len(empty_pdf.info), 0)
            self.assertFalse(empty_pdf.should_close_buf)
            self.assertFalse(empty_pdf.should_close_file)

        # make a PDF file
        pdf_filename = self.helper_save_as_pdf("RGB")

        # open the PDF file
        with PdfParser.PdfParser(filename=pdf_filename) as hopper_pdf:
            self.assertEqual(len(hopper_pdf.pages), 1)
            self.assertTrue(hopper_pdf.should_close_buf)
            self.assertTrue(hopper_pdf.should_close_file)

        # read a PDF file from a buffer with a non-zero offset
        with open(pdf_filename, "rb") as f:
            content = b"xyzzy" + f.read()
        with PdfParser.PdfParser(buf=content, start_offset=5) as hopper_pdf:
            self.assertEqual(len(hopper_pdf.pages), 1)
            self.assertFalse(hopper_pdf.should_close_buf)
            self.assertFalse(hopper_pdf.should_close_file)

        # read a PDF file from an already open file
        with open(pdf_filename, "rb") as f:
            with PdfParser.PdfParser(f=f) as hopper_pdf:
                self.assertEqual(len(hopper_pdf.pages), 1)
                self.assertTrue(hopper_pdf.should_close_buf)
                self.assertFalse(hopper_pdf.should_close_file)

    def test_pdf_append_fails_on_nonexistent_file(self):
        im = hopper("RGB")
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertRaises(
                IOError, im.save, os.path.join(temp_dir, "nonexistent.pdf"), append=True
            )

    def check_pdf_pages_consistency(self, pdf):
        pages_info = pdf.read_indirect(pdf.pages_ref)
        self.assertNotIn(b"Parent", pages_info)
        self.assertIn(b"Kids", pages_info)
        kids_not_used = pages_info[b"Kids"]
        for page_ref in pdf.pages:
            while True:
                if page_ref in kids_not_used:
                    kids_not_used.remove(page_ref)
                page_info = pdf.read_indirect(page_ref)
                self.assertIn(b"Parent", page_info)
                page_ref = page_info[b"Parent"]
                if page_ref == pdf.pages_ref:
                    break
            self.assertEqual(pdf.pages_ref, page_info[b"Parent"])
        self.assertEqual(kids_not_used, [])

    def test_pdf_append(self):
        # make a PDF file
        pdf_filename = self.helper_save_as_pdf("RGB", producer="PdfParser")

        # open it, check pages and info
        with PdfParser.PdfParser(pdf_filename, mode="r+b") as pdf:
            self.assertEqual(len(pdf.pages), 1)
            self.assertEqual(len(pdf.info), 4)
            self.assertEqual(
                pdf.info.Title, os.path.splitext(os.path.basename(pdf_filename))[0]
            )
            self.assertEqual(pdf.info.Producer, "PdfParser")
            self.assertIn(b"CreationDate", pdf.info)
            self.assertIn(b"ModDate", pdf.info)
            self.check_pdf_pages_consistency(pdf)

            # append some info
            pdf.info.Title = "abc"
            pdf.info.Author = "def"
            pdf.info.Subject = "ghi\uABCD"
            pdf.info.Keywords = "qw)e\\r(ty"
            pdf.info.Creator = "hopper()"
            pdf.start_writing()
            pdf.write_xref_and_trailer()

        # open it again, check pages and info again
        with PdfParser.PdfParser(pdf_filename) as pdf:
            self.assertEqual(len(pdf.pages), 1)
            self.assertEqual(len(pdf.info), 8)
            self.assertEqual(pdf.info.Title, "abc")
            self.assertIn(b"CreationDate", pdf.info)
            self.assertIn(b"ModDate", pdf.info)
            self.check_pdf_pages_consistency(pdf)

        # append two images
        mode_CMYK = hopper("CMYK")
        mode_P = hopper("P")
        mode_CMYK.save(pdf_filename, append=True, save_all=True, append_images=[mode_P])

        # open the PDF again, check pages and info again
        with PdfParser.PdfParser(pdf_filename) as pdf:
            self.assertEqual(len(pdf.pages), 3)
            self.assertEqual(len(pdf.info), 8)
            self.assertEqual(PdfParser.decode_text(pdf.info[b"Title"]), "abc")
            self.assertEqual(pdf.info.Title, "abc")
            self.assertEqual(pdf.info.Producer, "PdfParser")
            self.assertEqual(pdf.info.Keywords, "qw)e\\r(ty")
            self.assertEqual(pdf.info.Subject, "ghi\uABCD")
            self.assertIn(b"CreationDate", pdf.info)
            self.assertIn(b"ModDate", pdf.info)
            self.check_pdf_pages_consistency(pdf)

    def test_pdf_info(self):
        # make a PDF file
        pdf_filename = self.helper_save_as_pdf(
            "RGB",
            title="title",
            author="author",
            subject="subject",
            keywords="keywords",
            creator="creator",
            producer="producer",
            creationDate=time.strptime("2000", "%Y"),
            modDate=time.strptime("2001", "%Y"),
        )

        # open it, check pages and info
        with PdfParser.PdfParser(pdf_filename) as pdf:
            self.assertEqual(len(pdf.info), 8)
            self.assertEqual(pdf.info.Title, "title")
            self.assertEqual(pdf.info.Author, "author")
            self.assertEqual(pdf.info.Subject, "subject")
            self.assertEqual(pdf.info.Keywords, "keywords")
            self.assertEqual(pdf.info.Creator, "creator")
            self.assertEqual(pdf.info.Producer, "producer")
            self.assertEqual(pdf.info.CreationDate, time.strptime("2000", "%Y"))
            self.assertEqual(pdf.info.ModDate, time.strptime("2001", "%Y"))
            self.check_pdf_pages_consistency(pdf)

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
