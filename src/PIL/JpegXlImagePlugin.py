from __future__ import annotations

import struct
from io import BytesIO

from . import Image, ImageFile

try:
    from . import _jpegxl

    SUPPORTED = True
except ImportError:
    SUPPORTED = False


## Future idea:
## it's not known how many frames does animated image have
## by default, _jxl_decoder_new will iterate over all frames without decoding them
## then libjxl decoder is rewinded and we're ready to decode frame by frame
## if OPEN_COUNTS_FRAMES is False, n_frames will be None until the last frame is decoded
## it only applies to animated jpeg xl images
# OPEN_COUNTS_FRAMES = True


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
    __loaded = 0
    __logical_frame = 0

    def _open(self) -> None:
        self._decoder = _jpegxl.JpegXlDecoder(self.fp.read())

        (
            self._size,
            self._mode,
            self.is_animated,
            tps_num,
            tps_denom,
            self.info["loop"],
            n_frames,
        ) = self._decoder.get_info()

        self._tps_dur_secs = 1
        self.n_frames: int | None = 1
        if self.is_animated:
            self.n_frames = None
            if n_frames > 0:
                self.n_frames = n_frames
                self._tps_dur_secs = tps_num / tps_denom

        # TODO: handle libjxl time codes
        self.__timestamp = 0

        if icc := self._decoder.get_icc():
            self.info["icc_profile"] = icc
        if exif := self._decoder.get_exif():
            # jpeg xl does some weird shenanigans when storing exif
            # it omits first 6 bytes of tiff header but adds 4 byte offset instead
            if len(exif) > 4:
                exif_start_offset = struct.unpack(">I", exif[:4])[0]
                self.info["exif"] = exif[exif_start_offset + 4 :]
        if xmp := self._decoder.get_xmp():
            self.info["xmp"] = xmp

        self._rewind()

    def _get_next(self) -> tuple[bytes, float, float, bool]:

        # Get next frame
        next_frame = self._decoder.get_next()
        self.__physical_frame += 1

        # this actually means EOF, errors are raised in _jxl
        if next_frame is None:
            msg = "failed to decode next frame in JXL file"
            raise EOFError(msg)

        data, tps_duration, is_last = next_frame
        if is_last and self.n_frames is None:
            # libjxl said this frame is the last one
            self.n_frames = self.__physical_frame

        # duration in miliseconds
        duration = 1000 * tps_duration * (1 / self._tps_dur_secs)
        timestamp = self.__timestamp
        self.__timestamp += duration

        return data, timestamp, duration, is_last

    def _rewind(self, hard: bool = False) -> None:
        if hard:
            self._decoder.rewind()
        self.__physical_frame = 0
        self.__loaded = -1
        self.__timestamp = 0

    def _seek(self, frame: int) -> None:
        if frame == self.__physical_frame:
            return  # Nothing to do
        if frame < self.__physical_frame:
            # also rewind libjxl decoder instance
            self._rewind(hard=True)

        while self.__physical_frame < frame:
            self._get_next()  # Advance to the requested frame

    def seek(self, frame: int) -> None:
        if not self._seek_check(frame):
            return

        # Set logical frame to requested position
        self.__logical_frame = frame

    def load(self) -> Image.core.PixelAccess | None:
        if self.__loaded != self.__logical_frame:
            self._seek(self.__logical_frame)

            data, timestamp, duration, is_last = self._get_next()
            self.info["timestamp"] = timestamp
            self.info["duration"] = duration
            self.__loaded = self.__logical_frame

            # Set tile
            if self.fp and self._exclusive_fp:
                self.fp.close()
            # this is horribly memory inefficient
            # you need probably 2*(raw image plane) bytes of memory
            self.fp = BytesIO(data)
            self.tile = [ImageFile._Tile("raw", (0, 0) + self.size, 0, self.mode)]

        return super().load()

    def load_seek(self, pos: int) -> None:
        pass

    def tell(self) -> int:
        return self.__logical_frame


Image.register_open(JpegXlImageFile.format, JpegXlImageFile, _accept)
Image.register_extension(JpegXlImageFile.format, ".jxl")
Image.register_mime(JpegXlImageFile.format, "image/jxl")
