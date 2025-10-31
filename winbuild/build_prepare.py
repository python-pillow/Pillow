from __future__ import annotations

import argparse
import os
import platform
import re
import shutil
import struct
import subprocess
import sys
from typing import Any


def cmd_cd(path: str) -> str:
    return f"cd /D {path}"


def cmd_set(name: str, value: str) -> str:
    return f"set {name}={value}"


def cmd_append(name: str, value: str) -> str:
    op = "path " if name == "PATH" else f"set {name}="
    return op + f"%{name}%;{value}"


def cmd_copy(src: str, tgt: str) -> str:
    return f'copy /Y /B "{src}" "{tgt}"'


def cmd_xcopy(src: str, tgt: str) -> str:
    return f'xcopy /Y /E "{src}" "{tgt}"'


def cmd_mkdir(path: str) -> str:
    return f'mkdir "{path}"'


def cmd_rmdir(path: str) -> str:
    return f'rmdir /S /Q "{path}"'


def cmd_nmake(
    makefile: str | None = None,
    target: str = "",
    params: list[str] | None = None,
) -> str:
    return " ".join(
        [
            "{nmake}",
            "-nologo",
            f'-f "{makefile}"' if makefile is not None else "",
            f'{" ".join(params)}' if params is not None else "",
            f'"{target}"',
        ]
    )


def cmds_cmake(
    target: str | tuple[str, ...] | list[str],
    *params: str,
    build_dir: str = ".",
    build_type: str = "Release",
) -> list[str]:
    if not isinstance(target, str):
        target = " ".join(target)

    return [
        " ".join(
            [
                "{cmake}",
                f"-DCMAKE_BUILD_TYPE={build_type}",
                "-DCMAKE_VERBOSE_MAKEFILE=ON",
                "-DCMAKE_RULE_MESSAGES:BOOL=OFF",  # for NMake
                "-DCMAKE_C_COMPILER=cl.exe",  # for Ninja
                "-DCMAKE_CXX_COMPILER=cl.exe",  # for Ninja
                "-DCMAKE_C_FLAGS=-nologo",
                "-DCMAKE_CXX_FLAGS=-nologo",
                *params,
                '-G "{cmake_generator}"',
                f'-B "{build_dir}"',
                "-S .",
            ]
        ),
        f'{{cmake}} --build "{build_dir}" --clean-first --parallel --target {target}',
    ]


def cmd_msbuild(
    file: str,
    configuration: str = "Release",
    target: str = "Build",
    plat: str = "{msbuild_arch}",
) -> str:
    return " ".join(
        [
            "{msbuild}",
            f"{file}",
            f'/t:"{target}"',
            f'/p:Configuration="{configuration}"',
            f"/p:Platform={plat}",
            "/m",
        ]
    )


SF_PROJECTS = "https://sourceforge.net/projects"

ARCHITECTURES = {
    "x86": {"vcvars_arch": "x86", "msbuild_arch": "Win32"},
    "AMD64": {"vcvars_arch": "x86_amd64", "msbuild_arch": "x64"},
    "ARM64": {"vcvars_arch": "x86_arm64", "msbuild_arch": "ARM64"},
}

V = {
    "BROTLI": "1.2.0",
    "FREETYPE": "2.14.1",
    "FRIBIDI": "1.0.16",
    "HARFBUZZ": "12.1.0",
    "JPEGTURBO": "3.1.2",
    "LCMS2": "2.17",
    "LIBAVIF": "1.3.0",
    "LIBIMAGEQUANT": "4.4.0",
    "LIBPNG": "1.6.50",
    "LIBWEBP": "1.6.0",
    "OPENJPEG": "2.5.4",
    "TIFF": "4.7.1",
    "XZ": "5.8.1",
    "ZLIBNG": "2.2.5",
}
V["LIBPNG_XY"] = "".join(V["LIBPNG"].split(".")[:2])


# dependencies, listed in order of compilation
DEPS: dict[str, dict[str, Any]] = {
    "libjpeg": {
        "url": f"https://github.com/libjpeg-turbo/libjpeg-turbo/releases/download/{V['JPEGTURBO']}/libjpeg-turbo-{V['JPEGTURBO']}.tar.gz",
        "filename": f"libjpeg-turbo-{V['JPEGTURBO']}.tar.gz",
        "license": ["README.ijg", "LICENSE.md"],
        "license_pattern": (
            "(LEGAL ISSUES\n============\n\n.+?)\n\nREFERENCES\n=========="
            ".+(libjpeg-turbo Licenses\n======================\n\n.+)$"
        ),
        "patch": {
            r"CMakeLists.txt": {
                # libjpeg-turbo does not detect MSVC x86_arm64 cross-compiler correctly
                'if(MSVC_IDE AND CMAKE_GENERATOR_PLATFORM MATCHES "arm64")': "if({architecture} STREQUAL ARM64)",  # noqa: E501
            },
        },
        "build": [
            *cmds_cmake(
                ("jpeg-static", "djpeg-static"),
                "-DENABLE_SHARED:BOOL=FALSE",
                "-DWITH_JPEG8:BOOL=TRUE",
                "-DWITH_CRT_DLL:BOOL=TRUE",
            ),
            cmd_copy("jpeg-static.lib", "libjpeg.lib"),
            cmd_copy("djpeg-static.exe", "djpeg.exe"),
        ],
        "headers": ["jconfig.h", r"src\j*.h"],
        "libs": ["libjpeg.lib"],
        "bins": ["djpeg.exe"],
    },
    "zlib": {
        "url": f"https://github.com/zlib-ng/zlib-ng/archive/refs/tags/{V['ZLIBNG']}.tar.gz",
        "filename": f"zlib-ng-{V['ZLIBNG']}.tar.gz",
        "license": "LICENSE.md",
        "patch": {
            r"CMakeLists.txt": {
                "set_target_properties(zlib PROPERTIES OUTPUT_NAME zlibstatic${{SUFFIX}})": "set_target_properties(zlib PROPERTIES OUTPUT_NAME zlib)",  # noqa: E501
            },
        },
        "build": [
            *cmds_cmake(
                "zlib", "-DBUILD_SHARED_LIBS:BOOL=OFF", "-DZLIB_COMPAT:BOOL=ON"
            ),
        ],
        "headers": [r"z*.h"],
        "libs": [r"zlib.lib"],
    },
    "xz": {
        "url": f"https://github.com/tukaani-project/xz/releases/download/v{V['XZ']}/FILENAME",
        "filename": f"xz-{V['XZ']}.tar.gz",
        "license": "COPYING",
        "build": [
            *cmds_cmake(
                "liblzma",
                "-DBUILD_SHARED_LIBS:BOOL=OFF"
                + (" -DXZ_CLMUL_CRC:BOOL=OFF" if struct.calcsize("P") == 4 else ""),
            ),
            cmd_mkdir(r"{inc_dir}\lzma"),
            cmd_copy(r"src\liblzma\api\lzma\*.h", r"{inc_dir}\lzma"),
        ],
        "headers": [r"src\liblzma\api\lzma.h"],
        "libs": [r"lzma.lib"],
    },
    "libwebp": {
        "url": "http://downloads.webmproject.org/releases/webp/FILENAME",
        "filename": f"libwebp-{V['LIBWEBP']}.tar.gz",
        "license": "COPYING",
        "patch": {
            r"src\enc\picture_csp_enc.c": {
                # link against libsharpyuv.lib
                '#include "sharpyuv/sharpyuv.h"': '#include "sharpyuv/sharpyuv.h"\n#pragma comment(lib, "libsharpyuv.lib")',  # noqa: E501
            }
        },
        "build": [
            *cmds_cmake(
                "webp webpmux webpdemux",
                "-DBUILD_SHARED_LIBS:BOOL=OFF",
                "-DWEBP_LINK_STATIC:BOOL=OFF",
            ),
            cmd_mkdir(r"{inc_dir}\webp"),
            cmd_copy(r"src\webp\*.h", r"{inc_dir}\webp"),
        ],
        "libs": [r"libsharpyuv.lib", r"libwebp*.lib"],
    },
    "libtiff": {
        "url": "https://download.osgeo.org/libtiff/FILENAME",
        "filename": f"tiff-{V['TIFF']}.tar.gz",
        "license": "LICENSE.md",
        "patch": {
            r"libtiff\tif_lzma.c": {
                # link against lzma.lib
                "#ifdef LZMA_SUPPORT": '#ifdef LZMA_SUPPORT\n#pragma comment(lib, "lzma.lib")',  # noqa: E501
            },
            r"libtiff\tif_webp.c": {
                # link against libwebp.lib
                "#ifdef WEBP_SUPPORT": '#ifdef WEBP_SUPPORT\n#pragma comment(lib, "libwebp.lib")',  # noqa: E501
            },
        },
        "build": [
            *cmds_cmake(
                "tiff",
                "-DBUILD_SHARED_LIBS:BOOL=OFF",
                "-DWebP_LIBRARY=libwebp",
                '-DCMAKE_C_FLAGS="-nologo -DLZMA_API_STATIC"',
            )
        ],
        "headers": [r"libtiff\tiff*.h"],
        "libs": [r"libtiff\*.lib"],
    },
    "libpng": {
        "url": f"{SF_PROJECTS}/libpng/files/libpng{V['LIBPNG_XY']}/{V['LIBPNG']}/"
        f"FILENAME/download",
        "filename": f"libpng-{V['LIBPNG']}.tar.gz",
        "license": "LICENSE",
        "build": [
            *cmds_cmake("png_static", "-DPNG_SHARED:BOOL=OFF", "-DPNG_TESTS:BOOL=OFF"),
            cmd_copy(
                f"libpng{V['LIBPNG_XY']}_static.lib", f"libpng{V['LIBPNG_XY']}.lib"
            ),
        ],
        "headers": [r"png*.h"],
        "libs": [f"libpng{V['LIBPNG_XY']}.lib"],
    },
    "brotli": {
        "url": f"https://github.com/google/brotli/archive/refs/tags/v{V['BROTLI']}.tar.gz",
        "filename": f"brotli-{V['BROTLI']}.tar.gz",
        "license": "LICENSE",
        "build": [
            *cmds_cmake(("brotlicommon", "brotlidec"), "-DBUILD_SHARED_LIBS:BOOL=OFF"),
            cmd_xcopy(r"c\include", "{inc_dir}"),
        ],
        "libs": ["*.lib"],
    },
    "freetype": {
        "url": "https://download.savannah.gnu.org/releases/freetype/FILENAME",
        "filename": f"freetype-{V['FREETYPE']}.tar.gz",
        "license": ["LICENSE.TXT", r"docs\FTL.TXT", r"docs\GPLv2.TXT"],
        "patch": {
            r"builds\windows\vc2010\freetype.vcxproj": {
                # freetype setting is /MD for .dll and /MT for .lib, we need /MD
                "<RuntimeLibrary>MultiThreaded</RuntimeLibrary>": "<RuntimeLibrary>MultiThreadedDLL</RuntimeLibrary>",  # noqa: E501
                # freetype doesn't specify SDK version, MSBuild may guess incorrectly
                '<PropertyGroup Label="Globals">': '<PropertyGroup Label="Globals">\n    <WindowsTargetPlatformVersion>$(WindowsSDKVersion)</WindowsTargetPlatformVersion>',  # noqa: E501
            },
            r"builds\windows\vc2010\freetype.user.props": {
                "<UserDefines></UserDefines>": "<UserDefines>FT_CONFIG_OPTION_SYSTEM_ZLIB;FT_CONFIG_OPTION_USE_PNG;FT_CONFIG_OPTION_USE_HARFBUZZ;FT_CONFIG_OPTION_USE_BROTLI</UserDefines>",  # noqa: E501
                "<UserIncludeDirectories></UserIncludeDirectories>": r"<UserIncludeDirectories>{dir_harfbuzz}\src;{inc_dir}</UserIncludeDirectories>",  # noqa: E501
                "<UserLibraryDirectories></UserLibraryDirectories>": "<UserLibraryDirectories>{lib_dir}</UserLibraryDirectories>",  # noqa: E501
                "<UserDependencies></UserDependencies>": f"<UserDependencies>zlib.lib;libpng{V['LIBPNG_XY']}.lib;brotlicommon.lib;brotlidec.lib</UserDependencies>",  # noqa: E501
            },
            r"src/autofit/afshaper.c": {
                # link against harfbuzz.lib
                "#ifdef FT_CONFIG_OPTION_USE_HARFBUZZ": '#ifdef FT_CONFIG_OPTION_USE_HARFBUZZ\n#pragma comment(lib, "harfbuzz.lib")',  # noqa: E501
            },
        },
        "build": [
            cmd_rmdir("objs"),
            cmd_msbuild(
                r"builds\windows\vc2010\freetype.vcxproj", "Release Static", "Clean"
            ),
            cmd_msbuild(
                r"builds\windows\vc2010\freetype.vcxproj", "Release Static", "Build"
            ),
            cmd_xcopy("include", "{inc_dir}"),
        ],
        "libs": [r"objs\{msbuild_arch}\Release Static\freetype.lib"],
    },
    "lcms2": {
        "url": f"{SF_PROJECTS}/lcms/files/lcms/{V['LCMS2']}/FILENAME/download",
        "filename": f"lcms2-{V['LCMS2']}.tar.gz",
        "license": "LICENSE",
        "patch": {
            r"Projects\VC2022\lcms2_static\lcms2_static.vcxproj": {
                # default is /MD for x86 and /MT for x64, we need /MD always
                "<RuntimeLibrary>MultiThreaded</RuntimeLibrary>": "<RuntimeLibrary>MultiThreadedDLL</RuntimeLibrary>",  # noqa: E501
                # retarget to default toolset (selected by vcvarsall.bat)
                "<PlatformToolset>v143</PlatformToolset>": "<PlatformToolset>$(DefaultPlatformToolset)</PlatformToolset>",  # noqa: E501
                # retarget to latest (selected by vcvarsall.bat)
                "<WindowsTargetPlatformVersion>10.0</WindowsTargetPlatformVersion>": "<WindowsTargetPlatformVersion>$(WindowsSDKVersion)</WindowsTargetPlatformVersion>",  # noqa: E501
            }
        },
        "build": [
            cmd_rmdir("Lib"),
            cmd_rmdir(r"Projects\VC2022\Release"),
            cmd_msbuild(r"Projects\VC2022\lcms2.sln", "Release", "Clean"),
            cmd_msbuild(
                r"Projects\VC2022\lcms2.sln", "Release", "lcms2_static:Rebuild"
            ),
            cmd_xcopy("include", "{inc_dir}"),
        ],
        "libs": [r"Lib\MS\*.lib"],
    },
    "openjpeg": {
        "url": f"https://github.com/uclouvain/openjpeg/archive/v{V['OPENJPEG']}.tar.gz",
        "filename": f"openjpeg-{V['OPENJPEG']}.tar.gz",
        "license": "LICENSE",
        "build": [
            *cmds_cmake(
                "openjp2", "-DBUILD_CODEC:BOOL=OFF", "-DBUILD_SHARED_LIBS:BOOL=OFF"
            ),
            cmd_mkdir(rf"{{inc_dir}}\openjpeg-{V['OPENJPEG']}"),
            cmd_copy(r"src\lib\openjp2\*.h", rf"{{inc_dir}}\openjpeg-{V['OPENJPEG']}"),
        ],
        "libs": [r"bin\*.lib"],
    },
    "libimagequant": {
        "url": "https://github.com/ImageOptim/libimagequant/archive/{V['LIBIMAGEQUANT']}.tar.gz",
        "filename": f"libimagequant-{V['LIBIMAGEQUANT']}.tar.gz",
        "license": "COPYRIGHT",
        "build": [
            cmd_cd("imagequant-sys"),
            "cargo build --release",
        ],
        "headers": ["libimagequant.h"],
        "libs": [r"..\target\release\imagequant_sys.lib"],
    },
    "harfbuzz": {
        "url": f"https://github.com/harfbuzz/harfbuzz/releases/download/{V['HARFBUZZ']}/FILENAME",
        "filename": f"harfbuzz-{V['HARFBUZZ']}.tar.xz",
        "license": "COPYING",
        "build": [
            *cmds_cmake(
                "harfbuzz",
                "-DHB_HAVE_FREETYPE:BOOL=TRUE",
                '-DCMAKE_CXX_FLAGS="-nologo -d2FH4-"',
            ),
        ],
        "headers": [r"src\*.h"],
        "libs": [r"*.lib"],
    },
    "fribidi": {
        "url": f"https://github.com/fribidi/fribidi/archive/v{V['FRIBIDI']}.zip",
        "filename": f"fribidi-{V['FRIBIDI']}.zip",
        "license": "COPYING",
        "build": [
            cmd_copy(r"COPYING", rf"{{bin_dir}}\fribidi-{V['FRIBIDI']}-COPYING"),
            cmd_copy(r"{winbuild_dir}\fribidi.cmake", r"CMakeLists.txt"),
            # generated tab.i files cannot be cross-compiled
            " ^&^& ".join(
                [
                    "if {architecture}==ARM64 cmd /c call {vcvarsall} x86",
                    *cmds_cmake("fribidi-gen", "-DARCH=x86", build_dir="build_x86"),
                ]
            ),
            *cmds_cmake("fribidi", "-DARCH={architecture}"),
        ],
        "bins": [r"*.dll"],
    },
    "libavif": {
        "url": f"https://github.com/AOMediaCodec/libavif/archive/v{V['LIBAVIF']}.tar.gz",
        "filename": f"libavif-{V['LIBAVIF']}.tar.gz",
        "license": "LICENSE",
        "build": [
            "rustup update",
            f"{sys.executable} -m pip install meson",
            *cmds_cmake(
                "avif_static",
                "-DBUILD_SHARED_LIBS=OFF",
                "-DAVIF_LIBSHARPYUV=LOCAL",
                "-DAVIF_LIBYUV=LOCAL",
                "-DAVIF_CODEC_AOM=LOCAL",
                "-DCONFIG_AV1_HIGHBITDEPTH=0",
                "-DAVIF_CODEC_AOM_DECODE=OFF",
                "-DAVIF_CODEC_DAV1D=LOCAL",
                "-DCMAKE_INTERPROCEDURAL_OPTIMIZATION=ON",
                build_type="MinSizeRel",
            ),
            cmd_xcopy("include", "{inc_dir}"),
        ],
        "libs": ["avif.lib"],
    },
}


# based on distutils._msvccompiler from CPython 3.7.4
def find_msvs(architecture: str) -> dict[str, str] | None:
    root = os.environ.get("ProgramFiles(x86)") or os.environ.get("ProgramFiles")
    if not root:
        print("Program Files not found")
        return None

    requires = ["-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64"]
    if architecture == "ARM64":
        requires += ["-requires", "Microsoft.VisualStudio.Component.VC.Tools.ARM64"]

    try:
        vspath = (
            subprocess.check_output(
                [
                    os.path.join(
                        root, "Microsoft Visual Studio", "Installer", "vswhere.exe"
                    ),
                    "-latest",
                    "-prerelease",
                    *requires,
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

    # vs2017
    msbuild = os.path.join(vspath, "MSBuild", "15.0", "Bin", "MSBuild.exe")
    if not os.path.isfile(msbuild):
        # vs2019
        msbuild = os.path.join(vspath, "MSBuild", "Current", "Bin", "MSBuild.exe")
        if not os.path.isfile(msbuild):
            print("Visual Studio MSBuild not found")
            return None

    vcvarsall = os.path.join(vspath, "VC", "Auxiliary", "Build", "vcvarsall.bat")
    if not os.path.isfile(vcvarsall):
        print("Visual Studio vcvarsall not found")
        return None

    return {
        "vs_dir": vspath,
        "msbuild": f'"{msbuild}"',
        "vcvarsall": f'"{vcvarsall}"',
        "nmake": "nmake.exe",  # nmake selected by vcvarsall
    }


def download_dep(url: str, file: str) -> None:
    import urllib.error
    import urllib.request

    ex = None
    for i in range(3):
        try:
            print(f"Fetching {url} (attempt {i + 1})...")
            content = urllib.request.urlopen(url).read()
            with open(file, "wb") as f:
                f.write(content)
            break
        except urllib.error.URLError as e:
            ex = e
    else:
        raise RuntimeError(ex)


def extract_dep(url: str, filename: str, prefs: dict[str, str]) -> None:
    import tarfile
    import zipfile

    depends_dir = prefs["depends_dir"]
    sources_dir = prefs["src_dir"]

    file = os.path.join(depends_dir, filename)
    if not os.path.exists(file):
        # First try our mirror
        mirror_url = (
            f"https://raw.githubusercontent.com/"
            f"python-pillow/pillow-depends/main/{filename}"
        )
        try:
            download_dep(mirror_url, file)
        except RuntimeError as exc:
            # Otherwise try upstream
            print(exc)
            download_dep(url.replace("FILENAME", filename), file)

    print("Extracting " + filename)
    sources_dir_abs = os.path.abspath(sources_dir)
    if filename.endswith(".zip"):
        with zipfile.ZipFile(file) as zf:
            for member in zf.namelist():
                member_abspath = os.path.abspath(os.path.join(sources_dir, member))
                member_prefix = os.path.commonpath([sources_dir_abs, member_abspath])
                if sources_dir_abs != member_prefix:
                    msg = "Attempted Path Traversal in Zip File"
                    raise RuntimeError(msg)
            zf.extractall(sources_dir)
    elif filename.endswith((".tar.gz", ".tar.xz")):
        with tarfile.open(file, "r:xz" if filename.endswith(".xz") else "r:gz") as tgz:
            for member in tgz.getnames():
                member_abspath = os.path.abspath(os.path.join(sources_dir, member))
                member_prefix = os.path.commonpath([sources_dir_abs, member_abspath])
                if sources_dir_abs != member_prefix:
                    msg = "Attempted Path Traversal in Tar File"
                    raise RuntimeError(msg)
            if sys.version_info >= (3, 12):
                tgz.extractall(sources_dir, filter="data")
            else:
                tgz.extractall(sources_dir)
    else:
        msg = "Unknown archive type: " + filename
        raise RuntimeError(msg)


def write_script(
    name: str, lines: list[str], prefs: dict[str, str], verbose: bool
) -> None:
    name = os.path.join(prefs["build_dir"], name)
    lines = [line.format(**prefs) for line in lines]
    print("Writing " + name)
    with open(name, "w", newline="") as f:
        f.write(os.linesep.join(lines))
    if verbose:
        for line in lines:
            print("    " + line)


def get_footer(dep: dict[str, Any]) -> list[str]:
    lines = []
    for out in dep.get("headers", []):
        lines.append(cmd_copy(out, "{inc_dir}"))
    for out in dep.get("libs", []):
        lines.append(cmd_copy(out, "{lib_dir}"))
    for out in dep.get("bins", []):
        lines.append(cmd_copy(out, "{bin_dir}"))
    return lines


def build_env(prefs: dict[str, str], verbose: bool) -> None:
    lines = [
        "if defined DISTUTILS_USE_SDK goto end",
        cmd_set("INCLUDE", "{inc_dir}"),
        cmd_set("INCLIB", "{lib_dir}"),
        cmd_set("LIB", "{lib_dir}"),
        cmd_append("PATH", "{bin_dir}"),
        "call {vcvarsall} {vcvars_arch}",
        cmd_set("DISTUTILS_USE_SDK", "1"),  # use same compiler to build Pillow
        cmd_set("py_vcruntime_redist", "true"),  # always use /MD, never /MT
        ":end",
        "@echo on",
    ]
    write_script("build_env.cmd", lines, prefs, verbose)


def build_dep(name: str, prefs: dict[str, str], verbose: bool) -> str:
    dep = DEPS[name]
    directory = dep["dir"]
    file = f"build_dep_{name}.cmd"
    license_dir = prefs["license_dir"]
    sources_dir = prefs["src_dir"]

    extract_dep(dep["url"], dep["filename"], prefs)

    licenses = dep["license"]
    if isinstance(licenses, str):
        licenses = [licenses]
    license_text = ""
    for license_file in licenses:
        with open(os.path.join(sources_dir, directory, license_file)) as f:
            license_text += f.read()
    if "license_pattern" in dep:
        match = re.search(dep["license_pattern"], license_text, re.DOTALL)
        assert match is not None
        license_text = "\n".join(match.groups())
    assert len(license_text) > 50
    with open(os.path.join(license_dir, f"{directory}.txt"), "w") as f:
        print(f"Writing license {directory}.txt")
        f.write(license_text)

    for patch_file, patch_list in dep.get("patch", {}).items():
        patch_file = os.path.join(sources_dir, directory, patch_file.format(**prefs))
        with open(patch_file) as f:
            text = f.read()
        for patch_from, patch_to in patch_list.items():
            patch_from = patch_from.format(**prefs)
            patch_to = patch_to.format(**prefs)
            assert patch_from in text
            text = text.replace(patch_from, patch_to)
        with open(patch_file, "w") as f:
            print(f"Patching {patch_file}")
            f.write(text)

    banner = f"Building {name} ({directory})"
    lines = [
        r'call "{build_dir}\build_env.cmd"',
        "@echo " + ("=" * 70),
        f"@echo ==== {banner:<60} ====",
        "@echo " + ("=" * 70),
        cmd_cd(os.path.join(sources_dir, directory)),
        *dep.get("build", []),
        *get_footer(dep),
    ]

    write_script(file, lines, prefs, verbose)
    return file


def build_dep_all(disabled: list[str], prefs: dict[str, str], verbose: bool) -> None:
    lines = [r'call "{build_dir}\build_env.cmd"']
    gha_groups = "GITHUB_ACTIONS" in os.environ
    for dep_name in DEPS:
        print()
        if dep_name in disabled:
            print(f"Skipping disabled dependency {dep_name}")
            continue
        script = build_dep(dep_name, prefs, verbose)
        if gha_groups:
            lines.append(f"@echo ::group::Running {script}")
        lines.append(rf'cmd.exe /c "{{build_dir}}\{script}"')
        lines.append("if errorlevel 1 echo Build failed! && exit /B 1")
        if gha_groups:
            lines.append("@echo ::endgroup::")
    print()
    lines.append("@echo All Pillow dependencies built successfully!")
    write_script("build_dep_all.cmd", lines, prefs, verbose)


def main() -> None:
    winbuild_dir = os.path.dirname(os.path.realpath(__file__))

    parser = argparse.ArgumentParser(
        prog="winbuild\\build_prepare.py",
        description="Download and generate build scripts for Pillow dependencies.",
        epilog="""Arguments can also be supplied using the environment variables
                  PILLOW_BUILD, PILLOW_DEPS, ARCHITECTURE. See winbuild\\build.rst
                  for more information.""",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="print generated scripts"
    )
    parser.add_argument(
        "-d",
        "--dir",
        "--build-dir",
        dest="build_dir",
        metavar="PILLOW_BUILD",
        default=os.environ.get("PILLOW_BUILD", os.path.join(winbuild_dir, "build")),
        help="build directory (default: 'winbuild\\build')",
    )
    parser.add_argument(
        "--depends",
        dest="depends_dir",
        metavar="PILLOW_DEPS",
        default=os.environ.get("PILLOW_DEPS", os.path.join(winbuild_dir, "depends")),
        help="directory used to store cached dependencies "
        "(default: 'winbuild\\depends')",
    )
    parser.add_argument(
        "--architecture",
        choices=ARCHITECTURES,
        default=os.environ.get(
            "ARCHITECTURE",
            (
                "ARM64"
                if platform.machine() == "ARM64"
                else ("x86" if struct.calcsize("P") == 4 else "AMD64")
            ),
        ),
        help="build architecture (default: same as host Python)",
    )
    parser.add_argument(
        "--nmake",
        dest="cmake_generator",
        action="store_const",
        const="NMake Makefiles",
        default="Ninja",
        help="build dependencies using NMake instead of Ninja",
    )
    parser.add_argument(
        "--no-imagequant",
        action="store_true",
        help="skip GPL-licensed optional dependency libimagequant",
    )
    parser.add_argument(
        "--no-fribidi",
        "--no-raqm",
        action="store_true",
        help="skip LGPL-licensed optional dependency FriBiDi",
    )
    parser.add_argument(
        "--no-avif",
        action="store_true",
        help="skip optional dependency libavif",
    )
    args = parser.parse_args()

    arch_prefs = ARCHITECTURES[args.architecture]
    print("Target architecture:", args.architecture)

    msvs = find_msvs(args.architecture)
    if msvs is None:
        msg = "Visual Studio not found. Please install Visual Studio 2017 or newer."
        raise RuntimeError(msg)
    print("Found Visual Studio at:", msvs["vs_dir"])

    # dependency cache directory
    args.depends_dir = os.path.abspath(args.depends_dir)
    os.makedirs(args.depends_dir, exist_ok=True)
    print("Caching dependencies in:", args.depends_dir)

    args.build_dir = os.path.abspath(args.build_dir)
    print("Using output directory:", args.build_dir)

    # build directory for *.h files
    inc_dir = os.path.join(args.build_dir, "inc")
    # build directory for *.lib files
    lib_dir = os.path.join(args.build_dir, "lib")
    # build directory for *.bin files
    bin_dir = os.path.join(args.build_dir, "bin")
    # directory for storing project files
    sources_dir = os.path.join(args.build_dir, "src")
    # copy dependency licenses to this directory
    license_dir = os.path.join(args.build_dir, "license")

    shutil.rmtree(args.build_dir, ignore_errors=True)
    os.makedirs(args.build_dir, exist_ok=False)
    for path in [inc_dir, lib_dir, bin_dir, sources_dir, license_dir]:
        os.makedirs(path, exist_ok=True)

    disabled = []
    if args.no_imagequant:
        disabled += ["libimagequant"]
    if args.no_fribidi:
        disabled += ["fribidi"]
    if args.no_avif or args.architecture == "ARM64":
        disabled += ["libavif"]

    prefs = {
        "architecture": args.architecture,
        **arch_prefs,
        # Pillow paths
        "winbuild_dir": winbuild_dir,
        # Build paths
        "bin_dir": bin_dir,
        "build_dir": args.build_dir,
        "depends_dir": args.depends_dir,
        "inc_dir": inc_dir,
        "lib_dir": lib_dir,
        "license_dir": license_dir,
        "src_dir": sources_dir,
        # Compilers / Tools
        **msvs,
        "cmake": "cmake.exe",  # TODO find CMAKE automatically
        "cmake_generator": args.cmake_generator,
        # TODO find NASM automatically
    }

    for k, v in DEPS.items():
        if "dir" not in v:
            v["dir"] = re.sub(r"\.(tar\.gz|tar\.xz|zip)", "", v["filename"])
        prefs[f"dir_{k}"] = os.path.join(sources_dir, v["dir"])

    print()

    write_script(".gitignore", ["*"], prefs, args.verbose)
    build_env(prefs, args.verbose)
    build_dep_all(disabled, prefs, args.verbose)


if __name__ == "__main__":
    main()
