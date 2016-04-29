# Pillow-SIMD

Pillow-SIMD is "following" Pillow fork (which is PIL fork itself).

For more information about original Pillow, please
[read the documentation][original-docs],
[check the changelog][original-changelog] and
[find out how to contribute][original-contribute].


## Why SIMD

There are many ways to improve the performance of image processing.
You can use better algorithms for the same task, you can make better
implementation for current algorithms, or you can use more processing unit
resources. It is perfect when you can just use more efficient algorithm like
when gaussian blur based on convolutions [was replaced][gaussian-blur-changes]
by sequential box filters. But a number of such improvements are very limited.
It is also very tempting to use more processor unit resources 
(via parallelization) when they are available. But it is handier just
to make things faster on the same resources. And that is where SIMD works better.

SIMD stands for "single instruction, multiple data". This is a way to perform
same operations against the huge amount of homogeneous data. 
Modern CPU have different SIMD instructions sets like
MMX, SSE-SSE4, AVX, AVX2, AVX512, NEON.

Currently, Pillow-SIMD can be [compiled](#installation) with SSE4 (default)
and AVX2 support.


## Status

[![Uploadcare][uploadcare.logo]][uploadcare.com]

Pillow-SIMD can be used in production. Pillow-SIMD has been operating on
[Uploadcare][uploadcare.com] servers for more than 1 year.
Uploadcare is SAAS for image storing and processing in the cloud
and the main sponsor of Pillow-SIMD project.

Currently, following operations are accelerated:

- Resize (convolution-based resampling): SSE4, AVX2
- Gaussian and box blur: SSE4
- Alpha composition: SSE4, AVX2
- RGBA → RGBa (alpha premultiplication): SSE4, AVX2
- RGBa → RGBA (division by alpha): AVX2

See [CHANGES](CHANGES.SIMD.rst).


## Benchmarks

The numbers in the table represent processed megapixels of source RGB 2560x1600
image per second. For example, if resize of 2560x1600 image is done
in 0.5 seconds, the result will be 8.2 Mpx/s.

- Skia 53
- ImageMagick 6.9.3-8 Q8 x86_64
- Pillow 3.3.0
- Pillow-SIMD 3.3.0.post1

Operation               | Filter  | IM   | Pillow| SIMD SSE4| SIMD AVX2| Skia 53
------------------------|---------|------|-------|----------|----------|--------
**Resize to 16x16**     | Bilinear| 41.37| 337.12|    571.67|    903.40|  809.49
                        | Bicubic | 20.58| 185.79|    305.72|    552.85|  453.10
                        | Lanczos | 14.17| 113.27|    189.19|    355.40|  292.57
**Resize to 320x180**   | Bilinear| 29.46| 209.06|    366.33|    558.57|  592.76
                        | Bicubic | 15.75| 124.43|    224.91|    353.53|  327.68
                        | Lanczos | 10.80|  82.25|    153.10|    244.22|  196.92
**Resize to 1920x1200** | Bilinear| 17.80|  55.87|    131.27|    152.11|  192.30
                        | Bicubic |  9.99|  43.64|     90.20|    112.34|  112.84
                        | Lanczos |  6.95|  34.51|     72.55|    103.16|  104.76
**Resize to 7712x4352** | Bilinear|  2.54|   6.71|     16.06|     20.33|   20.58
                        | Bicubic |  1.60|   5.51|     12.65|     16.46|   16.52
                        | Lanczos |  1.09|   4.62|      9.84|     13.38|   12.05
**Blur**                | 1px     |  6.60|  16.94|     35.16|          |        
                        | 10px    |  2.28|  16.94|     35.47|          |        
                        | 100px   |  0.34|  16.93|     35.53|          |        


### Some conclusion

Pillow is always faster than ImageMagick. And Pillow-SIMD is faster
than Pillow in 2—2.5 times. In general, Pillow-SIMD with AVX2 always
**8-20 times faster** than ImageMagick and almost equal to the Skia results,
high-speed graphics library used in Chromium.

### Methodology

All tests were performed on Ubuntu 14.04 64-bit running on
Intel Core i5 4258U with AVX2 CPU on the single thread.

ImageMagick performance was measured with command-line tool `convert` with
`-verbose` and `-bench` arguments. I use command line because
I need to test the latest version and this is the easiest way to do that.

All operations produce exactly the same results.
Resizing filters compliance:

- PIL.Image.BILINEAR == Triangle
- PIL.Image.BICUBIC == Catrom
- PIL.Image.LANCZOS == Lanczos

In ImageMagick, the radius of gaussian blur is called sigma and the second
parameter is called radius. In fact, there should not be additional parameters
for *gaussian blur*, because if the radius is too small, this is *not*
gaussian blur anymore. And if the radius is big this does not give any
advantages but makes operation slower. For the test, I set the radius
to sigma × 2.5.

Following script was used for testing:
https://gist.github.com/homm/f9b8d8a84a57a7e51f9c2a5828e40e63


## Why Pillow itself is so fast

There are no cheats. High-quality resize and blur methods are used for all
benchmarks. Results are almost pixel-perfect. The difference is only effective
algorithms. Resampling in Pillow was rewritten in version 2.7 with 
minimal usage of floating point numbers, precomputed coefficients and
cache-awareness transposition.


## Why Pillow-SIMD is even faster

Because of SIMD, of course. There are some ideas how to achieve even better
performance.

- **Efficient work with memory** Currently, each pixel is read from 
  memory to the SSE register, while every SSE register can handle
  four pixels at once.
- **Integer-based arithmetic** Experiments show that integer-based arithmetic
  does not affect the quality and increases the performance of non-SIMD code
  up to 50%.
- **Aligned pixels allocation** Well-known that the SIMD load and store
  commands work better with aligned memory.


## Why do not contribute SIMD to the original Pillow

Well, it's not that simple. First of all, Pillow supports a large number
of architectures, not only x86. But even for x86 platforms, Pillow is often
distributed via precompiled binaries. To integrate SIMD in precompiled binaries
we need to do runtime checks of CPU capabilities.
To compile the code with runtime checks we need to pass `-mavx2` option
to the compiler. However this automatically activates all `if (__AVX2__)`
and below conditions. And SIMD instructions under such conditions exist
even in standard C library and they do not have any runtime checks.
Currently, I don't know how to allow SIMD instructions in the code
but *do not allow* such instructions without runtime checks.


## Installation

In general, you need to do `pip install pillow-simd` as always and if you
are using SSE4-capable CPU everything should run smoothly.
Do not forget to remove original Pillow package first.

If you want the AVX2-enabled version, you need to pass the additional flag to C
compiler. The easiest way to do that is define `CC` variable while compilation.

```bash
$ pip uninstall pillow
$ CC="cc -mavx2" pip install -U --force-reinstall pillow-simd
```


## Contributing to Pillow-SIMD

Pillow-SIMD and Pillow are two separate projects.
Please submit bugs and improvements not related to SIMD to 
[original Pillow][original-issues]. All bugs and fixes in Pillow
will appear in next Pillow-SIMD version automatically.


  [original-docs]: http://pillow.readthedocs.io/
  [original-issues]: https://github.com/python-pillow/Pillow/issues/new
  [original-changelog]: https://github.com/python-pillow/Pillow/blob/master/CHANGES.rst
  [original-contribute]: https://github.com/python-pillow/Pillow/blob/master/.github/CONTRIBUTING.md
  [gaussian-blur-changes]: http://pillow.readthedocs.io/en/3.2.x/releasenotes/2.7.0.html#gaussian-blur-and-unsharp-mask
  [uploadcare.com]: https://uploadcare.com/?utm_source=github&utm_medium=description&utm_campaign=pillow-simd
  [uploadcare.logo]: https://ucarecdn.com/dc4b8363-e89f-402f-8ea8-ce606664069c/-/preview/
