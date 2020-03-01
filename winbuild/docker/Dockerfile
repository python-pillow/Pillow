# escape=`

# Use the latest Windows Server Core image with .NET Framework 4.8.
FROM mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2019

# Restore the default Windows shell for correct batch processing.
SHELL ["cmd", "/S", "/C"]

RUN powershell.exe -Command `
    $ErrorActionPreference = 'Stop'; `
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
    wget https://www.nasm.us/pub/nasm/releasebuilds/2.14.02/win64/nasm-2.14.02-win64.zip -OutFile c:\nasm.zip ; `
    Expand-Archive c:\nasm.zip -DestinationPath c:\

ARG PYTHON=3.7.3
ARG PYTHON_DIR=Python37
RUN powershell.exe -Command `
    $ErrorActionPreference = 'Stop'; `
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; `
    wget https://www.python.org/ftp/python/%PYTHON%/python-%PYTHON%.exe -OutFile c:\python-%PYTHON%.exe ; `
    Start-Process c:\python-%PYTHON%.exe -ArgumentList '/quiet TargetDir=c:\%PYTHON_DIR%\ InstallAllUsers=1 PrependPath=1' -Wait ; `
    Remove-Item c:\python-%PYTHON%.exe -Force ; `
    setx /M PYTHON C:\%PYTHON_DIR%

RUN C:\%PYTHON_DIR%\Scripts\pip.exe install pytest pytest-cov

# Default to PowerShell if no other command specified.
CMD ["powershell.exe", "-NoLogo", "-ExecutionPolicy", "Bypass"]

# Download the Build Tools bootstrapper.
ADD https://aka.ms/vs/16/release/vs_buildtools.exe C:\vs_buildtools.exe

# Install Build Tools excluding workloads and components with known issues.
RUN C:\vs_buildtools.exe --quiet --wait --norestart --nocache `
    --installPath C:\BuildTools `
    --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended `
 || IF "%ERRORLEVEL%"=="3010" EXIT 0

# Default to PowerShell if no other command specified.
CMD ["powershell.exe", "-NoLogo", "-ExecutionPolicy", "Bypass"]
