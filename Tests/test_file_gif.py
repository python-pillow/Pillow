from __future__ import annotations

import warnings
from collections.abc import Generator
from io import BytesIO
from pathlib import Path
from typing import Any

import pytest

from PIL import GifImagePlugin, Image, ImageDraw, ImagePalette, ImageSequence, features

from .helper import (
    assert_image_equal,
    assert_image_equal_tofile,
    assert_image_similar,
    hopper,
    is_pypy,
    netpbm_available,
)

# sample gif stream
TEST_GIF = "Tests/images/hopper.gif"


def test_sanity() -> None:
    with Image.open(TEST_GIF) as im:
        im.load()
        assert im.mode == "P"
        assert im.size == (128, 128)
        assert im.format == "GIF"
        assert im.info["version"] == b"GIF89a"


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file() -> None:
    def open_test_image() -> None:
        im = Image.open(TEST_GIF)
        im.load()

    with pytest.warns(ResourceWarning):
        open_test_image()


def test_closed_file() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        im = Image.open(TEST_GIF)
        im.load()
        im.close()


def test_seek_after_close() -> None:
    im = Image.open("Tests/images/iss634.gif")
    assert isinstance(im, GifImagePlugin.GifImageFile)
    im.load()
    im.close()

    with pytest.raises(ValueError):
        im.is_animated
    with pytest.raises(ValueError):
        im.n_frames
    with pytest.raises(ValueError):
        im.seek(1)


def test_context_manager() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        with Image.open(TEST_GIF) as im:
            im.load()


def test_invalid_file() -> None:
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        GifImagePlugin.GifImageFile(invalid_file)


def test_l_mode_transparency() -> None:
    with Image.open("Tests/images/no_palette_with_transparency.gif") as im:
        assert im.mode == "L"
        assert im.getpixel((0, 0)) == 128
        assert im.info["transparency"] == 255

        im.seek(1)
        assert im.mode == "L"
        assert im.getpixel((0, 0)) == 128


def test_l_mode_after_rgb() -> None:
    with Image.open("Tests/images/no_palette_after_rgb.gif") as im:
        im.seek(1)
        assert im.mode == "RGB"

        im.seek(2)
        assert im.mode == "RGB"


def test_l_mode_transparency_after_rgb() -> None:
    with Image.open("Tests/images/no_palette_with_transparency_after_rgb.gif") as im:
        expected = im.convert("RGB")
        d = ImageDraw.Draw(expected)
        d.rectangle([(0, 0), (64, 128)], fill="#000")

        im.seek(1)
        assert im.mode == "RGB"

        assert_image_equal(im, expected)


def test_palette_not_needed_for_second_frame() -> None:
    with Image.open("Tests/images/palette_not_needed_for_second_frame.gif") as im:
        im.seek(1)
        assert_image_similar(im, hopper("L").convert("RGB"), 8)


def test_strategy(monkeypatch: pytest.MonkeyPatch) -> None:
    with Image.open("Tests/images/iss634.gif") as im:
        expected_rgb_always = im.convert("RGB")

    with Image.open("Tests/images/chi.gif") as im:
        expected_rgb_always_rgba = im.convert("RGBA")

        im.seek(1)
        expected_different = im.convert("RGB")

    monkeypatch.setattr(
        GifImagePlugin, "LOADING_STRATEGY", GifImagePlugin.LoadingStrategy.RGB_ALWAYS
    )
    with Image.open("Tests/images/iss634.gif") as im:
        assert im.mode == "RGB"
        assert_image_equal(im, expected_rgb_always)

    with Image.open("Tests/images/chi.gif") as im:
        assert im.mode == "RGBA"
        assert_image_equal(im, expected_rgb_always_rgba)

    monkeypatch.setattr(
        GifImagePlugin,
        "LOADING_STRATEGY",
        GifImagePlugin.LoadingStrategy.RGB_AFTER_DIFFERENT_PALETTE_ONLY,
    )
    # Stay in P mode with only a global palette
    with Image.open("Tests/images/chi.gif") as im:
        assert im.mode == "P"

        im.seek(1)
        assert im.mode == "P"
        assert_image_equal(im.convert("RGB"), expected_different)

    # Change to RGB mode when a frame has an individual palette
    with Image.open("Tests/images/iss634.gif") as im:
        assert im.mode == "P"

        im.seek(1)
        assert im.mode == "RGB"


def test_optimize() -> None:
    def test_grayscale(optimize: int) -> int:
        im = Image.new("L", (1, 1), 0)
        filename = BytesIO()
        im.save(filename, "GIF", optimize=optimize)
        return len(filename.getvalue())

    def test_bilevel(optimize: int) -> int:
        im = Image.new("1", (1, 1), 0)
        test_file = BytesIO()
        im.save(test_file, "GIF", optimize=optimize)
        return len(test_file.getvalue())

    assert test_grayscale(0) == 799
    assert test_grayscale(1) == 43
    assert test_bilevel(0) == 799
    assert test_bilevel(1) == 799


@pytest.mark.parametrize(
    "colors, size, expected_palette_length",
    (
        # These do optimize the palette
        (256, 511, 256),
        (255, 511, 255),
        (129, 511, 129),
        (128, 511, 128),
        (64, 511, 64),
        (4, 511, 4),
        # These don't optimize the palette
        (128, 513, 256),
        (64, 513, 256),
        (4, 513, 256),
    ),
)
def test_optimize_correctness(
    colors: int, size: int, expected_palette_length: int
) -> None:
    # 256 color Palette image, posterize to > 128 and < 128 levels.
    # Size bigger and smaller than 512x512.
    # Check the palette for number of colors allocated.
    # Check for correctness after conversion back to RGB.

    # make an image with empty colors in the start of the palette range
    im = Image.frombytes(
        "P", (colors, colors), bytes(range(256 - colors, 256)) * colors
    )
    im = im.resize((size, size))
    outfile = BytesIO()
    im.save(outfile, "GIF")
    outfile.seek(0)
    with Image.open(outfile) as reloaded:
        # check palette length
        palette_length = max(i + 1 for i, v in enumerate(reloaded.histogram()) if v)
        assert expected_palette_length == palette_length

        assert_image_equal(im.convert("RGB"), reloaded.convert("RGB"))


def test_optimize_full_l() -> None:
    im = Image.frombytes("L", (16, 16), bytes(range(256)))
    test_file = BytesIO()
    im.save(test_file, "GIF", optimize=True)
    assert im.mode == "L"


def test_optimize_if_palette_can_be_reduced_by_half() -> None:
    im = Image.new("P", (8, 1))
    im.palette = ImagePalette.raw("RGB", bytes((0, 0, 0) * 150))
    for i in range(8):
        im.putpixel((i, 0), (i + 1, 0, 0))

    for optimize, colors in ((False, 256), (True, 8)):
        out = BytesIO()
        im.save(out, "GIF", optimize=optimize)
        with Image.open(out) as reloaded:
            assert reloaded.palette is not None
            assert len(reloaded.palette.palette) // 3 == colors


def test_full_palette_second_frame(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"
    im = Image.new("P", (1, 256))

    full_palette_im = Image.new("P", (1, 256))
    for i in range(256):
        full_palette_im.putpixel((0, i), i)
    full_palette_im.palette = ImagePalette.ImagePalette(
        "RGB", bytearray(i // 3 for i in range(768))
    )
    full_palette_im.palette.dirty = 1

    im.save(out, save_all=True, append_images=[full_palette_im])

    with Image.open(out) as reloaded:
        reloaded.seek(1)

        for i in range(256):
            reloaded.getpixel((0, i)) == i


def test_roundtrip(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"
    im = hopper()
    im.save(out)
    with Image.open(out) as reread:
        assert_image_similar(reread.convert("RGB"), im, 50)


def test_roundtrip2(tmp_path: Path) -> None:
    # see https://github.com/python-pillow/Pillow/issues/403
    out = tmp_path / "temp.gif"
    with Image.open(TEST_GIF) as im:
        im2 = im.copy()
        im2.save(out)
    with Image.open(out) as reread:
        assert_image_similar(reread.convert("RGB"), hopper(), 50)


def test_roundtrip_save_all(tmp_path: Path) -> None:
    # Single frame image
    out = tmp_path / "temp.gif"
    im = hopper()
    im.save(out, save_all=True)
    with Image.open(out) as reread:
        assert_image_similar(reread.convert("RGB"), im, 50)

    # Multiframe image
    with Image.open("Tests/images/dispose_bgnd.gif") as im:
        out = tmp_path / "temp.gif"
        im.save(out, save_all=True)

    with Image.open(out) as reread:
        assert reread.n_frames == 5


def test_roundtrip_save_all_1(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"
    im = Image.new("1", (1, 1))
    im2 = Image.new("1", (1, 1), 1)
    im.save(out, save_all=True, append_images=[im2])

    with Image.open(out) as reloaded:
        assert reloaded.getpixel((0, 0)) == 0

        reloaded.seek(1)
        assert reloaded.getpixel((0, 0)) == 255


@pytest.mark.parametrize(
    "path, mode",
    (
        ("Tests/images/dispose_bgnd.gif", "RGB"),
        # Hexeditted copy of dispose_bgnd to add transparency
        ("Tests/images/dispose_bgnd_rgba.gif", "RGBA"),
    ),
)
def test_loading_multiple_palettes(path: str, mode: str) -> None:
    with Image.open(path) as im:
        assert im.mode == "P"
        assert im.palette is not None
        first_frame_colors = im.palette.colors.keys()
        original_color = im.convert("RGB").getpixel((0, 0))

        im.seek(1)
        assert im.mode == mode
        if mode == "RGBA":
            im = im.convert("RGB")

        # Check a color only from the old palette
        assert im.getpixel((0, 0)) == original_color

        # Check a color from the new palette
        assert im.getpixel((24, 24)) not in first_frame_colors


def test_headers_saving_for_animated_gifs(tmp_path: Path) -> None:
    important_headers = ["background", "version", "duration", "loop"]
    # Multiframe image
    with Image.open("Tests/images/dispose_bgnd.gif") as im:
        info = im.info.copy()

        out = tmp_path / "temp.gif"
        im.save(out, save_all=True)
    with Image.open(out) as reread:
        for header in important_headers:
            assert info[header] == reread.info[header]


def test_palette_handling(tmp_path: Path) -> None:
    # see https://github.com/python-pillow/Pillow/issues/513

    with Image.open(TEST_GIF) as im:
        im = im.convert("RGB")

        im = im.resize((100, 100), Image.Resampling.LANCZOS)
        im2 = im.convert("P", palette=Image.Palette.ADAPTIVE, colors=256)

        f = tmp_path / "temp.gif"
        im2.save(f, optimize=True)

    with Image.open(f) as reloaded:
        assert_image_similar(im, reloaded.convert("RGB"), 10)


def test_palette_434(tmp_path: Path) -> None:
    # see https://github.com/python-pillow/Pillow/issues/434

    def roundtrip(im: Image.Image, **kwargs: bool) -> Image.Image:
        out = tmp_path / "temp.gif"
        im.copy().save(out, "GIF", **kwargs)
        reloaded = Image.open(out)

        return reloaded

    orig = "Tests/images/test.colors.gif"
    with Image.open(orig) as im:
        with roundtrip(im) as reloaded:
            assert_image_similar(im, reloaded, 1)
        with roundtrip(im, optimize=True) as reloaded:
            assert_image_similar(im, reloaded, 1)

        im = im.convert("RGB")
        # check automatic P conversion
        with roundtrip(im) as reloaded:
            reloaded = reloaded.convert("RGB")
            assert_image_equal(im, reloaded)


@pytest.mark.skipif(not netpbm_available(), reason="Netpbm not available")
def test_save_netpbm_bmp_mode(tmp_path: Path) -> None:
    with Image.open(TEST_GIF) as img:
        img = img.convert("RGB")

        tempfile = str(tmp_path / "temp.gif")
        b = BytesIO()
        GifImagePlugin._save_netpbm(img, b, tempfile)
        with Image.open(tempfile) as reloaded:
            assert_image_similar(img, reloaded.convert("RGB"), 0)


@pytest.mark.skipif(not netpbm_available(), reason="Netpbm not available")
def test_save_netpbm_l_mode(tmp_path: Path) -> None:
    with Image.open(TEST_GIF) as img:
        img = img.convert("L")

        tempfile = str(tmp_path / "temp.gif")
        b = BytesIO()
        GifImagePlugin._save_netpbm(img, b, tempfile)
        with Image.open(tempfile) as reloaded:
            assert_image_similar(img, reloaded.convert("L"), 0)


def test_seek() -> None:
    with Image.open("Tests/images/dispose_none.gif") as img:
        assert isinstance(img, GifImagePlugin.GifImageFile)
        frame_count = 0
        try:
            while True:
                frame_count += 1
                img.seek(img.tell() + 1)
        except EOFError:
            assert frame_count == 5

        img.seek(0)
        with pytest.raises(ValueError, match="cannot seek to frame 2"):
            img._seek(2)


def test_seek_info() -> None:
    with Image.open("Tests/images/iss634.gif") as im:
        info = im.info.copy()

        im.seek(1)
        im.seek(0)

        assert im.info == info


def test_seek_rewind() -> None:
    with Image.open("Tests/images/iss634.gif") as im:
        im.seek(2)
        im.seek(1)

        with Image.open("Tests/images/iss634.gif") as expected:
            expected.seek(1)
            assert_image_equal(im, expected)


@pytest.mark.parametrize(
    "path, n_frames",
    (
        (TEST_GIF, 1),
        ("Tests/images/comment_after_last_frame.gif", 2),
        ("Tests/images/iss634.gif", 42),
    ),
)
def test_n_frames(path: str, n_frames: int) -> None:
    # Test is_animated before n_frames
    with Image.open(path) as im:
        assert isinstance(im, GifImagePlugin.GifImageFile)
        assert im.is_animated == (n_frames != 1)

    # Test is_animated after n_frames
    with Image.open(path) as im:
        assert isinstance(im, GifImagePlugin.GifImageFile)
        assert im.n_frames == n_frames
        assert im.is_animated == (n_frames != 1)


def test_no_change() -> None:
    # Test n_frames does not change the image
    with Image.open("Tests/images/dispose_bgnd.gif") as im:
        im.seek(1)
        expected = im.copy()
        assert isinstance(im, GifImagePlugin.GifImageFile)
        assert im.n_frames == 5
        assert_image_equal(im, expected)

    # Test is_animated does not change the image
    with Image.open("Tests/images/dispose_bgnd.gif") as im:
        im.seek(3)
        expected = im.copy()
        assert isinstance(im, GifImagePlugin.GifImageFile)
        assert im.is_animated
        assert_image_equal(im, expected)

    with Image.open("Tests/images/comment_after_only_frame.gif") as im:
        expected = Image.new("P", (1, 1))
        assert isinstance(im, GifImagePlugin.GifImageFile)
        assert not im.is_animated
        assert_image_equal(im, expected)


def test_eoferror() -> None:
    with Image.open(TEST_GIF) as im:
        assert isinstance(im, GifImagePlugin.GifImageFile)
        n_frames = im.n_frames

        # Test seeking past the last frame
        with pytest.raises(EOFError):
            im.seek(n_frames)
        assert im.tell() < n_frames

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames - 1)


def test_first_frame_transparency() -> None:
    with Image.open("Tests/images/first_frame_transparency.gif") as im:
        assert im.getpixel((0, 0)) == im.info["transparency"]


def test_dispose_none() -> None:
    with Image.open("Tests/images/dispose_none.gif") as img:
        assert isinstance(img, GifImagePlugin.GifImageFile)
        try:
            while True:
                img.seek(img.tell() + 1)
                assert img.disposal_method == 1
        except EOFError:
            pass


def test_dispose_none_load_end() -> None:
    # Test image created with:
    #
    # im = Image.open("transparent.gif")
    # im_rotated = im.rotate(180)
    # im.save("dispose_none_load_end.gif",
    #         save_all=True, append_images=[im_rotated], disposal=[1,2])
    with Image.open("Tests/images/dispose_none_load_end.gif") as img:
        img.seek(1)

        assert_image_equal_tofile(img, "Tests/images/dispose_none_load_end_second.png")


def test_dispose_background() -> None:
    with Image.open("Tests/images/dispose_bgnd.gif") as img:
        assert isinstance(img, GifImagePlugin.GifImageFile)
        try:
            while True:
                img.seek(img.tell() + 1)
                assert img.disposal_method == 2
        except EOFError:
            pass


def test_dispose_background_transparency() -> None:
    with Image.open("Tests/images/dispose_bgnd_transparency.gif") as img:
        img.seek(2)
        px = img.load()
        assert px is not None
        value = px[35, 30]
        assert isinstance(value, tuple)
        assert value[3] == 0


@pytest.mark.parametrize(
    "loading_strategy, expected_colors",
    (
        (
            GifImagePlugin.LoadingStrategy.RGB_AFTER_FIRST,
            (
                (2, 1, 2),
                ((0, 255, 24, 255), (0, 0, 255, 255), (0, 255, 24, 255)),
                ((0, 0, 0, 0), (0, 0, 255, 255), (0, 0, 0, 0)),
            ),
        ),
        (
            GifImagePlugin.LoadingStrategy.RGB_AFTER_DIFFERENT_PALETTE_ONLY,
            (
                (2, 1, 2),
                (0, 1, 0),
                (2, 1, 2),
            ),
        ),
    ),
)
def test_transparent_dispose(
    loading_strategy: GifImagePlugin.LoadingStrategy,
    expected_colors: tuple[tuple[int | tuple[int, int, int, int], ...]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(GifImagePlugin, "LOADING_STRATEGY", loading_strategy)
    with Image.open("Tests/images/transparent_dispose.gif") as img:
        for frame in range(3):
            img.seek(frame)
            for x in range(3):
                color = img.getpixel((x, 0))
                assert color == expected_colors[frame][x]


def test_dispose_previous() -> None:
    with Image.open("Tests/images/dispose_prev.gif") as img:
        assert isinstance(img, GifImagePlugin.GifImageFile)
        try:
            while True:
                img.seek(img.tell() + 1)
                assert img.disposal_method == 3
        except EOFError:
            pass


def test_dispose_previous_first_frame() -> None:
    with Image.open("Tests/images/dispose_prev_first_frame.gif") as im:
        im.seek(1)
        assert_image_equal_tofile(
            im, "Tests/images/dispose_prev_first_frame_seeked.png"
        )


def test_previous_frame_loaded() -> None:
    with Image.open("Tests/images/dispose_none.gif") as img:
        img.load()
        img.seek(1)
        img.load()
        img.seek(2)
        with Image.open("Tests/images/dispose_none.gif") as img_skipped:
            img_skipped.seek(2)
            assert_image_equal(img_skipped, img)


def test_save_dispose(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"
    im_list = [
        Image.new("L", (100, 100), "#000"),
        Image.new("L", (100, 100), "#111"),
        Image.new("L", (100, 100), "#222"),
    ]
    for method in range(4):
        im_list[0].save(out, save_all=True, append_images=im_list[1:], disposal=method)
        with Image.open(out) as img:
            assert isinstance(img, GifImagePlugin.GifImageFile)
            for _ in range(2):
                img.seek(img.tell() + 1)
                assert img.disposal_method == method

    # Check per frame disposal
    im_list[0].save(
        out,
        save_all=True,
        append_images=im_list[1:],
        disposal=tuple(range(len(im_list))),
    )

    with Image.open(out) as img:
        assert isinstance(img, GifImagePlugin.GifImageFile)
        for i in range(2):
            img.seek(img.tell() + 1)
            assert img.disposal_method == i + 1


def test_dispose2_palette(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    # Four colors: white, gray, black, red
    circles = [(255, 255, 255), (153, 153, 153), (0, 0, 0), (255, 0, 0)]

    im_list = []
    for circle in circles:
        # Red background
        img = Image.new("RGB", (100, 100), (255, 0, 0))

        # Circle in center of each frame
        d = ImageDraw.Draw(img)
        d.ellipse([(40, 40), (60, 60)], fill=circle)

        im_list.append(img)

    im_list[0].save(out, save_all=True, append_images=im_list[1:], disposal=2)

    with Image.open(out) as img:
        for i, circle in enumerate(circles):
            img.seek(i)
            rgb_img = img.convert("RGB")

            # Check top left pixel matches background
            assert rgb_img.getpixel((0, 0)) == (255, 0, 0)

            # Center remains red every frame
            assert rgb_img.getpixel((50, 50)) == circle

            # Check that frame transparency wasn't added unnecessarily
            assert getattr(img, "_frame_transparency") is None


def test_dispose2_diff(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    # 4 frames: red/blue, red/red, blue/blue, red/blue
    circles = [
        ((255, 0, 0, 255), (0, 0, 255, 255)),
        ((255, 0, 0, 255), (255, 0, 0, 255)),
        ((0, 0, 255, 255), (0, 0, 255, 255)),
        ((255, 0, 0, 255), (0, 0, 255, 255)),
    ]

    im_list = []
    for i in range(len(circles)):
        # Transparent BG
        img = Image.new("RGBA", (100, 100), (255, 255, 255, 0))

        # Two circles per frame
        d = ImageDraw.Draw(img)
        d.ellipse([(0, 30), (40, 70)], fill=circles[i][0])
        d.ellipse([(60, 30), (100, 70)], fill=circles[i][1])

        im_list.append(img)

    im_list[0].save(
        out, save_all=True, append_images=im_list[1:], disposal=2, transparency=0
    )

    with Image.open(out) as img:
        for i, colours in enumerate(circles):
            img.seek(i)
            rgb_img = img.convert("RGBA")

            # Check left circle is correct colour
            assert rgb_img.getpixel((20, 50)) == colours[0]

            # Check right circle is correct colour
            assert rgb_img.getpixel((80, 50)) == colours[1]

            # Check BG is correct colour
            assert rgb_img.getpixel((1, 1)) == (255, 255, 255, 0)


def test_dispose2_background(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    im_list = []

    im = Image.new("P", (100, 100))
    d = ImageDraw.Draw(im)
    d.rectangle([(50, 0), (100, 100)], fill="#f00")
    d.rectangle([(0, 0), (50, 100)], fill="#0f0")
    im_list.append(im)

    im = Image.new("P", (100, 100))
    d = ImageDraw.Draw(im)
    d.rectangle([(0, 0), (100, 50)], fill="#f00")
    d.rectangle([(0, 50), (100, 100)], fill="#0f0")
    im_list.append(im)

    im_list[0].save(
        out, save_all=True, append_images=im_list[1:], disposal=[0, 2], background=1
    )

    with Image.open(out) as im:
        im.seek(1)
        assert im.getpixel((0, 0)) == (255, 0, 0)


def test_dispose2_background_frame(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    im_list = [Image.new("RGBA", (1, 20))]

    different_frame = Image.new("RGBA", (1, 20))
    different_frame.putpixel((0, 10), (255, 0, 0, 255))
    im_list.append(different_frame)

    # Frame that matches the background
    im_list.append(Image.new("RGBA", (1, 20)))

    im_list[0].save(out, save_all=True, append_images=im_list[1:], disposal=2)

    with Image.open(out) as im:
        assert isinstance(im, GifImagePlugin.GifImageFile)
        assert im.n_frames == 3


def test_dispose2_previous_frame(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    im = Image.new("P", (100, 100))
    im.info["transparency"] = 0
    d = ImageDraw.Draw(im)
    d.rectangle([(0, 0), (100, 50)], 1)
    im.putpalette((0, 0, 0, 255, 0, 0))

    im2 = Image.new("P", (100, 100))
    im2.putpalette((0, 0, 0))

    im.save(out, save_all=True, append_images=[im2], disposal=[0, 2])

    with Image.open(out) as im:
        im.seek(1)
        assert im.getpixel((0, 0)) == (0, 0, 0, 255)


def test_dispose2_without_transparency(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    im = Image.new("P", (100, 100))

    im2 = Image.new("P", (100, 100), (0, 0, 0))
    im2.putpixel((50, 50), (255, 0, 0))

    im.save(out, save_all=True, append_images=[im2], disposal=2)

    with Image.open(out) as reloaded:
        reloaded.seek(1)
        assert reloaded.tile[0].extents == (0, 0, 100, 100)


def test_transparency_in_second_frame(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"
    with Image.open("Tests/images/different_transparency.gif") as im:
        assert im.info["transparency"] == 0

        # Seek to the second frame
        im.seek(im.tell() + 1)
        assert "transparency" not in im.info

        assert_image_equal_tofile(im, "Tests/images/different_transparency_merged.png")

        im.save(out, save_all=True)

    with Image.open(out) as reread:
        reread.seek(reread.tell() + 1)
        assert_image_equal_tofile(
            reread, "Tests/images/different_transparency_merged.png"
        )


def test_no_transparency_in_second_frame() -> None:
    with Image.open("Tests/images/iss634.gif") as img:
        # Seek to the second frame
        img.seek(img.tell() + 1)
        assert "transparency" not in img.info

        # All transparent pixels should be replaced with the color from the first frame
        assert img.histogram()[255] == 0


def test_remapped_transparency(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    im = Image.new("P", (1, 2))
    im2 = im.copy()

    # Add transparency at a higher index
    # so that it will be optimized to a lower index
    im.putpixel((0, 1), 5)
    im.info["transparency"] = 5
    im.save(out, save_all=True, append_images=[im2])

    with Image.open(out) as reloaded:
        assert reloaded.info["transparency"] == reloaded.getpixel((0, 1))


def test_duration(tmp_path: Path) -> None:
    duration = 1000

    out = tmp_path / "temp.gif"
    im = Image.new("L", (100, 100), "#000")

    # Check that the argument has priority over the info settings
    im.info["duration"] = 100
    im.save(out, duration=duration)

    with Image.open(out) as reread:
        assert reread.info["duration"] == duration


def test_multiple_duration(tmp_path: Path) -> None:
    duration_list = [1000, 2000, 3000]

    out = tmp_path / "temp.gif"
    im_list = [
        Image.new("L", (100, 100), "#000"),
        Image.new("L", (100, 100), "#111"),
        Image.new("L", (100, 100), "#222"),
    ]

    # Duration as list
    im_list[0].save(
        out, save_all=True, append_images=im_list[1:], duration=duration_list
    )
    with Image.open(out) as reread:
        for duration in duration_list:
            assert reread.info["duration"] == duration
            try:
                reread.seek(reread.tell() + 1)
            except EOFError:
                pass

    # Duration as tuple
    im_list[0].save(
        out, save_all=True, append_images=im_list[1:], duration=tuple(duration_list)
    )
    with Image.open(out) as reread:
        for duration in duration_list:
            assert reread.info["duration"] == duration
            try:
                reread.seek(reread.tell() + 1)
            except EOFError:
                pass


def test_roundtrip_info_duration(tmp_path: Path) -> None:
    duration_list = [100, 500, 500]

    out = tmp_path / "temp.gif"
    with Image.open("Tests/images/transparent_dispose.gif") as im:
        assert [
            frame.info["duration"] for frame in ImageSequence.Iterator(im)
        ] == duration_list

        im.save(out, save_all=True)

    with Image.open(out) as reloaded:
        assert [
            frame.info["duration"] for frame in ImageSequence.Iterator(reloaded)
        ] == duration_list


def test_roundtrip_info_duration_combined(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"
    with Image.open("Tests/images/duplicate_frame.gif") as im:
        assert [frame.info["duration"] for frame in ImageSequence.Iterator(im)] == [
            1000,
            1000,
            1000,
        ]
        im.save(out, save_all=True)

    with Image.open(out) as reloaded:
        assert [
            frame.info["duration"] for frame in ImageSequence.Iterator(reloaded)
        ] == [1000, 2000]


def test_identical_frames(tmp_path: Path) -> None:
    duration_list = [1000, 1500, 2000, 4000]

    out = tmp_path / "temp.gif"
    im_list = [
        Image.new("L", (100, 100), "#000"),
        Image.new("L", (100, 100), "#000"),
        Image.new("L", (100, 100), "#000"),
        Image.new("L", (100, 100), "#111"),
    ]

    # Duration as list
    im_list[0].save(
        out, save_all=True, append_images=im_list[1:], duration=duration_list
    )
    with Image.open(out) as reread:
        assert isinstance(reread, GifImagePlugin.GifImageFile)

        # Assert that the first three frames were combined
        assert reread.n_frames == 2

        # Assert that the new duration is the total of the identical frames
        assert reread.info["duration"] == 4500


@pytest.mark.parametrize(
    "duration",
    (
        [1000, 1500, 2000],
        (1000, 1500, 2000),
        # One more duration than the number of frames
        [1000, 1500, 2000, 4000],
        1500,
    ),
)
def test_identical_frames_to_single_frame(
    duration: int | list[int], tmp_path: Path
) -> None:
    out = tmp_path / "temp.gif"
    im_list = [
        Image.new("L", (100, 100), "#000"),
        Image.new("L", (100, 100), "#000"),
        Image.new("L", (100, 100), "#000"),
    ]

    im_list[0].save(out, save_all=True, append_images=im_list[1:], duration=duration)
    with Image.open(out) as reread:
        assert isinstance(reread, GifImagePlugin.GifImageFile)

        # Assert that all frames were combined
        assert reread.n_frames == 1

        # Assert that the new duration is the total of the identical frames
        assert reread.info["duration"] == 4500


def test_loop_none(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"
    im = Image.new("L", (100, 100), "#000")
    im.save(out, loop=None)
    with Image.open(out) as reread:
        assert "loop" not in reread.info


def test_number_of_loops(tmp_path: Path) -> None:
    number_of_loops = 2

    out = tmp_path / "temp.gif"
    im = Image.new("L", (100, 100), "#000")
    im.save(out, loop=number_of_loops)
    with Image.open(out) as reread:
        assert reread.info["loop"] == number_of_loops

    # Check that even if a subsequent GIF frame has the number of loops specified,
    # only the value from the first frame is used
    with Image.open("Tests/images/duplicate_number_of_loops.gif") as im:
        assert im.info["loop"] == 2

        im.seek(1)
        assert im.info["loop"] == 2


def test_background(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"
    im = Image.new("L", (100, 100), "#000")
    im.info["background"] = 1
    im.save(out)
    with Image.open(out) as reread:
        assert reread.info["background"] == im.info["background"]


def test_webp_background(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    # Test opaque WebP background
    if features.check("webp"):
        with Image.open("Tests/images/hopper.webp") as im:
            assert im.info["background"] == (255, 255, 255, 255)
            im.save(out)

    # Test non-opaque WebP background
    im = Image.new("L", (100, 100), "#000")
    im.info["background"] = (0, 0, 0, 0)
    im.save(out)


def test_comment(tmp_path: Path) -> None:
    with Image.open(TEST_GIF) as im:
        assert im.info["comment"] == b"File written by Adobe Photoshop\xa8 4.0"

    out = tmp_path / "temp.gif"
    im = Image.new("L", (100, 100), "#000")
    im.info["comment"] = b"Test comment text"
    im.save(out)
    with Image.open(out) as reread:
        assert reread.info["comment"] == im.info["comment"]

    im.info["comment"] = "Test comment text"
    im.save(out)
    with Image.open(out) as reread:
        assert reread.info["comment"] == im.info["comment"].encode()

        # Test that GIF89a is used for comments
        assert reread.info["version"] == b"GIF89a"


def test_comment_over_255(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"
    im = Image.new("L", (100, 100), "#000")
    comment = b"Test comment text"
    while len(comment) < 256:
        comment += comment
    im.info["comment"] = comment
    im.save(out)
    with Image.open(out) as reread:
        assert reread.info["comment"] == comment

        # Test that GIF89a is used for comments
        assert reread.info["version"] == b"GIF89a"


def test_zero_comment_subblocks() -> None:
    with Image.open("Tests/images/hopper_zero_comment_subblocks.gif") as im:
        assert_image_equal_tofile(im, TEST_GIF)


def test_read_multiple_comment_blocks() -> None:
    with Image.open("Tests/images/multiple_comments.gif") as im:
        # Multiple comment blocks in a frame are separated not concatenated
        assert im.info["comment"] == b"Test comment 1\nTest comment 2"


def test_empty_string_comment(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"
    with Image.open("Tests/images/chi.gif") as im:
        assert "comment" in im.info

        # Empty string comment should suppress existing comment
        im.save(out, save_all=True, comment="")

    with Image.open(out) as reread:
        for frame in ImageSequence.Iterator(reread):
            assert "comment" not in frame.info


def test_retain_comment_in_subsequent_frames(tmp_path: Path) -> None:
    # Test that a comment block at the beginning is kept
    with Image.open("Tests/images/chi.gif") as im:
        for frame in ImageSequence.Iterator(im):
            assert frame.info["comment"] == b"Created with GIMP"

    with Image.open("Tests/images/second_frame_comment.gif") as im:
        assert "comment" not in im.info

        # Test that a comment in the middle is read
        im.seek(1)
        assert im.info["comment"] == b"Comment in the second frame"

        # Test that it is still present in a later frame
        im.seek(2)
        assert im.info["comment"] == b"Comment in the second frame"

        # Test that rewinding removes the comment
        im.seek(0)
        assert "comment" not in im.info

    # Test that a saved image keeps the comment
    out = tmp_path / "temp.gif"
    with Image.open("Tests/images/dispose_prev.gif") as im:
        im.save(out, save_all=True, comment="Test")

    with Image.open(out) as reread:
        for frame in ImageSequence.Iterator(reread):
            assert frame.info["comment"] == b"Test"


def test_version(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    def assert_version_after_save(im: Image.Image, version: bytes) -> None:
        im.save(out)
        with Image.open(out) as reread:
            assert reread.info["version"] == version

    # Test that GIF87a is used by default
    im = Image.new("L", (100, 100), "#000")
    assert_version_after_save(im, b"GIF87a")

    # Test setting the version to 89a
    im = Image.new("L", (100, 100), "#000")
    im.info["version"] = b"89a"
    assert_version_after_save(im, b"GIF89a")

    # Test that adding a GIF89a feature changes the version
    im.info["transparency"] = 1
    assert_version_after_save(im, b"GIF89a")

    # Test that a GIF87a image is also saved in that format
    with Image.open("Tests/images/test.colors.gif") as im:
        assert_version_after_save(im, b"GIF87a")

        # Test that a GIF89a image is also saved in that format
        im.info["version"] = b"GIF89a"
        assert_version_after_save(im, b"GIF87a")


def test_append_images(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    # Test appending single frame images
    im = Image.new("RGB", (100, 100), "#f00")
    ims = [Image.new("RGB", (100, 100), color) for color in ["#0f0", "#00f"]]
    im.copy().save(out, save_all=True, append_images=ims)

    with Image.open(out) as reread:
        assert isinstance(reread, GifImagePlugin.GifImageFile)
        assert reread.n_frames == 3

    # Test append_images without save_all
    im.copy().save(out, append_images=ims)

    with Image.open(out) as reread:
        assert isinstance(reread, GifImagePlugin.GifImageFile)
        assert reread.n_frames == 3

    # Tests appending using a generator
    def im_generator(ims: list[Image.Image]) -> Generator[Image.Image, None, None]:
        yield from ims

    im.save(out, save_all=True, append_images=im_generator(ims))

    with Image.open(out) as reread:
        assert isinstance(reread, GifImagePlugin.GifImageFile)
        assert reread.n_frames == 3

    # Tests appending single and multiple frame images
    with Image.open("Tests/images/dispose_none.gif") as im:
        with Image.open("Tests/images/dispose_prev.gif") as im2:
            im.save(out, save_all=True, append_images=[im2])

    with Image.open(out) as reread:
        assert isinstance(reread, GifImagePlugin.GifImageFile)
        assert reread.n_frames == 10


def test_append_different_size_image(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    im = Image.new("RGB", (100, 100))
    bigger_im = Image.new("RGB", (200, 200), "#f00")

    im.save(out, save_all=True, append_images=[bigger_im])

    with Image.open(out) as reread:
        assert reread.size == (100, 100)

        reread.seek(1)
        assert reread.size == (100, 100)


def test_transparent_optimize(tmp_path: Path) -> None:
    # From issue #2195, if the transparent color is incorrectly optimized out, GIF loses
    # transparency.
    # Need a palette that isn't using the 0 color,
    # where the transparent color is actually the top palette entry to trigger the bug.

    data = bytes(range(1, 254))
    palette = ImagePalette.ImagePalette("RGB", list(range(256)) * 3)

    im = Image.new("L", (253, 1))
    im.frombytes(data)
    im.putpalette(palette)

    out = tmp_path / "temp.gif"
    im.save(out, transparency=im.getpixel((252, 0)))

    with Image.open(out) as reloaded:
        assert reloaded.info["transparency"] == reloaded.getpixel((252, 0))


def test_removed_transparency(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"
    im = Image.new("RGB", (256, 1))

    for x in range(256):
        im.putpixel((x, 0), (x, 0, 0))

    im.info["transparency"] = (255, 255, 255)
    with pytest.warns(
        UserWarning, match="Couldn't allocate palette entry for transparency"
    ):
        im.save(out)

    with Image.open(out) as reloaded:
        assert "transparency" not in reloaded.info


def test_rgb_transparency(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    # Single frame
    im = Image.new("RGB", (1, 1))
    im.info["transparency"] = (255, 0, 0)
    im.save(out)

    with Image.open(out) as reloaded:
        assert "transparency" in reloaded.info

    # Multiple frames
    im = Image.new("RGB", (1, 1))
    im.info["transparency"] = b""
    ims = [Image.new("RGB", (1, 1))]
    with pytest.warns(UserWarning, match="should be converted to RGBA images"):
        im.save(out, save_all=True, append_images=ims)

    with Image.open(out) as reloaded:
        assert "transparency" not in reloaded.info


def test_rgba_transparency(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    im = hopper("P")
    im.save(out, save_all=True, append_images=[Image.new("RGBA", im.size)])

    with Image.open(out) as reloaded:
        reloaded.seek(1)
        assert_image_equal(hopper("P").convert("RGB"), reloaded)


def test_background_outside_palettte() -> None:
    with Image.open("Tests/images/background_outside_palette.gif") as im:
        im.seek(1)
        assert im.info["background"] == 255


def test_bbox(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    im = Image.new("RGB", (100, 100), "#fff")
    ims = [Image.new("RGB", (100, 100), "#000")]
    im.save(out, save_all=True, append_images=ims)

    with Image.open(out) as reread:
        assert isinstance(reread, GifImagePlugin.GifImageFile)
        assert reread.n_frames == 2


def test_bbox_alpha(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"

    im = Image.new("RGBA", (1, 2), (255, 0, 0, 255))
    im.putpixel((0, 1), (255, 0, 0, 0))
    im2 = Image.new("RGBA", (1, 2), (255, 0, 0, 0))
    im.save(out, save_all=True, append_images=[im2])

    with Image.open(out) as reread:
        assert isinstance(reread, GifImagePlugin.GifImageFile)
        assert reread.n_frames == 2


def test_palette_save_L(tmp_path: Path) -> None:
    # Generate an L mode image with a separate palette

    im = hopper("P")
    im_l = Image.frombytes("L", im.size, im.tobytes())
    palette = im.getpalette()
    assert palette is not None

    out = tmp_path / "temp.gif"
    im_l.save(out, palette=bytes(palette))

    with Image.open(out) as reloaded:
        assert_image_equal(reloaded.convert("RGB"), im.convert("RGB"))


def test_palette_save_P(tmp_path: Path) -> None:
    im = Image.new("P", (1, 2))
    im.putpixel((0, 1), 1)

    out = tmp_path / "temp.gif"
    im.save(out, palette=bytes((1, 2, 3, 4, 5, 6)))

    with Image.open(out) as reloaded:
        reloaded_rgb = reloaded.convert("RGB")

        assert reloaded_rgb.getpixel((0, 0)) == (1, 2, 3)
        assert reloaded_rgb.getpixel((0, 1)) == (4, 5, 6)


def test_palette_save_duplicate_entries(tmp_path: Path) -> None:
    im = Image.new("P", (1, 2))
    im.putpixel((0, 1), 1)

    im.putpalette((0, 0, 0, 0, 0, 0))

    out = tmp_path / "temp.gif"
    im.save(out, palette=[0, 0, 0, 0, 0, 0, 1, 1, 1])

    with Image.open(out) as reloaded:
        assert reloaded.convert("RGB").getpixel((0, 1)) == (0, 0, 0)


def test_palette_save_all_P(tmp_path: Path) -> None:
    frames = []
    colors = ((255, 0, 0), (0, 255, 0))
    for color in colors:
        frame = Image.new("P", (100, 100))
        frame.putpalette(color)
        frames.append(frame)

    out = tmp_path / "temp.gif"
    frames[0].save(
        out, save_all=True, palette=[255, 0, 0, 0, 255, 0], append_images=frames[1:]
    )

    with Image.open(out) as im:
        # Assert that the frames are correct, and each frame has the same palette
        assert_image_equal(im.convert("RGB"), frames[0].convert("RGB"))
        assert im.palette is not None
        assert im.global_palette is not None
        assert im.palette.palette == im.global_palette.palette

        im.seek(1)
        assert_image_equal(im.convert("RGB"), frames[1].convert("RGB"))
        assert im.palette.palette == im.global_palette.palette


def test_palette_save_ImagePalette(tmp_path: Path) -> None:
    # Pass in a different palette, as an ImagePalette.ImagePalette
    # effectively the same as test_palette_save_P

    im = hopper("P")
    palette = ImagePalette.ImagePalette("RGB", list(range(256))[::-1] * 3)

    out = tmp_path / "temp.gif"
    im.save(out, palette=palette)

    with Image.open(out) as reloaded:
        im.putpalette(palette)
        assert_image_equal(reloaded.convert("RGB"), im.convert("RGB"))


def test_save_I(tmp_path: Path) -> None:
    # Test saving something that would trigger the auto-convert to 'L'

    im = hopper("I")

    out = tmp_path / "temp.gif"
    im.save(out)

    with Image.open(out) as reloaded:
        assert_image_equal(reloaded.convert("L"), im.convert("L"))


def test_getdata(monkeypatch: pytest.MonkeyPatch) -> None:
    # Test getheader/getdata against legacy values.
    # Create a 'P' image with holes in the palette.
    im = Image.linear_gradient(mode="L").resize((16, 16), Image.Resampling.NEAREST)
    im.putpalette(ImagePalette.ImagePalette("RGB"))
    im.info = {"background": 0}

    passed_palette = bytes(255 - i // 3 for i in range(768))

    monkeypatch.setattr(GifImagePlugin, "_FORCE_OPTIMIZE", True)

    h = GifImagePlugin.getheader(im, passed_palette)
    d = GifImagePlugin.getdata(im)

    import pickle

    # Enable to get target values on pre-refactor version
    # with open('Tests/images/gif_header_data.pkl', 'wb') as f:
    #    pickle.dump((h, d), f, 1)
    with open("Tests/images/gif_header_data.pkl", "rb") as f:
        (h_target, d_target) = pickle.load(f)

    assert h == h_target
    assert d == d_target


def test_lzw_bits() -> None:
    # see https://github.com/python-pillow/Pillow/issues/2811
    with Image.open("Tests/images/issue_2811.gif") as im:
        args = im.tile[0][3]
        assert isinstance(args, tuple)
        assert args[0] == 11  # LZW bits
        # codec error prepatch
        im.load()


@pytest.mark.parametrize(
    "test_file, loading_strategy",
    (
        ("test_extents.gif", GifImagePlugin.LoadingStrategy.RGB_AFTER_FIRST),
        (
            "test_extents.gif",
            GifImagePlugin.LoadingStrategy.RGB_AFTER_DIFFERENT_PALETTE_ONLY,
        ),
        (
            "test_extents_transparency.gif",
            GifImagePlugin.LoadingStrategy.RGB_AFTER_FIRST,
        ),
    ),
)
def test_extents(
    test_file: str,
    loading_strategy: GifImagePlugin.LoadingStrategy,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(GifImagePlugin, "LOADING_STRATEGY", loading_strategy)
    with Image.open("Tests/images/" + test_file) as im:
        assert isinstance(im, GifImagePlugin.GifImageFile)
        assert im.size == (100, 100)

        # Check that n_frames does not change the size
        assert im.n_frames == 2
        assert im.size == (100, 100)

        im.seek(1)
        assert im.size == (150, 150)

        im.load()
        assert im.im.size == (150, 150)


def test_missing_background() -> None:
    # The Global Color Table Flag isn't set, so there is no background color index,
    # but the disposal method is "Restore to background color"
    with Image.open("Tests/images/missing_background.gif") as im:
        im.seek(1)
        assert_image_equal_tofile(im, "Tests/images/missing_background_first_frame.png")


def test_saving_rgba(tmp_path: Path) -> None:
    out = tmp_path / "temp.gif"
    with Image.open("Tests/images/transparent.png") as im:
        im.save(out)

    with Image.open(out) as reloaded:
        reloaded_rgba = reloaded.convert("RGBA")
        px = reloaded_rgba.load()
        assert px is not None
        value = px[0, 0]
        assert isinstance(value, tuple)
        assert value[3] == 0


@pytest.mark.parametrize("params", ({}, {"disposal": 2, "optimize": False}))
def test_p_rgba(tmp_path: Path, params: dict[str, Any]) -> None:
    out = tmp_path / "temp.gif"

    im1 = Image.new("P", (100, 100))
    d = ImageDraw.Draw(im1)
    d.ellipse([(40, 40), (60, 60)], fill=1)
    data = [0, 0, 0, 0, 0, 0, 0, 255] + [0, 0, 0, 0] * 254
    im1.putpalette(data, "RGBA")

    im2 = Image.new("P", (100, 100))
    im2.putpalette(data, "RGBA")

    im1.save(out, save_all=True, append_images=[im2], **params)

    with Image.open(out) as reloaded:
        assert isinstance(reloaded, GifImagePlugin.GifImageFile)
        assert reloaded.n_frames == 2
