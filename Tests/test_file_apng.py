from __future__ import annotations

from pathlib import Path

import pytest

from PIL import Image, ImageSequence, PngImagePlugin


# APNG browser support tests and fixtures via:
# https://philip.html5.org/tests/apng/tests.html
# (referenced from https://wiki.mozilla.org/APNG_Specification)
def test_apng_basic() -> None:
    with Image.open("Tests/images/apng/single_frame.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        assert not im.is_animated
        assert im.n_frames == 1
        assert im.get_format_mimetype() == "image/apng"
        assert im.info.get("default_image") is None
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/single_frame_default.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        assert im.is_animated
        assert im.n_frames == 2
        assert im.get_format_mimetype() == "image/apng"
        assert im.info.get("default_image")
        assert im.getpixel((0, 0)) == (255, 0, 0, 255)
        assert im.getpixel((64, 32)) == (255, 0, 0, 255)
        im.seek(1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

        # test out of bounds seek
        with pytest.raises(EOFError):
            im.seek(2)

        im.seek(0)
        with pytest.raises(ValueError, match="cannot seek to frame 2"):
            im._seek(2)

        # test rewind support
        assert im.getpixel((0, 0)) == (255, 0, 0, 255)
        assert im.getpixel((64, 32)) == (255, 0, 0, 255)
        im.seek(1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)


@pytest.mark.parametrize(
    "filename",
    ("Tests/images/apng/split_fdat.png", "Tests/images/apng/split_fdat_zero_chunk.png"),
)
def test_apng_fdat(filename: str) -> None:
    with Image.open(filename) as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)


def test_apng_dispose() -> None:
    with Image.open("Tests/images/apng/dispose_op_none.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/dispose_op_background.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)

    with Image.open("Tests/images/apng/dispose_op_background_final.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/dispose_op_previous.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/dispose_op_previous_final.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/dispose_op_previous_first.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)


def test_apng_dispose_region() -> None:
    with Image.open("Tests/images/apng/dispose_op_none_region.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/dispose_op_background_before_region.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)

    with Image.open("Tests/images/apng/dispose_op_background_region.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 0, 255, 255)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)

    with Image.open("Tests/images/apng/dispose_op_previous_region.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)


def test_apng_dispose_op_previous_frame() -> None:
    # Test that the dispose settings being used are from the previous frame
    #
    # Image created with:
    # red = Image.new("RGBA", (128, 64), (255, 0, 0, 255))
    # green = red.copy()
    # green.paste(Image.new("RGBA", (64, 32), (0, 255, 0, 255)))
    # blue = red.copy()
    # blue.paste(Image.new("RGBA", (64, 32), (0, 255, 0, 255)), (64, 32))
    #
    # red.save(
    #     "Tests/images/apng/dispose_op_previous_frame.png",
    #     save_all=True,
    #     append_images=[green, blue],
    #     disposal=[
    #         PngImagePlugin.Disposal.OP_NONE,
    #         PngImagePlugin.Disposal.OP_PREVIOUS,
    #         PngImagePlugin.Disposal.OP_PREVIOUS
    #     ],
    # )
    with Image.open("Tests/images/apng/dispose_op_previous_frame.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (255, 0, 0, 255)


def test_apng_dispose_op_background_p_mode() -> None:
    with Image.open("Tests/images/apng/dispose_op_background_p_mode.png") as im:
        im.seek(1)
        im.load()
        assert im.size == (128, 64)


def test_apng_blend() -> None:
    with Image.open("Tests/images/apng/blend_op_source_solid.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/blend_op_source_transparent.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)

    with Image.open("Tests/images/apng/blend_op_source_near_transparent.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 2)
        assert im.getpixel((64, 32)) == (0, 255, 0, 2)

    with Image.open("Tests/images/apng/blend_op_over.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/blend_op_over_near_transparent.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 97)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)


def test_apng_blend_transparency() -> None:
    with Image.open("Tests/images/blend_transparency.png") as im:
        im.seek(1)
        assert im.getpixel((0, 0)) == (255, 0, 0)


def test_apng_chunk_order() -> None:
    with Image.open("Tests/images/apng/fctl_actl.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)


def test_apng_delay() -> None:
    with Image.open("Tests/images/apng/delay.png") as im:
        im.seek(1)
        assert im.info.get("duration") == 500.0
        im.seek(2)
        assert im.info.get("duration") == 1000.0
        im.seek(3)
        assert im.info.get("duration") == 500.0
        im.seek(4)
        assert im.info.get("duration") == 1000.0

    with Image.open("Tests/images/apng/delay_round.png") as im:
        im.seek(1)
        assert im.info.get("duration") == 500.0
        im.seek(2)
        assert im.info.get("duration") == 1000.0

    with Image.open("Tests/images/apng/delay_short_max.png") as im:
        im.seek(1)
        assert im.info.get("duration") == 500.0
        im.seek(2)
        assert im.info.get("duration") == 1000.0

    with Image.open("Tests/images/apng/delay_zero_denom.png") as im:
        im.seek(1)
        assert im.info.get("duration") == 500.0
        im.seek(2)
        assert im.info.get("duration") == 1000.0

    with Image.open("Tests/images/apng/delay_zero_numer.png") as im:
        im.seek(1)
        assert im.info.get("duration") == 0.0
        im.seek(2)
        assert im.info.get("duration") == 0.0
        im.seek(3)
        assert im.info.get("duration") == 500.0
        im.seek(4)
        assert im.info.get("duration") == 1000.0


def test_apng_num_plays() -> None:
    with Image.open("Tests/images/apng/num_plays.png") as im:
        assert im.info.get("loop") == 0

    with Image.open("Tests/images/apng/num_plays_1.png") as im:
        assert im.info.get("loop") == 1


def test_apng_mode() -> None:
    with Image.open("Tests/images/apng/mode_16bit.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        assert im.mode == "RGBA"
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 0, 128, 191)
        assert im.getpixel((64, 32)) == (0, 0, 128, 191)

    with Image.open("Tests/images/apng/mode_grayscale.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        assert im.mode == "L"
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == 128
        assert im.getpixel((64, 32)) == 255

    with Image.open("Tests/images/apng/mode_grayscale_alpha.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        assert im.mode == "LA"
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (128, 191)
        assert im.getpixel((64, 32)) == (128, 191)

    with Image.open("Tests/images/apng/mode_palette.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        assert im.mode == "P"
        im.seek(im.n_frames - 1)
        im = im.convert("RGB")
        assert im.getpixel((0, 0)) == (0, 255, 0)
        assert im.getpixel((64, 32)) == (0, 255, 0)

    with Image.open("Tests/images/apng/mode_palette_alpha.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        assert im.mode == "P"
        im.seek(im.n_frames - 1)
        im = im.convert("RGBA")
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/mode_palette_1bit_alpha.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        assert im.mode == "P"
        im.seek(im.n_frames - 1)
        im = im.convert("RGBA")
        assert im.getpixel((0, 0)) == (0, 0, 255, 128)
        assert im.getpixel((64, 32)) == (0, 0, 255, 128)


def test_apng_chunk_errors() -> None:
    with Image.open("Tests/images/apng/chunk_no_actl.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        assert not im.is_animated

    with pytest.warns(UserWarning, match="Invalid APNG"):
        im = Image.open("Tests/images/apng/chunk_multi_actl.png")
    assert isinstance(im, PngImagePlugin.PngImageFile)
    assert not im.is_animated
    im.close()

    with Image.open("Tests/images/apng/chunk_actl_after_idat.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        assert not im.is_animated

    with Image.open("Tests/images/apng/chunk_no_fctl.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        with pytest.raises(SyntaxError):
            im.seek(im.n_frames - 1)

    with Image.open("Tests/images/apng/chunk_repeat_fctl.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        with pytest.raises(SyntaxError):
            im.seek(im.n_frames - 1)

    with Image.open("Tests/images/apng/chunk_no_fdat.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        with pytest.raises(SyntaxError):
            im.seek(im.n_frames - 1)


def test_apng_syntax_errors() -> None:
    with pytest.warns(UserWarning, match="Invalid APNG"):
        im = Image.open("Tests/images/apng/syntax_num_frames_zero.png")
    assert isinstance(im, PngImagePlugin.PngImageFile)
    assert not im.is_animated
    with pytest.raises(OSError):
        im.load()
    im.close()

    with pytest.warns(UserWarning, match="Invalid APNG"):
        im = Image.open("Tests/images/apng/syntax_num_frames_zero_default.png")
    assert isinstance(im, PngImagePlugin.PngImageFile)
    assert not im.is_animated
    im.load()
    im.close()

    # we can handle this case gracefully
    with Image.open("Tests/images/apng/syntax_num_frames_low.png") as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)

    with pytest.raises(OSError):
        with Image.open("Tests/images/apng/syntax_num_frames_high.png") as im:
            assert isinstance(im, PngImagePlugin.PngImageFile)
            im.seek(im.n_frames - 1)
            im.load()

    with pytest.warns(UserWarning, match="Invalid APNG"):
        im = Image.open("Tests/images/apng/syntax_num_frames_invalid.png")
    assert isinstance(im, PngImagePlugin.PngImageFile)
    assert not im.is_animated
    im.load()
    im.close()


@pytest.mark.parametrize(
    "test_file",
    (
        "sequence_start.png",
        "sequence_gap.png",
        "sequence_repeat.png",
        "sequence_repeat_chunk.png",
        "sequence_reorder.png",
        "sequence_reorder_chunk.png",
        "sequence_fdat_fctl.png",
    ),
)
def test_apng_sequence_errors(test_file: str) -> None:
    with pytest.raises(SyntaxError):
        with Image.open(f"Tests/images/apng/{test_file}") as im:
            assert isinstance(im, PngImagePlugin.PngImageFile)
            im.seek(im.n_frames - 1)
            im.load()


def test_apng_save(tmp_path: Path) -> None:
    with Image.open("Tests/images/apng/single_frame.png") as im:
        test_file = tmp_path / "temp.png"
        im.save(test_file, save_all=True)

    with Image.open(test_file) as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.load()
        assert not im.is_animated
        assert im.n_frames == 1
        assert im.get_format_mimetype() == "image/png"
        assert im.info.get("default_image") is None
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/single_frame_default.png") as im:
        frames = [frame_im.copy() for frame_im in ImageSequence.Iterator(im)]
        frames[0].save(
            test_file, save_all=True, default_image=True, append_images=frames[1:]
        )

    with Image.open(test_file) as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.load()
        assert im.is_animated
        assert im.n_frames == 2
        assert im.get_format_mimetype() == "image/apng"
        assert im.info.get("default_image")
        im.seek(1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)


def test_apng_save_alpha(tmp_path: Path) -> None:
    test_file = tmp_path / "temp.png"

    im = Image.new("RGBA", (1, 1), (255, 0, 0, 255))
    im2 = Image.new("RGBA", (1, 1), (255, 0, 0, 127))
    im.save(test_file, save_all=True, append_images=[im2])

    with Image.open(test_file) as reloaded:
        assert reloaded.getpixel((0, 0)) == (255, 0, 0, 255)

        reloaded.seek(1)
        assert reloaded.getpixel((0, 0)) == (255, 0, 0, 127)


def test_apng_save_split_fdat(tmp_path: Path) -> None:
    # test to make sure we do not generate sequence errors when writing
    # frames with image data spanning multiple fdAT chunks (in this case
    # both the default image and first animation frame will span multiple
    # data chunks)
    test_file = tmp_path / "temp.png"
    with Image.open("Tests/images/old-style-jpeg-compression.png") as im:
        frames = [im.copy(), Image.new("RGBA", im.size, (255, 0, 0, 255))]
        im.save(
            test_file,
            save_all=True,
            default_image=True,
            append_images=frames,
        )
    with Image.open(test_file) as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        im.seek(im.n_frames - 1)
        im.load()


def test_apng_save_duration_loop(tmp_path: Path) -> None:
    test_file = tmp_path / "temp.png"
    with Image.open("Tests/images/apng/delay.png") as im:
        frames = []
        durations = []
        loop = im.info.get("loop")
        default_image = im.info.get("default_image")
        for i, frame_im in enumerate(ImageSequence.Iterator(im)):
            frames.append(frame_im.copy())
            if i != 0 or not default_image:
                durations.append(frame_im.info.get("duration", 0))
        frames[0].save(
            test_file,
            save_all=True,
            default_image=default_image,
            append_images=frames[1:],
            duration=durations,
            loop=loop,
        )

    with Image.open(test_file) as im:
        im.load()
        assert im.info.get("loop") == loop
        im.seek(1)
        assert im.info.get("duration") == 500.0
        im.seek(2)
        assert im.info.get("duration") == 1000.0
        im.seek(3)
        assert im.info.get("duration") == 500.0
        im.seek(4)
        assert im.info.get("duration") == 1000.0

    # test removal of duplicated frames
    frame = Image.new("RGBA", (128, 64), (255, 0, 0, 255))
    frame.save(
        test_file, save_all=True, append_images=[frame, frame], duration=[500, 100, 150]
    )
    with Image.open(test_file) as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        assert im.n_frames == 1
        assert "duration" not in im.info

    different_frame = Image.new("RGBA", (128, 64))
    frame.save(
        test_file,
        save_all=True,
        append_images=[frame, different_frame],
        duration=[500, 100, 150],
    )
    with Image.open(test_file) as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        assert im.n_frames == 2
        assert im.info["duration"] == 600

        im.seek(1)
        assert im.info["duration"] == 150

    # test info duration
    frame.info["duration"] = 300
    frame.save(test_file, save_all=True, append_images=[frame, different_frame])
    with Image.open(test_file) as im:
        assert isinstance(im, PngImagePlugin.PngImageFile)
        assert im.n_frames == 2
        assert im.info["duration"] == 600


def test_apng_save_disposal(tmp_path: Path) -> None:
    test_file = tmp_path / "temp.png"
    size = (128, 64)
    red = Image.new("RGBA", size, (255, 0, 0, 255))
    green = Image.new("RGBA", size, (0, 255, 0, 255))
    transparent = Image.new("RGBA", size, (0, 0, 0, 0))

    # test OP_NONE
    red.save(
        test_file,
        save_all=True,
        append_images=[green, transparent],
        disposal=PngImagePlugin.Disposal.OP_NONE,
        blend=PngImagePlugin.Blend.OP_OVER,
    )
    with Image.open(test_file) as im:
        im.seek(2)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    # test OP_BACKGROUND
    disposal = [
        PngImagePlugin.Disposal.OP_NONE,
        PngImagePlugin.Disposal.OP_BACKGROUND,
        PngImagePlugin.Disposal.OP_NONE,
    ]
    red.save(
        test_file,
        save_all=True,
        append_images=[red, transparent],
        disposal=disposal,
        blend=PngImagePlugin.Blend.OP_OVER,
    )
    with Image.open(test_file) as im:
        im.seek(2)
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)

    disposal = [
        PngImagePlugin.Disposal.OP_NONE,
        PngImagePlugin.Disposal.OP_BACKGROUND,
    ]
    red.save(
        test_file,
        save_all=True,
        append_images=[green],
        disposal=disposal,
        blend=PngImagePlugin.Blend.OP_OVER,
    )
    with Image.open(test_file) as im:
        im.seek(1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    # test OP_PREVIOUS
    disposal = [
        PngImagePlugin.Disposal.OP_NONE,
        PngImagePlugin.Disposal.OP_PREVIOUS,
        PngImagePlugin.Disposal.OP_NONE,
    ]
    red.save(
        test_file,
        save_all=True,
        append_images=[green, red, transparent],
        default_image=True,
        disposal=disposal,
        blend=PngImagePlugin.Blend.OP_OVER,
    )
    with Image.open(test_file) as im:
        im.seek(3)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    disposal = [
        PngImagePlugin.Disposal.OP_NONE,
        PngImagePlugin.Disposal.OP_PREVIOUS,
    ]
    red.save(
        test_file,
        save_all=True,
        append_images=[green],
        disposal=disposal,
        blend=PngImagePlugin.Blend.OP_OVER,
    )
    with Image.open(test_file) as im:
        im.seek(1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    # test info disposal
    red.info["disposal"] = PngImagePlugin.Disposal.OP_BACKGROUND
    red.save(
        test_file,
        save_all=True,
        append_images=[Image.new("RGBA", (10, 10), (0, 255, 0, 255))],
    )
    with Image.open(test_file) as im:
        im.seek(1)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)


def test_apng_save_disposal_previous(tmp_path: Path) -> None:
    test_file = tmp_path / "temp.png"
    size = (128, 64)
    blue = Image.new("RGBA", size, (0, 0, 255, 255))
    red = Image.new("RGBA", size, (255, 0, 0, 255))
    green = Image.new("RGBA", size, (0, 255, 0, 255))

    # test OP_NONE
    blue.save(
        test_file,
        save_all=True,
        append_images=[red, green],
        disposal=PngImagePlugin.Disposal.OP_PREVIOUS,
    )
    with Image.open(test_file) as im:
        assert im.getpixel((0, 0)) == (0, 0, 255, 255)

        im.seek(2)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)


def test_apng_save_blend(tmp_path: Path) -> None:
    test_file = tmp_path / "temp.png"
    size = (128, 64)
    red = Image.new("RGBA", size, (255, 0, 0, 255))
    green = Image.new("RGBA", size, (0, 255, 0, 255))
    transparent = Image.new("RGBA", size, (0, 0, 0, 0))

    # test OP_SOURCE on solid color
    blend = [
        PngImagePlugin.Blend.OP_OVER,
        PngImagePlugin.Blend.OP_SOURCE,
    ]
    red.save(
        test_file,
        save_all=True,
        append_images=[red, green],
        default_image=True,
        disposal=PngImagePlugin.Disposal.OP_NONE,
        blend=blend,
    )
    with Image.open(test_file) as im:
        im.seek(2)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    # test OP_SOURCE on transparent color
    blend = [
        PngImagePlugin.Blend.OP_OVER,
        PngImagePlugin.Blend.OP_SOURCE,
    ]
    red.save(
        test_file,
        save_all=True,
        append_images=[red, transparent],
        default_image=True,
        disposal=PngImagePlugin.Disposal.OP_NONE,
        blend=blend,
    )
    with Image.open(test_file) as im:
        im.seek(2)
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)

    # test OP_OVER
    red.save(
        test_file,
        save_all=True,
        append_images=[green, transparent],
        default_image=True,
        disposal=PngImagePlugin.Disposal.OP_NONE,
        blend=PngImagePlugin.Blend.OP_OVER,
    )
    with Image.open(test_file) as im:
        im.seek(1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)
        im.seek(2)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    # test info blend
    red.info["blend"] = PngImagePlugin.Blend.OP_OVER
    red.save(test_file, save_all=True, append_images=[green, transparent])
    with Image.open(test_file) as im:
        im.seek(2)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)


def test_apng_save_size(tmp_path: Path) -> None:
    test_file = tmp_path / "temp.png"

    im = Image.new("L", (100, 100))
    im.save(test_file, save_all=True, append_images=[Image.new("L", (200, 200))])

    with Image.open(test_file) as reloaded:
        assert reloaded.size == (200, 200)


def test_seek_after_close() -> None:
    im = Image.open("Tests/images/apng/delay.png")
    im.seek(1)
    im.close()

    with pytest.raises(ValueError):
        im.seek(0)


@pytest.mark.parametrize("mode", ("RGBA", "RGB", "P"))
@pytest.mark.parametrize("default_image", (True, False))
@pytest.mark.parametrize("duplicate", (True, False))
def test_different_modes_in_later_frames(
    mode: str, default_image: bool, duplicate: bool, tmp_path: Path
) -> None:
    test_file = tmp_path / "temp.png"

    im = Image.new("L", (1, 1))
    im.save(
        test_file,
        save_all=True,
        default_image=default_image,
        append_images=[im.convert(mode) if duplicate else Image.new(mode, (1, 1), 1)],
    )
    with Image.open(test_file) as reloaded:
        assert reloaded.mode == mode


def test_different_durations(tmp_path: Path) -> None:
    test_file = tmp_path / "temp.png"

    with Image.open("Tests/images/apng/different_durations.png") as im:
        for _ in range(3):
            im.seek(0)
            assert im.info["duration"] == 4000

            im.seek(1)
            assert im.info["duration"] == 1000

        im.save(test_file, save_all=True)

    with Image.open(test_file) as reloaded:
        assert reloaded.info["duration"] == 4000

        reloaded.seek(1)
        assert reloaded.info["duration"] == 1000
