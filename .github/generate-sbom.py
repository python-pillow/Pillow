#!/usr/bin/env python3
"""Generate a CycloneDX 1.7 SBOM for Pillow's C extensions and their
vendored/optional native library dependencies.

Usage:
    python3 .github/generate-sbom.py [output-file]

Output defaults to pillow-{version}.cdx.json in the current directory.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
import uuid
from pathlib import Path


def get_version() -> str:
    version_file = Path(__file__).parent.parent / "src" / "PIL" / "_version.py"
    return version_file.read_text(encoding="utf-8").split('"')[1]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate(version: str) -> dict:
    serial = str(uuid.uuid4())
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    purl = f"pkg:pypi/pillow@{version}"
    root = Path(__file__).parent.parent
    thirdparty = root / "src" / "thirdparty"

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
            "hashes": [
                {
                    "alg": "SHA-256",
                    "content": sha256_file(thirdparty / "raqm" / "raqm.c"),
                }
            ],
            "pedigree": {
                "notes": "Vendored unmodified from upstream HOST-Oman/libraqm v0.10.3."
            },
            "externalReferences": [
                {"type": "vcs", "url": "https://github.com/HOST-Oman/libraqm"},
                {
                    "type": "distribution",
                    "url": "https://github.com/HOST-Oman/libraqm/releases/tag/v0.10.3",
                },
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
            "hashes": [
                {
                    "alg": "SHA-256",
                    "content": sha256_file(thirdparty / "fribidi-shim" / "fribidi.c"),
                }
            ],
            "pedigree": {
                "notes": "Pillow-authored shim; not taken from an upstream project."
            },
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
            "hashes": [
                {
                    "alg": "SHA-256",
                    "content": sha256_file(thirdparty / "pythoncapi_compat.h"),
                }
            ],
            "pedigree": {
                "notes": "Vendored unmodified from upstream python/pythoncapi-compat."
            },
            "externalReferences": [
                {
                    "type": "vcs",
                    "url": "https://github.com/python/pythoncapi-compat",
                },
                {
                    "type": "distribution",
                    "url": "https://github.com/python/pythoncapi-compat/releases",
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
            "and libjpeg-turbo 2-3.",
            "licenses": [
                {"license": {"id": "IJG"}},
                {"license": {"id": "BSD-3-Clause"}},
            ],
            "externalReferences": [
                {"type": "website", "url": "https://libjpeg-turbo.org"},
                {"type": "website", "url": "https://ijg.org"},
                {
                    "type": "distribution",
                    "url": "https://github.com/libjpeg-turbo/libjpeg-turbo/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/zlib",
            "type": "library",
            "name": "zlib",
            "description": "Deflate/PNG compression (required by default; "
            "disable with -C zlib=disable).",
            "licenses": [{"license": {"id": "Zlib"}}],
            "externalReferences": [
                {"type": "website", "url": "https://zlib.net"},
                {"type": "distribution", "url": "https://zlib.net/"},
            ],
        },
        {
            "bom-ref": "pkg:generic/libtiff",
            "type": "library",
            "name": "libtiff",
            "scope": "optional",
            "description": "TIFF codec (optional). Tested with libtiff 4.0-4.7.1.",
            "licenses": [{"license": {"id": "HPND"}}],
            "externalReferences": [
                {"type": "website", "url": "https://libtiff.gitlab.io/libtiff/"},
                {
                    "type": "distribution",
                    "url": "https://download.osgeo.org/libtiff/",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/freetype2",
            "type": "library",
            "name": "FreeType",
            "scope": "optional",
            "description": "Font rendering (optional, used by PIL._imagingft). "
            "Required for text/font support.",
            "licenses": [{"license": {"id": "FTL"}}],
            "externalReferences": [
                {"type": "website", "url": "https://freetype.org"},
                {
                    "type": "distribution",
                    "url": "https://download.savannah.gnu.org/releases/freetype/",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/littlecms2",
            "type": "library",
            "name": "Little CMS 2",
            "scope": "optional",
            "description": "Colour management (optional, used by PIL._imagingcms). "
            "Tested with lcms2 2.7-2.18.",
            "licenses": [{"license": {"id": "MIT"}}],
            "externalReferences": [
                {"type": "website", "url": "https://www.littlecms.com"},
                {
                    "type": "distribution",
                    "url": "https://github.com/mm2/Little-CMS/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/libwebp",
            "type": "library",
            "name": "libwebp",
            "scope": "optional",
            "description": "WebP codec (optional, used by PIL._webp).",
            "licenses": [{"license": {"id": "BSD-3-Clause"}}],
            "externalReferences": [
                {
                    "type": "website",
                    "url": "https://chromium.googlesource.com/webm/libwebp",
                },
                {
                    "type": "distribution",
                    "url": "https://chromium.googlesource.com/webm/libwebp",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/openjpeg",
            "type": "library",
            "name": "OpenJPEG",
            "scope": "optional",
            "description": "JPEG 2000 codec (optional). "
            "Tested with openjpeg 2.0.0-2.5.4.",
            "licenses": [{"license": {"id": "BSD-2-Clause"}}],
            "externalReferences": [
                {"type": "website", "url": "https://www.openjpeg.org"},
                {
                    "type": "distribution",
                    "url": "https://github.com/uclouvain/openjpeg/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/libavif",
            "type": "library",
            "name": "libavif",
            "scope": "optional",
            "description": "AVIF codec (optional, used by PIL._avif). "
            "Requires libavif >= 1.0.0.",
            "licenses": [{"license": {"id": "BSD-2-Clause"}}],
            "externalReferences": [
                {"type": "website", "url": "https://github.com/AOMediaCodec/libavif"},
                {
                    "type": "distribution",
                    "url": "https://github.com/AOMediaCodec/libavif/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/harfbuzz",
            "type": "library",
            "name": "HarfBuzz",
            "scope": "optional",
            "description": "Text shaping (optional, required by libraqm "
            "for complex text layout).",
            "licenses": [{"license": {"id": "MIT"}}],
            "externalReferences": [
                {"type": "website", "url": "https://harfbuzz.github.io"},
                {
                    "type": "distribution",
                    "url": "https://github.com/harfbuzz/harfbuzz/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/fribidi",
            "type": "library",
            "name": "FriBiDi",
            "scope": "optional",
            "description": "Unicode bidi algorithm library (optional, "
            "loaded at runtime by fribidi-shim).",
            "licenses": [{"license": {"id": "LGPL-2.1-or-later"}}],
            "externalReferences": [
                {"type": "website", "url": "https://github.com/fribidi/fribidi"},
                {
                    "type": "distribution",
                    "url": "https://github.com/fribidi/fribidi/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/libimagequant",
            "type": "library",
            "name": "libimagequant",
            "scope": "optional",
            "description": "Improved colour quantization (optional). "
            "Tested with 2.6-4.4.1. NOTE: GPLv3 licensed.",
            "licenses": [{"license": {"id": "GPL-3.0-only"}}],
            "externalReferences": [
                {"type": "website", "url": "https://pngquant.org/lib/"},
                {
                    "type": "distribution",
                    "url": "https://github.com/ImageOptim/libimagequant/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/libxcb",
            "type": "library",
            "name": "libxcb",
            "scope": "optional",
            "description": "X11 screen-grab support (optional, "
            "used by PIL._imagingtk on Linux).",
            "licenses": [{"license": {"id": "MIT"}}],
            "externalReferences": [
                {"type": "website", "url": "https://xcb.freedesktop.org"},
                {
                    "type": "distribution",
                    "url": "https://xcb.freedesktop.org/dist/",
                },
            ],
        },
        {
            "bom-ref": "pkg:pypi/pybind11",
            "type": "library",
            "name": "pybind11",
            "scope": "optional",
            "description": "C++/Python binding library "
            "(build-time dependency for PIL._imagingmath).",
            "licenses": [{"license": {"id": "BSD-3-Clause"}}],
            "externalReferences": [
                {"type": "website", "url": "https://pybind11.readthedocs.io"},
                {
                    "type": "distribution",
                    "url": "https://github.com/pybind/pybind11/releases",
                },
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
        "specVersion": "1.7",
        "serialNumber": f"urn:uuid:{serial}",
        "version": 1,
        "metadata": {
            "timestamp": now,
            "lifecycles": [{"phase": "build"}],
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
