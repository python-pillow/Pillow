#!/usr/bin/env python3

import getopt
import os
import shutil
import subprocess
import sys

from config import (
    VIRT_BASE,
    X64_EXT,
    bit_from_env,
    compiler_from_env,
    compilers,
    pythons,
    pyversion_from_env,
)


def setup_vms():
    ret = []
    for py in pythons:
        for arch in ("", X64_EXT):
            ret.append(
                "virtualenv -p c:/Python%s%s/python.exe --clear %s%s%s"
                % (py, arch, VIRT_BASE, py, arch)
            )
            ret.append(
                r"%s%s%s\Scripts\pip.exe install pytest pytest-cov"
                % (VIRT_BASE, py, arch)
            )
    return "\n".join(ret)


def run_script(params):
    (version, script) = params
    try:
        print("Running %s" % version)
        filename = "build_pillow_%s.cmd" % version
        with open(filename, "w") as f:
            f.write(script)

        command = ["powershell", "./%s" % filename]
        proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        (trace, stderr) = proc.communicate()
        status = proc.returncode
        print("-- stderr --")
        print(stderr.decode())
        print("-- stdout --")
        print(trace.decode())
        print("Done with {}: {}".format(version, status))
        return (version, status, trace, stderr)
    except Exception as msg:
        print("Error with {}: {}".format(version, str(msg)))
        return (version, -1, "", str(msg))


def header(op):
    return r"""
setlocal
set MPLSRC=%%~dp0\..
set INCLIB=%%~dp0\depends
set BLDOPT=%s
cd /D %%MPLSRC%%
""" % (
        op
    )


def footer():
    return """endlocal
exit
"""


def vc_setup(compiler, bit):
    script = ""
    if compiler["vc_version"] == "2015":
        arch = "x86" if bit == 32 else "x86_amd64"
        script = (
            r"""
call "C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat" %s
echo on"""
            % arch
        )
    return script


def build_one(py_ver, compiler, bit):
    # UNDONE virtual envs if we're not running on AppVeyor
    args = {}
    args.update(compiler)
    if "PYTHON" in os.environ:
        args["python_path"] = "%PYTHON%"
    else:
        args["python_path"] = "{}{}\\Scripts".format(VIRT_BASE, py_ver)

    args["executable"] = "python.exe"
    if "EXECUTABLE" in os.environ:
        args["executable"] = "%EXECUTABLE%"

    args["py_ver"] = py_ver
    args["tcl_ver"] = "86"

    if compiler["vc_version"] == "2015":
        args["imaging_libs"] = " build_ext --add-imaging-libs=msvcrt"
    else:
        args["imaging_libs"] = ""

    args["vc_setup"] = vc_setup(compiler, bit)

    script = r"""
setlocal EnableDelayedExpansion
call "%%ProgramFiles%%\Microsoft SDKs\Windows\%(env_version)s\Bin\SetEnv.Cmd" /Release %(env_flags)s
set DISTUTILS_USE_SDK=1
set LIB=%%LIB%%;%%INCLIB%%\%(inc_dir)s
set INCLUDE=%%INCLUDE%%;%%INCLIB%%\%(inc_dir)s;%%INCLIB%%\tcl%(tcl_ver)s\include

setlocal
set LIB=%%LIB%%;C:\Python%(py_ver)s\tcl%(vc_setup)s
call %(python_path)s\%(executable)s setup.py %(imaging_libs)s %%BLDOPT%%
call %(python_path)s\%(executable)s -c "from PIL import _webp;import os, shutil;shutil.copy(r'%%INCLIB%%\freetype.dll', os.path.dirname(_webp.__file__));"
endlocal

endlocal
"""  # noqa: E501
    return script % args


def clean():
    try:
        shutil.rmtree("../build")
    except Exception:
        # could already be removed
        pass
    run_script(("virtualenvs", setup_vms()))


def main(op):
    scripts = []

    for py_version, py_info in pythons.items():
        py_compilers = compilers[py_info["compiler"]][py_info["vc"]]
        scripts.append(
            (
                py_version,
                "\n".join(
                    [header(op), build_one(py_version, py_compilers[32], 32), footer()]
                ),
            )
        )

        scripts.append(
            (
                "{}{}".format(py_version, X64_EXT),
                "\n".join(
                    [
                        header(op),
                        build_one("%sx64" % py_version, py_compilers[64], 64),
                        footer(),
                    ]
                ),
            )
        )

    results = map(run_script, scripts)

    for (version, status, trace, err) in results:
        print("Compiled {}: {}".format(version, status and "ERR" or "OK"))


def run_one(op):

    compiler = compiler_from_env()
    py_version = pyversion_from_env()
    bit = bit_from_env()

    run_script(
        (
            py_version,
            "\n".join([header(op), build_one(py_version, compiler, bit), footer()]),
        )
    )


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "", ["clean", "wheel"])
    opts = dict(opts)

    if "--clean" in opts:
        clean()

    op = "install"
    if "--wheel" in opts:
        op = "bdist_wheel"

    if "PYTHON" in os.environ:
        run_one(op)
    else:
        main(op)
