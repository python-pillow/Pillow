import pytest

from PIL import Image, ImageShow

from .helper import hopper, is_win32, on_ci


def test_sanity():
    dir(Image)
    dir(ImageShow)


def test_register():
    # Test registering a viewer that is not a class
    ImageShow.register("not a class")

    # Restore original state
    ImageShow._viewers.pop()


@pytest.mark.parametrize(
    "order",
    [-1, 0],
)
def test_viewer_show(order):
    class TestViewer(ImageShow.Viewer):
        def show_image(self, image, **options):
            self.methodCalled = True
            return True

    viewer = TestViewer()
    ImageShow.register(viewer, order)

    for mode in ("1", "I;16", "LA", "RGB", "RGBA"):
        viewer.methodCalled = False
        with hopper(mode) as im:
            assert ImageShow.show(im)
        assert viewer.methodCalled

    # Restore original state
    ImageShow._viewers.pop(0)


@pytest.mark.skipif(
    not on_ci() or is_win32(),
    reason="Only run on CIs; hangs on Windows CIs",
)
@pytest.mark.parametrize("mode", ("1", "I;16", "LA", "RGB", "RGBA"))
def test_show(mode):
    im = hopper(mode)
    assert ImageShow.show(im)


def test_show_without_viewers():
    viewers = ImageShow._viewers
    ImageShow._viewers = []

    with hopper() as im:
        assert not ImageShow.show(im)

    ImageShow._viewers = viewers


def test_viewer():
    viewer = ImageShow.Viewer()

    assert viewer.get_format(None) is None

    with pytest.raises(NotImplementedError):
        viewer.get_command(None)


@pytest.mark.parametrize("viewer", ImageShow._viewers)
def test_viewers(viewer):
    try:
        viewer.get_command("test.jpg")
    except NotImplementedError:
        pass


def test_ipythonviewer():
    pytest.importorskip("IPython", reason="IPython not installed")
    for viewer in ImageShow._viewers:
        if isinstance(viewer, ImageShow.IPythonViewer):
            test_viewer = viewer
            break
    else:
        assert False

    im = hopper()
    assert test_viewer.show(im) == 1
