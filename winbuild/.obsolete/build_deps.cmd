setlocal
set MSBUILD=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe
set CMAKE="C:\Program Files (x86)\CMake 2.8\bin\cmake.exe"
set INCLIB=%~dp0\depends
set BUILD=%~dp0\build
set OPENJPEG=%BUILD%\openjpeg-2.0.0
set TIFF=%BUILD%\tiff-4.0.3
set LCMS=%BUILD%\lcms2-2.6
set ZLIB=%BUILD%\zlib-1.2.8
set WEBP=%BUILD%\libwebp-0.4.0
set FREETYPE=%BUILD%\freetype-2.5.3
set JPEG=%BUILD%\jpeg-9a

mkdir %INCLIB%\tcl85\include\X11
copy /Y /B %BUILD%\tcl8.5.13\generic\*.h %INCLIB%\tcl85\include\
copy /Y /B %BUILD%\tk8.5.13\generic\*.h %INCLIB%\tcl85\include\
copy /Y /B %BUILD%\tk8.5.13\xlib\X11\* %INCLIB%\tcl85\include\X11\

setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.Cmd" /Release /x64 /vista
set INCLIB=%INCLIB%\msvcr10-x64
mkdir %INCLIB%


rem build openjpeg
setlocal
@echo on
cd /D %OPENJPEG%
nmake -f Makefile clean
%CMAKE% -DBUILD_THIRDPARTY:BOOL=ON -G "NMake Makefiles" .
nmake -f Makefile
copy /Y /B bin/* %INCLIB%
mkdir %INCLIB%/openjpeg-2.0
copy /Y /B src/lib/openjp2/openjpeg.h %INCLIB%/openjpeg-2.0
copy /Y /B src/lib/openjp2/opj_stdint.h %INCLIB%/openjpeg-2.0
endlocal


endlocal

setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.0\Bin\SetEnv.Cmd" /Release /x86 /xp
set INCLIB=%INCLIB%\msvcr90-x32
mkdir %INCLIB%


rem build openjpeg
setlocal
@echo on
cd /D %OPENJPEG%
nmake -f Makefile clean
%CMAKE% -DBUILD_THIRDPARTY:BOOL=ON -G "NMake Makefiles" .
nmake -f Makefile
copy /Y /B bin/* %INCLIB%
mkdir %INCLIB%/openjpeg-2.0
copy /Y /B src/lib/openjp2/openjpeg.h %INCLIB%/openjpeg-2.0
copy /Y /B src/lib/openjp2/opj_stdint.h %INCLIB%/openjpeg-2.0
endlocal


endlocal

setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.0\Bin\SetEnv.Cmd" /Release /x64 /vista
set INCLIB=%INCLIB%\msvcr90-x64
mkdir %INCLIB%


rem build openjpeg
setlocal
@echo on
cd /D %OPENJPEG%
nmake -f Makefile clean
%CMAKE% -DBUILD_THIRDPARTY:BOOL=ON -G "NMake Makefiles" .
nmake -f Makefile
copy /Y /B bin/* %INCLIB%
mkdir %INCLIB%/openjpeg-2.0
copy /Y /B src/lib/openjp2/openjpeg.h %INCLIB%/openjpeg-2.0
copy /Y /B src/lib/openjp2/opj_stdint.h %INCLIB%/openjpeg-2.0
endlocal


endlocal

setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.Cmd" /Release /x86 /xp
set INCLIB=%INCLIB%\msvcr10-x32
mkdir %INCLIB%


rem build openjpeg
setlocal
@echo on
cd /D %OPENJPEG%
nmake -f Makefile clean
%CMAKE% -DBUILD_THIRDPARTY:BOOL=ON -G "NMake Makefiles" .
nmake -f Makefile
copy /Y /B bin/* %INCLIB%
mkdir %INCLIB%/openjpeg-2.0
copy /Y /B src/lib/openjp2/openjpeg.h %INCLIB%/openjpeg-2.0
copy /Y /B src/lib/openjp2/opj_stdint.h %INCLIB%/openjpeg-2.0
endlocal


endlocal
