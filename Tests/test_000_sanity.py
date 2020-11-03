import PIL
import PIL.Image


def test_sanity():
    # Make sure we have the binary extension
    PIL.Image.core.new("L", (100, 100))

    # Create an image and do stuff with it.
    im = PIL.Image.new("1", (100, 100))
    assert (im.mode, im.size) == ("1", (100, 100))
    assert len(im.tobytes()) == 1300

    # Create images in all remaining major modes.
    PIL.Image.new("L", (100, 100))
    PIL.Image.new("P", (100, 100))
    PIL.Image.new("RGB", (100, 100))
    PIL.Image.new("I", (100, 100))
    PIL.Image.new("F", (100, 100))
