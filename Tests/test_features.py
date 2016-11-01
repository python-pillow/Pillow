from helper import unittest, PillowTestCase

from PIL import features


class TestFeatures(PillowTestCase):

    def test_check_features(self):
        for feature in features.modules:
            self.assertTrue(
                features.check_module(feature) in [True, False, None])
        for feature in features.codecs:
            self.assertTrue(features.check_codec(feature) in [True, False])

    def test_supported_features(self):
        self.assertIsInstance(features.get_supported_modules(), list)
        self.assertIsInstance(features.get_supported_codecs(), list)

    def test_unsupported_codec(self):
        # Arrange
        codec = "unsupported_codec"
        # Act / Assert
        self.assertRaises(ValueError, lambda: features.check_codec(codec))

    def test_unsupported_module(self):
        # Arrange
        module = "unsupported_module"
        # Act / Assert
        self.assertRaises(ValueError, lambda: features.check_module(module))


if __name__ == '__main__':
    unittest.main()
