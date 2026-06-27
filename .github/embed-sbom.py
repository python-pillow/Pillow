"""Embed Pillow's SBOM into each wheel's `.dist-info/sboms/` directory,
as specified by PEP 770.

The SBOM (produced by `generate-sbom.py`) is injected into every `.whl` in
the given directory, updating each wheel's `RECORD` so the result remains a
valid, installable wheel.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import zipfile
from pathlib import Path


def record_entry(path: str, data: bytes) -> bytes:
    """Build a RECORD line: `path,sha256=<base64url-nopad>,<size>`."""
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest())
    return (
        path.encode("utf-8")
        + b",sha256="
        + digest.rstrip(b"=")
        + b","
        + str(len(data)).encode()
    )


def embed(wheel: Path, sbom: Path) -> None:
    with zipfile.ZipFile(wheel) as zf:
        infos = zf.infolist()
        contents = {info.filename: zf.read(info.filename) for info in infos}

    record_name = next(
        name
        for name in contents
        if name.endswith(".dist-info/RECORD") and name.count("/") == 1
    )
    dist_info = record_name.split("/", 1)[0]

    sbom_bytes = sbom.read_bytes()
    sbom_path = f"{dist_info}/sboms/{sbom.name}"

    # Append a matching RECORD line for the SBOM (RECORD's own line has no hash).
    lines = contents[record_name].splitlines()
    lines.append(record_entry(sbom_path, sbom_bytes))
    contents[record_name] = b"\n".join(lines) + b"\n"

    with zipfile.ZipFile(wheel, "w", zipfile.ZIP_DEFLATED) as zf:
        # Re-use each original ZipInfo to preserve timestamps, mode bits and
        # compression; only RECORD's contents change
        for info in infos:
            zf.writestr(info, contents[info.filename])
        zf.writestr(sbom_path, sbom_bytes)

    print(f"Embedded {sbom.name} in {wheel.name}")


def scan_dir(path: Path) -> Path:
    """If `path` is a directory, return the path of the SBOM within."""
    if path.is_dir():
        candidates = list(path.glob("*.cdx.json"))
        if len(candidates) != 1:
            msg = f"expected exactly one *.cdx.json in {path}, found {len(candidates)}"
            raise SystemExit(msg)
        return candidates[0]
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "wheelhouse", type=Path, help="directory of wheels to embed the SBOM into"
    )
    parser.add_argument(
        "sbom",
        type=Path,
        help="SBOM file, or a directory containing a single `.cdx.json`",
    )
    args = parser.parse_args()

    sbom = scan_dir(args.sbom)

    wheels = sorted(args.wheelhouse.glob("*.whl"))
    if not wheels:
        parser.error(f"no wheels found in {args.wheelhouse}")

    for wheel in wheels:
        embed(wheel, sbom)


if __name__ == "__main__":
    main()
