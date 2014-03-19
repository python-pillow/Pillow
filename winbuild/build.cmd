rem @echo off
rem Build Pillow
rem for Python 2.6, 2.7, 3.2, and 3.3, 32 and 64 bit 
rem using Windows SDK 7.0 and 7.1

setlocal
rem Adjust the following if necessary
set MPLSRC=%~dp0\..
set INCLIB=%~dp0\depends
rem set BLDOPT=bdist_wininst --user-access-control=auto
set BLDOPT=build_ext
cd /D %MPLSRC%

rem Set TkAgg as default backend
echo [rc_options] > setup.cfg
echo backend = TkAgg >> setup.cfg
echo [gui_support] >> setup.cfg
echo tkagg = True >> setup.cfg

rem Using Windows SDK 7.0
rem "%ProgramFiles%\Microsoft SDKs\Windows\v7.0\Setup\WindowsSdkVer.exe" -q -version:v7.0

rem Build for 64 bit Python 2.6, 2.7, 3.2
setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.0\Bin\SetEnv.Cmd" /Release /x64 /vista
set DISTUTILS_USE_SDK=1
set LIB=%LIB%;%INCLIB%\msvcr90-x64
set INCLUDE=%INCLUDE%;%INCLIB%\msvcr90-x64;%INCLIB%\tcl85\include

setlocal
set LIB=%LIB%;C:\Python27x64\tcl
rd /q /s build
call C:\Python27x64\python.exe setup.py %BLDOPT%
endlocal

endlocal

exit

rem Using Windows SDK 7.1
rem "%ProgramFiles%\Microsoft SDKs\Windows\v7.1\Setup\WindowsSdkVer.exe" -q -version:v7.1

rem Build for 32 bit Python 3.3
setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.Cmd" /Release /x86 /xp
set DISTUTILS_USE_SDK=1
set LIB=%LIB%;%INCLIB%\msvcr100-x32
set INCLUDE=%INCLUDE%;%INCLIB%\msvcr100-x32;%INCLIB%\tcl85\include
setlocal
set LIB=%LIB%;C:\Python33\tcl
rd /q /s build
call C:\Python33\python.exe setup.py %BLDOPT%
endlocal
endlocal

rem Build for 64 bit Python 3.3
setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.Cmd" /Release /x64 /vista
set DISTUTILS_USE_SDK=1
set LIB=%LIB%;%INCLIB%\msvcr100-x64
set INCLUDE=%INCLUDE%;%INCLIB%\msvcr100-x64;%INCLIB%\tcl85\include
setlocal
set LIB=%LIB%;C:\Python33x64\tcl
rd /q /s build
call C:\Python33x64\python.exe setup.py %BLDOPT%
endlocal
endlocal

rd /q /s build
rem copy /Y /B dist\*.* %~dp0
endlocal