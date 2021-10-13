from io import BytesIO

import pytest

from PIL import GifImagePlugin, Image, ImageDraw, ImagePalette, features

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

with open(TEST_GIF, "rb") as f:
    data = f.read()


def test_sanity():
    with Image.open(TEST_GIF) as im:
        im.load()
        assert im.mode == "P"
        assert im.size == (128, 128)
        assert im.format == "GIF"
        assert im.info["version"] == b"GIF89a"


@pytest.mark.skipif(is_pypy(), reason="Requires CPython")
def test_unclosed_file():
    def open():
        im = Image.open(TEST_GIF)
        im.load()

    pytest.warns(ResourceWarning, open)


def test_closed_file():
    with pytest.warns(None) as record:
        im = Image.open(TEST_GIF)
        im.load()
        im.close()

    assert not record


def test_context_manager():
    with pytest.warns(None) as record:
        with Image.open(TEST_GIF) as im:
            im.load()

    assert not record


def test_invalid_file():
    invalid_file = "Tests/images/flower.jpg"

    with pytest.raises(SyntaxError):
        GifImagePlugin.GifImageFile(invalid_file)


def test_optimize():
    def test_grayscale(optimize):
        im = Image.new("L", (1, 1), 0)
        filename = BytesIO()
        im.save(filename, "GIF", optimize=optimize)
        return len(filename.getvalue())

    def test_bilevel(optimize):
        im = Image.new("1", (1, 1), 0)
        test_file = BytesIO()
        im.save(test_file, "GIF", optimize=optimize)
        return len(test_file.getvalue())

    assert test_grayscale(0) == 799
    assert test_grayscale(1) == 43
    assert test_bilevel(0) == 799
    assert test_bilevel(1) == 799


def test_optimize_correctness():
    # 256 color Palette image, posterize to > 128 and < 128 levels
    # Size bigger and smaller than 512x512
    # Check the palette for number of colors allocated.
    # Check for correctness after conversion back to RGB
    def check(colors, size, expected_palette_length):
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

    # These do optimize the palette
    check(128, 511, 128)
    check(64, 511, 64)
    check(4, 511, 4)

    # These don't optimize the palette
    check(128, 513, 256)
    check(64, 513, 256)
    check(4, 513, 256)

    # Other limits that don't optimize the palette
    check(129, 511, 256)
    check(255, 511, 256)
    check(256, 511, 256)


def test_optimize_full_l():
    im = Image.frombytes("L", (16, 16), bytes(range(256)))
    test_file = BytesIO()
    im.save(test_file, "GIF", optimize=True)
    assert im.mode == "L"


def test_roundtrip(tmp_path):
    out = str(tmp_path / "temp.gif")
    im = hopper()
    im.save(out)
    with Image.open(out) as reread:

        assert_image_similar(reread.convert("RGB"), im, 50)


def test_roundtrip2(tmp_path):
    # see https://github.com/python-pillow/Pillow/issues/403
    out = str(tmp_path / "temp.gif")
    with Image.open(TEST_GIF) as im:
        im2 = im.copy()
        im2.save(out)
    with Image.open(out) as reread:

        assert_image_similar(reread.convert("RGB"), hopper(), 50)


def test_roundtrip_save_all(tmp_path):
    # Single frame image
    out = str(tmp_path / "temp.gif")
    im = hopper()
    im.save(out, save_all=True)
    with Image.open(out) as reread:

        assert_image_similar(reread.convert("RGB"), im, 50)

    # Multiframe image
    with Image.open("Tests/images/dispose_bgnd.gif") as im:
        out = str(tmp_path / "temp.gif")
        im.save(out, save_all=True)

    with Image.open(out) as reread:
        assert reread.n_frames == 5


def test_headers_saving_for_animated_gifs(tmp_path):
    important_headers = ["background", "version", "duration", "loop"]
    # Multiframe image
    with Image.open("Tests/images/dispose_bgnd.gif") as im:

        info = im.info.copy()

        out = str(tmp_path / "temp.gif")
        im.save(out, save_all=True)
    with Image.open(out) as reread:

        for header in important_headers:
            assert info[header] == reread.info[header]


def test_palette_handling(tmp_path):
    # see https://github.com/python-pillow/Pillow/issues/513

    with Image.open(TEST_GIF) as im:
        im = im.convert("RGB")

        im = im.resize((100, 100), Image.LANCZOS)
        im2 = im.convert("P", palette=Image.ADAPTIVE, colors=256)

        f = str(tmp_path / "temp.gif")
        im2.save(f, optimize=True)

    with Image.open(f) as reloaded:

        assert_image_similar(im, reloaded.convert("RGB"), 10)


def test_palette_434(tmp_path):
    # see https://github.com/python-pillow/Pillow/issues/434

    def roundtrip(im, *args, **kwargs):
        out = str(tmp_path / "temp.gif")
        im.copy().save(out, *args, **kwargs)
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
def test_save_netpbm_bmp_mode(tmp_path):
    with Image.open(TEST_GIF) as img:
        img = img.convert("RGB")

        tempfile = str(tmp_path / "temp.gif")
        GifImagePlugin._save_netpbm(img, 0, tempfile)
        with Image.open(tempfile) as reloaded:
            assert_image_similar(img, reloaded.convert("RGB"), 0)


@pytest.mark.skipif(not netpbm_available(), reason="Netpbm not available")
def test_save_netpbm_l_mode(tmp_path):
    with Image.open(TEST_GIF) as img:
        img = img.convert("L")

        tempfile = str(tmp_path / "temp.gif")
        GifImagePlugin._save_netpbm(img, 0, tempfile)
        with Image.open(tempfile) as reloaded:
            assert_image_similar(img, reloaded.convert("L"), 0)


def test_seek():
    with Image.open("Tests/images/dispose_none.gif") as img:
        frame_count = 0
        try:
            while True:
                frame_count += 1
                img.seek(img.tell() + 1)
        except EOFError:
            assert frame_count == 5


def test_seek_info():
    with Image.open("Tests/images/iss634.gif") as im:
        info = im.info.copy()

        im.seek(1)
        im.seek(0)

        assert im.info == info


def test_seek_rewind():
    with Image.open("Tests/images/iss634.gif") as im:
        im.seek(2)
        im.seek(1)

        with Image.open("Tests/images/iss634.gif") as expected:
            expected.seek(1)
            assert_image_equal(im, expected)


def test_n_frames():
    for path, n_frames in [[TEST_GIF, 1], ["Tests/images/iss634.gif", 42]]:
        # Test is_animated before n_frames
        with Image.open(path) as im:
            assert im.is_animated == (n_frames != 1)

        # Test is_animated after n_frames
        with Image.open(path) as im:
            assert im.n_frames == n_frames
            assert im.is_animated == (n_frames != 1)


def test_eoferror():
    with Image.open(TEST_GIF) as im:
        n_frames = im.n_frames

        # Test seeking past the last frame
        with pytest.raises(EOFError):
            im.seek(n_frames)
        assert im.tell() < n_frames

        # Test that seeking to the last frame does not raise an error
        im.seek(n_frames - 1)


def test_first_frame_transparency():
    with Image.open("Tests/images/first_frame_transparency.gif") as im:
        px = im.load()
        assert px[0, 0] == im.info["transparency"]


def test_dispose_none():
    with Image.open("Tests/images/dispose_none.gif") as img:
        try:
            while True:
                img.seek(img.tell() + 1)
                assert img.disposal_method == 1
        except EOFError:
            pass


def test_dispose_none_load_end():
    # Test image created with:
    #
    # im = Image.open("transparent.gif")
    # im_rotated = im.rotate(180)
    # im.save("dispose_none_load_end.gif",
    #         save_all=True, append_images=[im_rotated], disposal=[1,2])
    with Image.open("Tests/images/dispose_none_load_end.gif") as img:
        img.seek(1)

        assert_image_equal_tofile(img, "Tests/images/dispose_none_load_end_second.gif")


def test_dispose_background():
    with Image.open("Tests/images/dispose_bgnd.gif") as img:
        try:
            while True:
                img.seek(img.tell() + 1)
                assert img.disposal_method == 2
        except EOFError:
            pass


def test_dispose_background_transparency():
    with Image.open("Tests/images/dispose_bgnd_transparency.gif") as img:
        img.seek(2)
        px = img.convert("RGBA").load()
        assert px[35, 30][3] == 0


def test_transparent_dispose():
    expected_colors = [(2, 1, 2), (0, 1, 0), (2, 1, 2)]
    with Image.open("Tests/images/transparent_dispose.gif") as img:
        for frame in range(3):
            img.seek(frame)
            for x in range(3):
                color = img.getpixel((x, 0))
                assert color == expected_colors[frame][x]


def test_dispose_previous():
    with Image.open("Tests/images/dispose_prev.gif") as img:
        try:
            while True:
                img.seek(img.tell() + 1)
                assert img.disposal_method == 3
        except EOFError:
            pass


def test_dispose_previous_first_frame():
    with Image.open("Tests/images/dispose_prev_first_frame.gif") as im:
        im.seek(1)
        assert_image_equal_tofile(
            im, "Tests/images/dispose_prev_first_frame_seeked.gif"
        )


def test_previous_frame_loaded():
    with Image.open("Tests/images/dispose_none.gif") as img:
        img.load()
        img.seek(1)
        img.load()
        img.seek(2)
        with Image.open("Tests/images/dispose_none.gif") as img_skipped:
            img_skipped.seek(2)
            assert_image_equal(img_skipped, img)


def test_save_dispose(tmp_path):
    out = str(tmp_path / "temp.gif")
    im_list = [
        Image.new("L", (100, 100), "#000"),
        Image.new("L", (100, 100), "#111"),
        Image.new("L", (100, 100), "#222"),
    ]
    for method in range(0, 4):
        im_list[0].save(out, save_all=True, append_images=im_list[1:], disposal=method)
        with Image.open(out) as img:
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

        for i in range(2):
            img.seek(img.tell() + 1)
            assert img.disposal_method == i + 1


def test_dispose2_palette(tmp_path):
    out = str(tmp_path / "temp.gif")

    # Four colors: white, grey, black, red
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


def test_dispose2_diff(tmp_path):
    out = str(tmp_path / "temp.gif")

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


def test_dispose2_background(tmp_path):
    out = str(tmp_path / "temp.gif")

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
        assert im.getpixel((0, 0)) == 0


def test_transparency_in_second_frame():
    with Image.open("Tests/images/different_transparency.gif") as im:
        assert im.info["transparency"] == 0

        # Seek to the second frame
        im.seek(im.tell() + 1)
        assert im.info["transparency"] == 0

        assert_image_equal_tofile(im, "Tests/images/different_transparency_merged.gif")


def test_no_transparency_in_second_frame():
    with Image.open("Tests/images/iss634.gif") as img:
        # Seek to the second frame
        img.seek(img.tell() + 1)
        assert "transparency" not in img.info

        # All transparent pixels should be replaced with the color from the first frame
        assert img.histogram()[255] == 0


def test_duration(tmp_path):
    duration = 1000

    out = str(tmp_path / "temp.gif")
    im = Image.new("L", (100, 100), "#000")

    # Check that the argument has priority over the info settings
    im.info["duration"] = 100
    im.save(out, duration=duration)

    with Image.open(out) as reread:
        assert reread.info["duration"] == duration


def test_multiple_duration(tmp_path):
    duration_list = [1000, 2000, 3000]

    out = str(tmp_path / "temp.gif")
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


def test_identical_frames(tmp_path):
    duration_list = [1000, 1500, 2000, 4000]

    out = str(tmp_path / "temp.gif")
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

        # Assert that the first three frames were combined
        assert reread.n_frames == 2

        # Assert that the new duration is the total of the identical frames
        assert reread.info["duration"] == 4500


def test_identical_frames_to_single_frame(tmp_path):
    for duration in ([1000, 1500, 2000, 4000], (1000, 1500, 2000, 4000), 8500):
        out = str(tmp_path / "temp.gif")
        im_list = [
            Image.new("L", (100, 100), "#000"),
            Image.new("L", (100, 100), "#000"),
            Image.new("L", (100, 100), "#000"),
        ]

        im_list[0].save(
            out, save_all=True, append_images=im_list[1:], duration=duration
        )
        with Image.open(out) as reread:
            # Assert that all frames were combined
            assert reread.n_frames == 1

            # Assert that the new duration is the total of the identical frames
            assert reread.info["duration"] == 8500


def test_number_of_loops(tmp_path):
    number_of_loops = 2

    out = str(tmp_path / "temp.gif")
    im = Image.new("L", (100, 100), "#000")
    im.save(out, loop=number_of_loops)
    with Image.open(out) as reread:

        assert reread.info["loop"] == number_of_loops


def test_background(tmp_path):
    out = str(tmp_path / "temp.gif")
    im = Image.new("L", (100, 100), "#000")
    im.info["background"] = 1
    im.save(out)
    with Image.open(out) as reread:

        assert reread.info["background"] == im.info["background"]

    if features.check("webp") and features.check("webp_anim"):
        with Image.open("Tests/images/hopper.webp") as im:
            assert isinstance(im.info["background"], tuple)
            im.save(out)


def test_comment(tmp_path):
    with Image.open(TEST_GIF) as im:
        assert im.info["comment"] == b"File written by Adobe Photoshop\xa8 4.0"

    out = str(tmp_path / "temp.gif")
    im = Image.new("L", (100, 100), "#000")
    im.info["comment"] = b"Test comment text"
    im.save(out)
    with Image.open(out) as reread:
        assert reread.info["comment"] == im.info["comment"]

    im.info["comment"] = "Test comment text"
    im.save(out)
    with Image.open(out) as reread:
        assert reread.info["comment"] == im.info["comment"].encode()


def test_comment_over_255(tmp_path):
    out = str(tmp_path / "temp.gif")
    im = Image.new("L", (100, 100), "#000")
    comment = b"Test comment text"
    while len(comment) < 256:
        comment += comment
    im.info["comment"] = comment
    im.save(out)
    with Image.open(out) as reread:

        assert reread.info["comment"] == comment


def test_zero_comment_subblocks():
    with Image.open("Tests/images/hopper_zero_comment_subblocks.gif") as im:
        assert_image_equal_tofile(im, TEST_GIF)


def test_version(tmp_path):
    out = str(tmp_path / "temp.gif")

    def assertVersionAfterSave(im, version):
        im.save(out)
        with Image.open(out) as reread:
            assert reread.info["version"] == version

    # Test that GIF87a is used by default
    im = Image.new("L", (100, 100), "#000")
    assertVersionAfterSave(im, b"GIF87a")

    # Test setting the version to 89a
    im = Image.new("L", (100, 100), "#000")
    im.info["version"] = b"89a"
    assertVersionAfterSave(im, b"GIF89a")

    # Test that adding a GIF89a feature changes the version
    im.info["transparency"] = 1
    assertVersionAfterSave(im, b"GIF89a")

    # Test that a GIF87a image is also saved in that format
    with Image.open("Tests/images/test.colors.gif") as im:
        assertVersionAfterSave(im, b"GIF87a")

        # Test that a GIF89a image is also saved in that format
        im.info["version"] = b"GIF89a"
        assertVersionAfterSave(im, b"GIF87a")


def test_append_images(tmp_path):
    out = str(tmp_path / "temp.gif")

    # Test appending single frame images
    im = Image.new("RGB", (100, 100), "#f00")
    ims = [Image.new("RGB", (100, 100), color) for color in ["#0f0", "#00f"]]
    im.copy().save(out, save_all=True, append_images=ims)

    with Image.open(out) as reread:
        assert reread.n_frames == 3

    # Tests appending using a generator
    def imGenerator(ims):
        yield from ims

    im.save(out, save_all=True, append_images=imGenerator(ims))

    with Image.open(out) as reread:
        assert reread.n_frames == 3

    # Tests appending single and multiple frame images
    with Image.open("Tests/images/dispose_none.gif") as im:
        with Image.open("Tests/images/dispose_prev.gif") as im2:
            im.save(out, save_all=True, append_images=[im2])

    with Image.open(out) as reread:
        assert reread.n_frames == 10


def test_transparent_optimize(tmp_path):
    # From issue #2195, if the transparent color is incorrectly optimized out, GIF loses
    # transparency.
    # Need a palette that isn't using the 0 color, and one that's > 128 items where the
    # transparent color is actually the top palette entry to trigger the bug.

    data = bytes(range(1, 254))
    palette = ImagePalette.ImagePalette("RGB", list(range(256)) * 3)

    im = Image.new("L", (253, 1))
    im.frombytes(data)
    im.putpalette(palette)

    out = str(tmp_path / "temp.gif")
    im.save(out, transparency=253)
    with Image.open(out) as reloaded:

        assert reloaded.info["transparency"] == 253


def test_rgb_transparency(tmp_path):
    out = str(tmp_path / "temp.gif")

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
    pytest.warns(UserWarning, im.save, out, save_all=True, append_images=ims)

    with Image.open(out) as reloaded:
        assert "transparency" not in reloaded.info


def test_bbox(tmp_path):
    out = str(tmp_path / "temp.gif")

    im = Image.new("RGB", (100, 100), "#fff")
    ims = [Image.new("RGB", (100, 100), "#000")]
    im.save(out, save_all=True, append_images=ims)

    with Image.open(out) as reread:
        assert reread.n_frames == 2


def test_palette_save_L(tmp_path):
    # Generate an L mode image with a separate palette

    im = hopper("P")
    im_l = Image.frombytes("L", im.size, im.tobytes())
    palette = bytes(im.getpalette())

    out = str(tmp_path / "temp.gif")
    im_l.save(out, palette=palette)

    with Image.open(out) as reloaded:
        assert_image_equal(reloaded.convert("RGB"), im.convert("RGB"))


def test_palette_save_P(tmp_path):
    # Pass in a different palette, then construct what the image would look like.
    # Forcing a non-straight grayscale palette.

    im = hopper("P")
    palette = bytes([255 - i // 3 for i in range(768)])

    out = str(tmp_path / "temp.gif")
    im.save(out, palette=palette)

    with Image.open(out) as reloaded:
        im.putpalette(palette)
        assert_image_equal(reloaded, im)


def test_palette_save_all_P(tmp_path):
    frames = []
    colors = ((255, 0, 0), (0, 255, 0))
    for color in colors:
        frame = Image.new("P", (100, 100))
        frame.putpalette(color)
        frames.append(frame)

    out = str(tmp_path / "temp.gif")
    frames[0].save(
        out, save_all=True, palette=[255, 0, 0, 0, 255, 0], append_images=frames[1:]
    )

    with Image.open(out) as im:
        # Assert that the frames are correct, and each frame has the same palette
        assert_image_equal(im.convert("RGB"), frames[0].convert("RGB"))
        assert im.palette.palette == im.global_palette.palette

        im.seek(1)
        assert_image_equal(im.convert("RGB"), frames[1].convert("RGB"))
        assert im.palette.palette == im.global_palette.palette


def test_palette_save_ImagePalette(tmp_path):
    # Pass in a different palette, as an ImagePalette.ImagePalette
    # effectively the same as test_palette_save_P

    im = hopper("P")
    palette = ImagePalette.ImagePalette("RGB", list(range(256))[::-1] * 3)

    out = str(tmp_path / "temp.gif")
    im.save(out, palette=palette)

    with Image.open(out) as reloaded:
        im.putpalette(palette)
        assert_image_equal(reloaded.convert("RGB"), im.convert("RGB"))


def test_save_I(tmp_path):
    # Test saving something that would trigger the auto-convert to 'L'

    im = hopper("I")

    out = str(tmp_path / "temp.gif")
    im.save(out)

    with Image.open(out) as reloaded:
        assert_image_equal(reloaded.convert("L"), im.convert("L"))


def test_getdata():
    # Test getheader/getdata against legacy values.
    # Create a 'P' image with holes in the palette.
    im = Image._wedge().resize((16, 16), Image.NEAREST)
    im.putpalette(ImagePalette.ImagePalette("RGB"))
    im.info = {"background": 0}

    passed_palette = bytes([255 - i // 3 for i in range(768)])

    GifImagePlugin._FORCE_OPTIMIZE = True
    try:
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
    finally:
        GifImagePlugin._FORCE_OPTIMIZE = False


def test_lzw_bits():
    # see https://github.com/python-pillow/Pillow/issues/2811
    with Image.open("Tests/images/issue_2811.gif") as im:
        assert im.tile[0][3][0] == 11  # LZW bits
        # codec error prepatch
        im.load()


def test_extents():
    with Image.open("Tests/images/test_extents.gif") as im:
        assert im.size == (100, 100)
        im.seek(1)
        assert im.size == (150, 150)


def test_missing_background():
    # The Global Color Table Flag isn't set, so there is no background color index,
    # but the disposal method is "Restore to background color"
    with Image.open("Tests/images/missing_background.gif") as im:
        im.seek(1)
        assert_image_equal_tofile(im, "Tests/images/missing_background_first_frame.gif")
