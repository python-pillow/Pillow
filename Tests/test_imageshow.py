from helper import unittest, PillowTestCase, hopper

from PIL import Image
from PIL import ImageShow


class TestImageShow(PillowTestCase):

    def test_sanity(self):
        dir(Image)
        dir(ImageShow)

    def test_register(self):
        # Test registering a viewer that is not a class
        ImageShow.register("not a class")

        # Restore original state
        ImageShow._viewers.pop()

    def test_show(self):
        class TestViewer:
            methodCalled = False

            def show(self, image, title=None, **options):
                self.methodCalled = True
                return True
        viewer = TestViewer()
        ImageShow.register(viewer, -1)

        im = hopper()
        self.assertTrue(ImageShow.show(im))
        self.assertTrue(viewer.methodCalled)

        # Restore original state
        ImageShow._viewers.pop(0)

    def test_viewer(self):
        viewer = ImageShow.Viewer()

        self.assertIsNone(viewer.get_format(None))

        self.assertRaises(NotImplementedError, viewer.get_command, None)

    def test_viewers(self):
        for viewer in ImageShow._viewers:
            viewer.get_command('test.jpg')


if __name__ == '__main__':
    unittest.main()
