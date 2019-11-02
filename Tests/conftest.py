def pytest_report_header(config):
    import os

    report = []

    def append(*args):
        report.append(" ".join(args))

    try:
        from PIL import Image, features

        append("-" * 68)
        append("Pillow", Image.__version__)
        append("-" * 68)
        append("Python modules loaded from", os.path.dirname(Image.__file__))
        append("Binary modules loaded from", os.path.dirname(Image.core.__file__))
        append("-" * 68)
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
            if features.check(name):
                append("---", feature, "support ok")
            else:
                append("***", feature, "support not installed")
        append("-" * 68)
    except Exception as e:
        return "pytest_report_header failed: %s" % str(e)
    return "\n".join(report)
