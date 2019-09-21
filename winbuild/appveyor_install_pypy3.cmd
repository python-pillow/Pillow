curl -fsSL -o pypy3.zip http://buildbot.pypy.org/nightly/py3.6/pypy-c-jit-97588-7392d01b93d0-win32.zip
7z x pypy3.zip -oc:\
c:\Python37\Scripts\virtualenv.exe -p c:\pypy-c-jit-97588-7392d01b93d0-win32\pypy3.exe c:\vp\pypy3
