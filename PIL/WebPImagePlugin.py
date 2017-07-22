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


def _save(im, fp, filename):
    image_mode = im.mode
    if im.mode not in _VALID_WEBP_MODES:
        raise IOError("cannot write mode %s as WEBP" % image_mode)

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

Image.register_extension(WebPImageFile.format, ".webp")
Image.register_mime(WebPImageFile.format, "image/webp")
