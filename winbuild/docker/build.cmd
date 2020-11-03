
set CI=true
path C:\nasm-2.14.02\;%PATH%
xcopy /s c:\pillow-depends\test_images\* c:\pillow\tests\images

cd c:\pillow\winbuild\
c:\python37\python.exe build_prepare.py -v --depends=C:\pillow-depends
if errorlevel 1 echo Build prepare failed! && exit /B 1
call build\build_dep_all.cmd
if errorlevel 1 echo Build dependencies failed! && exit /B 1
call build\build_pillow.cmd install
if errorlevel 1 echo Build failed! && exit /B 1

cd c:\pillow
path c:\pillow\winbuild\build\bin;%PATH%
c:\python37\python.exe selftest.py --installed
if errorlevel 1 echo Selftest failed! && exit /B 1
c:\python37\python.exe -m pytest -vx -W always --cov PIL --cov Tests --cov-report term --cov-report xml Tests
