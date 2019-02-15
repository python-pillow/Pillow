from .helper import PillowTestCase, hopper
from PIL._util import py3


class TestImageGetIm(PillowTestCase):

    def test_sanity(self):
        im = hopper()
        type_repr = repr(type(im.getim()))

        if py3:
            self.assertIn("PyCapsule", type_repr)

        self.assertIsInstance(im.im.id, int)
