from helper import unittest, PillowTestCase

from PIL import features

try:
    from PIL import _webp
    HAVE_WEBP = True
except:
    HAVE_WEBP = False


class TestFeatures(PillowTestCase):

    def test_check(self):
        # Check the correctness of the convenience function
        for module in features.modules:
            self.assertEqual(features.check_module(module),
                             features.check(module))
        for codec in features.codecs:
            self.assertEqual(features.check_codec(codec),
                             features.check(codec))
        for feature in features.features:
            self.assertEqual(features.check_feature(feature),
                             features.check(feature))

    @unittest.skipUnless(HAVE_WEBP, True)
    def check_webp_transparency(self):
        self.assertEqual(features.check('transp_webp'),
                         not _webp.WebPDecoderBuggyAlpha())
        self.assertEqual(features.check('transp_webp'),
                         _webp.HAVE_TRANSPARENCY)

    @unittest.skipUnless(HAVE_WEBP, True)
    def check_webp_mux(self):
        self.assertEqual(features.check('webp_mux'),
                         _webp.HAVE_WEBPMUX)

    def test_check_modules(self):
        for feature in features.modules:
            self.assertIn(features.check_module(feature), [True, False])
        for feature in features.codecs:
            self.assertIn(features.check_codec(feature), [True, False])

    def test_supported_modules(self):
        self.assertIsInstance(features.get_supported_modules(), list)
        self.assertIsInstance(features.get_supported_codecs(), list)
        self.assertIsInstance(features.get_supported_features(), list)
        self.assertIsInstance(features.get_supported(), list)

    def test_unsupported_codec(self):
        # Arrange
        codec = "unsupported_codec"
        # Act / Assert
        self.assertRaises(ValueError, features.check_codec, codec)

    def test_unsupported_module(self):
        # Arrange
        module = "unsupported_module"
        # Act / Assert
        self.assertRaises(ValueError, features.check_module, module)


if __name__ == '__main__':
    unittest.main()
