#/usr/bin/env python3

import subprocess
import shutil
import sys
import getopt
import os

from config import *


def setup_vms():
    ret = []
    for py in pythons.keys():
        for arch in ('', X64_EXT):
            ret.append("virtualenv -p c:/Python%s%s/python.exe --clear %s%s%s"
                       % (py, arch, VIRT_BASE, py, arch))
            ret.append("%s%s%s\Scripts\pip.exe install nose" %
                       (VIRT_BASE, py, arch))
            if py == '26':
                ret.append("%s%s%s\Scripts\pip.exe install unittest2" %
                           (VIRT_BASE, py, arch))
    return "\n".join(ret)


def run_script(params):
    (version, script) = params
    try:
        print("Running %s" % version)
        filename = 'build_pillow_%s.cmd' % version
        with open(filename, 'w') as f:
            f.write(script)

        command = ['powershell', "./%s" % filename]
        proc = subprocess.Popen(command,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                )
        (trace, stderr) = proc.communicate()
        status = proc.returncode
        print(stderr)
        print("Done with %s: %s" % (version, status))
        return (version, status, trace, stderr)
    except Exception as msg:
        print("Error with %s: %s" % (version, str(msg)))
        return (version, -1, "", str(msg))


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
    # UNDONE virtual envs if we're not running on appveyor
    args = {}
    args.update(compiler)
    if 'PYTHON' in os.environ:
        args['python_path'] = "%PYTHON%"
    else:
        args['python_path'] = "%s%s\\Scripts" % (VIRT_BASE, py_ver)
    args['py_ver'] = py_ver
    if '34' in py_ver:
        args['tcl_ver'] = '86'
    else:
        args['tcl_ver'] = '85'

    return r"""
setlocal EnableDelayedExpansion
call "%%ProgramFiles%%\Microsoft SDKs\Windows\%(env_version)s\Bin\SetEnv.Cmd" /Release %(env_flags)s
set DISTUTILS_USE_SDK=1
set LIB=%%LIB%%;%%INCLIB%%\%(inc_dir)s
set INCLUDE=%%INCLUDE%%;%%INCLIB%%\%(inc_dir)s;%%INCLIB%%\tcl%(tcl_ver)s\include

setlocal
set LIB=%%LIB%%;C:\Python%(py_ver)s\tcl
call %(python_path)s\python.exe setup.py %%BLDOPT%%
endlocal

endlocal
""" % args


def clean():
    try:
        shutil.rmtree('../build')
    except:
        # could already be removed
        pass
    run_script(('virtualenvs', setup_vms()))


def main(op):
    scripts = []

    for py_version, compiler_version in pythons.items():
        scripts.append((py_version,
                        "\n".join([header(op),
                                   build_one(py_version,
                                             compilers[(compiler_version,
                                                        32)]),
                                   footer()])))

        scripts.append(("%s%s" % (py_version, X64_EXT),
                        "\n".join([header(op),
                                   build_one("%sx64" % py_version,
                                             compilers[(compiler_version,
                                                        64)]),
                                   footer()])))

    results = map(run_script, scripts)

    for (version, status, trace, err) in results:
        print("Compiled %s: %s" % (version, status and 'ERR' or 'OK'))


def run_one(op):

    compiler = compiler_fromEnv()
    py_version = pyversion_fromEnv()

    run_script((py_version,
                "\n".join([header(op),
                           build_one(py_version, compiler),
                           footer()])
                ))


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], '', ['clean', 'dist'])
    opts = dict(opts)

    if '--clean' in opts:
        clean()

    op = 'install'
    if '--dist' in opts:
        op = "bdist_wininst --user-access-control=auto"

    if 'PYTHON' in os.environ:
        run_one(op)
    else:
        main(op)
