import pytest

from PIL import Image, WmfImagePlugin

from .helper import assert_image_similar, hopper


def test_load_raw():

    # Test basic EMF open and rendering
    with Image.open("Tests/images/drawing.emf") as im:
        if hasattr(Image.core, "drawwmf"):
            # Currently, support for WMF/EMF is Windows-only
            im.load()
            # Compare to reference rendering
            with Image.open("Tests/images/drawing_emf_ref.png") as imref:
                imref.load()
                assert_image_similar(im, imref, 0)

    # Test basic WMF open and rendering
    with Image.open("Tests/images/drawing.wmf") as im:
        if hasattr(Image.core, "drawwmf"):
            # Currently, support for WMF/EMF is Windows-only
            im.load()
            # Compare to reference rendering
            with Image.open("Tests/images/drawing_wmf_ref.png") as imref:
                imref.load()
                assert_image_similar(im, imref, 2.0)


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


def test_load_dpi_rounding():
    # Round up
    with Image.open("Tests/images/drawing.emf") as im:
        assert im.info["dpi"] == 1424

    # Round down
    with Image.open("Tests/images/drawing_roundDown.emf") as im:
        assert im.info["dpi"] == 1426


def test_load_set_dpi():
    with Image.open("Tests/images/drawing.wmf") as im:
        assert im.size == (82, 82)

        if hasattr(Image.core, "drawwmf"):
            im.load(144)
            assert im.size == (164, 164)

            with Image.open("Tests/images/drawing_wmf_ref_144.png") as expected:
                assert_image_similar(im, expected, 2.1)


def test_save(tmp_path):
    im = hopper()

    for ext in [".wmf", ".emf"]:
        tmpfile = str(tmp_path / ("temp" + ext))
        with pytest.raises(OSError):
            im.save(tmpfile)
