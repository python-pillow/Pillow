# Pillow-SIMD

Pillow-SIMD is "following" Pillow (which is a PIL's fork itself).
"Following" here means than Pillow-SIMD versions are 100% compatible
drop-in replacements for Pillow of the same version.
For example, `Pillow-SIMD 3.2.0.post3` is a drop-in replacement for
`Pillow 3.2.0`, and  `Pillow-SIMD 3.3.3.post0` — for `Pillow 3.3.3`.

For more information on the original Pillow, please refer to:
[read the documentation][original-docs],
[check the changelog][original-changelog] and
[find out how to contribute][original-contribute].


## Why SIMD

There are multiple ways to tweak image processing performance.
To name a few, such ways can be: utilizing better algorithms, optimizing existing implementations, 
using more processing power and/or resources. 
One of the great examples of using a more efficient algorithm is [replacing][gaussian-blur-changes] 
a convolution-based Gaussian blur with a sequential-box one.

Such examples are rather rare, though. It is also known, that certain processes might be optimized 
by using parallel processing to run the respective routines.
But a more practical key to optimizations might be making things work faster 
using the resources at hand. For instance, SIMD computing might be the case.

SIMD stands for "single instruction, multiple data" and its essence is 
in performing the same operation on multiple data points simultaneously 
by using multiple processing elements. 
Common CPU SIMD instruction sets are MMX, SSE-SSE4, AVX, AVX2, AVX512, NEON.

Currently, Pillow-SIMD can be [compiled](#installation) with SSE4 (default) or AVX2 support.


## Status

Pillow-SIMD project is production-ready.
The project is supported by Uploadcare, a SAAS for cloud-based image storing and processing.

[![Uploadcare][uploadcare.logo]][uploadcare.com]

In fact, Uploadcare has been running Pillow-SIMD for about two years now.

The following image operations are currently SIMD-accelerated:

- Resize (convolution-based resampling): SSE4, AVX2
- Gaussian and box blur: SSE4
- Alpha composition: SSE4, AVX2
- RGBA → RGBa (alpha premultiplication): SSE4, AVX2
- RGBa → RGBA (division by alpha): AVX2

See [CHANGES](CHANGES.SIMD.rst) for more information.



## Benchmarks

In order for you to clearly assess the productivity of implementing SIMD computing into Pillow image processing, 
we ran a number of benchmarks. The respective results can be found in the table below (the more — the better). 
The numbers represent processing rates in megapixels per second (Mpx/s). 
For instance, the rate at which a 2560x1600 RGB image is processed in 0.5 seconds equals to 8.2 Mpx/s.
Here is the list of libraries and their versions we've been up to during the benchmarks:

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


### A brief conclusion

The results show that Pillow is always faster than ImageMagick, 
Pillow-SIMD, in turn, is even faster than the original Pillow by the factor of 4-5. 
In general, Pillow-SIMD with AVX2 is always **16 to 40 times faster** than 
ImageMagick and outperforms Skia, the high-speed graphics library used in Chromium.

### Methodology

All rates were measured using the following setup: Ubuntu 14.04 64-bit, 
single-thread AVX2-enabled Intel i5 4258U CPU.
ImageMagick performance was measured with the `convert` command-line tool 
followed by `-verbose` and `-bench` arguments.
Such approach was used because there's usually a need in testing 
the latest software versions and command-line is the easiest way to do that.
All the routines involved with the testing procedure produced identic results.
Resizing filters compliance:

- PIL.Image.BILINEAR == Triangle
- PIL.Image.BICUBIC == Catrom
- PIL.Image.LANCZOS == Lanczos

In ImageMagick, Gaussian blur operation invokes two parameters: 
the first is called 'radius' and the second is called 'sigma'.
In fact, in order for the blur operation to be Gaussian, there should be no additional parameters. 
When the radius value is too small the blur procedure ceases to be Gaussian and 
if the value is excessively big the operation gets slowed down with zero benefits in exchange. 
For the benchmarking purposes, the radius was set to `sigma × 2.5`.

Following script was used for the benchmarking procedure:
https://gist.github.com/homm/f9b8d8a84a57a7e51f9c2a5828e40e63


## Why Pillow itself is so fast

No cheats involved. We've used identical high-quality resize and blur methods for the benchmark. 
Outcomes produced by different libraries are in almost pixel-perfect agreement. 
The difference in measured rates is only provided with the performance of every involved algorithm. 

## Why Pillow-SIMD is even faster

Because of the SIMD computing, of course. But there's more to it: 
heavy loops unrolling, specific instructions, which aren't available for scalar data types.


## Why do not contribute SIMD to the original Pillow

Well, it's not that simple. First of all, the original Pillow supports 
a large number of architectures, not just x86.
But even for x86 platforms, Pillow is often distributed via precompiled binaries.
In order for us to integrate SIMD into the precompiled binaries 
we'd need to execute runtime CPU capabilities checks.
To compile the code this way we need to pass the `-mavx2` option to the compiler.
But with the option included, a compiler will inject AVX instructions even
for SSE functions (i.e. interchange them) since every SSE instruction has its AVX equivalent.
So there is no easy way to compile such library, especially with setuptools.


## Installation

If there's a copy of the original Pillow installed, it has to be removed first
with `$ pip uninstall -y pillow`.
The installation itself is simple just as running `$ pip install pillow-simd`, 
and if you're using SSE4-capable CPU everything should run smoothly.
If you'd like to install the AVX2-enabled version, 
you need to pass the additional flag to a C compiler. 
The easiest way to do so is to define the `CC` variable during the compilation.

```bash
$ pip uninstall pillow
$ CC="cc -mavx2" pip install -U --force-reinstall pillow-simd
```

## Contributing to Pillow-SIMD

Please be aware that Pillow-SIMD and Pillow are two separate projects.
Please submit bugs and improvements not related to SIMD to the [original Pillow][original-issues].
All bugfixes to the original Pillow will then be transferred to the next Pillow-SIMD version automatically.


  [original-docs]: http://pillow.readthedocs.io/
  [original-issues]: https://github.com/python-pillow/Pillow/issues/new
  [original-changelog]: https://github.com/python-pillow/Pillow/blob/master/CHANGES.rst
  [original-contribute]: https://github.com/python-pillow/Pillow/blob/master/.github/CONTRIBUTING.md
  [gaussian-blur-changes]: http://pillow.readthedocs.io/en/3.2.x/releasenotes/2.7.0.html#gaussian-blur-and-unsharp-mask
  [uploadcare.com]: https://uploadcare.com/?utm_source=github&utm_medium=description&utm_campaign=pillow-simd
  [uploadcare.logo]: https://ucarecdn.com/dc4b8363-e89f-402f-8ea8-ce606664069c/-/preview/
