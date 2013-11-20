from tester import *

from PIL import Image

#Our two EPS test files (they are identical except for their bounding boxes)
file1 = "Tests/images/zero_bb.eps"
file2 = "Tests/images/non_zero_bb.eps"

#Due to palletization, we'll need to convert these to RGB after load
file1_compare = "Tests/images/zero_bb.png"
file1_compare_scale2 = "Tests/images/zero_bb_scale2.png"

file2_compare = "Tests/images/non_zero_bb.png"
file2_compare_scale2 = "Tests/images/non_zero_bb_scale2.png"

def test_sanity():
    #Regular scale
    image1 = Image.open(file1)
    image1.load()
    assert_equal(image1.mode, "RGB")
    assert_equal(image1.size, (460, 352))
    assert_equal(image1.format, "EPS")

    image2 = Image.open(file2)
    image2.load()
    assert_equal(image2.mode, "RGB")
    assert_equal(image2.size, (360, 252))
    assert_equal(image2.format, "EPS")

    #Double scale
    image1_scale2 = Image.open(file1)
    image1_scale2.load(scale=2)
    assert_equal(image1_scale2.mode, "RGB")
    assert_equal(image1_scale2.size, (920, 704))
    assert_equal(image1_scale2.format, "EPS")

    image2_scale2 = Image.open(file2)
    image2_scale2.load(scale=2)
    assert_equal(image2_scale2.mode, "RGB")
    assert_equal(image2_scale2.size, (720, 504))
    assert_equal(image2_scale2.format, "EPS")

def test_render_scale1():
    #We need png support for these render test
    codecs = dir(Image.core)
    if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
        skip("zip/deflate support not available")

    #Zero bounding box
    image1 = Image.open(file1)
    image1.load()
    image1_compare = Image.open(file1_compare).convert("RGB")
    image1_compare.load()
    assert_image_equal(image1, image1_compare)

    #Non-Zero bounding box
    image2 = Image.open(file2)
    image2.load()
    image2_compare = Image.open(file2_compare).convert("RGB")
    image2_compare.load()
    assert_image_equal(image2, image2_compare)

def test_render_scale2():
    #We need png support for these render test
    codecs = dir(Image.core)
    if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
        skip("zip/deflate support not available")

    #Zero bounding box
    image1 = Image.open(file1)
    image1.load(scale=2)
    image1_compare = Image.open(file1_compare_scale2).convert("RGB")
    image1_compare.load()
    assert_image_equal(image1, image1_compare)

    #Non-Zero bounding box
    image2 = Image.open(file2)
    image2.load(scale=2)
    image2_compare = Image.open(file2_compare_scale2).convert("RGB")
    image2_compare.load()
    assert_image_equal(image2, image2_compare)

