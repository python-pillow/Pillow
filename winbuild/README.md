Quick README
------------

For more extensive info, see the [Windows build instructions](build.rst).

* See [Current Windows Build/Testing process (Pillow#553)](https://github.com/python-pillow/Pillow/issues/553#issuecomment-37877416),
  [Definitive docs for how to compile on Windows (matplotlib#1717)](https://github.com/matplotlib/matplotlib/issues/1717#issuecomment-13343859),
  [Test Windows with GitHub Actions (Pillow#4084)](https://github.com/python-pillow/Pillow/pull/4084).


* Requires Microsoft Visual Studio 2017 or newer with C++ component.
* Requires NASM for libjpeg-turbo, a required dependency when using this script.
* Requires CMake 3.12 or newer (available as Visual Studio component).
* Tested on Windows Server 2016 with Visual Studio 2017 Community (AppVeyor).
* Tested on Windows Server 2019 with Visual Studio 2019 Enterprise (GitHub Actions).

The following is a simplified version of the script used on AppVeyor:
```
set PYTHON=C:\Python38\bin
cd /D C:\Pillow\winbuild
C:\Python37\bin\python.exe build_prepare.py -v --depends=C:\pillow-depends
build\build_dep_all.cmd
build\build_pillow.cmd install
cd ..
path C:\Pillow\winbuild\build\bin;%PATH%
%PYTHON%\python.exe selftest.py
%PYTHON%\python.exe -m pytest -vx --cov PIL --cov Tests --cov-report term --cov-report xml Tests
build\build_pillow.cmd bdist_wheel
```
