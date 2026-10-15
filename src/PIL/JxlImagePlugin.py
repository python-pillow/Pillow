#
# The Python Imaging Library.
#
# JPEG XL support for PIL, via the optional ``imagecodecs`` package
# (which bundles libjxl). Without it, opening or saving .jxl files
# raises an error, mirroring how the external pillow-jxl-plugin works.
#
# See the README file for information on usage and redistribution.
#
from __future__ import annotations

import io
from typing import IO

from . import Image, ImageFile

try:
    import imagecodecs

    SUPPORTED = True
except ImportError:
    SUPPORTED = False

_CODESTREAM_MAGIC = b"\xff\x0a"
_CONTAINER_MAGIC = b"\x00\x00\x00\x0cJXL \x0d\x0a\x87\x0a"


def _accept(prefix: bytes) -> bool:
    return prefix.startswith((_CODESTREAM_MAGIC, _CONTAINER_MAGIC))


class JxlImageFile(ImageFile.ImageFile):
    format = "JXL"
    format_description = "JPEG XL"

    def _open(self) -> None:
        if not SUPPORTED:
            msg = "image file could not be opened because JPEG XL support not installed"
            raise SyntaxError(msg)

        assert self.fp is not None
        data = self.fp.read()
        try:
            import numpy as np

            arr = np.asarray(imagecodecs.jpegxl_decode(data))
        except Exception as e:
            msg = "could not decode JPEG XL image"
            raise SyntaxError(msg) from e

        if arr.ndim == 2:
            self._mode = "L"
        elif arr.shape[2] == 3:
            self._mode = "RGB"
        elif arr.shape[2] == 4:
            self._mode = "RGBA"
        else:
            msg = f"unsupported JPEG XL channel count: {arr.shape}"
            raise SyntaxError(msg)

        self._size = arr.shape[1], arr.shape[0]
        # Hand the decoded pixels to Pillow's raw decoder.
        self.fp = io.BytesIO(arr.tobytes())
        self.tile = [ImageFile._Tile("raw", (0, 0, *self._size), 0, (self._mode, 0, 1))]
        self._fp = self.fp


def _save(im: Image.Image, fp: IO[bytes], filename: str | bytes) -> None:
    if not SUPPORTED:
        msg = "JPEG XL support not installed"
        raise ValueError(msg)

    import numpy as np

    if im.mode not in ("L", "RGB", "RGBA"):
        im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
    arr = np.asarray(im)
    lossless = bool(im.info.get("lossless", False))
    encoded = imagecodecs.jpegxl_encode(
        arr,
        lossless=lossless,
        distance=None if lossless else float(im.info.get("distance", 1.0)),
        effort=int(im.info.get("effort", 7)),
    )
    fp.write(bytes(encoded))


Image.register_open(JxlImageFile.format, JxlImageFile, _accept)
Image.register_save(JxlImageFile.format, _save)
Image.register_extension(JxlImageFile.format, ".jxl")
Image.register_mime(JxlImageFile.format, "image/jxl")
