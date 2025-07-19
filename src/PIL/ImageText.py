from __future__ import annotations

from typing import AnyStr

from . import ImageFont
from ._typing import _Ink


class ImageText:
    def __init__(
        self,
        text: AnyStr,
        font: (
            ImageFont.ImageFont
            | ImageFont.FreeTypeFont
            | ImageFont.TransposedFont
            | None
        ) = None,
        mode: str = "RGB",
        spacing: float = 4,
        direction: str | None = None,
        features: list[str] | None = None,
        language: str | None = None,
    ) -> None:
        self.text = text.encode() if isinstance(text, str) else text
        self.font = font or ImageFont.load_default()

        self.mode = mode
        self.spacing = spacing
        self.direction = direction
        self.features = features
        self.language = language

        self.embedded_color = False

        self.stroke_width: float = 0
        self.stroke_fill: _Ink | None = None

    def embed_color(self) -> None:
        if self.mode not in ("RGB", "RGBA"):
            msg = "Embedded color supported only in RGB and RGBA modes"
            raise ValueError(msg)
        self.embedded_color = True

    def stroke(self, width: float = 0, fill: _Ink | None = None) -> None:
        self.stroke_width = width
        self.stroke_fill = fill

    def _get_fontmode(self) -> str:
        if self.mode in ("1", "P", "I", "F"):
            return "1"
        elif self.embedded_color:
            return "RGBA"
        else:
            return "L"

    def get_length(self):
        if b"\n" in self.text:
            msg = "can't measure length of multiline text"
            raise ValueError(msg)
        return self.font.getlength(
            self.text,
            self._get_fontmode(),
            self.direction,
            self.features,
            self.language,
        )

    def _split(
        self, xy: tuple[float, float], anchor: str | None, align: str = "left"
    ) -> list[tuple[tuple[float, float], str, bytes]]:
        if anchor is None:
            anchor = "lt" if self.direction == "ttb" else "la"
        elif len(anchor) != 2:
            msg = "anchor must be a 2 character string"
            raise ValueError(msg)

        lines = self.text.split(b"\n")
        if len(lines) == 1:
            return [(xy, anchor, self.text)]

        if anchor[1] in "tb" and self.direction != "ttb":
            msg = "anchor not supported for multiline text"
            raise ValueError(msg)

        fontmode = self._get_fontmode()
        line_spacing = (
            self.font.getbbox(
                "A",
                fontmode,
                self.direction,
                self.features,
                self.language,
                self.stroke_width,
            )[3]
            + self.stroke_width
            + self.spacing
        )

        top = xy[1]
        parts = []
        if self.direction == "ttb":
            left = xy[0]
            for line in lines:
                parts.append(((left, top), anchor, line))
                left += line_spacing
        else:
            widths = []
            max_width: float = 0
            for line in lines:
                line_width = self.font.getlength(
                    line, fontmode, self.direction, self.features, self.language
                )
                widths.append(line_width)
                max_width = max(max_width, line_width)

            if anchor[1] == "m":
                top -= (len(lines) - 1) * line_spacing / 2.0
            elif anchor[1] == "d":
                top -= (len(lines) - 1) * line_spacing

            for idx, line in enumerate(lines):
                left = xy[0]
                width_difference = max_width - widths[idx]

                # align by align parameter
                if align in ("left", "justify"):
                    pass
                elif align == "center":
                    left += width_difference / 2.0
                elif align == "right":
                    left += width_difference
                else:
                    msg = 'align must be "left", "center", "right" or "justify"'
                    raise ValueError(msg)

                if (
                    align == "justify"
                    and width_difference != 0
                    and idx != len(lines) - 1
                ):
                    words = line.split(b" ")
                    if len(words) > 1:
                        # align left by anchor
                        if anchor[0] == "m":
                            left -= max_width / 2.0
                        elif anchor[0] == "r":
                            left -= max_width

                        word_widths = [
                            self.font.getlength(
                                word,
                                fontmode,
                                self.direction,
                                self.features,
                                self.language,
                            )
                            for word in words
                        ]
                        word_anchor = "l" + anchor[1]
                        width_difference = max_width - sum(word_widths)
                        for i, word in enumerate(words):
                            parts.append(((left, top), word_anchor, word))
                            left += word_widths[i] + width_difference / (len(words) - 1)
                        top += line_spacing
                        continue

                # align left by anchor
                if anchor[0] == "m":
                    left -= width_difference / 2.0
                elif anchor[0] == "r":
                    left -= width_difference
                parts.append(((left, top), anchor, line))
                top += line_spacing

        return parts

    def get_bbox(
        self, xy: tuple[float, float] = (0, 0), anchor: str | None = None
    ) -> tuple[float, float, float, float]:
        bbox: tuple[float, float, float, float] | None = None
        fontmode = self._get_fontmode()
        for xy, anchor, line in self._split(xy, anchor):
            bbox_line = self.font.getbbox(
                line,
                fontmode,
                self.direction,
                self.features,
                self.language,
                self.stroke_width,
                anchor,
            )
            bbox_line = (
                bbox_line[0] + xy[0],
                bbox_line[1] + xy[1],
                bbox_line[2] + xy[0],
                bbox_line[3] + xy[1],
            )
            if bbox is None:
                bbox = bbox_line
            else:
                bbox = (
                    min(bbox[0], bbox_line[0]),
                    min(bbox[1], bbox_line[1]),
                    max(bbox[2], bbox_line[2]),
                    max(bbox[3], bbox_line[3]),
                )

        if bbox is None:
            return xy[0], xy[1], xy[0], xy[1]
        return bbox
