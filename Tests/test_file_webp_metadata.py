from tester import *

from PIL import Image

try:
    from PIL import _webp
    if not _webp.HAVE_WEBPMUX:
        skip('webpmux support not installed')
except:
    skip('webp support not installed')



def test_read_exif_metadata():

    file_path = "Images/flower.webp"
    image = Image.open(file_path)

    assert_equal(image.format, "WEBP")
    exif_data = image.info.get("exif", None)
    assert_true(exif_data)

    exif = image._getexif()

    #camera make
    assert_equal(exif[271], "Canon")

    jpeg_image = Image.open('Tests/images/flower.jpg')
    expected_exif = jpeg_image.info['exif']

    assert_equal(exif_data, expected_exif)


def test_write_exif_metadata():
    file_path = "Tests/images/flower.jpg"
    image = Image.open(file_path)
    expected_exif = image.info['exif']

    buffer = BytesIO()

    image.save(buffer, "webp", exif=expected_exif)

    buffer.seek(0)
    webp_image = Image.open(buffer)

    webp_exif = webp_image.info.get('exif', None)
    assert_true(webp_exif)
    if webp_exif:
        assert_equal(webp_exif, expected_exif, "Webp Exif didn't match")


def test_read_icc_profile():

    file_path = "Images/flower2.webp"
    image = Image.open(file_path)

    assert_equal(image.format, "WEBP")
    assert_true(image.info.get("icc_profile", None))

    icc = image.info['icc_profile']

    jpeg_image = Image.open('Tests/images/flower2.jpg')
    expected_icc = jpeg_image.info['icc_profile']

    assert_equal(icc, expected_icc)


def test_write_icc_metadata():
    file_path = "Tests/images/flower2.jpg"
    image = Image.open(file_path)
    expected_icc_profile = image.info['icc_profile']

    buffer = BytesIO()

    image.save(buffer, "webp", icc_profile=expected_icc_profile)

    buffer.seek(0)
    webp_image = Image.open(buffer)

    webp_icc_profile = webp_image.info.get('icc_profile', None)
    
    assert_true(webp_icc_profile)
    if webp_icc_profile:
        assert_equal(webp_icc_profile, expected_icc_profile, "Webp ICC didn't match")


def test_read_no_exif():
    file_path = "Tests/images/flower.jpg"
    image = Image.open(file_path)
    expected_exif = image.info['exif']

    buffer = BytesIO()

    image.save(buffer, "webp")
    
    buffer.seek(0)
    webp_image = Image.open(buffer)

    assert_false(webp_image._getexif())
    
 
