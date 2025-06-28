Third-party plugins
===================

Pillow uses a plugin model which allows users to add their own
decoders and encoders to the library, without any changes to the library
itself.

Here is a list of PyPI projects that offer additional plugins:

* :pypi:`DjvuRleImagePlugin`: Plugin for the DjVu RLE image format as defined in the DjVuLibre docs.
* :pypi:`heif-image-plugin`: Simple HEIF/HEIC images plugin, based on the pyheif library.
* :pypi:`jxlpy`: Introduces reading and writing support for JPEG XL.
* :pypi:`pillow-heif`: Python bindings to libheif for working with HEIF images.
* :pypi:`pillow-jpls`: Plugin for the JPEG-LS codec, based on the Charls JPEG-LS implemetation. Python bindings implemented using pybind11.
* :pypi:`pillow-jxl-plugin`: Plugin for JPEG-XL, using Rust for bindings.
* :pypi:`pillow-mbm`: Adds support for KSP's proprietary MBM texture format.
* :pypi:`pillow-svg`: Implements basic SVG read support. Supports basic paths, shapes, and text.
* :pypi:`raw-pillow-opener`: Simple camera raw opener, based on the rawpy library.
