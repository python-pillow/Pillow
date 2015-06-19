Quick README
------------ 

For more extensive info, see the windows build instructions `docs/build.rst`.

* See https://github.com/python-imaging/Pillow/issues/553#issuecomment-37877416 and https://github.com/matplotlib/matplotlib/issues/1717#issuecomment-13343859 

*  Works best with Python 3.4, due to virtualenv and pip batteries included. Python3+ required for fetch command. 
*  Check config.py for virtual env paths, suffix for 64 bit releases. Defaults to `x64`, set `X64_EXT` to change.
*  When running in CI with one python per invocation, set the `PYTHON` env variable to the python folder. (e.g. `PYTHON`=`c:\Python27\`) This overrides the matrix in config.py and will just build and test for the specific python. 
* `python get_pythons.py` downloads all the python releases, and their signatures. (Manually) Install in `c:\PythonXX[x64]\`.
* `python build_dep.py` downloads and creates a build script for all the dependencies, in 32 and 64 bit versions, and with both compiler versions.
* (in powershell) `build_deps.cmd` invokes the dependency build.
* `python build.py --clean` makes pillow for the matrix of pythons. 
* `python test.py` runs the tests on pillow in all the virtual envs.
*  Currently working with zlib, libjpeg, freetype, and libtiff on Python 2.7, 3.3, and 3.4, both 32 and 64 bit, on a local win7 pro machine and appveyor.com (3.3 untested there)
* Webp is built, not detected.
* LCMS and OpenJpeg are not building. 
