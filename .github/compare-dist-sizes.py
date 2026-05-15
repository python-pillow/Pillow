"""Compare sizes of newly-built dists against the latest release on PyPI.

Fetches file sizes for the latest Pillow release from the PyPI JSON API
(no download required) and compares them to a directory of freshly-built
wheels and sdist. Outputs a table to stdout (and to
`$GITHUB_STEP_SUMMARY` if set).

Usage:
    `uv run .github/compare-dist-sizes.py <dist-dir>`
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "humanize",
#     "prettytable",
#     "termcolor",
# ]
# ///

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

import humanize
from prettytable import PrettyTable, TableStyle
from termcolor import colored

PYPI_JSON_URL = "https://pypi.org/pypi/pillow/json"

# Wheel filename: {distribution}-{version}(-{build})?-{python}-{abi}-{platform}.whl
# sdist filename: {distribution}-{version}.tar.gz
WHEEL_RE = re.compile(
    r"^[^-]+-[^-]+(?:-(?P<build>\d[^-]*))?"
    r"-(?P<python>[^-]+)-(?P<abi>[^-]+)-(?P<platform>[^-]+)\.whl$",
    re.IGNORECASE,
)
SDIST_RE = re.compile(
    r"^(?P<dist>[^-]+)-(?P<version>.+)\.tar\.gz$",
    re.IGNORECASE,
)


def key_for(filename: str) -> str:
    """Return a version-independent identifier for a dist file."""
    if m := WHEEL_RE.match(filename):
        build = f"{m['build']}-" if m["build"] else ""
        return f"wheel:{build}{m['python']}-{m['abi']}-{m['platform']}"
    if SDIST_RE.match(filename):
        return "sdist"
    msg = f"Unexpected dist name: {filename}"
    raise ValueError(msg)


def display_for(filename: str) -> str:
    """Strip the `pillow-{version}-` prefix for compact table display."""
    if m := WHEEL_RE.match(filename):
        build = f"{m['build']}-" if m["build"] else ""
        return f"{build}{m['python']}-{m['abi']}-{m['platform']}.whl"
    if SDIST_RE.match(filename):
        return "sdist (.tar.gz)"
    return filename


def fetch_pypi_sizes() -> tuple[str, dict[str, tuple[str, int]]]:
    """Return (version, {key: (filename, size)}) for the latest PyPI release."""
    with urllib.request.urlopen(PYPI_JSON_URL) as response:
        data = json.load(response)
    version = data["info"]["version"]
    sizes: dict[str, tuple[str, int]] = {}
    for entry in data.get("urls", []):
        filename = entry["filename"]
        key = key_for(filename)
        sizes[key] = (filename, entry["size"])
    return version, sizes


def collect_local_sizes(dist_dir: Path) -> dict[str, tuple[str, int]]:
    sizes: dict[str, tuple[str, int]] = {}
    for path in sorted(dist_dir.iterdir()):
        if not path.is_file():
            continue
        key = key_for(path.name)
        sizes[key] = (path.name, path.stat().st_size)
    return sizes


def human(n: int | None) -> str:
    if n is None:
        return "n/a"
    return humanize.naturalsize(n)


def pct_change(before: int | None, after: int | None) -> str:
    if before is None or after is None:
        return "n/a"
    delta = 0 if before == 0 else (after - before) / before * 100
    return f"{delta:+.2f}%"


def pct_severity(text: str) -> dict[str, str] | None:
    """Return status indicators based on the change percent."""
    if text == "n/a":
        return None
    pct = float(text.rstrip("%"))
    if pct >= 5:
        return {"color": "red", "emoji": "🔴"}
    if pct > 0:
        return {"color": "yellow", "emoji": "🟡"}
    else:
        return {"color": "green", "emoji": "🟢"}


def render_table(
    baseline_label: str,
    baseline_sizes: dict[str, tuple[str, int]],
    local_sizes: dict[str, tuple[str, int]],
    *,
    markdown: bool,
) -> str:
    table = PrettyTable()
    table.set_style(TableStyle.MARKDOWN if markdown else TableStyle.SINGLE_BORDER)
    table.field_names = ["File", "Size before", "Size now", "Change"]
    table.align = "r"
    table.align["File"] = "l"

    def style(cells: list[str], role: str) -> list[str]:
        severity = pct_severity(cells[3])
        if markdown:
            if severity:
                cells[3] = f"{severity['emoji']} {cells[3]}"
            if role == "orphan":
                return [f"*{c}*" for c in cells]
            if role == "summary":
                return [f"**{c}**" for c in cells]
            return cells

        if role == "orphan":
            return [colored(c, "dark_grey") for c in cells]

        bold_attrs = ["bold"] if role == "summary" else []
        if bold_attrs:
            cells[:3] = [colored(c, attrs=bold_attrs) for c in cells[:3]]
        if severity:
            cells[3] = colored(cells[3], severity["color"], attrs=bold_attrs)
        elif bold_attrs:
            cells[3] = colored(cells[3], attrs=bold_attrs)
        return cells

    keys = list(set(baseline_sizes) | set(local_sizes))
    # Put sdist first for readability
    keys.sort(key=lambda k: (k != "sdist", k))

    wheel_before = []
    wheel_after = []
    total_before = []
    total_after = []
    for key in keys:
        baseline_entry = baseline_sizes.get(key)
        local_entry = local_sizes.get(key)
        display_name = display_for((local_entry or baseline_entry)[0])
        before = baseline_entry[1] if baseline_entry else None
        after = local_entry[1] if local_entry else None
        if after is None:
            # Removed since baseline: ignore in totals
            role = "orphan"
        else:
            # Present locally (in both, or newly added): count in totals
            total_after.append(after)
            if before is not None:
                total_before.append(before)
            if key != "sdist":
                wheel_after.append(after)
                if before is not None:
                    wheel_before.append(before)
            role = "data"
        cells = [
            display_name,
            human(before),
            human(after),
            pct_change(before, after),
        ]
        table.add_row(style(cells, role))

    if not markdown:
        table.add_divider()

    if wheel_after:
        avg_before = sum(wheel_before) // len(wheel_before) if wheel_before else None
        table.add_row(
            style(
                [
                    f"wheel average ({len(wheel_after)} wheels)",
                    human(avg_before),
                    human(sum(wheel_after) // len(wheel_after)),
                    pct_change(avg_before, sum(wheel_after) // len(wheel_after)),
                ],
                "summary",
            )
        )
        table.add_row(
            style(
                [
                    f"wheel total ({len(wheel_after)} wheels)",
                    human(sum(wheel_before)),
                    human(sum(wheel_after)),
                    pct_change(sum(wheel_before), sum(wheel_after)),
                ],
                "summary",
            ),
            divider=not markdown,
        )

    if total_after:
        table.add_row(
            style(
                [
                    f"artifacts total ({len(total_after)} artifacts)",
                    human(sum(total_before)),
                    human(sum(total_after)),
                    pct_change(sum(total_before), sum(total_after)),
                ],
                "summary",
            )
        )

    title = f"## Dist size comparison vs {baseline_label}"
    if not markdown:
        title = colored(title, attrs=["bold"])
    return f"{title}\n\n{table.get_string()}\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "dist_dir",
        type=Path,
        help="Directory containing newly-built wheels and sdist",
    )
    args = parser.parse_args()

    if not args.dist_dir.is_dir():
        print(f"error: {args.dist_dir} is not a directory", file=sys.stderr)
        return 1

    baseline_version, baseline_sizes = fetch_pypi_sizes()
    baseline_label = f"Pillow {baseline_version} on PyPI"

    local_sizes = collect_local_sizes(args.dist_dir)

    print(render_table(baseline_label, baseline_sizes, local_sizes, markdown=False))

    if summary_path := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(
                render_table(baseline_label, baseline_sizes, local_sizes, markdown=True)
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
