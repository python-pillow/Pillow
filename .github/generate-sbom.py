#!/usr/bin/env python3
"""Generate a CycloneDX 1.7 SBOM for Pillow's C extensions and their
vendored/optional native library dependencies.

Usage:
    python3 .github/generate-sbom.py [output-file]

Output defaults to pillow-{version}.cdx.json in the current directory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import uuid
from pathlib import Path


def get_version() -> str:
    version_file = Path(__file__).parent.parent / "src" / "PIL" / "_version.py"
    return version_file.read_text(encoding="utf-8").split('"')[1]


def load_dep_versions() -> dict[str, str]:
    deps_file = Path(__file__).parent / "dependencies.json"
    return json.loads(deps_file.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate(version: str) -> dict:
    serial = str(uuid.uuid4())
    now = dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    purl = f"pkg:pypi/pillow@{version}"
    root = Path(__file__).parent.parent
    thirdparty = root / "src" / "thirdparty"
    versions = load_dep_versions()

    metadata_component = {
        "bom-ref": purl,
        "type": "library",
        "name": "Pillow",
        "version": version,
        "description": "Python Imaging Library (fork)",
        "licenses": [{"license": {"id": "MIT-CMU"}}],
        "purl": purl,
        "externalReferences": [
            {"type": "website", "url": "https://python-pillow.org"},
            {"type": "vcs", "url": "https://github.com/python-pillow/Pillow"},
            {"type": "documentation", "url": "https://pillow.readthedocs.io"},
            {
                "type": "security-contact",
                "url": "https://github.com/python-pillow/Pillow/security/policy",
            },
        ],
    }

    c_extensions = [
        ("PIL._avif", "AVIF image format extension"),
        (
            "PIL._imaging",
            (
                "Core image processing extension "
                "(decode, encode, map, display, outline, path, libImaging)"
            ),
        ),
        ("PIL._imagingcms", "LittleCMS2 colour management extension"),
        ("PIL._imagingft", "FreeType font rendering extension"),
        ("PIL._imagingmath", "Image math operations extension"),
        ("PIL._imagingmorph", "Image morphology extension"),
        ("PIL._imagingtk", "Tk/Tcl display extension"),
        ("PIL._webp", "WebP image format extension"),
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
            "bom-ref": "pkg:github/python/pythoncapi-compat",
            "type": "library",
            "name": "pythoncapi_compat",
            "description": "Backport header for new CPython C-API functions "
            "(vendored in src/thirdparty/pythoncapi_compat.h)",
            "licenses": [{"license": {"id": "0BSD"}}],
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
            ],
        },
    ]

    native_deps = [
        {
            "bom-ref": "pkg:generic/freetype2",
            "type": "library",
            "name": "FreeType",
            "version": versions["freetype"],
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
            "bom-ref": "pkg:generic/harfbuzz",
            "type": "library",
            "name": "HarfBuzz",
            "version": versions["harfbuzz"],
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
            "bom-ref": "pkg:generic/libavif",
            "type": "library",
            "name": "libavif",
            "version": versions["libavif"],
            "scope": "optional",
            "description": "AVIF codec (optional, used by PIL._avif).",
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
            "bom-ref": "pkg:generic/libimagequant",
            "type": "library",
            "name": "libimagequant",
            "version": versions["libimagequant"],
            "scope": "optional",
            "description": "Improved colour quantization (optional).",
            "licenses": [{"license": {"id": "GPL-3.0-or-later"}}],
            "externalReferences": [
                {"type": "website", "url": "https://pngquant.org/lib/"},
                {
                    "type": "distribution",
                    "url": "https://github.com/ImageOptim/libimagequant/tags",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/libjpeg",
            "type": "library",
            "name": "libjpeg / libjpeg-turbo",
            "version": versions["jpegturbo"],
            "description": "JPEG codec (required by default; disable with "
            "-C jpeg=disable).",
            "licenses": [
                {"license": {"id": "IJG"}},
                {"license": {"id": "BSD-3-Clause"}},
            ],
            "externalReferences": [
                {"type": "website", "url": "https://ijg.org"},
                {"type": "website", "url": "https://libjpeg-turbo.org"},
                {
                    "type": "distribution",
                    "url": "https://github.com/libjpeg-turbo/libjpeg-turbo/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/libtiff",
            "type": "library",
            "name": "libtiff",
            "version": versions["tiff"],
            "scope": "optional",
            "description": "TIFF codec (optional).",
            "licenses": [{"license": {"id": "libtiff"}}],
            "externalReferences": [
                {"type": "website", "url": "https://libtiff.gitlab.io/libtiff/"},
                {
                    "type": "distribution",
                    "url": "https://download.osgeo.org/libtiff/",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/libwebp",
            "type": "library",
            "name": "libwebp",
            "version": versions["libwebp"],
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
            "bom-ref": "pkg:generic/libxcb",
            "type": "library",
            "name": "libxcb",
            "version": versions["libxcb"],
            "scope": "optional",
            "description": "X11 screen-grab support (optional, "
            "used by PIL._imaging on macOS and Linux).",
            "licenses": [{"license": {"id": "X11"}}],
            "externalReferences": [
                {"type": "website", "url": "https://xcb.freedesktop.org"},
                {
                    "type": "distribution",
                    "url": "https://xcb.freedesktop.org/dist/",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/littlecms2",
            "type": "library",
            "name": "Little CMS 2",
            "version": versions["lcms2"],
            "scope": "optional",
            "description": "Colour management (optional, used by PIL._imagingcms).",
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
            "bom-ref": "pkg:generic/openjpeg",
            "type": "library",
            "name": "OpenJPEG",
            "version": versions["openjpeg"],
            "scope": "optional",
            "description": "JPEG 2000 codec (optional).",
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
            "bom-ref": "pkg:generic/raqm",
            "type": "library",
            "name": "Raqm",
            "version": versions["raqm"],
            "scope": "optional",
            "description": "Complex text layout (optional, used by PIL._imagingft).",
            "licenses": [{"license": {"id": "MIT"}}],
            "externalReferences": [
                {"type": "website", "url": "https://github.com/HOST-Oman/libraqm"},
                {
                    "type": "distribution",
                    "url": "https://github.com/HOST-Oman/libraqm/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/sheenbidi",
            "type": "library",
            "name": "SheenBidi",
            "version": versions["sheenbidi"],
            "scope": "optional",
            "description": "Unicode bidirectional algorithm (optional, required "
            "by libraqm for bidirectional text).",
            "licenses": [{"license": {"id": "Apache-2.0"}}],
            "externalReferences": [
                {"type": "website", "url": "https://github.com/Tehreer/SheenBidi"},
                {
                    "type": "distribution",
                    "url": "https://github.com/Tehreer/SheenBidi/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:pypi/pybind11",
            "type": "library",
            "name": "pybind11",
            "scope": "excluded",
            "description": "Parallel C compilation library (build-time dependency).",
            "licenses": [{"license": {"id": "BSD-3-Clause"}}],
            "externalReferences": [
                {"type": "website", "url": "https://pybind11.readthedocs.io"},
                {
                    "type": "distribution",
                    "url": "https://github.com/pybind/pybind11/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/zlib",
            "type": "library",
            "name": "zlib",
            "version": versions["zlib-ng"],
            "description": "Deflate/PNG compression (required by default; "
            "disable with -C zlib=disable).",
            "licenses": [{"license": {"id": "Zlib"}}],
            "externalReferences": [
                {"type": "website", "url": "https://zlib.net"},
                {"type": "distribution", "url": "https://zlib.net"},
            ],
        },
    ]

    dependencies = [
        {
            "ref": purl,
            "dependsOn": [e["bom-ref"] for e in ext_components],
        },
        {
            "ref": f"{purl}#c-ext/PIL._avif",
            "dependsOn": ["pkg:generic/libavif"],
        },
        {
            "ref": f"{purl}#c-ext/PIL._imaging",
            "dependsOn": [
                "pkg:generic/libimagequant",
                "pkg:generic/libjpeg",
                "pkg:generic/libtiff",
                "pkg:generic/libxcb",
                "pkg:generic/openjpeg",
                "pkg:generic/zlib",
            ],
        },
        {
            "ref": f"{purl}#c-ext/PIL._imagingcms",
            "dependsOn": ["pkg:generic/littlecms2"],
        },
        {
            "ref": f"{purl}#c-ext/PIL._imagingft",
            "dependsOn": [
                "pkg:generic/freetype2",
                "pkg:generic/raqm",
            ],
        },
        {
            "ref": f"{purl}#c-ext/PIL._webp",
            "dependsOn": ["pkg:generic/libwebp"],
        },
        {
            "ref": "pkg:generic/raqm",
            "dependsOn": [
                "pkg:generic/freetype2",
                "pkg:generic/harfbuzz",
                "pkg:generic/sheenbidi",
            ],
        },
    ]

    return {
        "$schema": "http://cyclonedx.org/schema/bom-1.7.schema.json",
        "bomFormat": "CycloneDX",
        "specVersion": "1.7",
        "serialNumber": f"urn:uuid:{serial}",
        "version": 1,
        "metadata": {
            "timestamp": now,
            "lifecycles": [{"phase": "build"}],
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "name": "generate-sbom.py",
                        "group": "pillow",
                    }
                ]
            },
            "component": metadata_component,
        },
        "components": ext_components + vendored_components + native_deps,
        "dependencies": dependencies,
    }


def main() -> None:
    version = get_version()

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        default=Path(f"pillow-{version}.cdx.json"),
        help="output file",
    )
    args = parser.parse_args()

    sbom = generate(version)
    args.output.write_text(json.dumps(sbom, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {args.output} (Pillow {version}, {len(sbom['components'])} components)"
    )


if __name__ == "__main__":
    main()
