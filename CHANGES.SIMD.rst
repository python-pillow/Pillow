Changelog (Pillow-SIMD)
=======================

7.0.0.post4
-----------

- Filter: fixed wrong offset handling for 3x3 single-band version

7.0.0.post3
-----------

- ColorLUT: fixed potential access violation, up to 2x faster

7.0.0.post2
-----------

- ColorLUT: SSE4 & AVX2

7.0.0.post1 & 6.2.2.post1 & 6.1.0.post1 & 6.0.0.post2
-----------------------------------------------------

- Bands: access violation in getband in some enviroments

7.0.0.post0
-----------

- Reduce: SSE4

6.0.0.post1
-----------

- GCC 9.0+: fixed unaligned read for ``_**_cvtepu8_epi32`` functions.

6.0.0.post0 and 5.3.0.post1
---------------------------

- Resampling: Correct max coefficient calculation. Some rare combinations of
  initial and requested sizes lead to black lines.

4.3.0.post0
-----------

- Float-based filters, single-band: 3x3 SSE4, 5x5 SSE4
- Float-based filters, multi-band: 3x3 SSE4 & AVX2, 5x5 SSE4
- Int-based filters, multi-band: 3x3 SSE4 & AVX2, 5x5 SSE4 & AVX2
- Box blur: fast path for radius < 1
- Alpha composite: fast div approximation
- Color conversion: RGB to L SSE4, fast div in RGBa to RGBA
- Resampling: optimized coefficients loading
- Split and get_channel: SSE4

3.4.1.post1
-----------

- Critical memory error for some combinations of source/destination 
  sizes is fixed.

3.4.1.post0
-----------

- A lot of optimizations in resampling including 16-bit
  intermediate color representation and heavy unrolling.

3.3.2.post0
-----------

- Maintenance release
 
3.3.0.post2
-----------

- Fixed error in RGBa -> RGBA conversion

3.3.0.post1
-----------

Alpha compositing
~~~~~~~~~~~~~~~~~

- SSE4 and AVX2 fixed-point full loading implementation.
  Up to 4.6x faster.

3.3.0.post0
-----------

Resampling
~~~~~~~~~~

- SSE4 and AVX2 fixed-point full loading horizontal pass.
- SSE4 and AVX2 fixed-point full loading vertical pass.

Conversion
~~~~~~~~~~

- RGBA -> RGBa SSE4 and AVX2 fixed-point full loading implementations.
  Up to 2.6x faster.
- RGBa -> RGBA AVX2 implementation using gather instructions.
  Up to 5x faster.


3.2.0.post3
-----------

Resampling
~~~~~~~~~~

- SSE4 and AVX2 float full loading horizontal pass.
- SSE4 float full loading vertical pass.


3.2.0.post2
-----------

Resampling
~~~~~~~~~~

- SSE4 and AVX2 float full loading horizontal pass.
- SSE4 float per-pixel loading vertical pass.


2.9.0.post1
-----------

Resampling
~~~~~~~~~~

- SSE4 and AVX2 float per-pixel loading horizontal pass.
- SSE4 float per-pixel loading vertical pass.
- SSE4: Up to 2x for downscaling. Up to 3.5x for upscaling.
- AVX2: Up to 2.7x for downscaling. Up to 3.5x for upscaling.


Box blur
~~~~~~~~

- Simple SSE4 fixed-point implementations with per-pixel loading.
- Up to 2.1x faster.
