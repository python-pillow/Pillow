param ([string]$python)
$ErrorActionPreference  = 'Stop'
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
if ($python -like "pypy*") {
    echo "Downloading https://aka.ms/vs/15/release/vc_redist.x64.exe"
    Invoke-WebRequest -Uri 'https://aka.ms/vs/15/release/vc_redist.x64.exe' -OutFile 'vc_redist.x64.exe'
    C:\vc_redist.x64.exe /install /quiet /norestart | Out-Null
    $url = 'https://downloads.python.org/pypy/{0}-v7.3.13-win64.zip' -f $python
    echo "Downloading $url"
    Invoke-WebRequest -Uri $url -OutFile 'pypy.zip'
    tar -xf 'pypy.zip'
    mv pypy*-win64 C:\Python
} else {
    $url = 'https://www.python.org/ftp/python/{0}.0/python-{0}.0-amd64.exe' -f $python
    echo "Downloading $url"
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
}
$env:CI = "true"
$env:path += ";C:\Python\;C:\pillow\winbuild\build\bin\"
cd C:\pillow
& python -VV
& python -m ensurepip
& python -m pip install -U pip
& python -m pip install pytest pytest-timeout
& python -m pip install "$(Get-ChildItem *.whl -Name)"
& python -m pytest -vx Tests\check_wheel.py Tests
if ((Test-Path -LiteralPath variable:\LASTEXITCODE)) { exit $LASTEXITCODE }
