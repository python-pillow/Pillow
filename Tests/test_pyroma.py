from helper import unittest, PillowTestCase

try:
    import pyroma
except ImportError:
    # Skip via setUp()
    pass


class TestPyroma(PillowTestCase):

    def setUp(self):
        try:
            import pyroma
        except ImportError:
            self.skipTest("ImportError")

    def test_pyroma(self):
        # Arrange
        data = pyroma.projectdata.get_data(".")

        # Act
        rating = pyroma.ratings.rate(data)

        # Assert
        # Should have a perfect score
        self.assertEqual(rating, (10, []))


if __name__ == '__main__':
    unittest.main()

# End of file
