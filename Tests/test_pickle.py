from PIL import Image

from .helper import PillowTestCase


class TestPickle(PillowTestCase):
    def helper_pickle_file(self, pickle, protocol=0, mode=None):
        # Arrange
        with Image.open("Tests/images/hopper.jpg") as im:
            filename = self.tempfile("temp.pkl")
            if mode:
                im = im.convert(mode)

            # Act
            with open(filename, "wb") as f:
                pickle.dump(im, f, protocol)
            with open(filename, "rb") as f:
                loaded_im = pickle.load(f)

            # Assert
            self.assertEqual(im, loaded_im)

    def helper_pickle_string(
        self, pickle, protocol=0, test_file="Tests/images/hopper.jpg", mode=None
    ):
        with Image.open(test_file) as im:
            if mode:
                im = im.convert(mode)

            # Act
            dumped_string = pickle.dumps(im, protocol)
            loaded_im = pickle.loads(dumped_string)

            # Assert
            self.assertEqual(im, loaded_im)

    def test_pickle_image(self):
        # Arrange
        import pickle

        # Act / Assert
        for protocol in range(0, pickle.HIGHEST_PROTOCOL + 1):
            self.helper_pickle_string(pickle, protocol)
            self.helper_pickle_file(pickle, protocol)

    def test_cpickle_image(self):
        # Arrange
        try:
            import cPickle
        except ImportError:
            return

        # Act / Assert
        for protocol in range(0, cPickle.HIGHEST_PROTOCOL + 1):
            self.helper_pickle_string(cPickle, protocol)
            self.helper_pickle_file(cPickle, protocol)

    def test_pickle_p_mode(self):
        # Arrange
        import pickle

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
                self.helper_pickle_string(
                    pickle, protocol=protocol, test_file=test_file
                )

    def test_pickle_pa_mode(self):
        # Arrange
        import pickle

        # Act / Assert
        for protocol in range(0, pickle.HIGHEST_PROTOCOL + 1):
            self.helper_pickle_string(pickle, protocol, mode="PA")
            self.helper_pickle_file(pickle, protocol, mode="PA")

    def test_pickle_l_mode(self):
        # Arrange
        import pickle

        # Act / Assert
        for protocol in range(0, pickle.HIGHEST_PROTOCOL + 1):
            self.helper_pickle_string(pickle, protocol, mode="L")
            self.helper_pickle_file(pickle, protocol, mode="L")

    def test_pickle_la_mode_with_palette(self):
        # Arrange
        import pickle

        filename = self.tempfile("temp.pkl")
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
            self.assertEqual(im, loaded_im)

    def test_cpickle_l_mode(self):
        # Arrange
        try:
            import cPickle
        except ImportError:
            return

        # Act / Assert
        for protocol in range(0, cPickle.HIGHEST_PROTOCOL + 1):
            self.helper_pickle_string(cPickle, protocol, mode="L")
            self.helper_pickle_file(cPickle, protocol, mode="L")
