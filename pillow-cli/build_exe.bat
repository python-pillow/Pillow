@echo off
echo Building Pillow CLI executable...
echo.

REM Check if PyInstaller is available
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller -
    if errorlevel 1 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "pillow-cli.exe" del "pillow-cli.exe"

echo.
echo Building executable using spec file...
pyinstaller pillow-cli.spec --clean --noconfirm
if errorlevel 1 (
    echo Build failed. Check the output above for errors.
    pause
    exit /b 1
)

REM Check if build was successful
if exist "dist\pillow-cli.exe" (
    echo.
    echo SUCCESS: Executable created at dist\pillow-cli.exe
    echo.
    echo Testing executable...
    dist\pillow-cli.exe --help
    echo.
    echo Build complete!
) else (
    echo.
    echo ERROR: Build failed. Check the output above for errors.
)

pause