from __future__ import annotations

from io import BytesIO
from typing import Any

import pytest

from PIL import (
    BmpImagePlugin,
    EpsImagePlugin,
    Image,
    ImageFile,
    UnidentifiedImageError,
    _binary,
    features,
)

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
    def test_parser(self) -> None:
        def roundtrip(format: str) -> tuple[Image.Image, Image.Image]:
            im = hopper("L").resize((1000, 1000), Image.Resampling.NEAREST)
            if format in ("MSP", "XBM"):
                im = im.convert("1")

            test_file = BytesIO()

            im.copy().save(test_file, format)

            data = test_file.getvalue()

            parser = ImageFile.Parser()
            parser.feed(data)
            im_out = parser.close()

            return im, im_out

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

    def test_ico(self) -> None:
        with open("Tests/images/python.ico", "rb") as f:
            data = f.read()
        with ImageFile.Parser() as p:
            p.feed(data)
            assert p.image is not None
            assert (48, 48) == p.image.size

    @pytest.mark.filterwarnings("ignore:Corrupt EXIF data")
    def test_incremental_tiff(self) -> None:
        with ImageFile.Parser() as p:
            with open("Tests/images/hopper.tif", "rb") as f:
                p.feed(f.read(1024))

                # Check that insufficient data was given in the first feed
                assert not p.image

                p.feed(f.read())
            assert p.image is not None
            assert (128, 128) == p.image.size

    @skip_unless_feature("webp")
    def test_incremental_webp(self) -> None:
        with ImageFile.Parser() as p:
            with open("Tests/images/hopper.webp", "rb") as f:
                p.feed(f.read(1024))

                # Check that insufficient data was given in the first feed
                assert not p.image

                p.feed(f.read())
            assert p.image is not None
            assert (128, 128) == p.image.size

    @skip_unless_feature("zlib")
    def test_safeblock(self) -> None:
        im1 = hopper()

        try:
            ImageFile.SAFEBLOCK = 1
            im2 = fromstring(tostring(im1, "PNG"))
        finally:
            ImageFile.SAFEBLOCK = SAFEBLOCK

        assert_image_equal(im1, im2)

    def test_tile_size(self) -> None:
        with open("Tests/images/hopper.tif", "rb") as im_fp:
            data = im_fp.read()

        reads = []

        class FP(BytesIO):
            def read(self, size: int | None = None) -> bytes:
                reads.append(size)
                return super().read(size)

        fp = FP(data)
        with Image.open(fp) as im:
            assert len(im.tile) == 7

            im.load()

        # Despite multiple tiles, assert only one tile caused a read of maxblock size
        assert reads.count(im.decodermaxblock) == 1

    def test_raise_typeerror(self) -> None:
        with pytest.raises(TypeError):
            parser = ImageFile.Parser()
            parser.feed(1)  # type: ignore[arg-type]

    def test_negative_stride(self) -> None:
        with open("Tests/images/raw_negative_stride.bin", "rb") as f:
            input = f.read()
        p = ImageFile.Parser()
        p.feed(input)
        with pytest.raises(OSError):
            p.close()

    def test_negative_offset(self) -> None:
        with Image.open("Tests/images/raw_negative_stride.bin") as im:
            with pytest.raises(ValueError, match="Tile offset cannot be negative"):
                im.load()

    def test_no_format(self) -> None:
        buf = BytesIO(b"\x00" * 255)

        class DummyImageFile(ImageFile.ImageFile):
            def _open(self) -> None:
                self._mode = "RGB"
                self._size = (1, 1)

        im = DummyImageFile(buf)
        assert im.format is None
        assert im.get_format_mimetype() is None

    def test_oserror(self) -> None:
        im = Image.new("RGB", (1, 1))
        with pytest.raises(OSError):
            im.save(BytesIO(), "JPEG2000", num_resolutions=2)

    def test_truncated(self) -> None:
        b = BytesIO(
            b"BM000000000000"  # head_data
            + _binary.o32le(
                ImageFile.SAFEBLOCK + 1 + 4
            )  # header_size, so BmpImagePlugin will try to read SAFEBLOCK + 1 bytes
            + (
                b"0" * ImageFile.SAFEBLOCK
            )  # only SAFEBLOCK bytes, so that the header is truncated
        )
        with pytest.raises(OSError, match="Truncated File Read"):
            BmpImagePlugin.BmpImageFile(b)

    @skip_unless_feature("zlib")
    def test_truncated_with_errors(self) -> None:
        with Image.open("Tests/images/truncated_image.png") as im:
            with pytest.raises(OSError):
                im.load()

            # Test that the error is raised if loaded a second time
            with pytest.raises(OSError):
                im.load()

    @skip_unless_feature("zlib")
    def test_truncated_without_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with Image.open("Tests/images/truncated_image.png") as im:
            monkeypatch.setattr(ImageFile, "LOAD_TRUNCATED_IMAGES", True)
            im.load()

    @skip_unless_feature("zlib")
    def test_broken_datastream_with_errors(self) -> None:
        with Image.open("Tests/images/broken_data_stream.png") as im:
            with pytest.raises(OSError):
                im.load()

    @skip_unless_feature("zlib")
    def test_broken_datastream_without_errors(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        with Image.open("Tests/images/broken_data_stream.png") as im:
            monkeypatch.setattr(ImageFile, "LOAD_TRUNCATED_IMAGES", True)
            im.load()


class MockPyDecoder(ImageFile.PyDecoder):
    last: MockPyDecoder

    def __init__(self, mode: str, *args: Any) -> None:
        MockPyDecoder.last = self

        super().__init__(mode, *args)

    def decode(self, buffer: bytes | Image.SupportsArrayInterface) -> tuple[int, int]:
        # eof
        return -1, 0


class MockPyEncoder(ImageFile.PyEncoder):
    last: MockPyEncoder | None

    def __init__(self, mode: str, *args: Any) -> None:
        MockPyEncoder.last = self

        super().__init__(mode, *args)

    def encode(self, bufsize: int) -> tuple[int, int, bytes]:
        return 1, 1, b""

    def cleanup(self) -> None:
        self.cleanup_called = True


xoff, yoff, xsize, ysize = 10, 20, 100, 100


class MockImageFile(ImageFile.ImageFile):
    def _open(self) -> None:
        self.rawmode = "RGBA"
        self._mode = "RGBA"
        self._size = (200, 200)
        self.tile = [
            ImageFile._Tile("MOCK", (xoff, yoff, xoff + xsize, yoff + ysize), 32, None)
        ]


class CodecsTest:
    @classmethod
    def setup_class(cls) -> None:
        Image.register_decoder("MOCK", MockPyDecoder)
        Image.register_encoder("MOCK", MockPyEncoder)


class TestPyDecoder(CodecsTest):
    def test_setimage(self) -> None:
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)

        im.load()

        assert MockPyDecoder.last.state.xoff == xoff
        assert MockPyDecoder.last.state.yoff == yoff
        assert MockPyDecoder.last.state.xsize == xsize
        assert MockPyDecoder.last.state.ysize == ysize

        with pytest.raises(ValueError):
            MockPyDecoder.last.set_as_raw(b"\x00")

    def test_extents_none(self) -> None:
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)
        im.tile = [ImageFile._Tile("MOCK", None, 32, None)]

        im.load()

        assert MockPyDecoder.last.state.xoff == 0
        assert MockPyDecoder.last.state.yoff == 0
        assert MockPyDecoder.last.state.xsize == 200
        assert MockPyDecoder.last.state.ysize == 200

    def test_negsize(self) -> None:
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)
        im.tile = [ImageFile._Tile("MOCK", (xoff, yoff, -10, yoff + ysize), 32, None)]

        with pytest.raises(ValueError):
            im.load()

        im.tile = [ImageFile._Tile("MOCK", (xoff, yoff, xoff + xsize, -10), 32, None)]
        with pytest.raises(ValueError):
            im.load()

    def test_oversize(self) -> None:
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)
        im.tile = [
            ImageFile._Tile(
                "MOCK", (xoff, yoff, xoff + xsize + 100, yoff + ysize), 32, None
            )
        ]

        with pytest.raises(ValueError):
            im.load()

        im.tile = [
            ImageFile._Tile(
                "MOCK", (xoff, yoff, xoff + xsize, yoff + ysize + 100), 32, None
            )
        ]
        with pytest.raises(ValueError):
            im.load()

    def test_decode(self) -> None:
        decoder = ImageFile.PyDecoder("")
        with pytest.raises(NotImplementedError):
            decoder.decode(b"")


class TestPyEncoder(CodecsTest):
    def test_setimage(self) -> None:
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)

        fp = BytesIO()
        ImageFile._save(
            im,
            fp,
            [
                ImageFile._Tile(
                    "MOCK", (xoff, yoff, xoff + xsize, yoff + ysize), 0, "RGB"
                )
            ],
        )

        assert MockPyEncoder.last
        assert MockPyEncoder.last.state.xoff == xoff
        assert MockPyEncoder.last.state.yoff == yoff
        assert MockPyEncoder.last.state.xsize == xsize
        assert MockPyEncoder.last.state.ysize == ysize

    def test_extents_none(self) -> None:
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)
        im.tile = [ImageFile._Tile("MOCK", None, 32, None)]

        fp = BytesIO()
        ImageFile._save(im, fp, [ImageFile._Tile("MOCK", None, 0, "RGB")])

        assert MockPyEncoder.last
        assert MockPyEncoder.last.state.xoff == 0
        assert MockPyEncoder.last.state.yoff == 0
        assert MockPyEncoder.last.state.xsize == 200
        assert MockPyEncoder.last.state.ysize == 200

    def test_negsize(self) -> None:
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)

        fp = BytesIO()
        MockPyEncoder.last = None
        with pytest.raises(ValueError):
            ImageFile._save(
                im,
                fp,
                [ImageFile._Tile("MOCK", (xoff, yoff, -10, yoff + ysize), 0, "RGB")],
            )
        last: MockPyEncoder | None = MockPyEncoder.last
        assert last
        assert last.cleanup_called

        with pytest.raises(ValueError):
            ImageFile._save(
                im,
                fp,
                [ImageFile._Tile("MOCK", (xoff, yoff, xoff + xsize, -10), 0, "RGB")],
            )

    def test_oversize(self) -> None:
        buf = BytesIO(b"\x00" * 255)

        im = MockImageFile(buf)

        fp = BytesIO()
        with pytest.raises(ValueError):
            ImageFile._save(
                im,
                fp,
                [
                    ImageFile._Tile(
                        "MOCK", (xoff, yoff, xoff + xsize + 100, yoff + ysize), 0, "RGB"
                    )
                ],
            )

        with pytest.raises(ValueError):
            ImageFile._save(
                im,
                fp,
                [
                    ImageFile._Tile(
                        "MOCK", (xoff, yoff, xoff + xsize, yoff + ysize + 100), 0, "RGB"
                    )
                ],
            )

    def test_encode(self) -> None:
        encoder = ImageFile.PyEncoder("")
        with pytest.raises(NotImplementedError):
            encoder.encode(0)

        bytes_consumed, errcode = encoder.encode_to_pyfd()
        assert bytes_consumed == 0
        assert ImageFile.ERRORS[errcode] == "bad configuration"

        encoder._pushes_fd = True
        with pytest.raises(NotImplementedError):
            encoder.encode_to_pyfd()

        with pytest.raises(NotImplementedError):
            encoder.encode_to_file(0, 0)

    def test_zero_height(self) -> None:
        with pytest.raises(UnidentifiedImageError):
            Image.open("Tests/images/zero_height.j2k")
