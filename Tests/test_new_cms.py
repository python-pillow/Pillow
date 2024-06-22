import pytest
from PIL import ImageCms

def test_buildTransform_flags_non_integer():
    with pytest.raises(ImageCms.PyCMSError):
        ImageCms.buildTransform(
            inputProfile="path/to/input/profile",
            outputProfile="path/to/output/profile",
            inMode="RGB",
            outMode="CMYK",
            renderingIntent=ImageCms.Intent.PERCEPTUAL,
            flags="not_an_integer"  # This should not be an integer
        )

def test_buildTransform_flags_out_of_range():
    with pytest.raises(ImageCms.PyCMSError):
        ImageCms.buildTransform(
            inputProfile="path/to/input/profile",
            outputProfile="path/to/output/profile",
            inMode="RGB",
            outMode="CMYK",
            renderingIntent=ImageCms.Intent.PERCEPTUAL,
            flags=999999  # Assuming this value is outside the valid range
        )

def test_renderingIntent_non_integer():
    with pytest.raises(ImageCms.PyCMSError) as exc_info:
        ImageCms.buildTransform(
            inputProfile="path/to/input/profile",
            outputProfile="path/to/output/profile",
            inMode="RGB",
            outMode="CMYK",
            renderingIntent="not an integer",  # This should trigger the error
            flags=0
        )
    assert str(exc_info.value) == "renderingIntent must be an integer between 0 and 3"

   