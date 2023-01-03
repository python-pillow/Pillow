from .helper import assert_image_equal, assert_image_similar, hopper


def test_upload_equal():
    result = hopper("P").convert("RGB")
    target = hopper("RGB")
    assert_image_equal(result, target)


def test_upload_similar():
    result = hopper("P").convert("RGB")
    target = hopper("RGB")
    assert_image_similar(result, target, 0)
