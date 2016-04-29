Changelog (Pillow-SIMD)
=======================

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

Convertion
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
