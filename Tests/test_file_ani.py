from __future__ import annotations

from io import BytesIO

import pytest

from PIL import Image


def test_aero_busy():
    with Image.open("Tests/images/ani/aero_busy.ani") as im:
        assert im.size == (64, 64)
        assert im.info["frames"] == 18

        with Image.open("Tests/images/ani/aero_busy_0.png") as png:
            assert png.tobytes() == im.tobytes()

        im.seek(8)
        with Image.open("Tests/images/ani/aero_busy_8.png") as png:
            assert png.tobytes() == im.tobytes()

        with pytest.raises(EOFError):
            im.seek(-1)

        with pytest.raises(EOFError):
            im.seek(18)


def test_posy_busy():
    with Image.open("Tests/images/ani/posy_busy.ani") as im:
        assert im.size == (96, 96)
        assert im.info["frames"] == 77

        with Image.open("Tests/images/ani/posy_busy_0.png") as png:
            assert png.tobytes() == im.tobytes()

        im.seek(24)
        with Image.open("Tests/images/ani/posy_busy_24.png") as png:
            assert png.tobytes() == im.tobytes()

        with pytest.raises(EOFError):
            im.seek(77)


def test_stopwtch():
    with Image.open("Tests/images/ani/stopwtch.ani") as im:
        assert im.size == (32, 32)
        assert im.info["frames"] == 8

        assert im.info["seq"][0] == 0
        assert im.info["seq"][2] == 0

        for i, r in enumerate(im.info["rate"]):
            if i == 1 or i == 2:
                assert r == 16
            else:
                assert r == 8

        with Image.open("Tests/images/ani/stopwtch_0.png") as png:
            assert png.tobytes() == im.tobytes()

        im.seek(5)
        with Image.open("Tests/images/ani/stopwtch_5.png") as png:
            assert png.tobytes() == im.tobytes()

        with pytest.raises(EOFError):
            im.seek(8)


def test_save():
    directory_path = "Tests/images/ani/"
    filenames = [
        "aero_busy_0.png",
        "aero_busy_8.png",
        "posy_busy_0.png",
        "posy_busy_24.png",
        "stopwtch_0.png",
        "stopwtch_5.png",
    ]

    images = [Image.open(directory_path + filename) for filename in filenames]

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
            assert im.info["frames"] == 6
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
