import pytest

from PIL import Image, ImageSequence, TiffImagePlugin

from .helper import assert_image_equal, hopper, skip_unless_feature


def test_sanity(tmp_path):

    test_file = str(tmp_path / "temp.im")

    im = hopper("RGB")
    im.save(test_file)

    seq = ImageSequence.Iterator(im)

    index = 0
    for frame in seq:
        assert_image_equal(im, frame)
        assert im.tell() == index
        index += 1

    assert index == 1

    with pytest.raises(AttributeError):
        ImageSequence.Iterator(0)


def test_iterator():
    with Image.open("Tests/images/multipage.tiff") as im:
        i = ImageSequence.Iterator(im)
        for index in range(0, im.n_frames):
            assert i[index] == next(i)
        with pytest.raises(IndexError):
            i[index + 1]
        with pytest.raises(StopIteration):
            next(i)


def test_iterator_min_frame():
    with Image.open("Tests/images/hopper.psd") as im:
        i = ImageSequence.Iterator(im)
        for index in range(1, im.n_frames):
            assert i[index] == next(i)


def _test_multipage_tiff():
    with Image.open("Tests/images/multipage.tiff") as im:
        for index, frame in enumerate(ImageSequence.Iterator(im)):
            frame.load()
            assert index == im.tell()
            frame.convert("RGB")


def test_tiff():
    _test_multipage_tiff()


@skip_unless_feature("libtiff")
def test_libtiff():
    TiffImagePlugin.READ_LIBTIFF = True
    _test_multipage_tiff()
    TiffImagePlugin.READ_LIBTIFF = False


def test_consecutive():
    with Image.open("Tests/images/multipage.tiff") as im:
        firstFrame = None
        for frame in ImageSequence.Iterator(im):
            if firstFrame is None:
                firstFrame = frame.copy()
        for frame in ImageSequence.Iterator(im):
            assert_image_equal(frame, firstFrame)
            break


def test_palette_mmap():
    # Using mmap in ImageFile can require to reload the palette.
    with Image.open("Tests/images/multipage-mmap.tiff") as im:
        color1 = im.getpalette()[0:3]
        im.seek(0)
        color2 = im.getpalette()[0:3]
        assert color1 == color2


def test_all_frames():
    # Test a single image
    with Image.open("Tests/images/iss634.gif") as im:
        ims = ImageSequence.all_frames(im)

        assert len(ims) == 42
        for i, im_frame in enumerate(ims):
            assert im_frame is not im

            im.seek(i)
            assert_image_equal(im, im_frame)

        # Test a series of images
        ims = ImageSequence.all_frames([im, hopper(), im])
        assert len(ims) == 85

        # Test an operation
        ims = ImageSequence.all_frames(im, lambda im_frame: im_frame.rotate(90))
        for i, im_frame in enumerate(ims):
            im.seek(i)
            assert_image_equal(im.rotate(90), im_frame)
