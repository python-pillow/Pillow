
setlocal
set MPLSRC=%~dp0\..
set INCLIB=%~dp0\depends
set BLDOPT=install
cd /D %MPLSRC%


setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.0\Bin\SetEnv.Cmd" /Release /x64 /vista
set DISTUTILS_USE_SDK=1
set LIB=%LIB%;%INCLIB%\msvcr90-x64
set INCLUDE=%INCLUDE%;%INCLIB%\msvcr90-x64;%INCLIB%\tcl85\include

setlocal
set LIB=%LIB%;C:\Python27x64\tcl
call c:\vp\27x64\Scripts\python.exe setup.py %BLDOPT%
endlocal

endlocal

endlocal
exit
