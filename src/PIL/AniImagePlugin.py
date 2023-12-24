from __future__ import annotations

import struct
from io import BytesIO

from PIL import BmpImagePlugin, CurImagePlugin, Image, ImageFile
from PIL._binary import i32le as i32
from PIL._binary import o8
from PIL._binary import o16le as o16
from PIL._binary import o32le as o32


def _accept(s):
    return s[:4] == b"RIFF"


def _save_frame(im: Image.Image, fp: BytesIO, filename: str, info: dict):
    fp.write(b"\0\0\2\0")
    bmp = True
    s = info.get(
        "sizes",
        [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    h = info.get("hotspots", [(0, 0) for _ in range(len(s))])

    if len(h) != len(s):
        msg = "Number of hotspots must be equal to number of cursor sizes"
        raise ValueError(msg)

    # sort and remove duplicate sizes
    sizes, hotspots = [], []
    for size, hotspot in sorted(zip(s, h), key=lambda x: x[0]):
        if size not in sizes:
            sizes.append(size)
            hotspots.append(hotspot)

    frames = []
    width, height = im.size
    for size in sorted(set(sizes)):
        if size[0] > width or size[1] > height or size[0] > 256 or size[1] > 256:
            continue

        # TODO: invent a more convenient method for proportional scalings
        frame = im.copy()
        frame.thumbnail(size, Image.Resampling.LANCZOS, reducing_gap=None)
        frames.append(frame)

    fp.write(o16(len(frames)))  # idCount(2)
    offset = fp.tell() + len(frames) * 16
    for hotspot, frame in zip(hotspots, frames):
        width, height = frame.size
        # 0 means 256
        fp.write(o8(width if width < 256 else 0))  # bWidth(1)
        fp.write(o8(height if height < 256 else 0))  # bHeight(1)

        bits, colors = BmpImagePlugin.SAVE[frame.mode][1:] if bmp else (32, 0)
        fp.write(o8(colors))  # bColorCount(1)
        fp.write(b"\0")  # bReserved(1)
        fp.write(o16(hotspot[0]))  # x_hotspot(2)
        fp.write(o16(hotspot[1]))  # y_hotspot(2)

        image_io = BytesIO()
        if bmp:
            if bits != 32:
                and_mask = Image.new("1", size)
                ImageFile._save(
                    and_mask, image_io, [("raw", (0, 0) + size, 0, ("1", 0, -1))]
                )
            else:
                frame.alpha = True

            frame.save(image_io, "dib")
        else:
            frame.save(image_io, "png")
        image_io.seek(0)
        image_bytes = image_io.read()
        if bmp:
            image_bytes = image_bytes[:8] + o32(height * 2) + image_bytes[12:]

        bytes_len = len(image_bytes)
        fp.write(o32(bytes_len))  # dwBytesInRes(4)
        fp.write(o32(offset))  # dwImageOffset(4)
        current = fp.tell()
        fp.seek(offset)
        fp.write(image_bytes)
        offset = offset + bytes_len
        fp.seek(current)


def _write_single_frame(im: Image.Image, fp: BytesIO, filename: str):
    fp.write(b"anih")
    anih = o32(36) + o32(36) + (o32(1) * 2) + (o32(0) * 4) + o32(60) + o32(1)
    fp.write(anih)

    fp.write(b"LIST" + o32(0))
    list_offset = fp.tell()
    fp.write(b"fram")

    fp.write(b"icon" + o32(0))
    icon_offset = fp.tell()
    with BytesIO(b"") as icon_fp:
        _save_frame(im, icon_fp, filename, im.encoderinfo)
        icon_fp.seek(0)
        icon_data = icon_fp.read()

    fp.write(icon_data)
    fram_end = fp.tell()

    fp.seek(icon_offset - 4)
    icon_size = fram_end - icon_offset
    fp.write(o32(icon_size))

    fp.seek(list_offset - 4)
    list_size = fram_end - list_offset
    fp.write(o32(list_size))

    fp.seek(fram_end)


def _write_multiple_frames(im: Image.Image, fp: BytesIO, filename: str):
    anih_offset = fp.tell()
    fp.write(b"anih" + o32(36))
    fp.write(o32(0) * 9)

    fp.write(b"LIST" + o32(0))
    list_offset = fp.tell()
    fp.write(b"fram")

    frames = [im]
    frames.extend(im.encoderinfo.get("append_images", []))
    for frame in frames:
        fp.write(b"icon" + o32(0))
        icon_offset = fp.tell()
        with BytesIO(b"") as icon_fp:
            _save_frame(frame, icon_fp, filename, im.encoderinfo)
            icon_fp.seek(0)
            icon_data = icon_fp.read()

        fp.write(icon_data)
        fram_end = fp.tell()

        fp.seek(icon_offset - 4)
        icon_size = fram_end - icon_offset
        fp.write(o32(icon_size))

        fp.seek(fram_end)

    fp.seek(list_offset - 4)
    list_size = fram_end - list_offset
    fp.write(o32(list_size))

    fp.seek(fram_end)

    seq = im.encoderinfo.get("seq", [])
    if seq:
        fp.write(b"seq " + o32(0))
        seq_offset = fp.tell()
        for i in seq:
            if i >= len(frames):
                msg = "Sequence index out of animation frame bounds"
                raise ValueError(msg)

            fp.write(o32(i))

        fram_end = fp.tell()
        fp.seek(seq_offset - 4)
        seq_size = fram_end - seq_offset
        fp.write(o32(seq_size))

        fp.seek(fram_end)

    rate = im.encoderinfo.get("rate", [])
    if rate:
        fp.write(b"rate" + o32(0))
        rate_offset = fp.tell()

        if seq:
            if len(rate) != len(seq):
                msg = "Length of rate must match length of sequence"
                raise ValueError(msg)
        else:
            if len(rate) != len(frames):
                msg = "Length of rate must match number of frames"
                raise ValueError(msg)

        for r in rate:
            fp.write(o32(r))

        fram_end = fp.tell()
        fp.seek(rate_offset - 4)
        rate_size = fram_end - rate_offset
        fp.write(o32(rate_size))

        fp.seek(fram_end)

    display_rate = im.encoderinfo.get("display_rate", 2)
    n_frames = len(frames)
    n_steps = len(seq) if seq else n_frames
    flag = 1 if not seq else 3

    fram_end = fp.tell()

    fp.seek(anih_offset)
    fp.write(b"anih")
    anih = (
        o32(36)
        + o32(36)
        + o32(n_frames)
        + o32(n_steps)
        + (o32(0) * 4)
        + o32(display_rate)
        + o32(flag)
    )
    fp.write(anih)

    fp.seek(fram_end)


def _write_info(im: Image.Image, fp: BytesIO, filename: str):
    fp.write(b"LIST" + o32(0))
    list_offset = fp.tell()

    inam = im.encoderinfo.get("inam", filename)
    iart = im.encoderinfo.get("iart", "Pillow")

    if isinstance(inam, str):
        inam = inam.encode()
    if not isinstance(inam, bytes):
        msg = "'inam' argument must be either a string or bytes"
        raise TypeError(msg)

    if isinstance(iart, str):
        iart = iart.encode()
    if not isinstance(iart, bytes):
        msg = "'iart' argument must be either a string or bytes"
        raise TypeError(msg)

    fp.write(b"INFO")
    fp.write(b"INAM" + o32(0))
    inam_offset = fp.tell()

    fp.write(inam + b"\x00")
    inam_size = fp.tell() - inam_offset

    fp.write(b"IART" + o32(0))
    iart_offset = fp.tell()

    fp.write(iart + b"\x00")
    iart_size = fp.tell() - iart_offset

    info_end = fp.tell()

    fp.seek(iart_offset - 4)
    fp.write(o32(iart_size))

    fp.seek(inam_offset - 4)
    fp.write(o32(inam_size))

    fp.seek(list_offset - 4)
    list_size = info_end - list_offset
    fp.write(o32(list_size))

    fp.seek(info_end)


def _save(im: Image.Image, fp: BytesIO, filename: str):
    fp.write(b"RIFF\x00\x00\x00\x00")
    riff_offset = fp.tell()

    fp.write(b"ACON")
    _write_info(im, fp, filename)

    frames = im.encoderinfo.get("append_images", [])
    if frames:
        _write_multiple_frames(im, fp, filename)
    else:
        _write_single_frame(im, fp, filename)
    pass

    riff_end = fp.tell()
    fp.seek(riff_offset - 4)
    riff_size = riff_end - riff_offset
    fp.write(o32(riff_size))

    fp.seek(riff_end)


class AniFile:
    def __init__(self, buf: BytesIO) -> None:
        self.image_data = []

        self.buf = buf
        self.rate = None
        self.seq = None
        self.anih = None

        riff, size, fformat = struct.unpack("<4sI4s", buf.read(12))
        if riff != b"RIFF":
            SyntaxError("Not an ANI file")

        self.riff = {"size": size, "fformat": fformat}

        chunkOffset = buf.tell()
        while chunkOffset < self.riff["size"]:
            buf.seek(chunkOffset)
            chunk, size = struct.unpack("<4sI", buf.read(8))
            chunkOffset = chunkOffset + size + 8

            if chunk == b"anih":
                s = buf.read(36)
                self.anih = {
                    "size": i32(s),  # Data structure size (in bytes)
                    "nFrames": i32(s, 4),  # Number of frames
                    "nSteps": i32(s, 8),  # Number of frames before repeat
                    "iWidth": i32(s, 12),  # Width of frame (in pixels)
                    "iHeight": i32(s, 16),  # Height of frame (in pixels)
                    "iBitCount": i32(s, 20),  # Number of bits per pixel
                    "nPlanes": i32(s, 24),  # Number of color planes
                    # Default frame display rate (1/60th sec)
                    "iDispRate": i32(s, 28),
                    "bfAttributes": i32(s, 32),  # ANI attribute bit flags
                }

            if chunk == b"seq ":
                s = buf.read(size)
                self.seq = [i32(s, i * 4) for i in range(size // 4)]

            if chunk == b"rate":
                s = buf.read(size)
                self.rate = [i32(s, i * 4) for i in range(size // 4)]

            if chunk == b"LIST":
                listtype = struct.unpack("<4s", buf.read(4))[0]
                if listtype != b"fram":
                    continue

                listOffset = 0
                while listOffset < size - 8:
                    _, lSize = struct.unpack("<4sI", buf.read(8))
                    self.image_data.append({"offset": buf.tell(), "size": lSize})

                    buf.read(lSize)
                    listOffset = listOffset + lSize + 8

        if self.anih is None:
            msg = "not an ANI file"
            raise SyntaxError(msg)

        if self.seq is None:
            self.seq = list(range(self.anih["nFrames"]))

        if self.rate is None:
            self.rate = [self.anih["iDispRate"] for i in range(self.anih["nFrames"])]

    def frame(self, frame):
        if frame > self.anih["nFrames"]:
            msg = "Frame index out of animation bounds"
            raise EOFError(msg)

        offset, size = self.image_data[frame].values()
        self.buf.seek(offset)
        data = self.buf.read(size)

        im = CurImagePlugin.CurImageFile(BytesIO(data))
        return im

    def sizes(self):
        return [data["size"] for data in self.image_data]

    def hotspots(self):
        pass


class AniImageFile(ImageFile.ImageFile):
    """
    PIL read-only image support for Microsoft Windows .ani files.

    By default the largest resolution image and first frame in the file will
    be loaded.

    The info dictionary has four keys:
        'seq': the sequence of the frames used for animation.
        'rate': the rate (in 1/60th of a second) for each frame in the sequence.
        'frames': the number of frames in the file.
        'sizes': a list of the sizes available for the current frame.
        'hotspots': a list of the cursor hotspots for a given frame.

    Saving is similar to GIF. Arguments for encoding are:
        'sizes': The sizes of the cursor (used for scaling by windows).
        'hotspots': The hotspot for each size, with (0, 0) being the top left.
        'append_images': The frames for animation. Please note that the sizes and
        hotspots are shared across each frame.
        'seq': The sequence of frames, zero indexed.
        'rate': The rate for each frame in the seq. Must be the same length as seq or
        equal to the number of frames if seq is not passed.
    """

    format = "ANI"
    format_description = "Windows Animated Cursor"

    def _open(self):
        self.ani = AniFile(self.fp)
        self.info["seq"] = self.ani.seq
        self.info["rate"] = self.ani.rate
        self.info["frames"] = self.ani.anih["nFrames"]

        self.frame = 0
        self._min_frame = 0
        self.seek(0)
        self.size = self.im.size

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if value not in self.info["sizes"]:
            msg = "This is not one of the allowed sizes of this image"
            raise ValueError(msg)
        self._size = value

    def load(self):
        im = self.ani.frame(self.frame)
        self.info["sizes"] = im.info["sizes"]
        self.info["hotspots"] = im.info["hotspots"]
        self.im = im.im
        self._mode = im.mode

    def seek(self, frame):
        if frame > self.info["frames"] - 1 or frame < 0:
            msg = "Frame index out of animation bounds"
            raise EOFError(msg)

        self.frame = frame
        self.load()


Image.register_open(AniImageFile.format, AniImageFile, _accept)
Image.register_extension(AniImageFile.format, ".ani")
Image.register_save(AniImageFile.format, _save)
