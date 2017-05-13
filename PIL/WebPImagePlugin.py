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
    preset = im.encoderinfo.get("preset", 0)  # 0:default 1:pict 2:photo 3:draw 4:icon 5:text
    method = im.encoderinfo.get("method", 4)
    target_size = im.encoderinfo.get("target_size", 0)
    target_PSNR = im.encoderinfo.get("target_PSNR", 0.0)
    segments = im.encoderinfo.get("segments", 4)
    sns_strength = im.encoderinfo.get("sns_strength", 50)
    filter_strength = im.encoderinfo.get("filter_strength", 60)
    filter_sharpness = im.encoderinfo.get("filter_sharpness", 0)
    filter_type = im.encoderinfo.get("filter_type", 1)  # 0:simple 1:strong
    autofilter = im.encoderinfo.get("autofilter", False)
    alpha_compression = im.encoderinfo.get("alpha_compression", True)
    alpha_filtering = im.encoderinfo.get("alpha_filtering", 1)  # 0:none 1:fast 2:best
    alpha_quality = im.encoderinfo.get("alpha_quality", 100)
    pass_count = im.encoderinfo.get("pass", 1)  # 1-10
    preprocessing = im.encoderinfo.get("preprocessing", 0)  # 0:none 1:segment-smooth 2:pseudo-random dithering
    partitions = im.encoderinfo.get("partitions", 0)  # 0-3
    partition_limit = im.encoderinfo.get("partition_limit", 0)  # 0-100
    emulate_jpeg_size = im.encoderinfo.get("emulate_jpeg_size", False)
    thread_level = im.encoderinfo.get("thread_level", 0)
    low_memory = im.encoderinfo.get("low_memory", False)

    data = _webp.WebPEncode(
        im.tobytes(),
        im.size[0],
        im.size[1],
        lossless,
        float(quality),
        im.mode,
        icc_profile,
        exif,
        preset,
        method,
        target_size,
        float(target_PSNR),
        segments,
        sns_strength,
        filter_strength,
        filter_sharpness,
        filter_type,
        autofilter,
        alpha_compression,
        alpha_filtering,
        alpha_quality,
        pass_count,
        preprocessing,
        partitions,
        partition_limit,
        emulate_jpeg_size,
        thread_level,
        low_memory
    )
    if data is None:
        raise IOError("cannot write file as WEBP (encoder returned None)")

    fp.write(data)


Image.register_open(WebPImageFile.format, WebPImageFile, _accept)
Image.register_save(WebPImageFile.format, _save)

Image.register_extension(WebPImageFile.format, ".webp")
Image.register_mime(WebPImageFile.format, "image/webp")
