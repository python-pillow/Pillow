#!/usr/bin/env python3
"""Generate a CycloneDX 1.7 SBOM for Pillow's C extensions and their
vendored/optional native library dependencies.

Usage:
    `python3 .github/generate-sbom.py [output-file]`

Output defaults to `pillow-{version}.cdx.json` in the current directory.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import difflib
import hashlib
import json
import urllib.request
import uuid
from pathlib import Path


class HelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter,
):
    pass


def get_version() -> str:
    version_file = Path(__file__).parent.parent / "src" / "PIL" / "_version.py"
    return version_file.read_text(encoding="utf-8").split('"')[1]


def load_dep_versions() -> dict[str, str]:
    deps_file = Path(__file__).parent / "dependencies.json"
    return json.loads(deps_file.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def upstream_diff_b64(
    upstream_url: str,
    upstream_display: bytes,
    local_path: Path,
    local_display: bytes,
) -> str:
    """
    Fetch an upstream file and return a base64-encoded unified diff vs the local copy.
    """
    with urllib.request.urlopen(upstream_url) as resp:
        upstream_text = resp.read()
    local_text = local_path.read_bytes()
    diff_lines = difflib.diff_bytes(
        difflib.unified_diff,
        upstream_text.splitlines(keepends=True),
        local_text.splitlines(keepends=True),
        fromfile=b"a/" + upstream_display,
        tofile=b"b/" + local_display,
    )
    return base64.b64encode(b"".join(diff_lines)).decode()


def generate(pillow_version: str, dep_versions: dict[str, str]) -> dict:
    serial = str(uuid.uuid4())
    now = dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    purl = f"pkg:pypi/pillow@{pillow_version}"
    root = Path(__file__).parent.parent
    thirdparty = root / "src" / "thirdparty"

    metadata_component = {
        "bom-ref": purl,
        "type": "library",
        "name": "Pillow",
        "version": pillow_version,
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
            "version": pillow_version,
            "description": desc,
            "licenses": [{"license": {"id": "MIT-CMU"}}],
            "purl": f"{purl}#c-ext/{name}",
        }
        for name, desc in c_extensions
    ]

    vendored_components = [
        {
            "bom-ref": f"{purl}#thirdparty/fribidi-shim",
            "type": "library",
            "name": "fribidi-shim",
            "version": "1.x",
            "description": "FriBiDi runtime-loading shim "
            "(vendored in src/thirdparty/fribidi-shim/); "
            "loads libfribidi dynamically",
            "licenses": [{"license": {"id": "MIT-CMU"}}],
            "hashes": [
                {
                    "alg": "SHA-256",
                    "content": sha256_file(thirdparty / "fribidi-shim" / "fribidi.c"),
                }
            ],
            "pedigree": {
                "notes": "Pillow-authored shim; not taken from an upstream project. "
                "fribidi.h declares the subset of FriBiDi's public API types, "
                "constants and function signatures needed to load libfribidi "
                "at runtime. No FriBiDi implementation code is included."
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
        {
            "bom-ref": f"{purl}#thirdparty/raqm",
            "type": "library",
            "name": "raqm",
            "version": "0.11.0",
            "description": "Complex text layout library "
            "(vendored in src/thirdparty/raqm/)",
            "licenses": [{"license": {"id": "MIT"}}],
            "hashes": [
                {
                    "alg": "SHA-256",
                    "content": sha256_file(thirdparty / "raqm" / "raqm.c"),
                }
            ],
            "pedigree": {
                "ancestors": [
                    {
                        "bom-ref": "pkg:github/HOST-Oman/libraqm@0.11.0#upstream",
                        "type": "library",
                        "name": "raqm",
                        "version": "0.11.0",
                        "purl": "pkg:github/HOST-Oman/libraqm@0.11.0",
                        "externalReferences": [
                            {
                                "type": "distribution",
                                "url": "https://github.com/HOST-Oman/libraqm/releases/tag/v0.11.0",
                            }
                        ],
                    }
                ],
                "patches": [
                    {
                        "type": "unofficial",
                        "diff": {
                            "text": {
                                # raqm-version.h.in → raqm-version.h:
                                # template @RAQM_VERSION_*@ placeholders replaced
                                # with literal 0.11.0 values; filename changed to
                                # drop the .in suffix.
                                "content": upstream_diff_b64(
                                    "https://raw.githubusercontent.com/HOST-Oman/libraqm/v0.11.0/src/raqm-version.h.in",
                                    b"src/raqm-version.h.in",
                                    thirdparty / "raqm" / "raqm-version.h",
                                    b"src/raqm-version.h",
                                ),
                                "encoding": "base64",
                            }
                        },
                    },
                    {
                        "type": "unofficial",
                        "diff": {
                            "text": {
                                # raqm.c: wrap the <fribidi.h> include in an
                                # #ifdef HAVE_FRIBIDI_SYSTEM guard so that when
                                # building without a system FriBiDi Pillow's own
                                # fribidi-shim is used instead.
                                "content": upstream_diff_b64(
                                    "https://raw.githubusercontent.com/HOST-Oman/libraqm/v0.11.0/src/raqm.c",
                                    b"src/raqm.c",
                                    thirdparty / "raqm" / "raqm.c",
                                    b"src/raqm.c",
                                ),
                                "encoding": "base64",
                            }
                        },
                    },
                ],
                "notes": (
                    "Vendored from upstream HOST-Oman/libraqm v0.11.0 with two "
                    "Pillow-specific modifications: (1) raqm-version.h.in was "
                    "pre-processed into raqm-version.h with version placeholders "
                    "replaced by literal values; (2) raqm.c wraps the <fribidi.h> "
                    "include in an #ifdef HAVE_FRIBIDI_SYSTEM guard so Pillow's "
                    "bundled fribidi-shim is used when a system FriBiDi is absent."
                ),
            },
            "externalReferences": [
                {
                    "type": "vcs",
                    "url": "https://github.com/python-pillow/Pillow/tree/main/src/thirdparty/raqm",
                },
            ],
        },
    ]

    native_deps = [
        {
            "bom-ref": "pkg:generic/freetype2",
            "type": "library",
            "name": "FreeType",
            "version": dep_versions.pop("freetype").replace("-", "."),
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
            "bom-ref": "pkg:generic/brotli",
            "type": "library",
            "name": "Brotli",
            "version": dep_versions.pop("brotli"),
            "scope": "optional",
            "description": "Lossless compression algorithm. "
            "Required for WOFF2 font support.",
            "licenses": [{"license": {"id": "MIT"}}],
            "externalReferences": [
                {"type": "website", "url": "https://brotli.org"},
                {
                    "type": "distribution",
                    "url": "https://github.com/google/brotli/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/bzip2",
            "type": "library",
            "name": "bzip2",
            "version": dep_versions.pop("bzip2"),
            "scope": "optional",
            "description": "bzip2 compression (optional, used by FreeType for "
            "compressed fonts; built for Linux wheels only).",
            "licenses": [{"license": {"id": "bzip2-1.0.6"}}],
            "externalReferences": [
                {"type": "website", "url": "https://sourceware.org/bzip2/"},
                {
                    "type": "distribution",
                    "url": "https://sourceware.org/pub/bzip2/",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/fribidi",
            "type": "library",
            "name": "FriBiDi",
            "version": dep_versions.pop("fribidi"),
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
            "bom-ref": "pkg:generic/harfbuzz",
            "type": "library",
            "name": "HarfBuzz",
            "version": dep_versions.pop("harfbuzz"),
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
            "version": dep_versions.pop("libavif"),
            "scope": "optional",
            "description": "AVIF codec (optional, used by PIL._avif).",
            "licenses": [{"license": {"id": "BSD-2-Clause"}}],
            "pedigree": {
                "ancestors": [
                    {
                        "bom-ref": "pkg:github/aomediacodec/libavif@1.4.2#upstream",
                        "type": "library",
                        "name": "libavif",
                        "version": "1.4.2",
                        "purl": "pkg:github/aomediacodec/libavif@1.4.2",
                        "externalReferences": [
                            {
                                "type": "distribution",
                                "url": "https://github.com/AOMediaCodec/libavif/releases/tag/v1.4.2",
                            }
                        ],
                    }
                ],
                "patches": [
                    {
                        "type": "unofficial",
                        "diff": {
                            "text": {
                                # partially apply https://github.com/AOMediaCodec/libavif/pull/3460/changes/c81f7ecfa0f13786b15336961686300781144beb
                                "content": base64.b64encode(
                                    (
                                        Path(__file__).parent.parent
                                        / "patches"
                                        / "libavif.patch"
                                    ).read_bytes()
                                ).decode(),
                                "encoding": "base64",
                            }
                        },
                    },
                ],
                "notes": (
                    "Vendored from upstream libavif 1.4.2, "
                    "patched to use dav1d 1.5.5 on Windows."
                ),
            },
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
            "version": dep_versions.pop("libimagequant"),
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
            "name": "libjpeg-turbo",
            "version": dep_versions.pop("jpegturbo"),
            "description": "JPEG codec, a libjpeg-compatible replacement for libjpeg "
            "(required by default; disable with -C jpeg=disable).",
            "licenses": [
                {"license": {"id": "IJG"}},
                {"license": {"id": "BSD-3-Clause"}},
            ],
            "externalReferences": [
                {"type": "website", "url": "https://libjpeg-turbo.org"},
                {
                    "type": "distribution",
                    "url": "https://github.com/libjpeg-turbo/libjpeg-turbo/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/libpng",
            "type": "library",
            "name": "libpng",
            "version": dep_versions.pop("libpng"),
            "scope": "optional",
            "description": "PNG codec (optional, used by FreeType for "
            "PNG-embedded bitmap fonts).",
            "licenses": [{"license": {"id": "libpng-2.0"}}],
            "externalReferences": [
                {
                    "type": "website",
                    "url": "https://www.libpng.org/pub/png/libpng.html",
                },
                {
                    "type": "distribution",
                    "url": "https://sourceforge.net/projects/libpng/files/",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/libtiff",
            "type": "library",
            "name": "libtiff",
            "version": dep_versions.pop("tiff"),
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
            "version": dep_versions.pop("libwebp"),
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
            "version": dep_versions.pop("libxcb"),
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
            "version": dep_versions.pop("lcms2"),
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
            "version": dep_versions.pop("openjpeg"),
            "scope": "optional",
            "description": "JPEG 2000 codec (optional).",
            "licenses": [{"license": {"id": "BSD-2-Clause"}}],
            "pedigree": {
                "ancestors": [
                    {
                        "bom-ref": "pkg:generic/openjpeg@2.5.4#upstream",
                        "type": "library",
                        "name": "OpenJPEG",
                        "version": "2.5.4",
                        "purl": "pkg:generic/openjpeg@2.5.4",
                        "externalReferences": [
                            {
                                "type": "distribution",
                                "url": "https://github.com/uclouvain/openjpeg/releases/tag/v2.5.4",
                            }
                        ],
                    }
                ],
                "patches": [
                    {
                        "type": "cherry-pick",
                        "diff": {
                            "text": {
                                # apply https://github.com/uclouvain/openjpeg/commit/91d08b11a72764f6d199f32fa0c1b1abd4edc2ad
                                "content": base64.b64encode(
                                    (
                                        Path(__file__).parent.parent
                                        / "patches"
                                        / "v2.5.4.tar.gz.patch"
                                    ).read_bytes()
                                ).decode(),
                                "encoding": "base64",
                            }
                        },
                    },
                ],
                "notes": (
                    "Vendored from upstream openjpeg 2.5.4 with commits from master "
                    "cherry-picked to fix OSV-2025-219 and CVE-2026-6192."
                ),
            },
            "externalReferences": [
                {"type": "website", "url": "https://www.openjpeg.org"},
                {
                    "type": "distribution",
                    "url": "https://github.com/uclouvain/openjpeg/releases",
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
            "bom-ref": "pkg:generic/xz",
            "type": "library",
            "name": "XZ Utils (liblzma)",
            "version": dep_versions.pop("xz"),
            "scope": "optional",
            "description": "LZMA compression (optional, used by libtiff).",
            "licenses": [{"license": {"id": "0BSD"}}],
            "externalReferences": [
                {
                    "type": "website",
                    "url": "https://tukaani.org/xz/",
                },
                {
                    "type": "distribution",
                    "url": "https://github.com/tukaani-project/xz/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/zlib",
            "type": "library",
            "name": "zlib-ng",
            "version": dep_versions.pop("zlib-ng"),
            "description": "Deflate/PNG compression, built in zlib-compatible mode "
            "as a replacement for zlib (required by default; "
            "disable with -C zlib=disable).",
            "licenses": [{"license": {"id": "Zlib"}}],
            "externalReferences": [
                {
                    "type": "website",
                    "url": "https://github.com/zlib-ng/zlib-ng",
                },
                {
                    "type": "distribution",
                    "url": "https://github.com/zlib-ng/zlib-ng/releases",
                },
            ],
        },
        {
            "bom-ref": "pkg:generic/zstd",
            "type": "library",
            "name": "Zstandard",
            "version": dep_versions.pop("zstd"),
            "scope": "optional",
            "description": "Zstandard compression (optional, used by libtiff; "
            "built for Linux wheels only).",
            "licenses": [{"expression": "BSD-3-Clause OR GPL-2.0-only"}],
            "externalReferences": [
                {
                    "type": "website",
                    "url": "https://meta.github.io/zstd/",
                },
                {
                    "type": "distribution",
                    "url": "https://github.com/meta/zstd/releases",
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
                "pkg:generic/fribidi",
                "pkg:generic/harfbuzz",
                f"{purl}#thirdparty/fribidi-shim",
                f"{purl}#thirdparty/raqm",
            ],
        },
        {
            "ref": f"{purl}#c-ext/PIL._webp",
            "dependsOn": ["pkg:generic/libwebp"],
        },
        {
            "ref": f"{purl}#thirdparty/raqm",
            "dependsOn": [
                "pkg:generic/harfbuzz",
                f"{purl}#thirdparty/fribidi-shim",
            ],
        },
        {
            "ref": "pkg:generic/freetype2",
            "dependsOn": [
                "pkg:generic/brotli",
                "pkg:generic/bzip2",
                "pkg:generic/libpng",
            ],
        },
        {
            "ref": "pkg:generic/libtiff",
            "dependsOn": [
                "pkg:generic/libjpeg",
                "pkg:generic/xz",
                "pkg:generic/zlib",
                "pkg:generic/zstd",
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
    pillow_version = get_version()

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=HelpFormatter)
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        default=Path(f"pillow-{pillow_version}.cdx.json"),
        help="output file",
    )
    args = parser.parse_args()

    dep_versions = load_dep_versions()
    sbom = generate(pillow_version, dep_versions)
    if dep_versions:
        parser.error(
            "In .github/dependencies.json but not in the SBOM: "
            f"{', '.join(sorted(dep_versions))}. "
            "Add to .github/generate-sbom.py"
        )
    args.output.write_text(json.dumps(sbom, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {args.output} "
        f"(Pillow {pillow_version}, {len(sbom['components'])} components)"
    )


if __name__ == "__main__":
    main()
