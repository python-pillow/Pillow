from helper import unittest, PillowTestCase
from PIL import Image, ImageFont, ImageDraw


image_font_installed = True
try:
    ImageFont.core.getfont
except ImportError:
    image_font_installed = False


@unittest.skipIf(not image_font_installed, "image font not installed")
class TestImageFontBitmap(PillowTestCase):
    def test_similar(self):
        text = 'EmbeddedBitmap'
        font_outline = ImageFont.truetype(
            font='Tests/fonts/DejaVuSans.ttf', size=24)
        font_bitmap = ImageFont.truetype(
            font='Tests/fonts/DejaVuSans-bitmap.ttf', size=24)
        size_outline = font_outline.getsize(text)
        size_bitmap = font_bitmap.getsize(text)
        size_final = max(size_outline[0], size_bitmap[0]), max(size_outline[1], size_bitmap[1])
        im_bitmap = Image.new('RGB', size_final, (255, 255, 255))
        im_outline = im_bitmap.copy()
        draw_bitmap = ImageDraw.Draw(im_bitmap)
        draw_outline = ImageDraw.Draw(im_outline)

        # Metrics are different on the bitmap and ttf fonts,
        # more so on some platforms and versions of freetype than others.
        # Mac has a 1px difference, linux doesn't.
        draw_bitmap.text((0, size_final[1] - size_bitmap[1]),
                         text, fill=(0, 0, 0), font=font_bitmap)
        draw_outline.text((0, size_final[1] - size_outline[1]),
                          text, fill=(0, 0, 0), font=font_outline)
        self.assert_image_similar(im_bitmap, im_outline, 20)

if __name__ == '__main__':
    unittest.main()
