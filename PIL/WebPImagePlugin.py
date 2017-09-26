from . import Image, ImageFile, _webp
from io import BytesIO


_VALID_WEBP_MODES = {
    "RGB": True,
    "RGBA": True,
    }

_VP8_MODES_BY_IDENTIFIER = {
    b"VP8 ": "RGB",
    b"VP8X": "RGBA",
    b"VP8L": "RGBA",  # lossless
    }


def _accept(prefix):
    is_riff_file_format = prefix[:4] == b"RIFF"
    is_webp_file = prefix[8:12] == b"WEBP"
    is_valid_vp8_mode = prefix[12:16] in _VP8_MODES_BY_IDENTIFIER

    return is_riff_file_format and is_webp_file and is_valid_vp8_mode


class WebPImageFile(ImageFile.ImageFile):

    format = "WEBP"
    format_description = "WebP image"

    def _open(self):
        data, width, height, self.mode, icc_profile, exif = \
            _webp.WebPDecode(self.fp.read())

        if icc_profile:
            self.info["icc_profile"] = icc_profile
        if exif:
            self.info["exif"] = exif

        self.size = width, height
        self.fp = BytesIO(data)
        self.tile = [("raw", (0, 0) + self.size, 0, self.mode)]

    def _getexif(self):
        from .JpegImagePlugin import _getexif
        return _getexif(self)


def _save_all(im, fp, filename):
    encoderinfo = im.encoderinfo.copy()
    append_images = encoderinfo.get("append_images", [])
    background = encoderinfo.get("background", (0, 0, 0, 0))
    duration = im.encoderinfo.get("duration", 0)
    loop = im.encoderinfo.get("loop", 0)
    minimize_size = im.encoderinfo.get("minimize_size", False)
    kmin = im.encoderinfo.get("kmin", None)
    kmax = im.encoderinfo.get("kmax", None)
    allow_mixed = im.encoderinfo.get("allow_mixed", False)
    verbose = False
    lossless = im.encoderinfo.get("lossless", False)
    quality = im.encoderinfo.get("quality", 80)
    method = im.encoderinfo.get("method", 0)
    icc_profile = im.encoderinfo.get("icc_profile", "")
    exif = im.encoderinfo.get("exif", "")
    if allow_mixed:
        lossless = False

    # Sensible keyframe defaults are from gif2webp.c script
    if kmin is None:
        kmin = 9 if lossless else 3
    if kmax is None:
        kmax = 17 if lossless else 5

    # Validate background color
    if (not isinstance(background, (list, tuple)) or len(background) != 4 or
            not all(v >= 0 and v < 256 for v in background)):
        raise IOError("Background color is not an RGBA tuple clamped to (0-255): %s" % str(background))
    bg_r, bg_g, bg_b, bg_a = background
    background = (bg_a << 24) | (bg_r << 16) | (bg_g << 8) | (bg_b << 0) # Convert to packed uint

    # Setup the WebP animation encoder
    enc = _webp.WebPAnimEncoder(
        im.size[0], im.size[1],
        background,
        loop,
        minimize_size,
        kmin, kmax,
        allow_mixed,
        verbose
    )

    # Add each frame
    frame_idx = 0
    timestamp = 0
    cur_idx = im.tell()
    try:
        for ims in [im]+append_images:
            # Get # of frames in this image
            if not hasattr(ims, "n_frames"):
                nfr = 1
            else:
                nfr = ims.n_frames

            for idx in range(nfr):
                ims.seek(idx)
                ims.load()

                # Make sure image mode is supported
                frame = ims if ims.mode in _VALID_WEBP_MODES else ims.convert("RGBA")

                # Append the frame to the animation encoder
                enc.add(
                    frame.tobytes(),
                    timestamp,
                    frame.size[0], frame.size[1],
                    frame.mode,
                    lossless,
                    quality,
                    method
                )

                # Update timestamp and frame index
                timestamp += duration[frame_idx] if isinstance(duration, (list, tuple)) else duration
                frame_idx += 1

    finally:
        im.seek(cur_idx)

    # Force encoder to flush frames
    enc.add(
        None,
        timestamp,
        0, 0, "", lossless, quality, 0
    )

    # Get the final output from the encoder
    data = enc.assemble(icc_profile, exif)
    if data is None:
        raise IOError("cannot write file as WEBP (encoder returned None)")

    fp.write(data)


def _save(im, fp, filename):
    image_mode = im.mode
    if im.mode not in _VALID_WEBP_MODES:
        im = im.convert("RGBA")

    lossless = im.encoderinfo.get("lossless", False)
    quality = im.encoderinfo.get("quality", 80)
    icc_profile = im.encoderinfo.get("icc_profile", "")
    exif = im.encoderinfo.get("exif", "")

    data = _webp.WebPEncode(
        im.tobytes(),
        im.size[0],
        im.size[1],
        lossless,
        float(quality),
        im.mode,
        icc_profile,
        exif
    )
    if data is None:
        raise IOError("cannot write file as WEBP (encoder returned None)")

    fp.write(data)


Image.register_open(WebPImageFile.format, WebPImageFile, _accept)
Image.register_save(WebPImageFile.format, _save)
Image.register_save_all(WebPImageFile.format, _save_all)
Image.register_extension(WebPImageFile.format, ".webp")
Image.register_mime(WebPImageFile.format, "image/webp")
