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

rem Get lcms2
py -3 fetch.py http://hivelocity.dl.sourceforge.net/project/lcms/lcms/2.6/lcms2-2.6.zip
py -3 unzip.py lcms2-2.6.zip %BUILD%
set LCMS=%BUILD%\lcms2-2.6
copy /Y /B lcms2-2.6.zip %INCLIB%

rem Build for VC 2008 64 bit
setlocal EnableDelayedExpansion
call "%ProgramFiles%\Microsoft SDKs\Windows\v7.0\Bin\SetEnv.Cmd" /Release /x64 /vista
set INCLIB=%INCLIB%\msvcr90-x64
mkdir %INCLIB%

rem Build lcms2
setlocal
py -3 %~dp0\fixproj.py %LCMS%\Projects\VC2008\lcms2.sln x64
py -3 %~dp0\fixproj.py %LCMS%\Projects\VC2008\lcms2.vcproj x64
rd /S /Q %LCMS%\objs
%MSBUILD% %LCMS%\Projects\VC2008\lcms2.sln /t:Clean;Build /p:Configuration="LIB Release";Platform=x64
xcopy /E /Q %LCMS%\include %INCLIB%
xcopy /E /Q %LCMS%\objs\win32\VC2008 %INCLIB%
copy /Y /B %LCMS%\objs\win32\VC2008\*.lib %INCLIB%\lcms2.lib
endlocal

endlocal
rem UNDONE --removeme!
exit

endlocal