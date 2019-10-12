import collections
import os
import sys
import warnings

import PIL

from . import Image

modules = {
    "pil": ("PIL._imaging", None),
    "tkinter": ("PIL._tkinter_finder", None),
    "freetype2": ("PIL._imagingft", "freetype2"),
    "littlecms2": ("PIL._imagingcms", "littlecms"),
    "webp": ("PIL._webp", None),
}


def check_module(feature):
    """
    Checks if a module is available.

    :param feature: The module to check for.
    :returns: ``True`` if available, ``False`` otherwise.
    :raises ValueError: If the module is not defined in this version of Pillow.
    """
    if not (feature in modules):
        raise ValueError("Unknown module %s" % feature)

    module, lib = modules[feature]

    try:
        __import__(module)
        return True
    except ImportError:
        return False


def version_module(feature):
    if not check_module(feature):
        return None

    module, lib = modules[feature]

    if lib is None:
        return None

    attr = lib + "_version"

    return getattr(__import__(module, fromlist=[attr]), attr)


def get_supported_modules():
    """
    :returns: A list of all supported modules.
    """
    return [f for f in modules if check_module(f)]


codecs = {
    "jpg": ("jpeg", "jpeglib"),
    "jpg_2000": ("jpeg2k", "jp2klib"),
    "zlib": ("zip", "zlib"),
    "libtiff": ("libtiff", "libtiff"),
}


def check_codec(feature):
    """
    Checks if a codec is available.

    :param feature: The codec to check for.
    :returns: ``True`` if available, ``False`` otherwise.
    :raises ValueError: If the codec is not defined in this version of Pillow.
    """
    if feature not in codecs:
        raise ValueError("Unknown codec %s" % feature)

    codec, lib = codecs[feature]

    return codec + "_encoder" in dir(Image.core)


def version_codec(feature):
    if not check_codec(feature):
        return None

    codec, lib = codecs[feature]

    version = getattr(Image.core, lib + "_version")

    if feature == "libtiff":
        return version.split("\n")[0].split("Version ")[1]

    return version


def get_supported_codecs():
    """
    :returns: A list of all supported codecs.
    """
    return [f for f in codecs if check_codec(f)]


features = {
    "webp_anim": ("PIL._webp", "HAVE_WEBPANIM"),
    "webp_mux": ("PIL._webp", "HAVE_WEBPMUX"),
    "transp_webp": ("PIL._webp", "HAVE_TRANSPARENCY"),
    "raqm": ("PIL._imagingft", "HAVE_RAQM"),
    "libjpeg_turbo": ("PIL._imaging", "HAVE_LIBJPEGTURBO"),
    "libimagequant": ("PIL._imaging", "HAVE_LIBIMAGEQUANT"),
    "xcb": ("PIL._imaging", "HAVE_XCB"),
}


def check_feature(feature):
    """
    Checks if a feature is available.

    :param feature: The feature to check for.
    :returns: ``True`` if available, ``False`` if unavailable, ``None`` if unknown.
    :raises ValueError: If the feature is not defined in this version of Pillow.
    """
    if feature not in features:
        raise ValueError("Unknown feature %s" % feature)

    module, flag = features[feature]

    try:
        imported_module = __import__(module, fromlist=["PIL"])
        return getattr(imported_module, flag)
    except ImportError:
        return None


def get_supported_features():
    """
    :returns: A list of all supported features.
    """
    return [f for f in features if check_feature(f)]


def check(feature):
    """
    :param feature: A module, feature, or codec name.
    :returns:
        ``True`` if the module, feature, or codec is available,
        ``False`` or ``None`` otherwise.
    """

    if feature in modules:
        return check_module(feature)
    if feature in codecs:
        return check_codec(feature)
    if feature in features:
        return check_feature(feature)
    warnings.warn("Unknown feature '%s'." % feature, stacklevel=2)
    return False


def version(feature):
    if feature in modules:
        return version_module(feature)
    if feature in codecs:
        return version_codec(feature)
    return None


def get_supported():
    """
    :returns: A list of all supported modules, features, and codecs.
    """

    ret = get_supported_modules()
    ret.extend(get_supported_features())
    ret.extend(get_supported_codecs())
    return ret


def pilinfo(out=None, supported_formats=True):
    """
    Prints information about this installation of Pillow.
    This function can be called with ``python -m PIL``.

    :param out:
        The output stream to print to. Defaults to ``sys.stdout`` if ``None``.
    :param supported_formats:
        If ``True``, a list of all supported image file formats will be printed.
    """

    if out is None:
        out = sys.stdout

    Image.init()

    print("-" * 68, file=out)
    print("Pillow {}".format(PIL.__version__), file=out)
    py_version = sys.version.splitlines()
    print("Python {}".format(py_version[0].strip()), file=out)
    for py_version in py_version[1:]:
        print("       {}".format(py_version.strip()), file=out)
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
        ("libimagequant", "LIBIMAGEQUANT (Quantization method)"),
        ("xcb", "XCB (X protocol)"),
    ]:
        if check(name):
            v = version(name)
            if v is not None:
                support = "ok (version {})".format(v)
            else:
                support = "ok"
            print("---", feature, "support", support, file=out)
        else:
            print("***", feature, "support not installed", file=out)
    print("-" * 68, file=out)

    if supported_formats:
        extensions = collections.defaultdict(list)
        for ext, i in Image.EXTENSION.items():
            extensions[i].append(ext)

        for i in sorted(Image.ID):
            line = "{}".format(i)
            if i in Image.MIME:
                line = "{} {}".format(line, Image.MIME[i])
            print(line, file=out)

            if i in extensions:
                print(
                    "Extensions: {}".format(", ".join(sorted(extensions[i]))), file=out
                )

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
