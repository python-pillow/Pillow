import pytest

from PIL import Image

@pytest.mark.filterwarnings("ignore:Possibly corrupt EXIF data")
@pytest.mark.filterwarnings("ignore:Metadata warning")
def test_tiff_crashes():
    test_file = "Tests/images/crash-63b1dffefc8c075ddc606c0a2f5fdc15ece78863.tif"
    with pytest.raises(IOError):
        with Image.open(test_file) as im:
            im.load()
