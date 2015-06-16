
setlocal
set MPLSRC=%~dp0\..
set INCLIB=%~dp0\depends
set BLDOPT=install
cd /D %MPLSRC%


setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.Cmd" /Release /x86 /xp
set DISTUTILS_USE_SDK=1
set LIB=%LIB%;%INCLIB%\msvcr10-x32
set INCLUDE=%INCLUDE%;%INCLIB%\msvcr10-x32;%INCLIB%\tcl85\include

setlocal
set LIB=%LIB%;C:\Python34\tcl
call c:\vp\34\Scripts\python.exe setup.py %BLDOPT%
endlocal

endlocal

endlocal
exit
