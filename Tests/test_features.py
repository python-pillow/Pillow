from helper import unittest, PillowTestCase

from PIL import features


class TestFeatures(PillowTestCase):

    def test_check_features(self):
        for feature in features.modules:
            self.assertTrue(features.check_module(feature) in [True, False, None])
        for feature in features.codecs:
            self.assertTrue(features.check_codec(feature) in [True, False])

    def test_supported_features(self):
        self.assertTrue(type(features.get_supported_modules()) is list)
        self.assertTrue(type(features.get_supported_codecs()) is list)

if __name__ == '__main__':
    unittest.main()

# End of file
