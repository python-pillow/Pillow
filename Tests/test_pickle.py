from helper import unittest, PillowTestCase

from PIL import Image


class TestPickle(PillowTestCase):

    def helper_pickle_file(self, pickle, protocol=0, mode=None):
        # Arrange
        im = Image.open('Tests/images/hopper.jpg')
        filename = self.tempfile('temp.pkl')
        if mode:
            im = im.convert(mode)

        # Act
        with open(filename, 'wb') as f:
            pickle.dump(im, f, protocol)
        with open(filename, 'rb') as f:
            loaded_im = pickle.load(f)

        # Assert
        self.assertEqual(im, loaded_im)

    def helper_pickle_string(self, pickle, protocol=0,
                             test_file='Tests/images/hopper.jpg', mode=None):
        im = Image.open(test_file)
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
                "Tests/images/pil123p.png"
        ]:
            self.helper_pickle_string(pickle, test_file=test_file)

    def test_pickle_l_mode(self):
        # Arrange
        import pickle

        # Act / Assert
        for protocol in range(0, pickle.HIGHEST_PROTOCOL + 1):
            self.helper_pickle_string(pickle, protocol, mode="L")
            self.helper_pickle_file(pickle, protocol, mode="L")

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

if __name__ == '__main__':
    unittest.main()
