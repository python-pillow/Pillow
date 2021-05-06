import pytest

from PIL import Image, WmfImagePlugin

from .helper import assert_image_similar_tofile, hopper


def test_load_raw():

    # Test basic EMF open and rendering
    with Image.open("Tests/images/drawing.emf") as im:
        if hasattr(Image.core, "drawwmf"):
            # Currently, support for WMF/EMF is Windows-only
            im.load()
            # Compare to reference rendering
            assert_image_similar_tofile(im, "Tests/images/drawing_emf_ref.png", 0)

    # Test basic WMF open and rendering
    with Image.open("Tests/images/drawing.wmf") as im:
        if hasattr(Image.core, "drawwmf"):
            # Currently, support for WMF/EMF is Windows-only
            im.load()
            # Compare to reference rendering
            assert_image_similar_tofile(im, "Tests/images/drawing_wmf_ref.png", 2.0)


def test_register_handler(tmp_path):
    class TestHandler:
        methodCalled = False

        def save(self, im, fp, filename):
            self.methodCalled = True

    handler = TestHandler()
    original_handler = WmfImagePlugin._handler
    WmfImagePlugin.register_handler(handler)

    im = hopper()
    tmpfile = str(tmp_path / "temp.wmf")
    im.save(tmpfile)
    assert handler.methodCalled

    # Restore the state before this test
    WmfImagePlugin.register_handler(original_handler)


def test_load_float_dpi():
    with Image.open("Tests/images/drawing.emf") as im:
        assert im.info["dpi"] == 1423.7668161434979


def test_load_set_dpi():
    with Image.open("Tests/images/drawing.wmf") as im:
        assert im.size == (82, 82)

        if hasattr(Image.core, "drawwmf"):
            im.load(144)
            assert im.size == (164, 164)

            assert_image_similar_tofile(im, "Tests/images/drawing_wmf_ref_144.png", 2.1)


def test_save(tmp_path):
    im = hopper()

    for ext in [".wmf", ".emf"]:
        tmpfile = str(tmp_path / ("temp" + ext))
        with pytest.raises(OSError):
            im.save(tmpfile)
