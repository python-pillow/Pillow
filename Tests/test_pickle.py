import pickle

from PIL import Image


def helper_pickle_file(tmp_path, pickle, protocol=0, mode=None):
    # Arrange
    with Image.open("Tests/images/hopper.jpg") as im:
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


def helper_pickle_string(
    pickle, protocol=0, test_file="Tests/images/hopper.jpg", mode=None
):
    with Image.open(test_file) as im:
        if mode:
            im = im.convert(mode)

        # Act
        dumped_string = pickle.dumps(im, protocol)
        loaded_im = pickle.loads(dumped_string)

        # Assert
        assert im == loaded_im


def test_pickle_image(tmp_path):
    # Act / Assert
    for protocol in range(0, pickle.HIGHEST_PROTOCOL + 1):
        helper_pickle_string(pickle, protocol)
        helper_pickle_file(tmp_path, pickle, protocol)


def test_pickle_p_mode():
    # Act / Assert
    for test_file in [
        "Tests/images/test-card.png",
        "Tests/images/zero_bb.png",
        "Tests/images/zero_bb_scale2.png",
        "Tests/images/non_zero_bb.png",
        "Tests/images/non_zero_bb_scale2.png",
        "Tests/images/p_trns_single.png",
        "Tests/images/pil123p.png",
        "Tests/images/itxt_chunks.png",
    ]:
        for protocol in range(0, pickle.HIGHEST_PROTOCOL + 1):
            helper_pickle_string(pickle, protocol=protocol, test_file=test_file)


def test_pickle_pa_mode(tmp_path):
    # Act / Assert
    for protocol in range(0, pickle.HIGHEST_PROTOCOL + 1):
        helper_pickle_string(pickle, protocol, mode="PA")
        helper_pickle_file(tmp_path, pickle, protocol, mode="PA")


def test_pickle_l_mode(tmp_path):
    # Act / Assert
    for protocol in range(0, pickle.HIGHEST_PROTOCOL + 1):
        helper_pickle_string(pickle, protocol, mode="L")
        helper_pickle_file(tmp_path, pickle, protocol, mode="L")


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
