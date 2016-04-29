# Pillow-SIMD

Pillow-SIMD is "following" Pillow fork (which is PIL fork itself).
"Following" means than Pillow-SIMD versions are 100% compatible
drop-in replacement for Pillow with the same version number.
For example, `Pillow-SIMD 3.2.0.post3` is drop-in replacement for
`Pillow 3.2.0` and  `Pillow-SIMD 3.3.3.post0` for `Pillow 3.3.3`.

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
- Pillow 3.4.1
- Pillow-SIMD 3.4.1.post1

Operation               | Filter  | IM   | Pillow| SIMD SSE4| SIMD AVX2| Skia 53
------------------------|---------|------|-------|----------|----------|--------
**Resize to 16x16**     | Bilinear| 41.37| 317.28|   1282.85|   1601.85|  809.49
                        | Bicubic | 20.58| 174.85|    712.95|    900.65|  453.10
                        | Lanczos | 14.17| 117.58|    438.60|    544.89|  292.57
**Resize to 320x180**   | Bilinear| 29.46| 195.21|    863.40|   1057.81|  592.76
                        | Bicubic | 15.75| 118.79|    503.75|    504.76|  327.68
                        | Lanczos | 10.80|  79.59|    312.05|    384.92|  196.92
**Resize to 1920x1200** | Bilinear| 17.80|  68.39|    215.15|    268.29|  192.30
                        | Bicubic |  9.99|  49.23|    170.41|    210.62|  112.84
                        | Lanczos |  6.95|  37.71|    130.00|    162.57|  104.76
**Resize to 7712x4352** | Bilinear|  2.54|   8.38|     22.81|     29.17|   20.58
                        | Bicubic |  1.60|   6.57|     18.23|     23.94|   16.52
                        | Lanczos |  1.09|   5.20|     14.90|     20.40|   12.05
**Blur**                | 1px     |  6.60|  16.94|     35.16|          |        
                        | 10px    |  2.28|  16.94|     35.47|          |        
                        | 100px   |  0.34|  16.93|     35.53|          |        


### Some conclusion

Pillow is always faster than ImageMagick. And Pillow-SIMD is faster
than Pillow in 4—5 times. In general, Pillow-SIMD with AVX2 always
**16-40 times faster** than ImageMagick and overperforms Skia,
high-speed graphics library used in Chromium, up to 2 times.

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
cache-awareness transposition. This result was improved in 3.3 & 3.4 with
integer-only arithmetics and other optimizations.


## Why Pillow-SIMD is even faster

Because of SIMD, of course. But this is not all. Heavy loops unrolling,
specific instructions, which not available for scalar.


## Why do not contribute SIMD to the original Pillow

Well, that's not simple. First of all, Pillow supports a large number
of architectures, not only x86. But even for x86 platforms, Pillow is often
distributed via precompiled binaries. To integrate SIMD in precompiled binaries
we need to do runtime checks of CPU capabilities.
To compile the code with runtime checks we need to pass `-mavx2` option
to the compiler. But with that option compiller will inject AVX instructions
enev for SSE functions, because every SSE instruction has AVX equivalent.
So there is no easy way to compile such library, especially with setuptools.


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
