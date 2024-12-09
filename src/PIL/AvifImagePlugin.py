from __future__ import annotations

import os
from io import BytesIO
from typing import IO

from . import ExifTags, Image, ImageFile

try:
    from . import _avif

    SUPPORTED = True
except ImportError:
    SUPPORTED = False

# Decoder options as module globals, until there is a way to pass parameters
# to Image.open (see https://github.com/python-pillow/Pillow/issues/569)
DECODE_CODEC_CHOICE = "auto"
DEFAULT_MAX_THREADS = 0

_VALID_AVIF_MODES = {"RGB", "RGBA"}


def _accept(prefix: bytes) -> bool | str:
    if prefix[4:8] != b"ftyp":
        return False
    major_brand = prefix[8:12]
    if major_brand in (
        # coding brands
        b"avif",
        b"avis",
        # We accept files with AVIF container brands; we can't yet know if
        # the ftyp box has the correct compatible brands, but if it doesn't
        # then the plugin will raise a SyntaxError which Pillow will catch
        # before moving on to the next plugin that accepts the file.
        #
        # Also, because this file might not actually be an AVIF file, we
        # don't raise an error if AVIF support isn't properly compiled.
        b"mif1",
        b"msf1",
    ):
        if not SUPPORTED:
            return (
                "image file could not be identified because AVIF "
                "support not installed"
            )
        return True
    return False


def _get_default_max_threads():
    if DEFAULT_MAX_THREADS:
        return DEFAULT_MAX_THREADS
    if hasattr(os, "sched_getaffinity"):
        return len(os.sched_getaffinity(0))
    else:
        return os.cpu_count() or 1


class AvifImageFile(ImageFile.ImageFile):
    format = "AVIF"
    format_description = "AVIF image"
    __loaded = -1
    __frame = 0

    def load_seek(self, pos: int) -> None:
        pass

    def _open(self) -> None:
        if not SUPPORTED:
            msg = (
                "image file could not be identified because AVIF "
                "support not installed"
            )
            raise SyntaxError(msg)

        if DECODE_CODEC_CHOICE != "auto" and not _avif.decoder_codec_available(
            DECODE_CODEC_CHOICE
        ):
            msg = "Invalid opening codec"
            raise ValueError(msg)
        self._decoder = _avif.AvifDecoder(
            self.fp.read(),
            DECODE_CODEC_CHOICE,
            _get_default_max_threads(),
        )

        # Get info from decoder
        width, height, n_frames, mode, icc, exif, xmp, exif_orientation = (
            self._decoder.get_info()
        )
        self._size = width, height
        self.n_frames = n_frames
        self.is_animated = self.n_frames > 1
        self._mode = mode

        if icc:
            self.info["icc_profile"] = icc
        if exif:
            self.info["exif"] = exif
        if xmp:
            self.info["xmp"] = xmp

        if exif_orientation != 1 or exif is not None:
            exif_data = Image.Exif()
            orig_orientation = 1
            if exif is not None:
                exif_data.load(exif)
                orig_orientation = exif_data.get(ExifTags.Base.Orientation, 1)
            if exif_orientation != orig_orientation:
                exif_data[ExifTags.Base.Orientation] = exif_orientation
                self.info["exif"] = exif_data.tobytes()

    def seek(self, frame: int) -> None:
        if not self._seek_check(frame):
            return

        self.__frame = frame

    def load(self) -> Image.core.PixelAccess | None:
        if self.__loaded != self.__frame:
            # We need to load the image data for this frame
            data, timescale, tsp_in_ts, dur_in_ts = self._decoder.get_frame(
                self.__frame
            )
            self.info["timestamp"] = round(1000 * (tsp_in_ts / timescale))
            self.info["duration"] = round(1000 * (dur_in_ts / timescale))
            self.__loaded = self.__frame

            # Set tile
            if self.fp and self._exclusive_fp:
                self.fp.close()
            self.fp = BytesIO(data)
            self.tile = [ImageFile._Tile("raw", (0, 0) + self.size, 0, self.mode)]

        return super().load()

    def tell(self) -> int:
        return self.__frame


def _save_all(im: Image.Image, fp: IO[bytes], filename: str | bytes) -> None:
    _save(im, fp, filename, save_all=True)


def _save(
    im: Image.Image, fp: IO[bytes], filename: str | bytes, save_all: bool = False
) -> None:
    info = im.encoderinfo.copy()
    if save_all:
        append_images = list(info.get("append_images", []))
    else:
        append_images = []

    total = 0
    for ims in [im] + append_images:
        total += getattr(ims, "n_frames", 1)

    is_single_frame = total == 1

    qmin = info.get("qmin", -1)
    qmax = info.get("qmax", -1)
    quality = info.get("quality", 75)
    if not isinstance(quality, int) or quality < 0 or quality > 100:
        msg = "Invalid quality setting"
        raise ValueError(msg)

    duration = info.get("duration", 0)
    subsampling = info.get("subsampling", "4:2:0")
    speed = info.get("speed", 6)
    max_threads = info.get("max_threads", _get_default_max_threads())
    codec = info.get("codec", "auto")
    if codec != "auto" and not _avif.encoder_codec_available(codec):
        msg = "Invalid saving codec"
        raise ValueError(msg)
    range_ = info.get("range", "full")
    tile_rows_log2 = info.get("tile_rows", 0)
    tile_cols_log2 = info.get("tile_cols", 0)
    alpha_premultiplied = bool(info.get("alpha_premultiplied", False))
    autotiling = bool(info.get("autotiling", tile_rows_log2 == tile_cols_log2 == 0))

    icc_profile = info.get("icc_profile", im.info.get("icc_profile"))
    exif = info.get("exif")
    if exif:
        if isinstance(exif, Image.Exif):
            exif_data = exif
            exif = exif.tobytes()
        else:
            exif_data = Image.Exif()
            exif_data.load(exif)
        exif_orientation = exif_data.pop(ExifTags.Base.Orientation, 0)
        if exif_orientation != 0:
            if len(exif_data):
                exif = exif_data.tobytes()
            else:
                exif = None
    else:
        exif_orientation = 0

    xmp = info.get("xmp")

    if isinstance(xmp, str):
        xmp = xmp.encode("utf-8")

    advanced = info.get("advanced")
    if isinstance(advanced, dict):
        advanced = tuple([k, v] for (k, v) in advanced.items())
    if advanced is not None:
        try:
            advanced = tuple(advanced)
        except TypeError:
            invalid = True
        else:
            invalid = all(isinstance(v, tuple) and len(v) == 2 for v in advanced)
        if invalid:
            msg = (
                "advanced codec options must be a dict of key-value string "
                "pairs or a series of key-value two-tuples"
            )
            raise ValueError(msg)
        advanced = tuple(
            (str(k).encode("utf-8"), str(v).encode("utf-8")) for k, v in advanced
        )

    # Setup the AVIF encoder
    enc = _avif.AvifEncoder(
        im.size[0],
        im.size[1],
        subsampling,
        qmin,
        qmax,
        quality,
        speed,
        max_threads,
        codec,
        range_,
        tile_rows_log2,
        tile_cols_log2,
        alpha_premultiplied,
        autotiling,
        icc_profile or b"",
        exif or b"",
        exif_orientation,
        xmp or b"",
        advanced,
    )

    # Add each frame
    frame_idx = 0
    frame_dur = 0
    cur_idx = im.tell()
    try:
        for ims in [im] + append_images:
            # Get # of frames in this image
            nfr = getattr(ims, "n_frames", 1)

            for idx in range(nfr):
                ims.seek(idx)

                # Make sure image mode is supported
                frame = ims
                rawmode = ims.mode
                if ims.mode not in _VALID_AVIF_MODES:
                    rawmode = "RGBA" if ims.has_transparency_data else "RGB"
                    frame = ims.convert(rawmode)

                # Update frame duration
                if isinstance(duration, (list, tuple)):
                    frame_dur = duration[frame_idx]
                else:
                    frame_dur = duration

                # Append the frame to the animation encoder
                enc.add(
                    frame.tobytes("raw", rawmode),
                    frame_dur,
                    frame.size[0],
                    frame.size[1],
                    rawmode,
                    is_single_frame,
                )

                # Update frame index
                frame_idx += 1

                if not save_all:
                    break

    finally:
        im.seek(cur_idx)

    # Get the final output from the encoder
    data = enc.finish()
    if data is None:
        msg = "cannot write file as AVIF (encoder returned None)"
        raise OSError(msg)

    fp.write(data)


Image.register_open(AvifImageFile.format, AvifImageFile, _accept)
if SUPPORTED:
    Image.register_save(AvifImageFile.format, _save)
    Image.register_save_all(AvifImageFile.format, _save_all)
    Image.register_extensions(AvifImageFile.format, [".avif", ".avifs"])
    Image.register_mime(AvifImageFile.format, "image/avif")
