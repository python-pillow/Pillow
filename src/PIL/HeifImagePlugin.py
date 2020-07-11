import io

from . import Image, ImageFile

try:
    import pyheif
except ImportError:
    pyheif = None

def _accept(prefix):
    check = pyheif.check(prefix)
    return check != pyheif.heif_filetype_no


class HeifImageFile(ImageFile.ImageFile):
    format = "HEIF"
    format_description = "HEIF Image File Format"

    def _open(self):
        b = self.fp.read()
        if not _accept(b):
            raise ValueError("Not a HEIF image file")

        heif_file = pyheif.read(b)
        self._size = heif_file.size
        self.mode = heif_file.mode
        self.fp = io.BytesIO(heif_file.data)
        self.tile = [("raw", (0, 0) + heif_file.size, 0, (heif_file.mode, heif_file.stride))]


if pyheif:
    Image.register_open(HeifImageFile.format, HeifImageFile, _accept)
    Image.register_extensions(HeifImageFile.format, [".heif", ".heic", ".hif"])
    Image.register_mime(HeifImageFile.format, "image/heif")
    Image.register_mime(HeifImageFile.format, "image/heic")

