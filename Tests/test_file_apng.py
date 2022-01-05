import pytest

from PIL import Image, ImageSequence, PngImagePlugin


# APNG browser support tests and fixtures via:
# https://philip.html5.org/tests/apng/tests.html
# (referenced from https://wiki.mozilla.org/APNG_Specification)
def test_apng_basic():
    with Image.open("Tests/images/apng/single_frame.png") as im:
        assert not im.is_animated
        assert im.n_frames == 1
        assert im.get_format_mimetype() == "image/apng"
        assert im.info.get("default_image") is None
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/single_frame_default.png") as im:
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

        # test rewind support
        im.seek(0)
        assert im.getpixel((0, 0)) == (255, 0, 0, 255)
        assert im.getpixel((64, 32)) == (255, 0, 0, 255)
        im.seek(1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)


def test_apng_fdat():
    with Image.open("Tests/images/apng/split_fdat.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/split_fdat_zero_chunk.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)


def test_apng_dispose():
    with Image.open("Tests/images/apng/dispose_op_none.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/dispose_op_background.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)

    with Image.open("Tests/images/apng/dispose_op_background_final.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/dispose_op_previous.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/dispose_op_previous_final.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/dispose_op_previous_first.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)


def test_apng_dispose_region():
    with Image.open("Tests/images/apng/dispose_op_none_region.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/dispose_op_background_before_region.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)

    with Image.open("Tests/images/apng/dispose_op_background_region.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 0, 255, 255)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)

    with Image.open("Tests/images/apng/dispose_op_previous_region.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)


def test_apng_dispose_op_previous_frame():
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
    #         PngImagePlugin.APNG_DISPOSE_OP_NONE,
    #         PngImagePlugin.APNG_DISPOSE_OP_PREVIOUS,
    #         PngImagePlugin.APNG_DISPOSE_OP_PREVIOUS
    #     ],
    # )
    with Image.open("Tests/images/apng/dispose_op_previous_frame.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (255, 0, 0, 255)


def test_apng_dispose_op_background_p_mode():
    with Image.open("Tests/images/apng/dispose_op_background_p_mode.png") as im:
        im.seek(1)
        im.load()
        assert im.size == (128, 64)


def test_apng_blend():
    with Image.open("Tests/images/apng/blend_op_source_solid.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/blend_op_source_transparent.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)

    with Image.open("Tests/images/apng/blend_op_source_near_transparent.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 2)
        assert im.getpixel((64, 32)) == (0, 255, 0, 2)

    with Image.open("Tests/images/apng/blend_op_over.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/blend_op_over_near_transparent.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 97)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)


def test_apng_chunk_order():
    with Image.open("Tests/images/apng/fctl_actl.png") as im:
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)


def test_apng_delay():
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


def test_apng_num_plays():
    with Image.open("Tests/images/apng/num_plays.png") as im:
        assert im.info.get("loop") == 0

    with Image.open("Tests/images/apng/num_plays_1.png") as im:
        assert im.info.get("loop") == 1


def test_apng_mode():
    with Image.open("Tests/images/apng/mode_16bit.png") as im:
        assert im.mode == "RGBA"
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (0, 0, 128, 191)
        assert im.getpixel((64, 32)) == (0, 0, 128, 191)

    with Image.open("Tests/images/apng/mode_greyscale.png") as im:
        assert im.mode == "L"
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == 128
        assert im.getpixel((64, 32)) == 255

    with Image.open("Tests/images/apng/mode_greyscale_alpha.png") as im:
        assert im.mode == "LA"
        im.seek(im.n_frames - 1)
        assert im.getpixel((0, 0)) == (128, 191)
        assert im.getpixel((64, 32)) == (128, 191)

    with Image.open("Tests/images/apng/mode_palette.png") as im:
        assert im.mode == "P"
        im.seek(im.n_frames - 1)
        im = im.convert("RGB")
        assert im.getpixel((0, 0)) == (0, 255, 0)
        assert im.getpixel((64, 32)) == (0, 255, 0)

    with Image.open("Tests/images/apng/mode_palette_alpha.png") as im:
        assert im.mode == "P"
        im.seek(im.n_frames - 1)
        im = im.convert("RGBA")
        assert im.getpixel((0, 0)) == (255, 0, 0, 0)
        assert im.getpixel((64, 32)) == (255, 0, 0, 0)

    with Image.open("Tests/images/apng/mode_palette_1bit_alpha.png") as im:
        assert im.mode == "P"
        im.seek(im.n_frames - 1)
        im = im.convert("RGBA")
        assert im.getpixel((0, 0)) == (0, 0, 255, 128)
        assert im.getpixel((64, 32)) == (0, 0, 255, 128)


def test_apng_chunk_errors():
    with Image.open("Tests/images/apng/chunk_no_actl.png") as im:
        assert not im.is_animated

    def open():
        with Image.open("Tests/images/apng/chunk_multi_actl.png") as im:
            im.load()
        assert not im.is_animated

    pytest.warns(UserWarning, open)

    with Image.open("Tests/images/apng/chunk_actl_after_idat.png") as im:
        assert not im.is_animated

    with Image.open("Tests/images/apng/chunk_no_fctl.png") as im:
        with pytest.raises(SyntaxError):
            im.seek(im.n_frames - 1)

    with Image.open("Tests/images/apng/chunk_repeat_fctl.png") as im:
        with pytest.raises(SyntaxError):
            im.seek(im.n_frames - 1)

    with Image.open("Tests/images/apng/chunk_no_fdat.png") as im:
        with pytest.raises(SyntaxError):
            im.seek(im.n_frames - 1)


def test_apng_syntax_errors():
    def open_frames_zero():
        with Image.open("Tests/images/apng/syntax_num_frames_zero.png") as im:
            assert not im.is_animated
            with pytest.raises(OSError):
                im.load()

    pytest.warns(UserWarning, open_frames_zero)

    def open_frames_zero_default():
        with Image.open("Tests/images/apng/syntax_num_frames_zero_default.png") as im:
            assert not im.is_animated
            im.load()

    pytest.warns(UserWarning, open_frames_zero_default)

    # we can handle this case gracefully
    exception = None
    with Image.open("Tests/images/apng/syntax_num_frames_low.png") as im:
        try:
            im.seek(im.n_frames - 1)
        except Exception as e:
            exception = e
        assert exception is None

    with pytest.raises(OSError):
        with Image.open("Tests/images/apng/syntax_num_frames_high.png") as im:
            im.seek(im.n_frames - 1)
            im.load()

    def open():
        with Image.open("Tests/images/apng/syntax_num_frames_invalid.png") as im:
            assert not im.is_animated
            im.load()

    pytest.warns(UserWarning, open)


def test_apng_sequence_errors():
    test_files = [
        "sequence_start.png",
        "sequence_gap.png",
        "sequence_repeat.png",
        "sequence_repeat_chunk.png",
        "sequence_reorder.png",
        "sequence_reorder_chunk.png",
        "sequence_fdat_fctl.png",
    ]
    for f in test_files:
        with pytest.raises(SyntaxError):
            with Image.open(f"Tests/images/apng/{f}") as im:
                im.seek(im.n_frames - 1)
                im.load()


def test_apng_save(tmp_path):
    with Image.open("Tests/images/apng/single_frame.png") as im:
        test_file = str(tmp_path / "temp.png")
        im.save(test_file, save_all=True)

    with Image.open(test_file) as im:
        im.load()
        assert not im.is_animated
        assert im.n_frames == 1
        assert im.get_format_mimetype() == "image/apng"
        assert im.info.get("default_image") is None
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    with Image.open("Tests/images/apng/single_frame_default.png") as im:
        frames = []
        for frame_im in ImageSequence.Iterator(im):
            frames.append(frame_im.copy())
        frames[0].save(
            test_file, save_all=True, default_image=True, append_images=frames[1:]
        )

    with Image.open(test_file) as im:
        im.load()
        assert im.is_animated
        assert im.n_frames == 2
        assert im.get_format_mimetype() == "image/apng"
        assert im.info.get("default_image")
        im.seek(1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)


def test_apng_save_split_fdat(tmp_path):
    # test to make sure we do not generate sequence errors when writing
    # frames with image data spanning multiple fdAT chunks (in this case
    # both the default image and first animation frame will span multiple
    # data chunks)
    test_file = str(tmp_path / "temp.png")
    with Image.open("Tests/images/old-style-jpeg-compression.png") as im:
        frames = [im.copy(), Image.new("RGBA", im.size, (255, 0, 0, 255))]
        im.save(
            test_file,
            save_all=True,
            default_image=True,
            append_images=frames,
        )
    with Image.open(test_file) as im:
        exception = None
        try:
            im.seek(im.n_frames - 1)
            im.load()
        except Exception as e:
            exception = e
        assert exception is None


def test_apng_save_duration_loop(tmp_path):
    test_file = str(tmp_path / "temp.png")
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
        im.load()
        assert im.n_frames == 1
        assert im.info.get("duration") == 750

    # test info duration
    frame.info["duration"] = 750
    frame.save(test_file, save_all=True)
    with Image.open(test_file) as im:
        assert im.info.get("duration") == 750


def test_apng_save_disposal(tmp_path):
    test_file = str(tmp_path / "temp.png")
    size = (128, 64)
    red = Image.new("RGBA", size, (255, 0, 0, 255))
    green = Image.new("RGBA", size, (0, 255, 0, 255))
    transparent = Image.new("RGBA", size, (0, 0, 0, 0))

    # test APNG_DISPOSE_OP_NONE
    red.save(
        test_file,
        save_all=True,
        append_images=[green, transparent],
        disposal=PngImagePlugin.APNG_DISPOSE_OP_NONE,
        blend=PngImagePlugin.APNG_BLEND_OP_OVER,
    )
    with Image.open(test_file) as im:
        im.seek(2)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    # test APNG_DISPOSE_OP_BACKGROUND
    disposal = [
        PngImagePlugin.APNG_DISPOSE_OP_NONE,
        PngImagePlugin.APNG_DISPOSE_OP_BACKGROUND,
        PngImagePlugin.APNG_DISPOSE_OP_NONE,
    ]
    red.save(
        test_file,
        save_all=True,
        append_images=[red, transparent],
        disposal=disposal,
        blend=PngImagePlugin.APNG_BLEND_OP_OVER,
    )
    with Image.open(test_file) as im:
        im.seek(2)
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)

    disposal = [
        PngImagePlugin.APNG_DISPOSE_OP_NONE,
        PngImagePlugin.APNG_DISPOSE_OP_BACKGROUND,
    ]
    red.save(
        test_file,
        save_all=True,
        append_images=[green],
        disposal=disposal,
        blend=PngImagePlugin.APNG_BLEND_OP_OVER,
    )
    with Image.open(test_file) as im:
        im.seek(1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    # test APNG_DISPOSE_OP_PREVIOUS
    disposal = [
        PngImagePlugin.APNG_DISPOSE_OP_NONE,
        PngImagePlugin.APNG_DISPOSE_OP_PREVIOUS,
        PngImagePlugin.APNG_DISPOSE_OP_NONE,
    ]
    red.save(
        test_file,
        save_all=True,
        append_images=[green, red, transparent],
        default_image=True,
        disposal=disposal,
        blend=PngImagePlugin.APNG_BLEND_OP_OVER,
    )
    with Image.open(test_file) as im:
        im.seek(3)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    disposal = [
        PngImagePlugin.APNG_DISPOSE_OP_NONE,
        PngImagePlugin.APNG_DISPOSE_OP_PREVIOUS,
    ]
    red.save(
        test_file,
        save_all=True,
        append_images=[green],
        disposal=disposal,
        blend=PngImagePlugin.APNG_BLEND_OP_OVER,
    )
    with Image.open(test_file) as im:
        im.seek(1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    # test info disposal
    red.info["disposal"] = PngImagePlugin.APNG_DISPOSE_OP_BACKGROUND
    red.save(
        test_file,
        save_all=True,
        append_images=[Image.new("RGBA", (10, 10), (0, 255, 0, 255))],
    )
    with Image.open(test_file) as im:
        im.seek(1)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)


def test_apng_save_disposal_previous(tmp_path):
    test_file = str(tmp_path / "temp.png")
    size = (128, 64)
    transparent = Image.new("RGBA", size, (0, 0, 0, 0))
    red = Image.new("RGBA", size, (255, 0, 0, 255))
    green = Image.new("RGBA", size, (0, 255, 0, 255))

    # test APNG_DISPOSE_OP_NONE
    transparent.save(
        test_file,
        save_all=True,
        append_images=[red, green],
        disposal=PngImagePlugin.APNG_DISPOSE_OP_PREVIOUS,
    )
    with Image.open(test_file) as im:
        im.seek(2)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)


def test_apng_save_blend(tmp_path):
    test_file = str(tmp_path / "temp.png")
    size = (128, 64)
    red = Image.new("RGBA", size, (255, 0, 0, 255))
    green = Image.new("RGBA", size, (0, 255, 0, 255))
    transparent = Image.new("RGBA", size, (0, 0, 0, 0))

    # test APNG_BLEND_OP_SOURCE on solid color
    blend = [
        PngImagePlugin.APNG_BLEND_OP_OVER,
        PngImagePlugin.APNG_BLEND_OP_SOURCE,
    ]
    red.save(
        test_file,
        save_all=True,
        append_images=[red, green],
        default_image=True,
        disposal=PngImagePlugin.APNG_DISPOSE_OP_NONE,
        blend=blend,
    )
    with Image.open(test_file) as im:
        im.seek(2)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    # test APNG_BLEND_OP_SOURCE on transparent color
    blend = [
        PngImagePlugin.APNG_BLEND_OP_OVER,
        PngImagePlugin.APNG_BLEND_OP_SOURCE,
    ]
    red.save(
        test_file,
        save_all=True,
        append_images=[red, transparent],
        default_image=True,
        disposal=PngImagePlugin.APNG_DISPOSE_OP_NONE,
        blend=blend,
    )
    with Image.open(test_file) as im:
        im.seek(2)
        assert im.getpixel((0, 0)) == (0, 0, 0, 0)
        assert im.getpixel((64, 32)) == (0, 0, 0, 0)

    # test APNG_BLEND_OP_OVER
    red.save(
        test_file,
        save_all=True,
        append_images=[green, transparent],
        default_image=True,
        disposal=PngImagePlugin.APNG_DISPOSE_OP_NONE,
        blend=PngImagePlugin.APNG_BLEND_OP_OVER,
    )
    with Image.open(test_file) as im:
        im.seek(1)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)
        im.seek(2)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
        assert im.getpixel((64, 32)) == (0, 255, 0, 255)

    # test info blend
    red.info["blend"] = PngImagePlugin.APNG_BLEND_OP_OVER
    red.save(test_file, save_all=True, append_images=[green, transparent])
    with Image.open(test_file) as im:
        im.seek(2)
        assert im.getpixel((0, 0)) == (0, 255, 0, 255)
