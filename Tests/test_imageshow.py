import pytest

from PIL import Image, ImageShow

from .helper import hopper, is_macos, is_win32, on_ci


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


@pytest.mark.skip(
    reason="""Current implementation of some viewers requires manual closing of an image,
        because of that the tests calling show() method will hang infinitely.
    """
)
def test_show():
    for mode in ("1", "I;16", "LA", "RGB", "RGBA"):
        im = hopper(mode)
        assert ImageShow.show(im)


def test_viewer():
    viewer = ImageShow.Viewer()

    assert viewer.get_format(None) == "PNG"

    with pytest.raises(NotImplementedError):
        viewer.get_command(None)


def test_viewers():
    for viewer in ImageShow._viewers:
        try:
            cmd = viewer.get_command("test.jpg")
            assert isinstance(cmd, str)
        except NotImplementedError:
            assert isinstance(viewer, ImageShow.IPythonViewer)


@pytest.mark.skipif(
    is_win32() or is_macos(), reason="The method is implemented for UnixViewers only"
)
def test_get_command_ex_interface():
    """get_command_ex() method used by UnixViewers only"""

    file = "some_image.jpg"
    assert isinstance(file, str)

    for viewer in ImageShow._viewers:
        if isinstance(viewer, ImageShow.UnixViewer):
            # method returns tuple
            result = viewer.get_command_ex(file)
            assert isinstance(result, tuple)
            # file name is a required argument
            with pytest.raises(TypeError) as err:
                viewer.get_command_ex()
            assert (
                "get_command_ex() missing 1 required positional argument: 'file'"
                in str(err.value)
            )


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


@pytest.mark.skipif(
    not on_ci() or is_win32(),
    reason="Only run on CIs; hangs on Windows CIs",
)
def test_file_deprecated(tmp_path):
    f = str(tmp_path / "temp.jpg")
    for viewer in ImageShow._viewers:
        hopper().save(f)
        if not isinstance(viewer, ImageShow.UnixViewer):
            # do not run this assertion with UnixViewers due to implementation
            with pytest.warns(DeprecationWarning):
                try:
                    viewer.show_file(file=f)
                except NotImplementedError:
                    pass
        with pytest.raises(TypeError):
            viewer.show_file()
