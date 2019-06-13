from .helper import PillowTestCase, hopper


class TestImageToBytes(PillowTestCase):
    def test_sanity(self):
        data = hopper().tobytes()
        self.assertIsInstance(data, bytes)
