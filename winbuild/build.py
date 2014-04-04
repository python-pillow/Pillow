#/usr/bin/env python34

from config import *

def setup_vms():
    ret = []
    for py in pythons.keys():
        for arch in ('', 'x64'):
            ret.append("virtualenv -p c:/Python%s%s/python.exe --clear %s%s%s" %
                       (py, arch, VIRT_BASE, py, arch))
    return "\n".join(ret)

def header(op):
   return r"""
setlocal
set MPLSRC=%%~dp0\..
set INCLIB=%%~dp0\depends
set BLDOPT=%s
cd /D %%MPLSRC%%
""" % (op)   

def footer():
    return """endlocal
exit
"""

def build_one(py_ver, compiler):
    args = {}
    args.update(compiler)
    args['py_ver'] = py_ver
    return r"""
setlocal EnableDelayedExpansion
call "%%ProgramFiles%%\Microsoft SDKs\Windows\%(env_version)s\Bin\SetEnv.Cmd" /Release %(env_flags)s
set DISTUTILS_USE_SDK=1
set LIB=%%LIB%%;%%INCLIB%%\%(inc_dir)s
set INCLUDE=%%INCLUDE%%;%%INCLIB%%\%(inc_dir)s;%%INCLIB%%\tcl85\include

setlocal
set LIB=%%LIB%%;C:\Python%(py_ver)s\tcl
rd /q /s build
call c:\vp\%(py_ver)s\Scripts\python.exe setup.py %%BLDOPT%%
endlocal

endlocal
""" % args

script = [setup_vms(), header('install')]
for py_version, compiler_version in pythons.items():
    script.append(build_one(py_version, compilers[(compiler_version, 32)]))
    script.append(build_one("%sx64" %py_version, compilers[(compiler_version, 64)]))
script.append(footer())

with open('build_pillows.cmd', 'w') as f:
    f.write("\n".join(script))

