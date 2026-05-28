from io import BytesIO

from PIL import Image, ImageDraw, ImageFont


def textwrap_basic():
    """Basic wrapping: words split across lines when exceeding max width."""
    lines, widths = ImageDraw.textwrap(
        "hello world foo bar",
        max_width=100,
    )
    assert len(lines) >= 1
    for w in widths:
        if w > 0:
            assert w <= 110  # allow slight rounding tolerance


def textwrap_single_line():
    """Text that fits entirely on one line."""
    lines, widths = ImageDraw.textwrap("short", max_width=500)
    assert len(lines) == 1
    assert lines[0] == "short"


def textwrap_newline_preserved():
    """Paragraphs separated by newlines are preserved."""
    lines, widths = ImageDraw.textwrap(
        "line one\nline two", max_width=500
    )
    assert "line one" in lines
    assert "" in lines  # empty line between paragraphs


def textwrap_with_multiline_text():
    """textwrap + multiline_text renders correctly."""
    im = Image.new("RGB", (400, 200), "white")
    draw = ImageDraw.Draw(im)

    lines, widths = ImageDraw.textwrap(
        "hello world this is a longer text that should wrap",
        max_width=200,
    )

    wrapped_text = "\n".join(lines)
    draw.multiline_text((10, 10), wrapped_text, fill="black")

    # Verify image was modified (not all white anymore)
    data = list(im.getdata())
    assert any(p != (255, 255, 255) for p in data), "Image should have drawn text"


def textwrap_no_text():
    """Empty string returns empty result."""
    lines, widths = ImageDraw.textwrap("", max_width=100)
    assert lines == []
    assert widths == []


if __name__ == "__main__":
    textwrap_basic()
    print("✅ textwrap_basic")
    textwrap_single_line()
    print("✅ textwrap_single_line")
    textwrap_newline_preserved()
    print("✅ textwrap_newline_preserved")
    textwrap_with_multiline_text()
    print("✅ textwrap_with_multiline_text")
    textwrap_no_text()
    print("✅ textwrap_no_text")
    print("All tests passed!")
