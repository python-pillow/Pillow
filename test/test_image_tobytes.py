from helper import unittest, lena


class TestImageToBytes(unittest.TestCase):

    def test_sanity(self):
        data = lena().tobytes()
        self.assertTrue(isinstance(data, bytes))

if __name__ == '__main__':
    unittest.main()

# End of file
