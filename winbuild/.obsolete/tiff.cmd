setlocal
set MSBUILD=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe
set CMAKE="C:\Program Files (x86)\CMake 2.8\bin\cmake.exe"
set INCLIB=%~dp0\depends
set BUILD=%~dp0\build

mkdir %INCLIB%
mkdir %BUILD%

rem get libtiff
py -3 fetch.py ftp://ftp.remotesensing.org/pub/libtiff/tiff-4.0.3.zip
py -3 unzip.py tiff-4.0.3.zip %BUILD%
set TIFF=%BUILD%\tiff-4.0.3
copy /Y /B tiff-4.0.3.zip %INCLIB%

rem Build for VC 2008 64 bit
setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.0\Bin\SetEnv.Cmd" /Release /x64 /vista
set INCLIB=%INCLIB%\msvcr90-x64
mkdir %INCLIB%


rem Build libtiff
setlocal
@echo on
rem do after building jpeg and zlib
copy %~dp0\nmake.opt %TIFF%

cd /D %TIFF%
nmake -f makefile.vc clean
nmake -f makefile.vc 
copy /Y /B libtiff\*.dll %INCLIB%
copy /Y /B libtiff\*.lib %INCLIB%
copy /Y /B libtiff\tiff*.h %INCLIB%
endlocal

endlocal
rem UNDONE --removeme!
exit
