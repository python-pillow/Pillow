
setlocal
set MSBUILD=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe
set CMAKE="C:\Program Files (x86)\CMake 2.8\bin\cmake.exe"
set INCLIB=%~dp0\depends
set BUILD=%~dp0\build
set LCMS=%BUILD%\lcms2-2.6
set ZLIB=%BUILD%\zlib-1.2.8
set WEBP=%BUILD%\libwebp-0.4.0
set TIFF=%BUILD%\tiff-4.0.3
set OPENJPEG=%BUILD%\openjpeg-2.0.0
set JPEG=%BUILD%\jpeg-9a
set FREETYPE=%BUILD%\freetype-2.5.3


call "%ProgramFiles%\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.Cmd" /Release /x64 /vista
set INCLIB=%INCLIB%\msvcr10-x64
mkdir %INCLIB%


rem build openjpeg
setlocal
@echo on
cd /D %OPENJPEG%
%CMAKE% -DBUILD_THIRDPARTY:BOOL=ON -G "NMake Makefiles" .
nmake -f Makefile clean
nmake -f Makefile
copy /Y /B bin/* %INCLIB%
mkdir %INCLIB%/openjpeg-2.0
copy /Y /B src/lib/openjp2/openjpeg.h %INCLIB%/openjpeg-2.0
copy /Y /B src/lib/openjp2/opj_stdint.h %INCLIB%/openjpeg2.0
endlocal


endlocal

