from tester import *
from PIL import Image, TiffImagePlugin, TiffTags

tag_ids = dict(zip(TiffTags.TAGS.values(), TiffTags.TAGS.keys()))

# Test writing arbitray metadata into the tiff image directory
# Use case is ImageJ private tags, one numeric, one arbitrary data.
# https://github.com/python-imaging/Pillow/issues/291

def test_rt_metadata():
    img = lena()

    textdata = "This is some arbitrary metadata for a text field"
    info = TiffImagePlugin.ImageFileDirectory()

    info[tag_ids['ImageJMetaDataByteCounts']] = len(textdata)
    info[tag_ids['ImageJMetaData']] = textdata

    f = tempfile("temp.tif")

    img.save(f, tiffinfo=info)
    
    loaded = Image.open(f)

    assert_equal(loaded.tag[50838], (len(textdata),))
    assert_equal(loaded.tag[50839], textdata)
    
