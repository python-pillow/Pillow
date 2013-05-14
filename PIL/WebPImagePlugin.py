from PIL import Image
from PIL import ImageFile
from io import BytesIO
import _webp


_VALID_WEBP_ENCODERS_BY_MODE = {
    "RGB": _webp.WebPEncodeRGB,
    "RGBA": _webp.WebPEncodeRGBA,
    }


_VALID_WEBP_DECODERS_BY_MODE = {
    "RGB": _webp.WebPDecode,
    "RGBA": _webp.WebPDecode,
    }


_STRIDE_MULTIPLIERS_BY_MODE = {
    "RGB": 3,
    "RGBA": 4,
    }


_VP8_MODES_BY_IDENTIFIER = {
    b"VP8 ": "RGB",
    b"VP8X": "RGBA",
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
        data, width, height, self.mode = _webp.WebPDecode(self.fp.read())
        self.size = width, height
        self.fp = BytesIO(data)
        self.tile = [("raw", (0, 0) + self.size, 0, self.mode)]


def _save(im, fp, filename):
    image_mode = im.mode
    if image_mode not in _VALID_WEBP_ENCODERS_BY_MODE:
        raise IOError("cannot write mode %s as WEBP" % image_mode)

    webp_encoder = _VALID_WEBP_ENCODERS_BY_MODE[image_mode]
    
    stride = im.size[0] * _STRIDE_MULTIPLIERS_BY_MODE[image_mode]
    quality = im.encoderinfo.get("quality", 80)
    
    data = webp_encoder(
        im.tobytes(),
        im.size[0],
        im.size[1],
        stride,
        float(quality),
        )
    fp.write(data)


Image.register_open("WEBP", WebPImageFile, _accept)
Image.register_save("WEBP", _save)

Image.register_extension("WEBP", ".webp")
Image.register_mime("WEBP", "image/webp")
