from io import BytesIO

import pytest
from PIL import EpsImagePlugin, Image, ImageFile, features

from .helper import (
    assert_image,
    assert_image_equal,
    assert_image_similar,
    fromstring,
    hopper,
    skip_unless_feature,
    tostring,
)

# save original block sizes
MAXBLOCK = ImageFile.MAXBLOCK
SAFEBLOCK = ImageFile.SAFEBLOCK


class TestImageFile:
    def test_parser(self):
        def roundtrip(format):

            im = hopper("L").resize((1000, 1000), Image.NEAREST)
            if format in ("MSP", "XBM"):
                im = im.convert("1")

            test_file = BytesIO()

            im.copy().save(test_file, format)

            data = test_file.getvalue()

            parser = ImageFile.Parser()
            parser.feed(data)
            imOut = parser.close()

            return im, imOut

        assert_image_equal(*roundtrip("BMP"))
        im1, im2 = roundtrip("GIF")
        assert_image_similar(im1.convert("P"), im2, 1)
        assert_image_equal(*roundtrip("IM"))
        assert_image_equal(*roundtrip("MSP"))
        if features.check("zlib"):
            try:
                # force multiple blocks in PNG driver
                ImageFile.MAXBLOCK = 8192
                assert_image_equal(*roundtrip("PNG"))
            finally:
                ImageFile.MAXBLOCK = MAXBLOCK
        assert_image_equal(*roundtrip("PPM"))
        assert_image_equal(*roundtrip("TIFF"))
        assert_image_equal(*roundtrip("XBM"))
        assert_image_equal(*roundtrip("TGA"))
        assert_image_equal(*roundtrip("PCX"))

        if EpsImagePlugin.has_ghostscript():
            im1, im2 = roundtrip("EPS")
            # This test fails on Ubuntu 12.04, PPC (Bigendian) It
            # appears to be a ghostscript 9.05 bug, since the
            # ghostscript rendering is wonky and the file is identical
            # to that written on ubuntu 12.04 x64
            # md5sum: ba974835ff2d6f3f2fd0053a23521d4a

            # EPS comes back in RGB:
            assert_image_similar(im1, im2.convert("L"), 20)

        if features.check("jpg"):
            im1, im2 = roundtrip("JPEG")  # lossy compression
            assert_image(im1, im2.mode, im2.size)

        with pytest.raises(OSError):
            roundtrip("PDF")

    def test_ico(self):
        with open("Tests/images/python.ico", "rb") as f:
            data = f.read()
        with ImageFile.Parser() as p:
            p.feed(data)
            assert (48, 48) == p.image.size

    @skip_unless_feature("zlib")
    def test_safeblock(self):
        im1 = hopper()

        try:
            ImageFile.SAFEBLOCK = 1
            im2 = fromstring(tostring(im1, "PNG"))
        finally:
            ImageFile.SAFEBLOCK = SAFEBLOCK

        assert_image_equal(im1, im2)

    def test_raise_ioerror(self):
        with pytest.raises(IOError):
            with pytest.warns(DeprecationWarning) as record:
                ImageFile.raise_ioerror(1)
        assert len(record) == 1

    def test_raise_oserror(self):
        with pytest.raises(OSError):
            ImageFile.raise_oserror(1)

    def test_raise_typeerror(self):
        with pytest.raises(TypeError):
            parser = ImageFile.Parser()
            parser.feed(1)

    def test_negative_stride(self):
        with open("Tests/images/raw_negative_stride.bin", "rb") as f:
            input = f.read()
        p = ImageFile.Parser()
        p.feed(input)
        with pytest.raises(OSError):
            p.close()

    @skip_unless_feature("zlib")
    def test_truncated_with_errors(self):
        with Image.open("Tests/images/truncated_image.png") as im:
            with pytest.raises(OSError):
                im.load()

            # Test that the error is raised if loaded a second time
            with pytest.raises(OSError):
                im.load()

    @skip_unless_feature("zlib")
    def test_truncated_without_errors(self):
        with Image.open("Tests/images/truncated_image.png") as im:
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            try:
                im.load()
            finally:
                ImageFile.LOAD_TRUNCATED_IMAGES = False

    @skip_unless_feature("zlib")
    def test_broken_datastream_with_errors(self):
        with Image.open("Tests/images/broken_data_stream.png") as im:
            with pytest.raises(OSError):
                im.load()

    @skip_unless_feature("zlib")
    def test_broken_datastream_without_errors(self):
        with Image.open("Tests/images/broken_data_stream.png") as im:
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            try:
                im.load()
            finally:
                ImageFile.LOAD_TRUNCATED_IMAGES = False


class MockPyDecoder(ImageFile.PyDecoder):
    def decode(self, buffer):
        # eof
        return -1, 0


xoff, yoff, xsize, ysize = 10, 20, 100, 100


class MockImageFile(ImageFile.ImageFile):
    def _open(self):
        self.rawmode = "RGBA"
        self.mode = "RGBA"
        self._size = (200, 200)
        self.tile = [("MOCK", (xoff, yoff, xoff + xsize, yoff + ysize), 32, None)]


class TestPyDecoder:
    def get_decoder(self):
        decoder = MockPyDecoder(None)

        def closure(mode, *args):
            decoder.__init__(mode, *args)
            return decoder

        Image.register_decoder("MOCK", closure)
        return decoder

    def test_setimage(self):
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)
        d = self.get_decoder()

        im.load()

        assert d.state.xoff == xoff
        assert d.state.yoff == yoff
        assert d.state.xsize == xsize
        assert d.state.ysize == ysize

        with pytest.raises(ValueError):
            d.set_as_raw(b"\x00")

    def test_extents_none(self):
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)
        im.tile = [("MOCK", None, 32, None)]
        d = self.get_decoder()

        im.load()

        assert d.state.xoff == 0
        assert d.state.yoff == 0
        assert d.state.xsize == 200
        assert d.state.ysize == 200

    def test_negsize(self):
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)
        im.tile = [("MOCK", (xoff, yoff, -10, yoff + ysize), 32, None)]
        self.get_decoder()

        with pytest.raises(ValueError):
            im.load()

        im.tile = [("MOCK", (xoff, yoff, xoff + xsize, -10), 32, None)]
        with pytest.raises(ValueError):
            im.load()

    def test_oversize(self):
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)
        im.tile = [("MOCK", (xoff, yoff, xoff + xsize + 100, yoff + ysize), 32, None)]
        self.get_decoder()

        with pytest.raises(ValueError):
            im.load()

        im.tile = [("MOCK", (xoff, yoff, xoff + xsize, yoff + ysize + 100), 32, None)]
        with pytest.raises(ValueError):
            im.load()

    def test_no_format(self):
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)
        assert im.format is None
        assert im.get_format_mimetype() is None

    def test_exif_jpeg(self, tmp_path):
        with Image.open("Tests/images/exif-72dpi-int.jpg") as im:  # Little endian
            exif = im.getexif()
            assert 258 not in exif
            assert 40960 in exif
            assert exif[40963] == 450
            assert exif[11] == "gThumb 3.0.1"

            out = str(tmp_path / "temp.jpg")
            exif[258] = 8
            del exif[40960]
            exif[40963] = 455
            exif[11] = "Pillow test"
            im.save(out, exif=exif)
        with Image.open(out) as reloaded:
            reloaded_exif = reloaded.getexif()
            assert reloaded_exif[258] == 8
            assert 40960 not in reloaded_exif
            assert reloaded_exif[40963] == 455
            assert reloaded_exif[11] == "Pillow test"

        with Image.open("Tests/images/no-dpi-in-exif.jpg") as im:  # Big endian
            exif = im.getexif()
            assert 258 not in exif
            assert 40962 in exif
            assert exif[40963] == 200
            assert exif[305] == "Adobe Photoshop CC 2017 (Macintosh)"

            out = str(tmp_path / "temp.jpg")
            exif[258] = 8
            del exif[34665]
            exif[40963] = 455
            exif[305] = "Pillow test"
            im.save(out, exif=exif)
        with Image.open(out) as reloaded:
            reloaded_exif = reloaded.getexif()
            assert reloaded_exif[258] == 8
            assert 34665 not in reloaded_exif
            assert reloaded_exif[40963] == 455
            assert reloaded_exif[305] == "Pillow test"

    @skip_unless_feature("webp")
    @skip_unless_feature("webp_anim")
    def test_exif_webp(self, tmp_path):
        with Image.open("Tests/images/hopper.webp") as im:
            exif = im.getexif()
            assert exif == {}

            out = str(tmp_path / "temp.webp")
            exif[258] = 8
            exif[40963] = 455
            exif[305] = "Pillow test"

            def check_exif():
                with Image.open(out) as reloaded:
                    reloaded_exif = reloaded.getexif()
                    assert reloaded_exif[258] == 8
                    assert reloaded_exif[40963] == 455
                    assert reloaded_exif[305] == "Pillow test"

            im.save(out, exif=exif)
            check_exif()
            im.save(out, exif=exif, save_all=True)
            check_exif()

    def test_exif_png(self, tmp_path):
        with Image.open("Tests/images/exif.png") as im:
            exif = im.getexif()
            assert exif == {274: 1}

            out = str(tmp_path / "temp.png")
            exif[258] = 8
            del exif[274]
            exif[40963] = 455
            exif[305] = "Pillow test"
            im.save(out, exif=exif)

        with Image.open(out) as reloaded:
            reloaded_exif = reloaded.getexif()
            assert reloaded_exif == {258: 8, 40963: 455, 305: "Pillow test"}

    def test_exif_interop(self):
        with Image.open("Tests/images/flower.jpg") as im:
            exif = im.getexif()
            assert exif.get_ifd(0xA005) == {
                1: "R98",
                2: b"0100",
                4097: 2272,
                4098: 1704,
            }
