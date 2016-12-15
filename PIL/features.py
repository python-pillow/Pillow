from PIL import Image

modules = {
    "pil": "PIL._imaging",
    "tkinter": "PIL._imagingtk",
    "freetype2": "PIL._imagingft",
    "littlecms2": "PIL._imagingcms",
    "webp": "PIL._webp",
    "transp_webp": ("WEBP", "WebPDecoderBuggyAlpha")
}


def check_module(feature):
    if feature not in modules:
        raise ValueError("Unknown module %s" % feature)

    module = modules[feature]

    method_to_call = None
    if isinstance(module, tuple):
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
    for feature in modules:
        if check_module(feature):
            supported_modules.append(feature)
    return supported_modules

codecs = {
    "jpg": "jpeg",
    "jpg_2000": "jpeg2k",
    "zlib": "zip",
    "libtiff": "libtiff"
}


def check_codec(feature):
    if feature not in codecs:
        raise ValueError("Unknown codec %s" % feature)

    codec = codecs[feature]

    return codec + "_encoder" in dir(Image.core)


def get_supported_codecs():
    supported_codecs = []
    for feature in codecs:
        if check_codec(feature):
            supported_codecs.append(feature)
    return supported_codecs
