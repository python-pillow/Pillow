param ([string]$venv, [string]$pillow="C:\pillow")
$ErrorActionPreference  = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Set-PSDebug -Trace 1
if ("$venv" -like "*\cibw-run-*\pp*-win_amd64\*") {
    # unlike CPython, PyPy requires Visual C++ Redistributable to be installed
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri 'https://aka.ms/vs/15/release/vc_redist.x64.exe' -OutFile 'vc_redist.x64.exe'
    C:\vc_redist.x64.exe /install /quiet /norestart | Out-Null
}
$env:path += ";$pillow\winbuild\build\bin\"
& "$venv\Scripts\activate.ps1"
& reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\python.exe" /v "GlobalFlag" /t REG_SZ /d "0x02000000" /f
cd $pillow
& python -VV
if (!$?) { exit $LASTEXITCODE }
& python selftest.py
if (!$?) { exit $LASTEXITCODE }
& python -m pytest -vx Tests\check_wheel.py
if (!$?) { exit $LASTEXITCODE }
& python -m pytest -vx Tests
if (!$?) { exit $LASTEXITCODE }
