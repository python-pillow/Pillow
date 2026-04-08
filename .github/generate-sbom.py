#!/usr/bin/env python3
"""Generate a CycloneDX 1.6 SBOM for Pillow's C extensions and their
vendored/optional native library dependencies.

Usage:
    python3 .github/generate-sbom.py [output-file]

Output defaults to pillow-{version}.cdx.json in the current directory.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


def get_version() -> str:
    version_file = Path(__file__).parent.parent / "src" / "PIL" / "_version.py"
    return version_file.read_text(encoding="utf-8").split('"')[1]


def generate(version: str) -> dict:
    serial = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    purl = f"pkg:pypi/pillow@{version}"

    metadata_component = {
        "bom-ref": purl,
        "type": "library",
        "name": "Pillow",
        "version": version,
        "description": "Python Imaging Library (fork)",
        "licenses": [{"license": {"id": "MIT-CMU"}}],
        "purl": purl,
        "externalReferences": [
            {"type": "website", "url": "https://python-pillow.github.io"},
            {"type": "vcs", "url": "https://github.com/python-pillow/Pillow"},
            {"type": "documentation", "url": "https://pillow.readthedocs.io"},
        ],
    }

    c_extensions = [
        (
            "PIL._imaging",
            "Core image processing extension "
            "(decode, encode, map, display, outline, path, libImaging)",
        ),
        ("PIL._imagingft", "FreeType font rendering extension"),
        ("PIL._imagingcms", "LittleCMS2 colour management extension"),
        ("PIL._webp", "WebP image format extension"),
        ("PIL._avif", "AVIF image format extension"),
        ("PIL._imagingtk", "Tk/Tcl display extension"),
        ("PIL._imagingmath", "Image math operations extension (via pybind11)"),
        ("PIL._imagingmorph", "Image morphology extension"),
    ]

    ext_components = [
        {
            "bom-ref": f"{purl}#c-ext/{name}",
            "type": "library",
            "name": name,
            "version": version,
            "description": desc,
            "licenses": [{"license": {"id": "MIT-CMU"}}],
            "purl": f"{purl}#c-ext/{name}",
        }
        for name, desc in c_extensions
    ]

    vendored_components = [
        {
            "bom-ref": "pkg:github/HOST-Oman/libraqm@0.10.3",
            "type": "library",
            "name": "raqm",
            "version": "0.10.3",
            "description": "Complex text layout library "
            "(vendored in src/thirdparty/raqm/)",
            "licenses": [{"license": {"id": "MIT"}}],
            "purl": "pkg:github/HOST-Oman/libraqm@0.10.3",
            "externalReferences": [
                {"type": "vcs", "url": "https://github.com/HOST-Oman/libraqm"},
            ],
        },
        {
            "bom-ref": f"{purl}#thirdparty/fribidi-shim",
            "type": "library",
            "name": "fribidi-shim",
            "version": "1.x",
            "description": "FriBiDi runtime-loading shim "
            "(vendored in src/thirdparty/fribidi-shim/); "
            "loads libfribidi dynamically",
            "licenses": [{"license": {"id": "LGPL-2.1-or-later"}}],
            "externalReferences": [
                {"type": "website", "url": "https://github.com/fribidi/fribidi"},
            ],
        },
        {
            "bom-ref": "pkg:github/python/pythoncapi-compat",
            "type": "library",
            "name": "pythoncapi_compat",
            "description": "Backport header for new CPython C-API functions "
            "(vendored in src/thirdparty/pythoncapi_compat.h)",
            "licenses": [{"license": {"id": "MIT-0"}}],
            "externalReferences": [
                {
                    "type": "vcs",
                    "url": "https://github.com/python/pythoncapi-compat",
                },
            ],
        },
    ]

    native_deps = [
        {
            "bom-ref": "pkg:generic/libjpeg",
            "type": "library",
            "name": "libjpeg / libjpeg-turbo",
            "description": "JPEG codec (required by default; disable with "
            "-C jpeg=disable). Tested with libjpeg 6b/8/9-9d "
            "and libjpeg-turbo 8.",
            "externalReferences": [
                {"type": "website", "url": "https://libjpeg-turbo.org"},
                {"type": "website", "url": "https://ijg.org"},
            ],
        },
        {
            "bom-ref": "pkg:generic/zlib",
            "type": "library",
            "name": "zlib",
            "description": "Deflate/PNG compression (required by default; "
            "disable with -C zlib=disable).",
            "externalReferences": [
                {"type": "website", "url": "https://zlib.net"},
            ],
        },
        {
            "bom-ref": "pkg:generic/libtiff",
            "type": "library",
            "name": "libtiff",
            "description": "TIFF codec (optional). Tested with libtiff 4.0-4.7.1.",
            "externalReferences": [
                {"type": "website", "url": "https://libtiff.gitlab.io/libtiff/"},
            ],
        },
        {
            "bom-ref": "pkg:generic/freetype2",
            "type": "library",
            "name": "FreeType",
            "description": "Font rendering (optional, used by PIL._imagingft). "
            "Required for text/font support.",
            "externalReferences": [
                {"type": "website", "url": "https://freetype.org"},
            ],
        },
        {
            "bom-ref": "pkg:generic/littlecms2",
            "type": "library",
            "name": "Little CMS 2",
            "description": "Colour management (optional, used by PIL._imagingcms). "
            "Tested with lcms2 2.7-2.18.",
            "externalReferences": [
                {"type": "website", "url": "https://www.littlecms.com"},
            ],
        },
        {
            "bom-ref": "pkg:generic/libwebp",
            "type": "library",
            "name": "libwebp",
            "description": "WebP codec (optional, used by PIL._webp).",
            "externalReferences": [
                {
                    "type": "website",
                    "url": "https://chromium.googlesource.com/webm/libwebp",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/openjpeg",
            "type": "library",
            "name": "OpenJPEG",
            "description": "JPEG 2000 codec (optional). "
            "Tested with openjpeg 2.0.0-2.5.4.",
            "externalReferences": [
                {"type": "website", "url": "https://www.openjpeg.org"},
            ],
        },
        {
            "bom-ref": "pkg:generic/libavif",
            "type": "library",
            "name": "libavif",
            "description": "AVIF codec (optional, used by PIL._avif). "
            "Requires libavif >= 1.0.0.",
            "externalReferences": [
                {"type": "website", "url": "https://github.com/AOMediaCodec/libavif"},
            ],
        },
        {
            "bom-ref": "pkg:generic/harfbuzz",
            "type": "library",
            "name": "HarfBuzz",
            "description": "Text shaping (optional, required by libraqm "
            "for complex text layout).",
            "externalReferences": [
                {"type": "website", "url": "https://harfbuzz.github.io"},
            ],
        },
        {
            "bom-ref": "pkg:generic/fribidi",
            "type": "library",
            "name": "FriBiDi",
            "description": "Unicode bidi algorithm library (optional, "
            "loaded at runtime by fribidi-shim).",
            "externalReferences": [
                {"type": "website", "url": "https://github.com/fribidi/fribidi"},
            ],
        },
        {
            "bom-ref": "pkg:generic/libimagequant",
            "type": "library",
            "name": "libimagequant",
            "description": "Improved colour quantization (optional). "
            "Tested with 2.6-4.4.1. NOTE: GPLv3 licensed.",
            "licenses": [{"license": {"id": "GPL-3.0-only"}}],
            "externalReferences": [
                {"type": "website", "url": "https://pngquant.org/lib/"},
            ],
        },
        {
            "bom-ref": "pkg:generic/libxcb",
            "type": "library",
            "name": "libxcb",
            "description": "X11 screen-grab support (optional, "
            "used by PIL._imagingtk on Linux).",
            "externalReferences": [
                {"type": "website", "url": "https://xcb.freedesktop.org"},
            ],
        },
        {
            "bom-ref": "pkg:pypi/pybind11",
            "type": "library",
            "name": "pybind11",
            "description": "C++/Python binding library "
            "(build-time dependency for PIL._imagingmath).",
            "externalReferences": [
                {"type": "website", "url": "https://pybind11.readthedocs.io"},
            ],
        },
    ]

    dependencies = [
        {
            "ref": purl,
            "dependsOn": [e["bom-ref"] for e in ext_components],
        },
        {
            "ref": f"{purl}#c-ext/PIL._imaging",
            "dependsOn": [
                "pkg:generic/libjpeg",
                "pkg:generic/zlib",
                "pkg:generic/libtiff",
                "pkg:generic/openjpeg",
            ],
        },
        {
            "ref": f"{purl}#c-ext/PIL._imagingft",
            "dependsOn": [
                "pkg:generic/freetype2",
                "pkg:github/HOST-Oman/libraqm@0.10.3",
                f"{purl}#thirdparty/fribidi-shim",
                "pkg:generic/harfbuzz",
                "pkg:generic/fribidi",
            ],
        },
        {
            "ref": f"{purl}#c-ext/PIL._imagingcms",
            "dependsOn": ["pkg:generic/littlecms2"],
        },
        {
            "ref": f"{purl}#c-ext/PIL._webp",
            "dependsOn": ["pkg:generic/libwebp"],
        },
        {
            "ref": f"{purl}#c-ext/PIL._avif",
            "dependsOn": ["pkg:generic/libavif"],
        },
        {
            "ref": f"{purl}#c-ext/PIL._imagingmath",
            "dependsOn": ["pkg:pypi/pybind11"],
        },
        {
            "ref": "pkg:github/HOST-Oman/libraqm@0.10.3",
            "dependsOn": [
                f"{purl}#thirdparty/fribidi-shim",
                "pkg:generic/harfbuzz",
            ],
        },
    ]

    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{serial}",
        "version": 1,
        "metadata": {
            "timestamp": now,
            "tools": [
                {
                    "type": "application",
                    "name": "generate-sbom.py",
                    "vendor": "Pillow",
                }
            ],
            "component": metadata_component,
        },
        "components": ext_components + vendored_components + native_deps,
        "dependencies": dependencies,
    }


if __name__ == "__main__":
    version = get_version()
    output = (
        Path(sys.argv[1]) if len(sys.argv) > 1 else Path(f"pillow-{version}.cdx.json")
    )
    sbom = generate(version)
    output.write_text(json.dumps(sbom, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output} (Pillow {version}, {len(sbom['components'])} components)")
