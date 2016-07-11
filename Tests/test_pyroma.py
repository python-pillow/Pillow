from helper import unittest, PillowTestCase

from PIL import PILLOW_VERSION

try:
    import pyroma
except ImportError:
    # Skip via setUp()
    pass


class TestPyroma(PillowTestCase):

    def setUp(self):
        try:
            import pyroma
            assert pyroma  # Ignore warning
        except ImportError:
            self.skipTest("ImportError")

    def test_pyroma(self):
        # Arrange
        data = pyroma.projectdata.get_data(".")

        # Act
        rating = pyroma.ratings.rate(data)

        # Assert
        if 'rc' in PILLOW_VERSION:
            # Pyroma needs to chill about RC versions
            # and not kill all our tests.
            self.assertEqual(rating, (9, [
                "The package's version number does not comply with PEP-386."]))

        else:
            # Should have a perfect score
            self.assertEqual(rating, (10, []))


if __name__ == '__main__':
    unittest.main()
