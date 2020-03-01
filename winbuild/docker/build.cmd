
xcopy c:\pillow-depends\*.zip c:\pillow\winbuild\
xcopy c:\pillow-depends\*.tar.gz c:\pillow\winbuild\
xcopy /s c:\pillow-depends\test_images\* c:\pillow\tests\images

cd c:\pillow\winbuild\
c:\python37\python.exe c:\pillow\winbuild\build_dep.py

rem Set up environment
set INCLUDE=
set INCLIB=c:\Pillow\winbuild\depends\msvcr10-x32
set BUILD=c:\Pillow\winbuild\build
call "C:\BuildTools\VC\Auxiliary\Build\vcvarsall.bat" x86
echo on
path C:\nasm-2.14.02\;%PATH%

rem Build Dependencies

rem -> Build libjpegturbo
setlocal
cd /D %BUILD%\libjpeg-turbo-2.0.3
set CMAKE=cmake.exe -DCMAKE_VERBOSE_MAKEFILE=ON -DCMAKE_RULE_MESSAGES:BOOL=OFF
set CMAKE=%CMAKE% -DENABLE_SHARED:BOOL=OFF -DWITH_JPEG8:BOOL=TRUE -DWITH_CRT_DLL:BOOL=TRUE -DCMAKE_BUILD_TYPE=Release
%CMAKE% -G "NMake Makefiles" .
nmake -nologo -f Makefile clean
nmake -nologo -f Makefile jpeg-static cjpeg-static djpeg-static
copy /Y /B j*.h %INCLIB%
copy /Y /B jpeg-static.lib %INCLIB%\libjpeg.lib
copy /Y /B cjpeg-static.exe %INCLIB%\cjpeg.exe
copy /Y /B djpeg-static.exe %INCLIB%\djpeg.exe
endlocal

rem -> Build zlib
setlocal
cd /D %BUILD%\zlib-1.2.11
nmake -nologo -f win32\Makefile.msc clean
nmake -nologo -f win32\Makefile.msc zlib.lib
copy /Y /B z*.h %INCLIB%
copy /Y /B *.lib %INCLIB%
copy /Y /B zlib.lib %INCLIB%\z.lib
endlocal

rem -> Build LibTiff
setlocal
cd /D %BUILD%\tiff-4.1.0
copy /Y c:\pillow\winbuild\tiff.opt nmake.opt
nmake -nologo -f makefile.vc clean
nmake -nologo -f makefile.vc lib
copy /Y /B libtiff\tiff*.h %INCLIB%
copy /Y /B libtiff\*.dll %INCLIB%
copy /Y /B libtiff\*.lib %INCLIB%
endlocal

rem -> Build WebP
setlocal
cd /D %BUILD%\libwebp-1.1.0
rmdir /S /Q output\release-static
nmake -nologo -f Makefile.vc CFG=release-static OBJDIR=output ARCH=x86 all
mkdir %INCLIB%\webp
copy /Y /B src\webp\*.h %INCLIB%\webp
copy /Y /B output\release-static\x86\lib\* %INCLIB%
endlocal

rem -> Build FreeType
setlocal
cd /D %BUILD%\freetype-2.10.1
rmdir /S /Q objs
set DefaultPlatformToolset=v142
set VCTargetsPath=C:\BuildTools\MSBuild\Microsoft\VC\v160\
set MSBUILD="C:\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
powershell -Command "(gc builds\windows\vc2010\freetype.vcxproj) -replace 'MultiThreaded<', 'MultiThreadedDLL<' | Out-File -encoding ASCII builds\windows\vc2010\freetype.vcxproj"
%MSBUILD% builds\windows\vc2010\freetype.sln /t:Build /p:Configuration="Release Static" /p:Platform=Win32 /m
xcopy /Y /E /Q include %INCLIB%
copy /Y /B "objs\Win32\Release Static\freetype.lib" %INCLIB%
endlocal

rem -> Build LCMS2
setlocal
cd /D %BUILD%\lcms2-2.8
rmdir /S /Q Lib
rmdir /S /Q Projects\VC2015\Release
set VCTargetsPath=C:\BuildTools\MSBuild\Microsoft\VC\v160\
set MSBUILD="C:\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
powershell C:\Pillow\winbuild\lcms2_patch.ps1
%MSBUILD% Projects\VC2015\lcms2.sln /t:Clean;lcms2_static /p:Configuration="Release" /p:Platform=Win32 /m
xcopy /Y /E /Q include %INCLIB%
copy /Y /B Lib\MS\*.lib %INCLIB%
endlocal

rem -> Build OpenJPEG
setlocal
cd /D %BUILD%\openjpeg-2.3.1msvcr10-x32
set CMAKE=cmake.exe -DCMAKE_VERBOSE_MAKEFILE=ON -DCMAKE_RULE_MESSAGES:BOOL=OFF
set CMAKE=%CMAKE% -DBUILD_THIRDPARTY:BOOL=OFF -DBUILD_SHARED_LIBS:BOOL=OFF
set CMAKE=%CMAKE% -DCMAKE_BUILD_TYPE=Release
%CMAKE% -G "NMake Makefiles" .
nmake -nologo -f Makefile clean
nmake -nologo -f Makefile
mkdir %INCLIB%\openjpeg-2.3.1
copy /Y /B src\lib\openjp2\*.h %INCLIB%\openjpeg-2.3.1
copy /Y /B bin\*.lib %INCLIB%
endlocal

rem -> Build libimagequant
setlocal
rem e5d454b: Merge tag '2.12.6' into msvc
cd /D %BUILD%\libimagequant-e5d454bc7f5eb63ee50c84a83a7fa5ac94f68ec4
echo (gc CMakeLists.txt) -replace 'add_library', "add_compile_options(-openmp-)`r`nadd_library" ^| Out-File -encoding ASCII CMakeLists.txt > patch.ps1
echo (gc CMakeLists.txt) -replace ' SHARED', ' STATIC' ^| Out-File -encoding ASCII CMakeLists.txt >> patch.ps1
powershell .\patch.ps1
set CMAKE=cmake.exe -DCMAKE_VERBOSE_MAKEFILE=ON -DCMAKE_RULE_MESSAGES:BOOL=OFF
set CMAKE=%CMAKE% -DCMAKE_BUILD_TYPE=Release
%CMAKE% -G "NMake Makefiles" .
nmake -nologo -f Makefile clean
nmake -nologo -f Makefile
copy /Y /B *.h %INCLIB%
copy /Y /B *.lib %INCLIB%
endlocal

rem -> Build HarfBuzz
setlocal
set INCLUDE=%INCLUDE%;%INCLIB%
set LIB=%LIB%;%INCLIB%
cd /D %BUILD%\harfbuzz-2.6.1
set CMAKE=cmake.exe -DCMAKE_VERBOSE_MAKEFILE=ON -DCMAKE_RULE_MESSAGES:BOOL=OFF
set CMAKE=%CMAKE% -DHB_HAVE_FREETYPE:BOOL=ON -DCMAKE_BUILD_TYPE=Release
%CMAKE% -G "NMake Makefiles" .
nmake -nologo -f Makefile clean
nmake -nologo -f Makefile harfbuzz
copy /Y /B src\*.h %INCLIB%
copy /Y /B *.lib %INCLIB%
endlocal

rem -> Build FriBidi
setlocal
cd /D %BUILD%\fribidi-1.0.7
copy /Y /B C:\Pillow\winbuild\fribidi.cmake CMakeLists.txt
set CMAKE=cmake.exe -DCMAKE_VERBOSE_MAKEFILE=ON -DCMAKE_RULE_MESSAGES:BOOL=OFF
set CMAKE=%CMAKE% -DCMAKE_BUILD_TYPE=Release
%CMAKE% -G "NMake Makefiles" .
nmake -nologo -f Makefile clean
nmake -nologo -f Makefile fribidi
copy /Y /B lib\*.h %INCLIB%
copy /Y /B *.lib %INCLIB%
endlocal

rem -> Build Raqm
setlocal
set INCLUDE=%INCLUDE%;%INCLIB%
set LIB=%LIB%;%INCLIB%
cd /D %BUILD%\libraqm-0.7.0
copy /Y /B C:\Pillow\winbuild\raqm.cmake CMakeLists.txt
set CMAKE=cmake.exe -DCMAKE_VERBOSE_MAKEFILE=ON -DCMAKE_RULE_MESSAGES:BOOL=OFF
set CMAKE=%CMAKE% -DCMAKE_BUILD_TYPE=Release
%CMAKE% -G "NMake Makefiles" .
nmake -nologo -f Makefile clean
nmake -nologo -f Makefile libraqm
copy /Y /B src\*.h %INCLIB%
copy /Y /B libraqm.dll %INCLIB%
endlocal

rem Build Pillow
cd c:\pillow\
set PYTHON=C:\Python37\
set MPLSRC=C:\Pillow\
set LIB=%INCLIB%;%PYTHON%\tcl;%LIB%
set INCLUDE=%INCLIB%;C:\Pillow\depends\tcl86\include;%INCLUDE%
set MSSdk=1
set DISTUTILS_USE_SDK=1
set py_vcruntime_redist=true
c:\python37\python.exe setup.py build_ext install

rem Test Pillow
cd c:\pillow
path %INCLIB%;%PATH%
c:\python37\python.exe selftest.py --installed
c:\python37\python.exe -m pytest -vx -W always --cov PIL --cov Tests --cov-report term --cov-report xml Tests
