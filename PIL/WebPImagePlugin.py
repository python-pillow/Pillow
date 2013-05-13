from PIL import Image
from PIL import ImageFile
from io import BytesIO
import _webp


_VALID_WEBP_ENCODERS_BY_MODE = {
    "RGB": _webp.WebPEncodeRGB,
    "RGBA": _webp.WebPEncodeRGBA,
    }


_VALID_WEBP_DECODERS_BY_MODE = {
    "RGB": _webp.WebPDecodeRGB,
    "RGBA": _webp.WebPDecodeRGBA,
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
        file_header = self.fp.read(16)
        vp8_header = file_header[12:16]
        try:
            webp_file_mode = _VP8_MODES_BY_IDENTIFIER[vp8_header]
        except KeyError:
            raise IOError("Unknown webp file mode")
        finally:
            self.fp.seek(0)
        
        self.mode = webp_file_mode
        webp_decoder = _VALID_WEBP_DECODERS_BY_MODE[webp_file_mode]
        
        data, width, height = webp_decoder(self.fp.read())
        self.size = width, height
        self.fp = BytesIO(data)
        self.tile = [("raw", (0, 0) + self.size, 0, webp_file_mode)]


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
