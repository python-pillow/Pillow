import pickle

import pytest

from PIL import Image

from .helper import skip_unless_feature


def helper_pickle_file(tmp_path, pickle, protocol, test_file, mode):
    # Arrange
    with Image.open(test_file) as im:
        filename = str(tmp_path / "temp.pkl")
        if mode:
            im = im.convert(mode)

        # Act
        with open(filename, "wb") as f:
            pickle.dump(im, f, protocol)
        with open(filename, "rb") as f:
            loaded_im = pickle.load(f)

        # Assert
        assert im == loaded_im


def helper_pickle_string(pickle, protocol, test_file, mode):
    with Image.open(test_file) as im:
        if mode:
            im = im.convert(mode)

        # Act
        dumped_string = pickle.dumps(im, protocol)
        loaded_im = pickle.loads(dumped_string)

        # Assert
        assert im == loaded_im


@pytest.mark.parametrize(
    ("test_file", "test_mode"),
    [
        ("Tests/images/hopper.jpg", None),
        ("Tests/images/hopper.jpg", "L"),
        ("Tests/images/hopper.jpg", "PA"),
        pytest.param(
            "Tests/images/hopper.webp", None, marks=skip_unless_feature("webp")
        ),
        ("Tests/images/hopper.tif", None),
        ("Tests/images/test-card.png", None),
        ("Tests/images/zero_bb.png", None),
        ("Tests/images/zero_bb_scale2.png", None),
        ("Tests/images/non_zero_bb.png", None),
        ("Tests/images/non_zero_bb_scale2.png", None),
        ("Tests/images/p_trns_single.png", None),
        ("Tests/images/pil123p.png", None),
        ("Tests/images/itxt_chunks.png", None),
    ],
)
def test_pickle_image(tmp_path, test_file, test_mode):
    # Act / Assert
    for protocol in range(0, pickle.HIGHEST_PROTOCOL + 1):
        helper_pickle_string(pickle, protocol, test_file, test_mode)
        helper_pickle_file(tmp_path, pickle, protocol, test_file, test_mode)


def test_pickle_la_mode_with_palette(tmp_path):
    # Arrange
    filename = str(tmp_path / "temp.pkl")
    with Image.open("Tests/images/hopper.jpg") as im:
        im = im.convert("PA")

    # Act / Assert
    for protocol in range(0, pickle.HIGHEST_PROTOCOL + 1):
        im.mode = "LA"
        with open(filename, "wb") as f:
            pickle.dump(im, f, protocol)
        with open(filename, "rb") as f:
            loaded_im = pickle.load(f)

        im.mode = "PA"
        assert im == loaded_im


@skip_unless_feature("webp")
def test_pickle_tell():
    # Arrange
    image = Image.open("Tests/images/hopper.webp")

    # Act: roundtrip
    unpickled_image = pickle.loads(pickle.dumps(image))

    # Assert
    assert unpickled_image.tell() == 0
