from tester import *

from PIL import Image
from PIL import PngImagePlugin
import zlib

codecs = dir(Image.core)

if "zip_encoder" not in codecs or "zip_decoder" not in codecs:
    skip("zip/deflate support not available")

# sample png stream

file = "Images/lena.png"
data = open(file, "rb").read()

# stuff to create inline PNG images

MAGIC = PngImagePlugin._MAGIC

def chunk(cid, *data):
    file = BytesIO()
    PngImagePlugin.putchunk(*(file, cid) + data)
    return file.getvalue()

o32 = PngImagePlugin.o32

IHDR = chunk(b"IHDR", o32(1), o32(1), b'\x08\x02', b'\0\0\0')
IDAT = chunk(b"IDAT")
IEND = chunk(b"IEND")

HEAD = MAGIC + IHDR
TAIL = IDAT + IEND

def load(data):
    return Image.open(BytesIO(data))

def roundtrip(im, **options):
    out = BytesIO()
    im.save(out, "PNG", **options)
    out.seek(0)
    return Image.open(out)

# --------------------------------------------------------------------

def test_sanity():

    # internal version number
    assert_match(Image.core.zlib_version, "\d+\.\d+\.\d+(\.\d+)?$")

    file = tempfile("temp.png")

    lena("RGB").save(file)

    im = Image.open(file)
    im.load()
    assert_equal(im.mode, "RGB")
    assert_equal(im.size, (128, 128))
    assert_equal(im.format, "PNG")

    lena("1").save(file)
    im = Image.open(file)

    lena("L").save(file)
    im = Image.open(file)

    lena("P").save(file)
    im = Image.open(file)

    lena("RGB").save(file)
    im = Image.open(file)

    lena("I").save(file)
    im = Image.open(file)

# --------------------------------------------------------------------

def test_broken():
    # Check reading of totally broken files.  In this case, the test
    # file was checked into Subversion as a text file.

    file = "Tests/images/broken.png"
    assert_exception(IOError, lambda: Image.open(file))

def test_bad_text():
    # Make sure PIL can read malformed tEXt chunks (@PIL152)

    im = load(HEAD + chunk(b'tEXt') + TAIL)
    assert_equal(im.info, {})

    im = load(HEAD + chunk(b'tEXt', b'spam') + TAIL)
    assert_equal(im.info, {'spam': ''})

    im = load(HEAD + chunk(b'tEXt', b'spam\0') + TAIL)
    assert_equal(im.info, {'spam': ''})

    im = load(HEAD + chunk(b'tEXt', b'spam\0egg') + TAIL)
    assert_equal(im.info, {'spam': 'egg'})

    im = load(HEAD + chunk(b'tEXt', b'spam\0egg\0') + TAIL)
    assert_equal(im.info,  {'spam': 'egg\x00'})

def test_bad_ztxt():
    # Test reading malformed zTXt chunks (python-imaging/Pillow#318)

    im = load(HEAD + chunk(b'zTXt') + TAIL)
    assert_equal(im.info, {})

    im = load(HEAD + chunk(b'zTXt', b'spam') + TAIL)
    assert_equal(im.info, {'spam': ''})

    im = load(HEAD + chunk(b'zTXt', b'spam\0') + TAIL)
    assert_equal(im.info, {'spam': ''})

    im = load(HEAD + chunk(b'zTXt', b'spam\0\0') + TAIL)
    assert_equal(im.info, {'spam': ''})

    im = load(HEAD + chunk(b'zTXt', b'spam\0\0' + zlib.compress(b'egg')[:1]) + TAIL)
    assert_equal(im.info, {'spam': ''})

    im = load(HEAD + chunk(b'zTXt', b'spam\0\0' + zlib.compress(b'egg')) + TAIL)
    assert_equal(im.info,  {'spam': 'egg'})

def test_interlace():

    file = "Tests/images/pil123p.png"
    im = Image.open(file)

    assert_image(im, "P", (162, 150))
    assert_true(im.info.get("interlace"))

    assert_no_exception(lambda: im.load())

    file = "Tests/images/pil123rgba.png"
    im = Image.open(file)

    assert_image(im, "RGBA", (162, 150))
    assert_true(im.info.get("interlace"))

    assert_no_exception(lambda: im.load())

def test_load_transparent_p():
    file = "Tests/images/pil123p.png"
    im = Image.open(file)

    assert_image(im, "P", (162, 150))
    im = im.convert("RGBA")
    assert_image(im, "RGBA", (162, 150))

    # image has 124 uniqe qlpha values
    assert_equal(len(im.split()[3].getcolors()), 124)

def test_load_transparent_rgb():
    file = "Tests/images/rgb_trns.png"
    im = Image.open(file)

    assert_image(im, "RGB", (64, 64))
    im = im.convert("RGBA")
    assert_image(im, "RGBA", (64, 64))

    # image has 876 transparent pixels
    assert_equal(im.split()[3].getcolors()[0][0], 876)

def test_save_p_transparent_palette():
    in_file = "Tests/images/pil123p.png"
    im = Image.open(in_file)

    file = tempfile("temp.png")
    assert_no_exception(lambda: im.save(file))

def test_save_p_single_transparency():
    in_file = "Tests/images/p_trns_single.png"
    im = Image.open(in_file)

    file = tempfile("temp.png")
    assert_no_exception(lambda: im.save(file))

def test_save_l_transparency():
    in_file = "Tests/images/l_trns.png"
    im = Image.open(in_file)

    file = tempfile("temp.png")
    assert_no_exception(lambda: im.save(file))

    # There are 559 transparent pixels. 
    im = im.convert('RGBA')
    assert_equal(im.split()[3].getcolors()[0][0], 559)

def test_save_rgb_single_transparency():
    in_file = "Tests/images/caption_6_33_22.png"
    im = Image.open(in_file)

    file = tempfile("temp.png")
    assert_no_exception(lambda: im.save(file))

def test_load_verify():
    # Check open/load/verify exception (@PIL150)

    im = Image.open("Images/lena.png")
    assert_no_exception(lambda: im.verify())

    im = Image.open("Images/lena.png")
    im.load()
    assert_exception(RuntimeError, lambda: im.verify())

def test_roundtrip_dpi():
    # Check dpi roundtripping

    im = Image.open(file)

    im = roundtrip(im, dpi=(100, 100))
    assert_equal(im.info["dpi"], (100, 100))

def test_roundtrip_text():
    # Check text roundtripping

    im = Image.open(file)

    info = PngImagePlugin.PngInfo()
    info.add_text("TXT", "VALUE")
    info.add_text("ZIP", "VALUE", 1)

    im = roundtrip(im, pnginfo=info)
    assert_equal(im.info, {'TXT': 'VALUE', 'ZIP': 'VALUE'})
    assert_equal(im.text, {'TXT': 'VALUE', 'ZIP': 'VALUE'})

def test_scary():
    # Check reading of evil PNG file.  For information, see:
    # http://scary.beasts.org/security/CESA-2004-001.txt
    # The first byte is removed from pngtest_bad.png
    # to avoid classification as malware.

    with open("Tests/images/pngtest_bad.png.bin", 'rb') as fd:
        data = b'\x89' + fd.read()

    pngfile = BytesIO(data)
    assert_exception(IOError, lambda: Image.open(pngfile))

def test_trns_rgb():
    # Check writing and reading of tRNS chunks for RGB images.
    # Independent file sample provided by Sebastian Spaeth.

    file = "Tests/images/caption_6_33_22.png"
    im = Image.open(file)
    assert_equal(im.info["transparency"], (248, 248, 248))

    # check saving transparency by default
    im = roundtrip(im)
    assert_equal(im.info["transparency"], (248, 248, 248))

    im = roundtrip(im, transparency=(0, 1, 2))
    assert_equal(im.info["transparency"], (0, 1, 2))

def test_trns_p():
    # Check writing a transparency of 0, issue #528
    im = lena('P')
    im.info['transparency']=0
    
    f = tempfile("temp.png")
    im.save(f)

    im2 = Image.open(f)
    assert_true('transparency' in im2.info)

    assert_image_equal(im2.convert('RGBA'), im.convert('RGBA'))
        
    
def test_save_icc_profile_none():
    # check saving files with an ICC profile set to None (omit profile)
    in_file = "Tests/images/icc_profile_none.png"
    im = Image.open(in_file)
    assert_equal(im.info['icc_profile'], None)

    im = roundtrip(im)
    assert_false('icc_profile' in im.info)

def test_roundtrip_icc_profile():
    # check that we can roundtrip the icc profile
    im = lena('RGB')

    jpeg_image = Image.open('Tests/images/flower2.jpg')
    expected_icc = jpeg_image.info['icc_profile']

    im.info['icc_profile'] = expected_icc
    im = roundtrip(im)
    assert_equal(im.info['icc_profile'], expected_icc)

