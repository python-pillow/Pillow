from helper import unittest, PillowTestCase

from PIL import __version__

try:
    import pyroma
except ImportError:
    pyroma = None


@unittest.skipIf(pyroma is None, "Pyroma is not installed")
class TestPyroma(PillowTestCase):

    def test_pyroma(self):
        # Arrange
        data = pyroma.projectdata.get_data(".")

        # Act
        rating = pyroma.ratings.rate(data)

        # Assert
        if 'rc' in __version__:
            # Pyroma needs to chill about RC versions
            # and not kill all our tests.
            self.assertEqual(rating, (9, [
                "The package's version number does not comply with PEP-386."]))

        else:
            # Should have a perfect score
            self.assertEqual(rating, (10, []))


if __name__ == '__main__':
    unittest.main()
