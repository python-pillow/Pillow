from PIL import Image

modules = {
    "PIL CORE": "PIL._imaging",
    "TKINTER": "PIL._imagingtk",
    "FREETYPE2": "PIL._imagingft",
    "LITTLECMS2": "PIL._imagingcms",
    "WEBP": "PIL._webp",
    "Transparent WEBP": ("WEBP", "WebPDecoderBuggyAlpha")
}


def check_module(feature):
    module = modules[feature]

    method_to_call = None
    if type(module) is tuple:
        module, method_to_call = module

    try:
        imported_module = __import__(module)
    except ImportError:
        # If a method is being checked, None means that
        # rather than the method failing, the module required for the method
        # failed to be imported first
        return None if method_to_call else False

    if method_to_call:
        method = getattr(imported_module, method_to_call)
        return method() is True
    else:
        return True


def get_supported_modules():
    supported_modules = []
    for feature in get_all_modules():
        if check_module(feature):
            supported_modules.append(feature)
    return supported_modules


def get_all_modules():
    # While the dictionary keys could be used here,
    # a static list is used to maintain order
    return ["PIL CORE", "TKINTER", "FREETYPE2",
            "LITTLECMS2", "WEBP", "Transparent WEBP"]

codecs = {
    "JPEG": "jpeg",
    "JPEG 2000": "jpeg2k",
    "ZLIB (PNG/ZIP)": "zip",
    "LIBTIFF": "libtiff"
}


def check_codec(feature):
    codec = codecs[feature]
    return codec + "_encoder" in dir(Image.core)


def get_supported_codecs():
    supported_codecs = []
    for feature in get_all_codecs():
        if check_codec(feature):
            supported_codecs.append(feature)
    return supported_codecs


def get_all_codecs():
    return ["JPEG", "JPEG 2000", "ZLIB (PNG/ZIP)", "LIBTIFF"]
