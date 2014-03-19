@echo off
rem Build Matplotlib Dependencies

setlocal
set MSBUILD=C:\Windows\Microsoft.NET\Framework64\v4.0.30319\MSBuild.exe
set CMAKE="C:\Program Files (x86)\CMake 2.8\bin\cmake.exe"
set INCLIB=%~dp0\depends
set BUILD=%~dp0\build

echo "Removing Directories" 
rd /S /Q %INCLIB%
rd /S /Q %BUILD%

mkdir %INCLIB%
mkdir %BUILD%

rem Get freetype
py -3 fetch.py http://download.savannah.gnu.org/releases/freetype/ft253.zip
py -3 unzip.py ft253.zip %BUILD%
set FREETYPE=%BUILD%\freetype-2.5.3
copy /Y /B ft253.zip %INCLIB%

rem Get zlib
py -3 fetch.py http://zlib.net/zlib128.zip
py -3 unzip.py zlib128.zip %BUILD%
set ZLIB=%BUILD%\zlib-1.2.8
copy /Y /B zlib128.zip %INCLIB%

rem Get tcl/tk
py -3 fetch.py http://hivelocity.dl.sourceforge.net/project/tcl/Tcl/8.5.13/tcl8513-src.zip
py -3 unzip.py tcl8513-src.zip %BUILD%
copy /Y /B tcl8513-src.zip %INCLIB%
py -3 fetch.py http://hivelocity.dl.sourceforge.net/project/tcl/Tcl/8.5.13/tk8513-src.zip
py -3 unzip.py tk8513-src.zip %BUILD%
copy /Y /B tk8513-src.zip %INCLIB%

mkdir %INCLIB%\tcl85\include\X11
copy /Y /B %BUILD%\tcl8.5.13\generic\*.h %INCLIB%\tcl85\include\
copy /Y /B %BUILD%\tk8.5.13\generic\*.h %INCLIB%\tcl85\include\
copy /Y /B %BUILD%\tk8.5.13\xlib\X11\* %INCLIB%\tcl85\include\X11\

rem Build for VC 2008 64 bit
setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.0\Bin\SetEnv.Cmd" /Release /x64 /vista
set INCLIB=%INCLIB%\msvcr90-x64
mkdir %INCLIB%

rem Build zlib
setlocal
cd /D %ZLIB%
nmake -f win32\Makefile.msc clean
nmake -f win32\Makefile.msc
copy /Y /B *.dll %INCLIB%
copy /Y /B *.lib %INCLIB%
copy /Y /B zlib.lib %INCLIB%\z.lib
copy /Y /B zlib.h %INCLIB%
copy /Y /B zconf.h %INCLIB%
endlocal

rem Build freetype
setlocal
py -3 %~dp0\fixproj.py %FREETYPE%\builds\windows\vc2008\freetype.sln x64
py -3 %~dp0\fixproj.py %FREETYPE%\builds\windows\vc2008\freetype.vcproj x64
rd /S /Q %FREETYPE%\objs
%MSBUILD% %FREETYPE%\builds\windows\vc2008\freetype.sln /t:Clean;Build /p:Configuration="LIB Release";Platform=x64
xcopy /E /Q %FREETYPE%\include %INCLIB%
xcopy /E /Q %FREETYPE%\objs\win32\vc2008 %INCLIB%
copy /Y /B %FREETYPE%\objs\win32\vc2008\*.lib %INCLIB%\freetype.lib
endlocal

endlocal

rem Build for VC 2008 32 bit
setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.0\Bin\SetEnv.Cmd" /Release /x86 /xp
set INCLIB=%INCLIB%\msvcr90-x32
mkdir %INCLIB%

rem Build zlib
setlocal
cd /D %ZLIB%
nmake -f win32\Makefile.msc clean
nmake -f win32\Makefile.msc
copy /Y /B *.dll %INCLIB%
copy /Y /B *.lib %INCLIB%
copy /Y /B zlib.lib %INCLIB%\z.lib
copy /Y /B zlib.h %INCLIB%
copy /Y /B zconf.h %INCLIB%
endlocal

rem Build freetype
setlocal
%~dp0\fixproj.py %FREETYPE%\builds\windows\vc2008\freetype.sln Win32
%~dp0\fixproj.py %FREETYPE%\builds\windows\vc2008\freetype.vcproj Win32
rd /S /Q %FREETYPE%\objs
%MSBUILD% %FREETYPE%\builds\windows\vc2008\freetype.sln /t:Clean;Build /p:Configuration="LIB Release";Platform=Win32
xcopy /E /Q %FREETYPE%\include %INCLIB%
xcopy /E /Q %FREETYPE%\objs\win32\vc2008 %INCLIB%
copy /Y /B %FREETYPE%\objs\win32\vc2008\*.lib %INCLIB%\freetype.lib
endlocal

endlocal

rem Build for VC 2010 64 bit
setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.Cmd" /Release /x64 /vista
set INCLIB=%INCLIB%\msvcr100-x64
mkdir %INCLIB%

rem Build zlib
setlocal
cd /D %ZLIB%
nmake -f win32\Makefile.msc clean
nmake -f win32\Makefile.msc
copy /Y /B *.dll %INCLIB%
copy /Y /B *.lib %INCLIB%
copy /Y /B zlib.lib %INCLIB%\z.lib
copy /Y /B zlib.h %INCLIB%
copy /Y /B zconf.h %INCLIB%
endlocal

rem Build freetype
setlocal
py -3 %~dp0\fixproj.py %FREETYPE%\builds\windows\vc2010\freetype.sln x64
py -3 %~dp0\fixproj.py %FREETYPE%\builds\windows\vc2010\freetype.vcxproj x64
rd /S /Q %FREETYPE%\objs
%MSBUILD% %FREETYPE%\builds\windows\vc2010\freetype.sln /t:Clean;Build /p:Configuration="Release";Platform=x64
xcopy /E /Q %FREETYPE%\include %INCLIB%
xcopy /E /Q %FREETYPE%\objs\win32\vc2010 %INCLIB%
copy /Y /B %FREETYPE%\objs\win32\vc2010\*.lib %INCLIB%\freetype.lib
endlocal

endlocal

rem Build for VC 2010 32 bit
setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.1\Bin\SetEnv.Cmd" /Release /x86 /xp
set INCLIB=%INCLIB%\msvcr100-x32
mkdir %INCLIB%

rem Build zlib
setlocal
cd /D %ZLIB%
nmake -f win32\Makefile.msc clean
nmake -f win32\Makefile.msc
copy /Y /B *.dll %INCLIB%
copy /Y /B *.lib %INCLIB%
copy /Y /B zlib.lib %INCLIB%\z.lib
copy /Y /B zlib.h %INCLIB%
copy /Y /B zconf.h %INCLIB%
endlocal

rem Build freetype
setlocal
%~dp0\fixproj.py %FREETYPE%\builds\windows\vc2010\freetype.sln Win32
%~dp0\fixproj.py %FREETYPE%\builds\windows\vc2010\freetype.vcxproj Win32
rd /S /Q %FREETYPE%\objs
%MSBUILD% %FREETYPE%\builds\windows\vc2010\freetype.sln /t:Clean;Build /p:Configuration="Release";Platform=Win32
xcopy /E /Q %FREETYPE%\include %INCLIB%
xcopy /E /Q %FREETYPE%\objs\win32\vc2010 %INCLIB%
copy /Y /B %FREETYPE%\objs\win32\vc2010\*.lib %INCLIB%\freetype.lib
endlocal

endlocal

endlocal