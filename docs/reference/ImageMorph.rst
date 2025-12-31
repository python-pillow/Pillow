.. py:module:: PIL.ImageMorph
.. py:currentmodule:: PIL.ImageMorph

:py:mod:`~PIL.ImageMorph` module
================================

The :py:mod:`~PIL.ImageMorph` module allows `morphology`_ operators ("MorphOp") to be
applied to L mode images::

  from PIL import Image, ImageMorph
  img = Image.open("Tests/images/hopper.bw")
  mop = ImageMorph.MorphOp(op_name="erosion4")
  count, imgOut = mop.apply(img)
  imgOut.show()

.. _morphology: https://en.wikipedia.org/wiki/Mathematical_morphology

In addition to applying operators, you can also analyse images.

You can inspect an image in isolation to determine which pixels are non-empty::

  print(mop.get_on_pixels(img))  # [(0, 0), (1, 0), (2, 0), ...]

Or you can retrieve a list of pixels that match the operator. This is the number of
pixels that will be non-empty after the operator is applied::

  coords = mop.match(img)
  print(coords)  # [(17, 1), (18, 1), (34, 1), ...]
  print(len(coords))  # 550

  imgOut = mop.apply(img)[1]
  print(len(mop.get_on_pixels(imgOut)))  # 550

If you would like more customized operators, you can pass patterns to the MorphOp
class::

  mop = ImageMorph.MorphOp(patterns=["1:(... ... ...)->0", "4:(00. 01. ...)->1"])

Or you can pass lookup table ("LUT") data directly. This LUT data can be constructed
with the :py:class:`~PIL.ImageMorph.LutBuilder`::

  builder = ImageMorph.LutBuilder()
  mop = ImageMorph.MorphOp(lut=builder.build_lut())

.. autoclass:: LutBuilder
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: MorphOp
    :members:
    :undoc-members:
    :show-inheritance:
