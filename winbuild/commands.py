# builtins


def cmd_cd(path):
    return "cd /D {path}".format(**locals())


def cmd_set(name, value):
    return "set {name}={value}".format(**locals())


def cmd_prepend(name, value):
    op = "path " if name == "PATH" else "set {name}="
    return (op + "{value};%{name}%").format(**locals())


def cmd_append(name, value):
    op = "path " if name == "PATH" else "set {name}="
    return (op + "%{name}%;{value}").format(**locals())


def cmd_copy(src, tgt):
    return 'copy /Y /B "{src}" "{tgt}"'.format(**locals())


def cmd_xcopy(src, tgt):
    return 'xcopy /Y /E "{src}" "{tgt}"'.format(**locals())


def cmd_mkdir(path):
    return 'mkdir "{path}"'.format(**locals())


def cmd_rmdir(path):
    return 'rmdir /S /Q "{path}"'.format(**locals())


def cmd_if_eq(a, b, cmd):
    return 'if "{a}"=="{b}" {cmd}'.format(**locals())


# tools


def cmd_nmake(makefile=None, target="", params=None):
    if params is None:
        params = ""
    elif isinstance(params, list) or isinstance(params, tuple):
        params = " ".join(params)
    else:
        params = str(params)

    return " ".join(
        [
            "{{nmake}}",
            "-nologo",
            '-f "{makefile}"' if makefile is not None else "",
            "{params}",
            '"{target}"',
        ]
    ).format(**locals())


def cmd_cmake(params=None, file="."):
    if params is None:
        params = ""
    elif isinstance(params, list) or isinstance(params, tuple):
        params = " ".join(params)
    else:
        params = str(params)
    return " ".join(
        [
            "{{cmake}}",
            "-DCMAKE_VERBOSE_MAKEFILE=ON",
            "-DCMAKE_RULE_MESSAGES:BOOL=OFF",
            "-DCMAKE_BUILD_TYPE=Release",
            "{params}",
            '-G "NMake Makefiles"',
            '"{file}"',
        ]
    ).format(**locals())


def cmd_msbuild(
    file, configuration="Release", target="Build", platform="{msbuild_arch}"
):
    return " ".join(
        [
            "{{msbuild}}",
            "{file}",
            '/t:"{target}"',
            '/p:Configuration="{configuration}"',
            "/p:Platform={platform}",
            "/m",
        ]
    ).format(**locals())
