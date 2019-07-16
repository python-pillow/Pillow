from __future__ import print_function, unicode_literals

import collections
import os
import sys

import PIL

from . import Image

modules = {
    "pil": "PIL._imaging",
    "tkinter": "PIL._tkinter_finder",
    "freetype2": "PIL._imagingft",
    "littlecms2": "PIL._imagingcms",
    "webp": "PIL._webp",
}


def check_module(feature):
    if not (feature in modules):
        raise ValueError("Unknown module %s" % feature)

    module = modules[feature]

    try:
        __import__(module)
        return True
    except ImportError:
        return False


def get_supported_modules():
    return [f for f in modules if check_module(f)]


codecs = {"jpg": "jpeg", "jpg_2000": "jpeg2k", "zlib": "zip", "libtiff": "libtiff"}


def check_codec(feature):
    if feature not in codecs:
        raise ValueError("Unknown codec %s" % feature)

    codec = codecs[feature]

    return codec + "_encoder" in dir(Image.core)


def get_supported_codecs():
    return [f for f in codecs if check_codec(f)]


features = {
    "webp_anim": ("PIL._webp", "HAVE_WEBPANIM"),
    "webp_mux": ("PIL._webp", "HAVE_WEBPMUX"),
    "transp_webp": ("PIL._webp", "HAVE_TRANSPARENCY"),
    "raqm": ("PIL._imagingft", "HAVE_RAQM"),
    "libjpeg_turbo": ("PIL._imaging", "HAVE_LIBJPEGTURBO"),
}


def check_feature(feature):
    if feature not in features:
        raise ValueError("Unknown feature %s" % feature)

    module, flag = features[feature]

    try:
        imported_module = __import__(module, fromlist=["PIL"])
        return getattr(imported_module, flag)
    except ImportError:
        return None


def get_supported_features():
    return [f for f in features if check_feature(f)]


def check(feature):
    return (
        feature in modules
        and check_module(feature)
        or feature in codecs
        and check_codec(feature)
        or feature in features
        and check_feature(feature)
    )


def get_supported():
    ret = get_supported_modules()
    ret.extend(get_supported_features())
    ret.extend(get_supported_codecs())
    return ret


def pilinfo(out=None):
    if out is None:
        out = sys.stdout

    Image.init()

    print("-" * 68, file=out)
    print("Pillow {}".format(PIL.__version__), file=out)
    print("-" * 68, file=out)
    print(
        "Python modules loaded from {}".format(os.path.dirname(Image.__file__)),
        file=out,
    )
    print(
        "Binary modules loaded from {}".format(os.path.dirname(Image.core.__file__)),
        file=out,
    )
    print("-" * 68, file=out)

    v = sys.version.splitlines()
    print("Python {}".format(v[0].strip()), file=out)
    for v in v[1:]:
        print("       {}".format(v.strip()), file=out)
    print("-" * 68, file=out)

    for name, feature in [
        ("pil", "PIL CORE"),
        ("tkinter", "TKINTER"),
        ("freetype2", "FREETYPE2"),
        ("littlecms2", "LITTLECMS2"),
        ("webp", "WEBP"),
        ("transp_webp", "WEBP Transparency"),
        ("webp_mux", "WEBPMUX"),
        ("webp_anim", "WEBP Animation"),
        ("jpg", "JPEG"),
        ("jpg_2000", "OPENJPEG (JPEG2000)"),
        ("zlib", "ZLIB (PNG/ZIP)"),
        ("libtiff", "LIBTIFF"),
        ("raqm", "RAQM (Bidirectional Text)"),
    ]:
        if check(name):
            print("---", feature, "support ok", file=out)
        else:
            print("***", feature, "support not installed", file=out)
    print("-" * 68, file=out)

    extensions = collections.defaultdict(list)
    for ext, i in Image.EXTENSION.items():
        extensions[i].append(ext)

    for i in sorted(Image.ID):
        line = "{}".format(i)
        if i in Image.MIME:
            line = "{} {}".format(line, Image.MIME[i])
        print(line, file=out)

        if i in extensions:
            print("Extensions: {}".format(", ".join(sorted(extensions[i]))), file=out)

        features = []
        if i in Image.OPEN:
            features.append("open")
        if i in Image.SAVE:
            features.append("save")
        if i in Image.SAVE_ALL:
            features.append("save_all")
        if i in Image.DECODERS:
            features.append("decode")
        if i in Image.ENCODERS:
            features.append("encode")

        print("Features: {}".format(", ".join(features)), file=out)
        print("-" * 68, file=out)
