from .helper import PillowTestCase, hopper


class TestImageGetIm(PillowTestCase):
    def test_sanity(self):
        im = hopper()
        type_repr = repr(type(im.getim()))

        self.assertIn("PyCapsule", type_repr)
        self.assertIsInstance(im.im.id, int)
