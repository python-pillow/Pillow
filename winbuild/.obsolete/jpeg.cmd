setlocal
set MSBUILD=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe
set CMAKE="C:\Program Files (x86)\CMake 2.8\bin\cmake.exe"
set INCLIB=%~dp0\depends
set BUILD=%~dp0\build

mkdir %INCLIB%
mkdir %BUILD%

rem Get libjpeg
py -3 fetch.py http://www.ijg.org/files/jpegsr9a.zip
py -3 unzip.py jpegsr9a.zip %BUILD%
set LIBJPEG=%BUILD%\jpeg-9a
copy /Y /B jpegsr9a.zip %INCLIB%

rem Build for VC 2008 64 bit
setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.0\Bin\SetEnv.Cmd" /Release /x64 /vista
set INCLIB=%INCLIB%\msvcr90-x64
mkdir %INCLIB%


rem Build libjpeg
setlocal
cd /D %LIBJPEG%
nmake -f makefile.vc setup-vc6
nmake -f makefile.vc clean
nmake -f makefile.vc all
copy /Y /B *.dll %INCLIB%
copy /Y /B *.lib %INCLIB%
copy /Y /B j*.h %INCLIB%

endlocal

endlocal
rem UNDONE --removeme!
exit
