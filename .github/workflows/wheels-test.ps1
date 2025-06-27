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
if (Test-Path $venv\Scripts\pypy.exe) {
  $python = "pypy.exe"
} else {
  $python = "python.exe"
}
& reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\python.exe" /v "GlobalFlag" /t REG_SZ /d "0x02000000" /f
if ("$venv" -like "*\cibw-run-*-win_amd64\*") {
  & $venv\Scripts\$python -m pip install numpy
}
cd $pillow
& $venv\Scripts\$python -VV
if (!$?) { exit $LASTEXITCODE }
& $venv\Scripts\$python selftest.py
if (!$?) { exit $LASTEXITCODE }
& $venv\Scripts\$python -m pytest -vv -x Tests\check_wheel.py
if (!$?) { exit $LASTEXITCODE }
& $venv\Scripts\$python -m pytest -vv -x Tests
if (!$?) { exit $LASTEXITCODE }
