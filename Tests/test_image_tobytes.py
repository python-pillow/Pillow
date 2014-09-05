from helper import unittest, PillowTestCase, hopper


class TestImageToBytes(PillowTestCase):

    def test_sanity(self):
        data = hopper().tobytes()
        self.assertTrue(isinstance(data, bytes))

if __name__ == '__main__':
    unittest.main()

# End of file
