Block Allocator
===============

Previous Design
---------------

Historically there have been two image allocators in Pillow:
``ImagingAllocateBlock`` and ``ImagingAllocateArray``. The first works
for images smaller than 16MB of data and allocates one large chunk of
memory of ``im->linesize * im->ysize`` bytes. The second works for
large images and makes one allocation for each scan line of size
``im->linesize`` bytes.  This makes for a very sharp transition
between one allocation and potentially thousands of small allocations,
leading to unpredictable performance penalties around the transition.

New Design
----------

``ImagingAllocateArray`` now allocates space for images as a chain of
blocks with a maximum size of 16MB. If there is a memory allocation
error, it falls back to allocating a 4KB block, or at least one scan
line. This is now the default for all internal allocations.

``ImagingAllocateBlock`` is now only used for those cases when we are
specifically requesting a single segment of memory for sharing with
other code.

Memory Pools
------------

There is now a memory pool to contain a supply of recently freed
blocks, which can then be reused without going back to the OS for a
fresh allocation. This caching of free blocks is currently disabled by
default, but can be enabled and tweaked using three environment
variables:

  * ``PILLOW_ALIGNMENT``, in bytes. Specifies the alignment of memory
    allocations. Valid values are powers of 2 between 1 and
    128, inclusive. Defaults to 1.

  * ``PILLOW_BLOCK_SIZE``, in bytes, K, or M.  Specifies the maximum
    block size for ``ImagingAllocateArray``. Valid values are
    integers, with an optional ``k`` or ``m`` suffix. Defaults to 16M.

  * ``PILLOW_BLOCKS_MAX`` Specifies the number of freed blocks to
    retain to fill future memory requests. Any freed blocks over this
    threshold will be returned to the OS immediately. Defaults to 0.
