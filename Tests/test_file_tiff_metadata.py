from tester import *
from PIL import Image, TiffImagePlugin, TiffTags

tag_ids = dict(zip(TiffTags.TAGS.values(), TiffTags.TAGS.keys()))

def test_rt_metadata():
    """ Test writing arbitray metadata into the tiff image directory
        Use case is ImageJ private tags, one numeric, one arbitrary
        data.  https://github.com/python-imaging/Pillow/issues/291
        """
    
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
    
def test_read_metadata():
    img = Image.open('Tests/images/lena_g4.tif')
    
    known = {'YResolution': ((1207959552, 16777216),),
             'PlanarConfiguration': (1,),
             'BitsPerSample': (1,),
             'ImageLength': (128,),
             'Compression': (4,),
             'FillOrder': (1,),
             'DocumentName': 'lena.g4.tif',
             'RowsPerStrip': (128,),
             'ResolutionUnit': (1,),
             'PhotometricInterpretation': (0,),
             'PageNumber': (0, 1),
             'XResolution': ((1207959552, 16777216),),
             'ImageWidth': (128,),
             'Orientation': (1,),
             'StripByteCounts': (1796,),
             'SamplesPerPixel': (1,),
             'StripOffsets': (8,),
             'Software': 'ImageMagick 6.5.7-8 2012-08-17 Q16 http://www.imagemagick.org'}

    # assert_equal is equivalent, but less helpful in telling what's wrong. 
    named = img.tag.named()
    for tag, value in named.items():
        assert_equal(known[tag], value)

    for tag, value in known.items():
        assert_equal(value, named[tag])


def test_write_metadata():
    """ Test metadata writing through the python code """
    img = Image.open('Tests/images/lena.tif')

    f = tempfile('temp.tiff')
    img.save(f, tiffinfo = img.tag)

    loaded = Image.open(f)

    original = img.tag.named()
    reloaded = loaded.tag.named()

    ignored = ['StripByteCounts', 'RowsPerStrip', 'PageNumber', 'StripOffsets']
    
    for tag, value in reloaded.items():
        if tag not in ignored:
            assert_equal(original[tag], value, "%s didn't roundtrip" % tag)

    for tag, value in original.items():
        if tag not in ignored: 
            assert_equal(value, reloaded[tag], "%s didn't roundtrip" % tag)
