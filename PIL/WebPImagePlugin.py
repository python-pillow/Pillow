import Image
import ImageFile
import StringIO
import _webp

def _accept(prefix):
    return prefix[:4] == "RIFF" and prefix[8:16] == "WEBPVP8 "

class WebPImageFile(ImageFile.ImageFile):

    format = "WEBP"
    format_description = "WebP image"

    def _open(self):
        self.mode = "RGB"
        data, width, height = _webp.WebPDecodeRGB(self.fp.read())
        self.size = width, height
        self.fp = StringIO.StringIO(data)
        self.tile = [("raw", (0, 0) + self.size, 0, 'RGB')]

def _save(im, fp, filename):
    if im.mode != "RGB":
        raise IOError("cannot write mode %s as WEBP" % im.mode)
    quality = im.encoderinfo.get("quality", 80)
    
    data = _webp.WebPEncodeRGB(im.tostring(), im.size[0], im.size[1], im.size[0] * 3, float(quality))
    fp.write(data)

Image.register_open("WEBP", WebPImageFile, _accept)
Image.register_save("WEBP", _save)

Image.register_extension("WEBP", ".webp")
Image.register_mime("WEBP", "image/webp")
