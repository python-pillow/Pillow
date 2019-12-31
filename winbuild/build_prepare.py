import os
import shutil
import subprocess
import sys
import winreg
from itertools import count

from commands import *

SF_MIRROR = "http://iweb.dl.sourceforge.net"

# use PYTHON to select architecture
architectures = {
    "x86": {"vcvars_arch": "x86", "msbuild_arch": "Win32"},
    "x64": {"vcvars_arch": "x86_amd64", "msbuild_arch": "x64"},
}

# use PYTHON + architecture to select config
pythons = {
    "pypy3.6": {"config-x86": "3.5"},
    "3.5": {"config-x86": "3.5", "config-x64": "3.5"},
    "3.6": {"config-x86": "3.6", "config-x64": "3.6"},
    "3.7": {"config-x86": "3.6", "config-x64": "3.6"},
}

# select preferred compiler
configs = {
    "3.5": {
        "vcvars_ver": "14.0",
        "vs_ver": "2015",
    },
    "3.6": {
        "vs_ver": "2017",
    },
}

# selected dependencies
deps_list = [
    "libjpeg-turbo-2.0.3",
    "zlib-1.2.11",
    "tiff-4.0.10",
    "libwebp-1.0.3",
    "freetype-2.10.1",
    "lcms2-2.9",
    "openjpeg-2.3.1",
]

header = [
    cmd_set("BUILD", "{build_dir}"),
    cmd_set("INCLUDE", "{inc_dir}"),
    cmd_set("INCLIB", "{lib_dir}"),
    cmd_set("LIB", "{lib_dir}"),
    cmd_append("PATH", "{bin_dir}"),
    "@echo on",
]

# dependencies
deps = {
    "libjpeg-turbo-2.0.3": {
        "name": "libjpeg",
        "url": SF_MIRROR + "/project/libjpeg-turbo/2.0.3/libjpeg-turbo-2.0.3.tar.gz",
        "filename": "libjpeg-turbo-2.0.3.tar.gz",
        "build": [
            cmd_cmake([
                "-DENABLE_SHARED:BOOL=FALSE",
                "-DWITH_JPEG8:BOOL=TRUE",
                "-DWITH_CRT_DLL:BOOL=TRUE",
            ]),
            cmd_nmake(target="clean"),
            cmd_nmake(target="jpeg-static"),
            cmd_copy("jpeg-static.lib", "libjpeg.lib"),
            cmd_nmake(target="cjpeg-static"),
            cmd_copy("cjpeg-static.exe", "cjpeg.exe"),
            cmd_nmake(target="djpeg-static"),
            cmd_copy("djpeg-static.exe", "djpeg.exe"),
        ],
        "headers": ["j*.h"],
        "libs": ["libjpeg.lib"],
        "bins": ["cjpeg.exe", "djpeg.exe"],
    },
    "zlib-1.2.11": {
        "name": "zlib",
        "url": "http://zlib.net/zlib1211.zip",
        "filename": "zlib1211.zip",
        "build": [
            cmd_nmake(r"win32\Makefile.msc", "clean"),
            cmd_nmake(r"win32\Makefile.msc", "zlib.lib"),
            cmd_copy("zlib.lib", "z.lib"),
        ],
        "headers": [r"z*.h"],
        "libs": [r"*.lib"],
    },
    "tiff-4.0.10": {
        "name": "libtiff",
        # FIXME FTP timeout
        "url": "ftp://download.osgeo.org/libtiff/tiff-4.0.10.tar.gz",
        "filename": "tiff-4.0.10.tar.gz",
        "build": [
            cmd_copy(r"{script_dir}\tiff.opt", "nmake.opt"),
            cmd_nmake("makefile.vc", "clean"),
            cmd_nmake("makefile.vc", "lib", "RuntimeLibrary=-MT"),
        ],
        "headers": [r"libtiff\tiff*.h"],
        "libs": [r"libtiff\*.lib"],
        # "bins": [r"libtiff\*.dll"],
    },
    "libwebp-1.0.3": {
        "name": "libwebp",
        "url": "http://downloads.webmproject.org/releases/webp/libwebp-1.0.3.tar.gz",  # noqa: E501
        "filename": "libwebp-1.0.3.tar.gz",
        "build": [
            cmd_rmdir(r"output\release-static"),  # clean
            cmd_nmake(
                "Makefile.vc",
                "all",
                ["CFG=release-static", "OBJDIR=output", "ARCH={architecture}"]
            ),
            cmd_mkdir(r"{inc_dir}\webp"),
            cmd_copy(r"src\webp\*.h", r"{inc_dir}\webp"),
        ],
        "libs": [r"output\release-static\{architecture}\lib\*.lib"],
    },
    "freetype-2.10.1": {
        "name": "freetype",
        "url": "https://download.savannah.gnu.org/releases/freetype/freetype-2.10.1.tar.gz",  # noqa: E501
        "filename": "freetype-2.10.1.tar.gz",
        "build": [
            cmd_rmdir("objs"),
            # freetype setting is /MD for .dll and /MT for .lib, we need /MD
            cmd_patch_replace(
                r"builds\windows\vc2010\freetype.vcxproj",
                "MultiThreaded<",
                "MultiThreadedDLL<"
            ),
            cmd_msbuild(r"builds\windows\vc2010\freetype.sln", "Release Static", "Clean"),  # TODO failing on GHA  # noqa: E501
            cmd_msbuild(r"builds\windows\vc2010\freetype.sln", "Release Static", "Build"),
            cmd_xcopy("include", "{inc_dir}"),
        ],
        "libs": [r"objs\{msbuild_arch}\Release Static\freetype.lib"],
        # "bins": [r"objs\{msbuild_arch}\Release\freetype.dll"],
    },
    "lcms2-2.9": {
        "name": "lcms2",
        "url": SF_MIRROR + "/project/lcms/lcms/2.8/lcms2-2.9.tar.gz",
        "filename": "lcms2-2.9.tar.gz",
        "build": [
            cmd_rmdir("Lib"),
            cmd_rmdir(r"Projects\VC{vs_ver}\Release"),
            # lcms2-2.8\VC2015 setting is /MD for x86 and /MT for x64, we need /MD always
            cmd_patch_replace(
                r"Projects\VC2017\lcms2.sln", "MultiThreaded<", "MultiThreadedDLL<"
            ),
            cmd_msbuild(r"Projects\VC{vs_ver}\lcms2.sln", "Release", "Clean"),
            cmd_msbuild(r"Projects\VC{vs_ver}\lcms2.sln", "Release", "lcms2_static"),
            cmd_xcopy("include", "{inc_dir}"),
        ],
        "libs": [r"Lib\MS\*.lib"],
    },
    "openjpeg-2.3.1": {
        "name": "openjpeg",
        "url": "https://github.com/uclouvain/openjpeg/archive/v2.3.1.tar.gz",
        "filename": "openjpeg-2.3.1.tar.gz",
        "build": [
            cmd_cmake(("-DBUILD_THIRDPARTY:BOOL=OFF", "-DBUILD_SHARED_LIBS:BOOL=OFF")),
            cmd_nmake(target="clean"),
            cmd_nmake(),
            cmd_mkdir(r"{inc_dir}\openjpeg-2.3.1"),
            cmd_copy(r"src\lib\openjp2\*.h", r"{inc_dir}\openjpeg-2.3.1"),
        ],
        "libs": [r"bin\*.lib"],
    },
}


# based on distutils._msvccompiler from CPython 3.7.4
def find_vs2017(config):
    root = os.environ.get("ProgramFiles(x86)") or os.environ.get("ProgramFiles")
    if not root:
        print("Program Files not found")
        return None

    try:
        vspath = subprocess.check_output([
            os.path.join(root, "Microsoft Visual Studio", "Installer", "vswhere.exe"),
            "-latest",
            "-prerelease",
            "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
            "-property", "installationPath",
            "-products", "*",
        ]).decode(encoding="mbcs").strip()
    except (subprocess.CalledProcessError, OSError, UnicodeDecodeError):
        print("vswhere not found")
        return None

    if not os.path.isdir(os.path.join(vspath, "VC", "Auxiliary", "Build")):
        print("Visual Studio seems to be missing C compiler")
        return None

    vs = {
        "header": [],
        # nmake selected by vcvarsall
        "nmake": "nmake.exe",
        "vs_dir": vspath,
    }

    # vs2017
    msbuild = os.path.join(vspath, "MSBuild", "15.0", "Bin", "MSBuild.exe")
    if os.path.isfile(msbuild):
        default_platform_toolset = "v140"
        vs["msbuild"] = '"{}"'.format(msbuild)
    else:
        # vs2019
        msbuild = os.path.join(vspath, "MSBuild", "Current", "Bin", "MSBuild.exe")
        if os.path.isfile(msbuild):
            default_platform_toolset = "v142"
            vs["msbuild"] = '"{}"'.format(msbuild)
        else:
            print("Visual Studio MSBuild not found")
            return None
    # vs["header"].append(cmd_set("DefaultPlatformToolset", default_platform_toolset))

    vcvarsall = os.path.join(vspath, "VC", "Auxiliary", "Build", "vcvarsall.bat")
    if not os.path.isfile(vcvarsall):
        print("Visual Studio vcvarsall not found")
        return None
    vcvars_ver = "-vcvars_ver={}".format(config["vcvars_ver"]) if "vcvars_ver" in config else ""
    vs["header"].append('call "{}" {{vcvars_arch}} {}'.format(vcvarsall, vcvars_ver))

    return vs


def find_sdk71a():
    try:
        key = winreg.OpenKeyEx(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Microsoft SDKs\Windows\v7.1A",
            access=winreg.KEY_READ | winreg.KEY_WOW64_32KEY,
        )
    except OSError:
        return None
    with key:
        for i in count():
            try:
                v_name, v_value, v_type = winreg.EnumValue(key, i)
            except OSError:
                return None
            if v_name == "InstallationFolder" and v_type == winreg.REG_SZ:
                sdk_dir = v_value
                break
        else:
            return None

    if not os.path.isdir(sdk_dir):
        return None

    sdk = {
        "header": [
            # for win32.mak
            cmd_append("INCLUDE", os.path.join(sdk_dir, "Include")),
            # for ghostscript
            cmd_set("RCOMP", '"{}"'.format(os.path.join(sdk_dir, "Bin", "RC.EXE"))),
        ],
        "sdk_dir": sdk_dir,
    }

    return sdk


def match(values, target):
    for key, value in values.items():
        if key in target:
            return {"name": key, **value}


def extract_dep(url, filename):
    import urllib.request
    import tarfile
    import zipfile

    file = os.path.join(depends_dir, filename)
    if not os.path.exists(file):
        ex = None
        for i in range(3):
            try:
                print("Fetching %s (attempt %d)..." % (url, i + 1))
                content = urllib.request.urlopen(url).read()
                with open(file, "wb") as f:
                    f.write(content)
                break
            except urllib.error.URLError as e:
                ex = e
        else:
            raise RuntimeError(ex)
    if filename.endswith(".zip"):
        with zipfile.ZipFile(file) as zf:
            zf.extractall(build_dir)
    elif filename.endswith(".tar.gz") or filename.endswith(".tgz"):
        with tarfile.open(file, "r:gz") as tgz:
            tgz.extractall(build_dir)
    else:
        raise RuntimeError("Unknown archive type: " + filename)


def write_script(name, lines):
    name = os.path.join(script_dir, name)
    lines = [line.format(**prefs) for line in lines]
    print("Writing " + name)
    with open(name, "w") as f:
        f.write("\n\r".join(lines))
    for line in lines:
        print("    " + line)


def get_footer(dep):
    lines = []
    for out in dep.get("headers", []):
        lines.append(cmd_copy(out, "{inc_dir}"))
    for out in dep.get("libs", []):
        lines.append(cmd_copy(out, "{lib_dir}"))
    for out in dep.get("bins", []):
        lines.append(cmd_copy(out, "{bin_dir}"))
    return lines


def build_dep(name):
    dep = deps[name]
    file = "build_dep_{name}.cmd".format(name=dep["name"])

    extract_dep(dep["url"], dep["filename"])

    lines = [
        "echo Building {name} ({dir})...".format(name=dep["name"], dir=name),
        "cd /D %s" % os.path.join(build_dir, name),
        *prefs["header"],
        *dep.get("build", []),
        *get_footer(dep),
    ]

    write_script(file, lines)
    return file


def build_dep_all():
    lines = [
        "$ErrorActionPreference = 'stop'",
        "cd {script_dir}",
    ]
    for dep_name in deps_list:
        lines.append('cmd.exe /c "%s"' % build_dep(dep_name))
    write_script("build_dep_all.ps1", lines)


def build_pillow(wheel=False):
    lines = []
    if path_dir is not None and not wheel:
        lines.append(cmd_xcopy("{bin_dir}", path_dir))
    lines.extend(prefs["header"])
    lines.extend(
        [
            cmd_cd("{pillow_dir}"),
            cmd_append("LIB", r"{python_dir}\tcl"),
            r'"{{python_dir}}\python.exe" setup.py build_ext %*',
            # r"""%PYTHON%\python.exe selftest.py --installed""",
        ]
    )

    write_script("build_pillow.cmd", lines)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    depends_dir = os.path.join(script_dir, "depends")
    python_dir = os.environ.get("PYTHON", os.path.dirname(os.path.realpath(sys.executable)))

    # copy binaries to this directory
    path_dir = os.environ.get("PILLOW_BIN")

    # use PYTHON to select architecture
    arch_prefs = match(architectures, python_dir)
    if arch_prefs is None:
        architecture = "x86"
        print("WARN: Could not determine architecture, guessing " + architecture)
        arch_prefs = architectures[architecture]
    else:
        architecture = arch_prefs["name"]

    # use PYTHON to select python version
    python_prefs = match(pythons, python_dir)
    if python_prefs is None:
        raise KeyError("Failed to determine Python version from PYTHON: " + python_dir)

    print("Target: Python {python_version} {architecture} at: {python_dir}".format(python_version=python_prefs["name"], architecture=architecture, python_dir=python_dir))

    # use python version + architecture to select build config
    config_name = python_prefs["config-" + architecture]
    config = configs[config_name]

    vs2017 = find_vs2017(config)
    if vs2017 is None:
        raise RuntimeError("Visual Studio 2017 not found")

    print("Found Visual Studio at: {}".format(vs2017["vs_dir"]))

    sdk71a = find_sdk71a()
    if sdk71a is None:
        raise RuntimeError("Windows SDK v7.1A not found")

    print("Found Windows SDK 7.1A at: {}".format(sdk71a["sdk_dir"]))

    build_dir = os.path.join(script_dir, "build", config_name, architecture)
    lib_dir = os.path.join(build_dir, "lib")
    inc_dir = os.path.join(build_dir, "inc")
    bin_dir = os.path.join(build_dir, "bin")

    # for path in [lib_dir, inc_dir, bin_dir]:
    #     shutil.rmtree(path)
    for path in [depends_dir, build_dir, lib_dir, inc_dir, bin_dir]:
        os.makedirs(path, exist_ok=True)

    prefs = {
        "python_version": python_prefs["name"],
        "architecture": architecture,
        "script_dir": script_dir,
        "depends_dir": depends_dir,
        "python_dir": python_dir,
        "build_dir": build_dir,
        "lib_dir": lib_dir,
        "inc_dir": inc_dir,
        "bin_dir": bin_dir,
        "pillow_dir": os.path.realpath(os.path.join(script_dir, "..")),
        # TODO auto find:
        "cmake": "cmake.exe",
    }

    dicts = [vs2017, sdk71a, arch_prefs, python_prefs, config]
    for x in dicts:
        prefs.update(x)
    prefs["header"] = sum((x.get("header", []) for x in dicts), header)
    del prefs["name"]

    build_dep_all()
    build_pillow()
