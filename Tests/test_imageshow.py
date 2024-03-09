from __future__ import annotations

from typing import Any

import pytest

from PIL import Image, ImageShow

from .helper import hopper, is_win32, on_ci


def test_sanity() -> None:
    dir(Image)
    dir(ImageShow)


def test_register() -> None:
    # Test registering a viewer that is not a class
    ImageShow.register("not a class")

    # Restore original state
    ImageShow._viewers.pop()


@pytest.mark.parametrize(
    "order",
    [-1, 0],
)
def test_viewer_show(order: int) -> None:
    class TestViewer(ImageShow.Viewer):
        def show_image(self, image: Image.Image, **options: Any) -> bool:
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
def test_show(mode: str) -> None:
    im = hopper(mode)
    assert ImageShow.show(im)


def test_show_without_viewers() -> None:
    viewers = ImageShow._viewers
    ImageShow._viewers = []

    with hopper() as im:
        assert not ImageShow.show(im)

    ImageShow._viewers = viewers


def test_viewer() -> None:
    viewer = ImageShow.Viewer()

    im = Image.new("L", (1, 1))
    assert viewer.get_format(im) is None

    with pytest.raises(NotImplementedError):
        viewer.get_command("")


@pytest.mark.parametrize("viewer", ImageShow._viewers)
def test_viewers(viewer: ImageShow.Viewer) -> None:
    try:
        viewer.get_command("test.jpg")
    except NotImplementedError:
        pass


def test_ipythonviewer() -> None:
    pytest.importorskip("IPython", reason="IPython not installed")
    for viewer in ImageShow._viewers:
        if isinstance(viewer, ImageShow.IPythonViewer):
            test_viewer = viewer
            break
    else:
        pytest.fail()

    im = hopper()
    assert test_viewer.show(im) == 1
