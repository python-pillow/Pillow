11.1.0
------

Deprecations
============

ExifTags.IFD.Makernote
^^^^^^^^^^^^^^^^^^^^^^

``ExifTags.IFD.Makernote`` has been deprecated. Instead, use
``ExifTags.IFD.MakerNote``.

API changes
===========

Writing XMP bytes to JPEG and MPO
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pillow 11.0.0 added writing XMP data to JPEG and MPO images::

    im.info["xmp"] = b"test"
    im.save("out.jpg")

However, this meant that XMP data was automatically kept from an opened image,
which is inconsistent with the rest of Pillow's behaviour. This functionality
has been removed. To write XMP data, the ``xmp`` argument can still be used for
JPEG files::

    im.save("out.jpg", xmp=b"test")

To save XMP data to the second frame of an MPO image, ``encoderinfo`` can now
be used::

    second_im.encoderinfo = {"xmp": b"test"}
    im.save("out.mpo", save_all=True, append_images=[second_im])

API additions
=============

Check for zlib-ng
^^^^^^^^^^^^^^^^^

You can check if Pillow has been built against the zlib-ng version of the
zlib library, and what version of zlib-ng is being used::

    from PIL import features
    features.check_feature("zlib_ng")  # True or False
    features.version_feature("zlib_ng")  # "2.2.2" for example, or None

Saving TIFF as BigTIFF
^^^^^^^^^^^^^^^^^^^^^^

TIFF images can now be saved as BigTIFF using a ``big_tiff`` argument::

    im.save("out.tiff", big_tiff=True)

Other changes
=============

Reading JPEG 2000 comments
^^^^^^^^^^^^^^^^^^^^^^^^^^

When opening a JPEG 2000 image, the comment may now be read into
:py:attr:`~PIL.Image.Image.info` for J2K images, not just JP2 images.

Saving JPEG 2000 CMYK images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With OpenJPEG 2.5.3 or later, Pillow can now save CMYK images as JPEG 2000 files.

Minimum C version
^^^^^^^^^^^^^^^^^

C99 is now the minimum version of C required to compile Pillow from source.

zlib-ng in wheels
^^^^^^^^^^^^^^^^^

Wheels are now built against zlib-ng for improved speed. In tests, saving a PNG
was found to be more than twice as fast at higher compression levels.
