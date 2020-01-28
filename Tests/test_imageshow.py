import pytest
from PIL import Image, ImageShow

from .helper import hopper, is_win32, on_ci, on_github_actions


def test_sanity():
    dir(Image)
    dir(ImageShow)


def test_register():
    # Test registering a viewer that is not a class
    ImageShow.register("not a class")

    # Restore original state
    ImageShow._viewers.pop()


def test_viewer_show():
    class TestViewer(ImageShow.Viewer):
        methodCalled = False

        def show_image(self, image, **options):
            self.methodCalled = True
            return True

    viewer = TestViewer()
    ImageShow.register(viewer, -1)

    for mode in ("1", "I;16", "LA", "RGB", "RGBA"):
        with hopper() as im:
            assert ImageShow.show(im)
        assert viewer.methodCalled

    # Restore original state
    ImageShow._viewers.pop(0)


@pytest.mark.skipif(
    not on_ci() or (is_win32() and on_github_actions()),
    reason="Only run on CIs; hangs on Windows on GitHub Actions",
)
def test_show():
    for mode in ("1", "I;16", "LA", "RGB", "RGBA"):
        im = hopper(mode)
        assert ImageShow.show(im)


def test_viewer():
    viewer = ImageShow.Viewer()

    assert viewer.get_format(None) is None

    with pytest.raises(NotImplementedError):
        viewer.get_command(None)


def test_viewers():
    for viewer in ImageShow._viewers:
        viewer.get_command("test.jpg")
