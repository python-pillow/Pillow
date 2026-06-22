from __future__ import annotations

from io import BytesIO

from PIL import Image, features


def test_image_save() -> None:
    # Some extensions specify the mode, and not all file objects are named.
    im = Image.new("RGBA", (1, 1))
    out = BytesIO()
    im.save(out, format=".bw")
    with Image.open(out) as reloaded:
        assert reloaded.mode == "L"

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
                    break
                else:
                    raise Exception(msg)


def test_image_save_all() -> None:
    ims = [Image.new(mode, (1, 1)) for mode in Image.MODES]
    for format in Image.SAVE_ALL.keys():
        if format in ("JPEG2000", "PDF") and not features.check_codec("jpg_2000"):
            # A test skip for this is logged elsewhere.
            continue
        out = BytesIO()
        try:
            ims[0].save(out, format=format, append_images=ims)
        except Exception as ex:
            msg = f"Multiframe to format {format}: {ex}"
            raise Exception(msg)
