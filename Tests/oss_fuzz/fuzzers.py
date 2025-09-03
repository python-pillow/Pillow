from __future__ import annotations

import io
import warnings

from PIL import Image, ImageDraw, ImageFile, ImageFilter, ImageFont


def enable_decompressionbomb_error() -> None:
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    warnings.filterwarnings("ignore")
    warnings.simplefilter("error", Image.DecompressionBombWarning)


def disable_decompressionbomb_error() -> None:
    ImageFile.LOAD_TRUNCATED_IMAGES = False
    warnings.resetwarnings()


def fuzz_image(data: bytes) -> None:
    # This will fail on some images in the corpus, as we have many
    # invalid images in the test suite.
    with Image.open(io.BytesIO(data)) as im:
        im.rotate(45)
        im.filter(ImageFilter.DETAIL)
        im.save(io.BytesIO(), "BMP")


def fuzz_font(data: bytes) -> None:
    wrapper = io.BytesIO(data)
    try:
        font = ImageFont.truetype(wrapper)
    except OSError:
        # Catch pcf/pilfonts/random garbage here. They return
        # different font objects.
        return

    font.getbbox("ABC")
    font.getmask("test text")
    with Image.new(mode="RGBA", size=(200, 200)) as im:
        draw = ImageDraw.Draw(im)
        draw.multiline_textbbox((10, 10), "ABC\nAaaa", font, stroke_width=2)
        draw.text((10, 10), "Test Text", font=font, fill="#000")
