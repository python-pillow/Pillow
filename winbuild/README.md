Quick README
------------ 

For more extensive info, see the windows build instructions `docs/build.rst`.

* See https://github.com/python-imaging/Pillow/issues/553#issuecomment-37877416 and https://github.com/matplotlib/matplotlib/issues/1717#issuecomment-13343859 

*  Works best with Python 3.4, due to virtualenv and pip batteries included. 
*  Check config.py for virtual env paths.
* `python get_pythons.py` downloads all the python releases, and their signatures. Install in `c:\PythonXX[x64]\`.
* `python build_dep.py` downloads and builds all the dependencies, in 32 and 64 bit versions, and with both compiler versions. 
* `python build.py --clean` makes pillow for the matrix of pythons. 
* `python test.py` runs the tests on pillow in all the virtual envs. 