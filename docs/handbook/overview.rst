Overview
========

The **Python Imaging Library** adds image processing capabilities to your
Python interpreter.

This library provides extensive file format support, an efficient internal
representation, and fairly powerful image processing capabilities.

The core image library is designed for fast access to data stored in a few
basic pixel formats. It should provide a solid foundation for a general image
processing tool.

Let’s look at a few possible uses of this library.

Image Archives
--------------

The Python Imaging Library is ideal for image archival and batch processing
applications. You can use the library to create thumbnails, convert between
file formats, print images, etc.

The current version identifies and reads a large number of formats. Write
support is intentionally restricted to the most commonly used interchange and
presentation formats.

Image Display
-------------

The current release includes Tk :py:class:`~PIL.ImageTk.PhotoImage` and
:py:class:`~PIL.ImageTk.BitmapImage` interfaces, as well as a :py:mod:`Windows
DIB interface <PIL.ImageWin>` that can be used with PythonWin and other
Windows-based toolkits. Many other GUI toolkits come with some kind of PIL
support.

For debugging, there’s also a :py:meth:`show` method which saves an image to
disk, and calls an external display utility.

Image Processing
----------------

The library contains basic image processing functionality, including point operations, filtering with a set of built-in convolution kernels, and colour space conversions.

The library also supports image resizing, rotation and arbitrary affine transforms.

There’s a histogram method allowing you to pull some statistics out of an image. This can be used for automatic contrast enhancement, and for global statistical analysis.
