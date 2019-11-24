import unittest

from PIL import Image, ImageShow

from .helper import PillowTestCase, hopper, is_win32, on_ci, on_github_actions


class TestImageShow(PillowTestCase):
    def test_sanity(self):
        dir(Image)
        dir(ImageShow)

    def test_register(self):
        # Test registering a viewer that is not a class
        ImageShow.register("not a class")

        # Restore original state
        ImageShow._viewers.pop()

    def test_viewer_show(self):
        class TestViewer(ImageShow.Viewer):
            methodCalled = False

            def show_image(self, image, **options):
                self.methodCalled = True
                return True

        viewer = TestViewer()
        ImageShow.register(viewer, -1)

        for mode in ("1", "I;16", "LA", "RGB", "RGBA"):
            with hopper() as im:
                self.assertTrue(ImageShow.show(im))
            self.assertTrue(viewer.methodCalled)

        # Restore original state
        ImageShow._viewers.pop(0)

    @unittest.skipUnless(
        on_ci() and not (is_win32() and on_github_actions()),
        "Only run on CIs; hangs on Windows on GitHub Actions",
    )
    def test_show(self):
        for mode in ("1", "I;16", "LA", "RGB", "RGBA"):
            im = hopper(mode)
            self.assertTrue(ImageShow.show(im))

    def test_viewer(self):
        viewer = ImageShow.Viewer()

        self.assertIsNone(viewer.get_format(None))

        self.assertRaises(NotImplementedError, viewer.get_command, None)

    def test_viewers(self):
        for viewer in ImageShow._viewers:
            viewer.get_command("test.jpg")
