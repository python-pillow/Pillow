"""YAFF bitmap font file parser.

Parses .yaff font files into structured glyph data with kerning support.
See https://github.com/robhagemans/monobit for the YAFF specification.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import BinaryIO

from . import Image
from ._typing import StrOrBytesPath


@dataclass
class YaffGlyph:
    """A single glyph from a YAFF font."""

    image: Image.Image
    left_bearing: int = 0
    right_bearing: int = 0
    shift_up: int = 0
    right_kerning: dict[int, int] = field(default_factory=dict)
    left_kerning: dict[int, int] = field(default_factory=dict)


@dataclass
class YaffFontData:
    """Parsed data from a YAFF font file."""

    glyphs: dict[int, YaffGlyph]
    properties: dict[str, str]
    ascent: int
    descent: int
    line_height: int
    default_char: int | None
    global_left_bearing: int
    global_right_bearing: int
    global_shift_up: int


def _parse_label(label_str: str) -> list[int]:
    """Parse a glyph label string into a list of Unicode codepoints.

    Returns a list of codepoints. For single-codepoint labels, returns a
    one-element list. Returns an empty list for tag labels or unparseable labels.
    """
    label_str = label_str.strip()

    # Character label: u+XXXX or U+XXXX, possibly comma-separated
    if label_str.startswith(("u+", "U+")):
        parts = [p.strip() for p in label_str.split(",")]
        codepoints = []
        for part in parts:
            part = part.strip()
            if part.startswith(("u+", "U+")):
                try:
                    codepoints.append(int(part[2:], 16))
                except ValueError:
                    return []
            else:
                return []
        return codepoints

    # Character label: single-quoted string
    if label_str.startswith("'") and label_str.endswith("'") and len(label_str) >= 2:
        chars = label_str[1:-1]
        return [ord(c) for c in chars]

    # Tag label: double-quoted string — skip (no codepoint mapping)
    if label_str.startswith('"') and label_str.endswith('"'):
        return []

    # Codepoint label: starts with digit
    if label_str and label_str[0].isdigit():
        parts = [p.strip() for p in label_str.split(",")]
        codepoints = []
        for part in parts:
            part = part.strip()
            try:
                if part.startswith(("0x", "0X")):
                    codepoints.append(int(part, 16))
                elif part.startswith(("0o", "0O")):
                    codepoints.append(int(part, 8))
                else:
                    codepoints.append(int(part))
            except ValueError:
                return []
        return codepoints

    # Bare character (deprecated but supported)
    if len(label_str) == 1:
        return [ord(label_str)]

    return []


def _parse_kerning_label(label_str: str) -> int | None:
    """Parse a label in a kerning property value to a single codepoint."""
    cps = _parse_label(label_str)
    if len(cps) == 1:
        return cps[0]
    return None


def _parse_bitmap(rows: list[str]) -> Image.Image:
    """Convert rows of '@' and '.' characters to a mode '1' PIL Image."""
    if not rows:
        return Image.new("1", (0, 0))
    height = len(rows)
    width = len(rows[0])
    pixels: list[int] = []
    for row in rows:
        pixels.extend(1 if ch == "@" else 0 for ch in row)
    img = Image.new("1", (width, height))
    img.putdata(pixels)
    return img


def _parse_kerning_block(lines: list[str]) -> dict[int, int]:
    """Parse a multiline kerning property value.

    Each line has the format: <label> <integer>
    e.g., "u+0056 -2" or "0x69 -2"
    """
    kerning: dict[int, int] = {}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Split from the right to find the integer value
        match = re.match(r"(.+)\s+(-?\d+)$", line)
        if match:
            label_str = match.group(1).strip()
            value = int(match.group(2))
            cp = _parse_kerning_label(label_str)
            if cp is not None:
                kerning[cp] = value
    return kerning


def _is_label_line(line: str) -> bool:
    """Check if a line is a glyph label (ends with ':' and starts at column 0)."""
    stripped = line.rstrip()
    if not stripped or not stripped.endswith(":"):
        return False
    # Must not start with whitespace
    if line[0] in (" ", "\t"):
        return False
    # The part before ':' should look like a label
    content = stripped[:-1].strip()
    # Empty label (bare colon) is valid
    if not content:
        return True
    # Not a property — properties have values after ':'
    # Labels either: start with u+/U+, start with ', start with ", start with digit,
    # or are a single non-ASCII char
    if content.startswith(("u+", "U+", "'", '"')):
        return True
    if content and content[0].isdigit():
        return True
    # Single character (deprecated bare label)
    if len(content) == 1 and not content[0].isalpha():
        return True
    return False


def _normalize_key(key: str) -> str:
    """Normalize a property key: lowercase, replace '-' with '_'."""
    return key.lower().replace("-", "_")


def load(
    font: StrOrBytesPath | BinaryIO,
) -> YaffFontData:
    """Load a YAFF font file.

    :param font: Path to a .yaff file or a file-like object.
    :return: Parsed font data.
    :raises SyntaxError: If the file is not a valid YAFF font.
    """
    if hasattr(font, "read"):
        data = font.read()
        if isinstance(data, bytes):
            text = data.decode("utf-8-sig")
        else:
            text = data
    else:
        with open(font, encoding="utf-8-sig") as f:
            text = f.read()

    lines = text.splitlines()
    return _parse_yaff(lines)


def _parse_yaff(lines: list[str]) -> YaffFontData:
    """Parse YAFF content from a list of lines."""
    glyphs: dict[int, YaffGlyph] = {}
    properties: dict[str, str] = {}
    in_glyphs = False
    i = 0

    # First pass: separate global properties from glyph definitions
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip blank lines and comments
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        # Check if this is a label line (start of glyph section)
        if _is_label_line(line):
            in_glyphs = True
            break

        # Global property
        if not line[0].isspace() and ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()

            # Check for multiline value
            if not value:
                ml_lines = []
                i += 1
                while i < len(lines) and lines[i] and lines[i][0] in (" ", "\t"):
                    ml_lines.append(lines[i].strip())
                    i += 1
                value = "\n".join(ml_lines)
            else:
                i += 1

            properties[_normalize_key(key)] = value
            continue

        i += 1

    # Second pass: parse glyph definitions
    if in_glyphs:
        _parse_glyphs(lines, i, glyphs, properties)

    # Extract font metrics
    ascent = int(properties.get("ascent", "0"))
    descent = int(properties.get("descent", "0"))
    line_height = int(properties.get("line_height", "0"))

    global_left_bearing = int(properties.get("left_bearing", "0"))
    global_right_bearing = int(properties.get("right_bearing", "0"))
    global_shift_up = int(properties.get("shift_up", "0"))

    # Derive ascent/descent from glyph heights if not specified
    if not ascent and not descent and glyphs:
        max_height = max(g.image.height for g in glyphs.values() if g.image.height > 0)
        ascent = max_height
        descent = 0

    if not line_height:
        line_height = ascent + descent

    # Parse default-char
    default_char: int | None = None
    dc = properties.get("default_char")
    if dc is not None:
        cps = _parse_label(dc)
        if len(cps) == 1:
            default_char = cps[0]

    return YaffFontData(
        glyphs=glyphs,
        properties=properties,
        ascent=ascent,
        descent=descent,
        line_height=line_height,
        default_char=default_char,
        global_left_bearing=global_left_bearing,
        global_right_bearing=global_right_bearing,
        global_shift_up=global_shift_up,
    )


def _parse_glyphs(
    lines: list[str],
    start: int,
    glyphs: dict[int, YaffGlyph],
    properties: dict[str, str],
) -> None:
    """Parse all glyph definitions starting from line index `start`."""
    i = start
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Skip blank lines and comments
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        # Collect label lines
        if not _is_label_line(line):
            i += 1
            continue

        labels: list[str] = []
        while i < n and _is_label_line(lines[i]):
            label_part = lines[i].rstrip()[:-1].strip()  # Remove trailing ':'
            labels.append(label_part)
            i += 1

        # Collect indented glyph bitmap lines
        bitmap_rows: list[str] = []
        indent: str | None = None
        while i < n:
            raw = lines[i]
            if not raw or not raw[0].isspace():
                break
            content = raw.strip()
            if not content:
                break
            # Detect indent
            if indent is None:
                indent = raw[: len(raw) - len(raw.lstrip())]
            bitmap_rows.append(content)
            i += 1

        # Check for empty glyph
        is_empty = len(bitmap_rows) == 1 and bitmap_rows[0] == "-"

        # Skip blank lines between bitmap and per-glyph properties
        while i < n and not lines[i].strip():
            i += 1

        # Collect per-glyph properties (indented lines with ':')
        glyph_props: dict[str, str | list[str]] = {}
        while i < n:
            raw = lines[i]
            if not raw or not raw[0].isspace():
                break
            content = raw.strip()
            if not content:
                # Blank line within properties section — might separate property blocks
                # Peek ahead to see if more indented content follows
                j = i + 1
                while j < n and not lines[j].strip():
                    j += 1
                if j < n and lines[j] and lines[j][0].isspace():
                    i = j
                    continue
                break

            if ":" in content:
                key, _, value = content.partition(":")
                key = _normalize_key(key.strip())
                value = value.strip()

                if value:
                    glyph_props[key] = value
                else:
                    # Multiline property value (e.g., kerning)
                    ml_lines: list[str] = []
                    i += 1
                    while i < n and lines[i] and lines[i][0].isspace():
                        inner = lines[i].strip()
                        if not inner:
                            break
                        # Check if this is a new property (contains ':' with alpha key)
                        if ":" in inner and re.match(r"[a-zA-Z_-]", inner):
                            break
                        ml_lines.append(inner)
                        i += 1
                    glyph_props[key] = ml_lines
                    continue
            i += 1

        # Build glyph
        if is_empty:
            image = Image.new("1", (0, 0))
        else:
            if bitmap_rows:
                image = _parse_bitmap(bitmap_rows)
            else:
                image = Image.new("1", (0, 0))

        left_bearing = 0
        right_bearing = 0
        shift_up = 0

        if "left_bearing" in glyph_props:
            v = glyph_props["left_bearing"]
            if isinstance(v, str):
                left_bearing = int(v)

        if "right_bearing" in glyph_props:
            v = glyph_props["right_bearing"]
            if isinstance(v, str):
                right_bearing = int(v)

        if "shift_up" in glyph_props:
            v = glyph_props["shift_up"]
            if isinstance(v, str):
                shift_up = int(v)

        # Handle deprecated 'offset' property (left-bearing, shift-up pair)
        if "offset" in glyph_props:
            v = glyph_props["offset"]
            if isinstance(v, str):
                parts = v.split()
                if len(parts) == 2:
                    left_bearing = int(parts[0])
                    shift_up = int(parts[1])

        # Handle deprecated 'tracking' (= right-bearing)
        if "tracking" in glyph_props:
            v = glyph_props["tracking"]
            if isinstance(v, str):
                right_bearing = int(v)

        # Parse kerning
        right_kerning: dict[int, int] = {}
        left_kerning: dict[int, int] = {}

        if "right_kerning" in glyph_props:
            v = glyph_props["right_kerning"]
            if isinstance(v, list):
                right_kerning = _parse_kerning_block(v)
            elif isinstance(v, str):
                right_kerning = _parse_kerning_block([v])

        # Handle deprecated 'kern_to' (= right-kerning)
        if "kern_to" in glyph_props:
            v = glyph_props["kern_to"]
            if isinstance(v, list):
                right_kerning.update(_parse_kerning_block(v))
            elif isinstance(v, str):
                right_kerning.update(_parse_kerning_block([v]))

        if "left_kerning" in glyph_props:
            v = glyph_props["left_kerning"]
            if isinstance(v, list):
                left_kerning = _parse_kerning_block(v)
            elif isinstance(v, str):
                left_kerning = _parse_kerning_block([v])

        glyph = YaffGlyph(
            image=image,
            left_bearing=left_bearing,
            right_bearing=right_bearing,
            shift_up=shift_up,
            right_kerning=right_kerning,
            left_kerning=left_kerning,
        )

        # Register glyph under all its label codepoints
        for label in labels:
            codepoints = _parse_label(label)
            if len(codepoints) == 1:
                glyphs[codepoints[0]] = glyph
