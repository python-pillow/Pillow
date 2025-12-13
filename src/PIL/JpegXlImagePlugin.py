from __future__ import annotations

import struct
from io import BytesIO

from . import Image, ImageFile

try:
    from . import _jpegxl

    SUPPORTED = True
except ImportError:
    SUPPORTED = False


def _accept(prefix: bytes) -> bool | str:
    is_jxl = prefix.startswith(
        (b"\xff\x0a", b"\x00\x00\x00\x0c\x4a\x58\x4c\x20\x0d\x0a\x87\x0a")
    )
    if is_jxl and not SUPPORTED:
        return "image file could not be identified because JXL support not installed"
    return is_jxl


class JpegXlImageFile(ImageFile.ImageFile):
    format = "JPEG XL"
    format_description = "JPEG XL image"
    __frame = 0

    def _open(self) -> None:
        self._decoder = _jpegxl.JpegXlDecoder(self.fp.read())

        (
            self._size,
            self._mode,
            self.is_animated,
            tps_num,
            tps_denom,
            self.info["loop"],
            tps_duration,
        ) = self._decoder.get_info()

        self._n_frames = None if self.is_animated else 1
        self._tps_dur_secs = tps_num / tps_denom if tps_denom != 0 else 1
        self.info["duration"] = 1000 * tps_duration * (1 / self._tps_dur_secs)

        # TODO: handle libjxl time codes
        self.info["timestamp"] = 0

        if icc := self._decoder.get_icc():
            self.info["icc_profile"] = icc
        if exif := self._decoder.get_exif():
            # JPEG XL does some weird shenanigans when storing exif
            # it omits first 6 bytes of tiff header but adds 4 byte offset instead
            if len(exif) > 4:
                exif_start_offset = struct.unpack(">I", exif[:4])[0]
                self.info["exif"] = exif[exif_start_offset + 4 :]
        if xmp := self._decoder.get_xmp():
            self.info["xmp"] = xmp
        self.tile = [ImageFile._Tile("raw", (0, 0) + self.size, 0, self.mode)]

    @property
    def n_frames(self) -> int:
        if self._n_frames is None:
            current = self.tell()
            self._n_frames = current + self._decoder.get_frames_left()
            self.seek(current)

        return self._n_frames

    def _get_next(self) -> bytes:
        data, tps_duration, is_last = self._decoder.get_next()

        if is_last and self._n_frames is None:
            self._n_frames = self.__frame

        # duration in milliseconds
        self.info["timestamp"] += self.info["duration"]
        self.info["duration"] = 1000 * tps_duration * (1 / self._tps_dur_secs)

        return data

    def seek(self, frame: int) -> None:
        if not self._seek_check(frame):
            return

        if frame < self.__frame:
            self.__frame = 0
            self._decoder.rewind()
            self.info["timestamp"] = 0

        last_frame = self.__frame
        while self.__frame < frame:
            self._get_next()
            self.__frame += 1
            if self._n_frames is not None and self._n_frames < frame:
                self.seek(last_frame)
                msg = "no more images in JPEG XL file"
                raise EOFError(msg)

        self.tile = [ImageFile._Tile("raw", (0, 0) + self.size, 0, self.mode)]

    def load(self) -> Image.core.PixelAccess | None:
        if self.tile:
            data = self._get_next()

            if self.fp and self._exclusive_fp:
                self.fp.close()
            self.fp = BytesIO(data)

        return super().load()

    def load_seek(self, pos: int) -> None:
        pass

    def tell(self) -> int:
        return self.__frame


Image.register_open(JpegXlImageFile.format, JpegXlImageFile, _accept)
Image.register_extension(JpegXlImageFile.format, ".jxl")
Image.register_mime(JpegXlImageFile.format, "image/jxl")
