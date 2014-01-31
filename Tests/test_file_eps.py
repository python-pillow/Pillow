from tester import *

from PIL import Image, EpsImagePlugin
import sys
import io

if not EpsImagePlugin.gs_windows_binary:
    # already checked. Not there.
    skip()

if not sys.platform.startswith('win'):
    import subprocess
    try:
        gs = subprocess.Popen(['gs','--version'], stdout=subprocess.PIPE)
        gs.stdout.read()
    except OSError:
        # no ghostscript
        skip()

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

def test_file_object():
    #issue 479
    image1 = Image.open(file1)
    with open(tempfile('temp_file.eps'), 'wb') as fh:
        image1.save(fh, 'EPS')

def test_iobase_object():
    #issue 479
    image1 = Image.open(file1)
    with io.open(tempfile('temp_iobase.eps'), 'wb') as fh:
        image1.save(fh, 'EPS')

def test_render_scale1():
    #We need png support for these render test
    codecs = dir(Image.core)
    if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
        skip("zip/deflate support not available")

    #Zero bounding box
    image1_scale1 = Image.open(file1)
    image1_scale1.load()
    image1_scale1_compare = Image.open(file1_compare).convert("RGB")
    image1_scale1_compare.load()
    assert_image_similar(image1_scale1, image1_scale1_compare, 5)

    #Non-Zero bounding box
    image2_scale1 = Image.open(file2)
    image2_scale1.load()
    image2_scale1_compare = Image.open(file2_compare).convert("RGB")
    image2_scale1_compare.load()
    assert_image_similar(image2_scale1, image2_scale1_compare, 10)

def test_render_scale2():
    #We need png support for these render test
    codecs = dir(Image.core)
    if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
        skip("zip/deflate support not available")

    #Zero bounding box
    image1_scale2 = Image.open(file1)
    image1_scale2.load(scale=2)
    image1_scale2_compare = Image.open(file1_compare_scale2).convert("RGB")
    image1_scale2_compare.load()
    assert_image_similar(image1_scale2, image1_scale2_compare, 5)

    #Non-Zero bounding box
    image2_scale2 = Image.open(file2)
    image2_scale2.load(scale=2)
    image2_scale2_compare = Image.open(file2_compare_scale2).convert("RGB")
    image2_scale2_compare.load()
    assert_image_similar(image2_scale2, image2_scale2_compare, 10)
