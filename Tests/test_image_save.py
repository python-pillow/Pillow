from __future__ import annotations

from io import BytesIO

from PIL import Image, features


def test_image_save() -> None:
    # Some extensions specify the mode, and not all file objects are named.
    im = Image.new("RGBA", (1, 1))
    out = BytesIO()
    im.save(out, format=".bw")
    im = Image.open(out)
    assert im.mode == "L"

    # This works:
    Image.new("LAB", (1, 1)).convert("RGBA").convert("PA")
    # But this fails on internal convert to RGBA:
    # Image.new('LAB', (1,1)).convert('PA')

    for format in Image.SAVE.keys():
        if format in ("JPEG2000", "PDF") and not features.check_codec("jpg_2000"):
            # A test skip for this is logged elsewhere.
            continue
        for mode in Image.MODES:
            im = Image.new(mode, (1, 1))
            out = BytesIO()
            try:
                im.save(out, format=format)
            except Exception as ex:
                msg = f"Mode {mode} to format {format}: {ex}"
                if "handler not installed" in str(ex):
                    print(msg)
                else:
                    raise Exception(msg)
