param ([string]$python,[string]$arch)
$ErrorActionPreference  = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$suffix = if ($arch -eq "x64") {"-amd64"} else {""}
$url = 'https://www.python.org/ftp/python/{0}/python-{0}{1}.exe' -f ($python, $suffix)
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $url -OutFile 'setup.exe'
Start-Process setup.exe -Wait -NoNewWindow -PassThru -ArgumentList @(
        '/quiet',
        'InstallAllUsers=0',
        'TargetDir=C:\Python',
        'PrependPath=1',
        'Shortcuts=0',
        'Include_doc=0',
        'Include_pip=1',
        'Include_test=0'
    )
$env:CI = "true"
$env:path += ";C:\Python\;C:\pillow\winbuild\build\bin\"
cd C:\pillow
& python -VV
& python -m ensurepip
& python -m pip install pytest pytest-timeout
& python -m pip install "dist\$(Get-ChildItem dist\*.whl -Name)"
& python -m pytest -vx Tests\check_wheel.py Tests
if ((Test-Path -LiteralPath variable:\LASTEXITCODE)) { exit $LASTEXITCODE }
