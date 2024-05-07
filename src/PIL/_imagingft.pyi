from typing import Any, TypedDict

class _Axis(TypedDict):
    minimum: int | None
    default: int | None
    maximum: int | None
    name: str | None

class Font:
    @property
    def family(self) -> str | None: ...
    @property
    def style(self) -> str | None: ...
    @property
    def ascent(self) -> int: ...
    @property
    def descent(self) -> int: ...
    @property
    def height(self) -> int: ...
    @property
    def x_ppem(self) -> int: ...
    @property
    def y_ppem(self) -> int: ...
    @property
    def glyphs(self) -> int: ...
    def render(
        self,
        string: str,
        fill,
        mode=...,
        dir=...,
        features=...,
        lang=...,
        stroke_width=...,
        anchor=...,
        foreground_ink_long=...,
        x_start=...,
        y_start=...,
        /,
    ) -> tuple[Any, tuple[int, int]]: ...
    def getsize(
        self, string: str, mode=..., dir=..., features=..., lang=..., anchor=..., /
    ) -> tuple[tuple[int, int], tuple[int, int]]: ...
    def getlength(
        self, string: str, mode=..., dir=..., features=..., lang=..., /
    ) -> int: ...
    def getvarnames(self) -> list[str]: ...
    def getvaraxes(self) -> list[_Axis]: ...
    def setvarname(self, instance_index: int, /) -> None: ...
    def setvaraxes(self, axes: list[float], /) -> None: ...

def getfont(
    filename: str | bytes | bytearray,
    size,
    index=...,
    encoding=...,
    font_bytes=...,
    layout_engine=...,
) -> Font: ...
def __getattr__(name: str) -> Any: ...
