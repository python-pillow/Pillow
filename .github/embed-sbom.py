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
import sys
import zipfile
from pathlib import Path


def record_entry(path: str, data: bytes) -> str:
    """Build a RECORD line: `path,sha256=<base64url-nopad>,<size>`."""
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest())
    return f"{path},sha256={digest.rstrip(b'=').decode()},{len(data)}"


def embed(wheel: Path, sbom_name: str, sbom_bytes: bytes) -> None:
    with zipfile.ZipFile(wheel) as zf:
        infos = zf.infolist()
        contents = {info.filename: zf.read(info.filename) for info in infos}

    record_name = next(
        name
        for name in contents
        if name.endswith(".dist-info/RECORD") and name.count("/") == 1
    )
    dist_info = record_name.rsplit("/", 1)[0]
    sbom_path = f"{dist_info}/sboms/{sbom_name}"

    # Append a matching RECORD line for the SBOM (RECORD's own line has no hash).
    lines = contents[record_name].decode("utf-8").splitlines()
    lines.append(record_entry(sbom_path, sbom_bytes))
    contents[record_name] = ("\n".join(lines) + "\n").encode("utf-8")

    tmp = wheel.with_name(wheel.name + ".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
        # Re-use each original ZipInfo to preserve timestamps, mode bits and
        # compression; only RECORD's contents change.
        for info in infos:
            zf.writestr(info, contents[info.filename])
        zf.writestr(sbom_path, sbom_bytes)
    tmp.replace(wheel)


def load_sbom(path: Path) -> tuple[str, bytes]:
    """Read the SBOM; `path` may be the file or a directory containing one."""
    if path.is_dir():
        candidates = list(path.glob("*.cdx.json"))
        if len(candidates) != 1:
            msg = f"expected exactly one *.cdx.json in {path}, found {len(candidates)}"
            raise SystemExit(msg)
        path = candidates[0]
    return path.name, path.read_bytes()


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

    sbom_name, sbom_bytes = load_sbom(args.sbom)

    wheels = sorted(args.wheelhouse.glob("*.whl"))
    if not wheels:
        print(f"error: no wheels found in {args.wheelhouse}", file=sys.stderr)
        raise SystemExit(1)

    for wheel in wheels:
        embed(wheel, sbom_name, sbom_bytes)
        print(f"Embedded {sbom_name} in {wheel.name}")


if __name__ == "__main__":
    main()
