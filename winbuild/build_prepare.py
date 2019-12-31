import os
import shutil
import subprocess
import sys
import winreg
from itertools import count

from commands import *

SF_MIRROR = "http://iweb.dl.sourceforge.net"

architectures = {
    "x86": {"vcvars_arch": "x86", "msbuild_arch": "Win32"},
    "x64": {"vcvars_arch": "x86_amd64", "msbuild_arch": "x64"},
}

header = [
    cmd_set("BUILD", "{build_dir}"),
    cmd_set("INCLUDE", "{inc_dir}"),
    cmd_set("INCLIB", "{lib_dir}"),
    cmd_set("LIB", "{lib_dir}"),
    cmd_append("PATH", "{bin_dir}"),
]

# dependencies
deps = {
    "libjpeg": {
        "url": SF_MIRROR + "/project/libjpeg-turbo/2.0.3/libjpeg-turbo-2.0.3.tar.gz",
        "filename": "libjpeg-turbo-2.0.3.tar.gz",
        "dir": "libjpeg-turbo-2.0.3",
        "build": [
            cmd_cmake(
                [
                    "-DENABLE_SHARED:BOOL=FALSE",
                    "-DWITH_JPEG8:BOOL=TRUE",
                    "-DWITH_CRT_DLL:BOOL=TRUE",
                ]
            ),
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
    "zlib": {
        "url": "http://zlib.net/zlib1211.zip",
        "filename": "zlib1211.zip",
        "dir": "zlib-1.2.11",
        "build": [
            cmd_nmake(r"win32\Makefile.msc", "clean"),
            cmd_nmake(r"win32\Makefile.msc", "zlib.lib"),
            cmd_copy("zlib.lib", "z.lib"),
        ],
        "headers": [r"z*.h"],
        "libs": [r"*.lib"],
    },
    "libtiff": {
        # FIXME FTP timeout
        "url": "ftp://download.osgeo.org/libtiff/tiff-4.1.0.tar.gz",
        "filename": "tiff-4.1.0.tar.gz",
        "dir": "tiff-4.1.0",
        "build": [
            cmd_copy(r"{script_dir}\tiff.opt", "nmake.opt"),
            cmd_nmake("makefile.vc", "clean"),
            cmd_nmake("makefile.vc", "lib"),
        ],
        "headers": [r"libtiff\tiff*.h"],
        "libs": [r"libtiff\*.lib"],
        # "bins": [r"libtiff\*.dll"],
    },
    "libwebp": {
        "url": "http://downloads.webmproject.org/releases/webp/libwebp-1.0.3.tar.gz",  # noqa: E501
        "filename": "libwebp-1.0.3.tar.gz",
        "dir": "libwebp-1.0.3",
        "build": [
            cmd_rmdir(r"output\release-static"),  # clean
            cmd_nmake(
                "Makefile.vc",
                "all",
                ["CFG=release-static", "OBJDIR=output", "ARCH={architecture}"],
            ),
            cmd_mkdir(r"{inc_dir}\webp"),
            cmd_copy(r"src\webp\*.h", r"{inc_dir}\webp"),
        ],
        "libs": [r"output\release-static\{architecture}\lib\*.lib"],
    },
    "freetype": {
        "url": "https://download.savannah.gnu.org/releases/freetype/freetype-2.10.1.tar.gz",  # noqa: E501
        "filename": "freetype-2.10.1.tar.gz",
        "dir": "freetype-2.10.1",
        "patch": {
            r"builds\windows\vc2010\freetype.vcxproj": {
                # freetype setting is /MD for .dll and /MT for .lib, we need /MD
                "<RuntimeLibrary>MultiThreaded</RuntimeLibrary>":
                    "<RuntimeLibrary>MultiThreadedDLL</RuntimeLibrary>",
            }
        },
        "build": [
            cmd_rmdir("objs"),
            cmd_msbuild(
                r"builds\windows\vc2010\freetype.sln", "Release Static", "Clean"
            ),
            cmd_msbuild(
                r"builds\windows\vc2010\freetype.sln", "Release Static", "Build"
            ),
            cmd_xcopy("include", "{inc_dir}"),
        ],
        "libs": [r"objs\{msbuild_arch}\Release Static\freetype.lib"],
        # "bins": [r"objs\{msbuild_arch}\Release\freetype.dll"],
    },
    "lcms2": {
        "url": SF_MIRROR + "/project/lcms/lcms/2.9/lcms2-2.9.tar.gz",
        "filename": "lcms2-2.9.tar.gz",
        "dir": "lcms2-2.9",
        "patch": {
            r"Projects\VC2017\lcms2_static\lcms2_static.vcxproj": {
                # default is /MD for x86 and /MT for x64, we need /MD always
                "<RuntimeLibrary>MultiThreaded</RuntimeLibrary>":
                    "<RuntimeLibrary>MultiThreadedDLL</RuntimeLibrary>",
                # retarget to default toolset (selected by vcvarsall.bat)
                "<PlatformToolset>v141</PlatformToolset>":
                    "<PlatformToolset>$(DefaultPlatformToolset)</PlatformToolset>",
                # retarget to latest (selected by vcvarsall.bat)
                "<WindowsTargetPlatformVersion>8.1</WindowsTargetPlatformVersion>":
                    "<WindowsTargetPlatformVersion>$(WindowsSDKVersion)</WindowsTargetPlatformVersion>",  # noqa E501
            }
        },
        "build": [
            cmd_rmdir("Lib"),
            cmd_rmdir(r"Projects\VC2017\Release"),
            cmd_msbuild(r"Projects\VC2017\lcms2.sln", "Release", "Clean"),
            cmd_msbuild(r"Projects\VC2017\lcms2.sln", "Release", "lcms2_static"),
            cmd_xcopy("include", "{inc_dir}"),
        ],
        "libs": [r"Lib\MS\*.lib"],
    },
    "openjpeg": {
        "url": "https://github.com/uclouvain/openjpeg/archive/v2.3.1.tar.gz",
        "filename": "openjpeg-2.3.1.tar.gz",
        "dir": "openjpeg-2.3.1",
        "build": [
            cmd_cmake(("-DBUILD_THIRDPARTY:BOOL=OFF", "-DBUILD_SHARED_LIBS:BOOL=OFF")),
            cmd_nmake(target="clean"),
            cmd_nmake(),
            cmd_mkdir(r"{inc_dir}\openjpeg-2.3.1"),
            cmd_copy(r"src\lib\openjp2\*.h", r"{inc_dir}\openjpeg-2.3.1"),
        ],
        "libs": [r"bin\*.lib"],
    },
    "libimagequant": {
        # ba653c8: Merge tag '2.12.5' into msvc
        "url": "https://github.com/ImageOptim/libimagequant/archive/ba653c8ccb34dde4e21c6076d85a72d21ed9d971.zip",  # noqa: E501
        "filename": "libimagequant-ba653c8ccb34dde4e21c6076d85a72d21ed9d971.zip",
        "dir": "libimagequant-ba653c8ccb34dde4e21c6076d85a72d21ed9d971",
        "patch": {
            "CMakeLists.txt": {
                "add_library": "add_compile_options(-openmp-)\r\nadd_library",
                " SHARED": " STATIC",
            }
        },
        "build": [
            # lint: do not inline
            cmd_cmake(),
            cmd_nmake(target="clean"),
            cmd_nmake(),
        ],
        "headers": [r"*.h"],
        "libs": [r"*.lib"],
    },
    "harfbuzz": {
        "url": "https://github.com/harfbuzz/harfbuzz/archive/2.6.1.zip",
        "filename": "harfbuzz-2.6.1.zip",
        "dir": "harfbuzz-2.6.1",
        "build": [
            cmd_cmake("-DHB_HAVE_FREETYPE:BOOL=TRUE"),
            cmd_nmake(target="clean"),
            cmd_nmake(target="harfbuzz"),
        ],
        "headers": [r"src\*.h"],
        "libs": [r"*.lib"],
    },
    "fribidi": {
        "url": "https://github.com/fribidi/fribidi/archive/v1.0.7.zip",
        "filename": "fribidi-1.0.7.zip",
        "dir": "fribidi-1.0.7",
        "build": [
            cmd_copy(r"{script_dir}\fribidi.cmake", r"CMakeLists.txt"),
            cmd_cmake(),
            cmd_nmake(target="clean"),
            cmd_nmake(target="fribidi"),
        ],
        "headers": [r"lib\*.h"],
        "libs": [r"*.lib"],
    },
    "libraqm": {
        "url": "https://github.com/HOST-Oman/libraqm/archive/v0.7.0.zip",
        "filename": "libraqm-0.7.0.zip",
        "dir": "libraqm-0.7.0",
        "build": [
            cmd_copy(r"{script_dir}\raqm.cmake", r"CMakeLists.txt"),
            cmd_cmake(),
            cmd_nmake(target="clean"),
            cmd_nmake(target="libraqm"),
        ],
        "headers": [r"src\*.h"],
        "bins": [r"libraqm.dll"],
    },
}


# based on distutils._msvccompiler from CPython 3.7.4
def find_msvs():
    root = os.environ.get("ProgramFiles(x86)") or os.environ.get("ProgramFiles")
    if not root:
        print("Program Files not found")
        return None

    try:
        vspath = (
            subprocess.check_output(
                [
                    os.path.join(
                        root, "Microsoft Visual Studio", "Installer", "vswhere.exe"
                    ),
                    "-latest",
                    "-prerelease",
                    "-requires",
                    "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                    "-property",
                    "installationPath",
                    "-products",
                    "*",
                ]
            )
            .decode(encoding="mbcs")
            .strip()
        )
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
        vs["msbuild"] = '"{}"'.format(msbuild)
    else:
        # vs2019
        msbuild = os.path.join(vspath, "MSBuild", "Current", "Bin", "MSBuild.exe")
        if os.path.isfile(msbuild):
            vs["msbuild"] = '"{}"'.format(msbuild)
        else:
            print("Visual Studio MSBuild not found")
            return None

    vcvarsall = os.path.join(vspath, "VC", "Auxiliary", "Build", "vcvarsall.bat")
    if not os.path.isfile(vcvarsall):
        print("Visual Studio vcvarsall not found")
        return None
    vs["header"].append('call "{}" {{vcvars_arch}}'.format(vcvarsall))

    return vs


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
    dir = dep["dir"]
    file = "build_dep_{name}.cmd".format(**locals())

    extract_dep(dep["url"], dep["filename"])

    for patch_file, patch_list in dep.get("patch", {}).items():
        patch_file = os.path.join(build_dir, dir, patch_file.format(**prefs))
        with open(patch_file, "r") as f:
            text = f.read()
        for patch_from, patch_to in patch_list.items():
            text = text.replace(patch_from.format(**prefs), patch_to.format(**prefs))
        with open(patch_file, "w") as f:
            f.write(text)

    lines = [
        "@echo ---- Building {name} ({dir}) ----".format(**locals()),
        "cd /D %s" % os.path.join(build_dir, dir),
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
    for dep_name in deps:
        lines.append('cmd.exe /c "%s"' % build_dep(dep_name))
    write_script("build_dep_all.ps1", lines)


def build_pillow(wheel=False):
    lines = []
    if path_dir is not None and not wheel:
        lines.append(cmd_xcopy("{bin_dir}", path_dir))
    lines.extend(prefs["header"])
    lines.extend(
        [
            "@echo ---- Building Pillow (%s) ----",
            cmd_cd("{pillow_dir}"),
            cmd_append("LIB", r"{python_dir}\tcl"),
            cmd_set("MSSdk", "1"),
            cmd_set("DISTUTILS_USE_SDK", "1"),
            cmd_set("py_vcruntime_redist", "true"),
            r'"{python_dir}\python.exe" setup.py build_ext %*',
        ]
    )

    write_script("build_pillow.cmd", lines)


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))
    depends_dir = os.path.join(script_dir, "depends")
    python_dir = os.environ.get(
        "PYTHON", os.path.dirname(os.path.realpath(sys.executable))
    )

    print("Target Python: {}".format(python_dir))

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

    print("Target Architecture: {}".format(architecture))

    msvs = find_msvs()
    if msvs is None:
        raise RuntimeError(
            "Visual Studio not found. Please install Visual Studio 2017 or newer."
        )

    print("Found Visual Studio at: {}".format(msvs["vs_dir"]))

    build_dir = os.path.join(script_dir, "build", architecture)
    lib_dir = os.path.join(build_dir, "lib")
    inc_dir = os.path.join(build_dir, "inc")
    bin_dir = os.path.join(build_dir, "bin")

    shutil.rmtree(build_dir, ignore_errors=True)
    for path in [depends_dir, build_dir, lib_dir, inc_dir, bin_dir]:
        os.makedirs(path, exist_ok=True)

    prefs = {
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
    prefs.update(msvs)
    prefs.update(arch_prefs)
    prefs["header"] = sum([header, msvs["header"], ["@echo on"]], [])

    build_dep_all()
    build_pillow()
