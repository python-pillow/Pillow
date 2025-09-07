from __future__ import annotations

from io import BytesIO

import pytest

from PIL import Image

from .helper import assert_image_equal_tofile


def test_aero_busy() -> None:
    with Image.open("Tests/images/ani/aero_busy.ani") as im:
        assert im.size == (64, 64)
        assert im.n_frames == 18

        assert_image_equal_tofile(im, "Tests/images/ani/aero_busy_0.png")

        im.seek(8)
        assert_image_equal_tofile(im, "Tests/images/ani/aero_busy_8.png")

        with pytest.raises(EOFError):
            im.seek(-1)

        with pytest.raises(EOFError):
            im.seek(18)


def test_posy_busy() -> None:
    with Image.open("Tests/images/ani/posy_busy.ani") as im:
        assert im.size == (96, 96)
        assert im.n_frames == 77

        assert_image_equal_tofile(im, "Tests/images/ani/posy_busy_0.png")

        im.seek(24)
        assert_image_equal_tofile(im, "Tests/images/ani/posy_busy_24.png")

        with pytest.raises(EOFError):
            im.seek(77)


def test_seq_rate() -> None:
    with Image.open("Tests/images/ani/stopwtch.ani") as im:
        assert im.size == (32, 32)
        assert im.n_frames == 8

        assert im.info["seq"][:3] == [0, 1, 0]
        assert im.info["rate"] == [8, 16, 16] + [8] * 42

        assert_image_equal_tofile(im, "Tests/images/ani/stopwtch_0.png")

        im.seek(5)
        assert_image_equal_tofile(im, "Tests/images/ani/stopwtch_5.png")

        with pytest.raises(EOFError):
            im.seek(8)


def test_save() -> None:
    filenames = [
        "aero_busy_0.png",
        "aero_busy_8.png",
        "posy_busy_0.png",
        "posy_busy_24.png",
        "stopwtch_0.png",
        "stopwtch_5.png",
    ]

    images = [Image.open("Tests/images/ani/" + filename) for filename in filenames]

    with BytesIO() as output:
        images[0].save(
            output, append_images=[images[1]], seq=[0, 1], rate=[5, 10], format="ANI"
        )

        with Image.open(output, formats=["ANI"]) as im:
            assert im.tobytes() == images[0].tobytes()
            im.seek(1)
            assert im.tobytes() == images[1].tobytes()
            assert im.info["seq"] == [0, 1]
            assert im.info["rate"] == [5, 10]

    with BytesIO() as output:
        images[2].save(
            output,
            append_images=[images[3]],
            seq=[1, 0],
            rate=[2, 2],
            format="ANI",
            sizes=[(96, 96)],
        )

        with Image.open(output, formats=["ANI"]) as im:
            assert im.tobytes() == images[2].tobytes()
            im.seek(1)
            assert im.tobytes() == images[3].tobytes()
            assert im.info["seq"] == [1, 0]
            assert im.info["rate"] == [2, 2]

    with BytesIO() as output:
        images[4].save(
            output, append_images=[images[5]], seq=[0, 1], rate=[3, 4], format="ANI"
        )

        with Image.open(output, formats=["ANI"]) as im:
            assert im.tobytes() == images[4].tobytes()
            im.seek(1)
            assert im.tobytes() == images[5].tobytes()
            assert im.info["seq"] == [0, 1]
            assert im.info["rate"] == [3, 4]

    with BytesIO() as output:
        images[0].save(
            output,
            append_images=images[1:],
            seq=[0, 2, 4, 1, 3, 5, 0, 1, 0, 1],
            rate=[1, 2, 3, 1, 2, 3, 1, 2, 3, 4],
            format="ANI",
            sizes=[(32, 32)],
        )

        with Image.open(output, formats=["ANI"]) as im:
            assert im.n_frames == 6
            assert im.info["seq"] == [0, 2, 4, 1, 3, 5, 0, 1, 0, 1]
            assert im.info["rate"] == [1, 2, 3, 1, 2, 3, 1, 2, 3, 4]
            assert im.size == (32, 32)

            im.seek(4)
            assert im.tobytes() == images[4].tobytes()

    with BytesIO() as output:
        with pytest.raises(ValueError):
            images[0].save(
                output,
                append_images=images[1:],
                seq=[0, 1, 8, 1, 2],
                rate=[1, 1, 1, 1, 1],
                format="ANI",
                sizes=[(32, 32)],
            )

        with pytest.raises(ValueError):
            images[0].save(
                output,
                append_images=images[1:],
                seq=[0, 1, 1, 1, 2],
                rate=[1, 1, 1, 1],
                format="ANI",
                sizes=[(32, 32)],
            )

        with pytest.raises(ValueError):
            images[0].save(
                output,
                append_images=images[1:],
                rate=[1, 1, 1, 1],
                format="ANI",
                sizes=[(32, 32)],
            )
