from PIL import Image

from .helper import fromstring, skip_unless_feature, tostring

pytestmark = skip_unless_feature("jpg")


def draft_roundtrip(in_mode, in_size, req_mode, req_size):
    im = Image.new(in_mode, in_size)
    data = tostring(im, "JPEG")
    im = fromstring(data)
    mode, box = im.draft(req_mode, req_size)
    scale, _ = im.decoderconfig
    assert box[:2] == (0, 0)
    assert (im.width - scale) < box[2] <= im.width
    assert (im.height - scale) < box[3] <= im.height
    return im


def test_size():
    for in_size, req_size, out_size in [
        ((435, 361), (2048, 2048), (435, 361)),  # bigger
        ((435, 361), (435, 361), (435, 361)),  # same
        ((128, 128), (64, 64), (64, 64)),
        ((128, 128), (32, 32), (32, 32)),
        ((128, 128), (16, 16), (16, 16)),
        # large requested width
        ((435, 361), (218, 128), (435, 361)),  # almost 2x
        ((435, 361), (217, 128), (218, 181)),  # more than 2x
        ((435, 361), (109, 64), (218, 181)),  # almost 4x
        ((435, 361), (108, 64), (109, 91)),  # more than 4x
        ((435, 361), (55, 32), (109, 91)),  # almost 8x
        ((435, 361), (54, 32), (55, 46)),  # more than 8x
        ((435, 361), (27, 16), (55, 46)),  # more than 16x
        # and vice versa
        ((435, 361), (128, 181), (435, 361)),  # almost 2x
        ((435, 361), (128, 180), (218, 181)),  # more than 2x
        ((435, 361), (64, 91), (218, 181)),  # almost 4x
        ((435, 361), (64, 90), (109, 91)),  # more than 4x
        ((435, 361), (32, 46), (109, 91)),  # almost 8x
        ((435, 361), (32, 45), (55, 46)),  # more than 8x
        ((435, 361), (16, 22), (55, 46)),  # more than 16x
    ]:
        im = draft_roundtrip("L", in_size, None, req_size)
        im.load()
        assert im.size == out_size


def test_mode():
    for in_mode, req_mode, out_mode in [
        ("RGB", "1", "RGB"),
        ("RGB", "L", "L"),
        ("RGB", "RGB", "RGB"),
        ("RGB", "YCbCr", "YCbCr"),
        ("L", "1", "L"),
        ("L", "L", "L"),
        ("L", "RGB", "L"),
        ("L", "YCbCr", "L"),
        ("CMYK", "1", "CMYK"),
        ("CMYK", "L", "CMYK"),
        ("CMYK", "RGB", "CMYK"),
        ("CMYK", "YCbCr", "CMYK"),
    ]:
        im = draft_roundtrip(in_mode, (64, 64), req_mode, None)
        im.load()
        assert im.mode == out_mode


def test_several_drafts():
    im = draft_roundtrip("L", (128, 128), None, (64, 64))
    im.draft(None, (64, 64))
    im.load()
