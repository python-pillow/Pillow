"""
Proof of concept for planar multiband images.

See ``docs/reference/multiband_design.rst``. This module is private and
experimental. It may change or be removed at any time without deprecation.

A planar image stores each band as a separate single-band core image
(``L``, ``I;16``, ``I`` or ``F``), plus metadata describing each band.
Operations that treat bands independently are applied to each plane.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import Image, ImageFilter, ImageMath

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

MODE = "planar"
MAX_BANDS = 256

SAMPLE_TYPES = {"uint8": "L", "uint16": "I;16", "int32": "I", "float32": "F"}
ROLES = ("color", "alpha", "extra")

# Value of a fully opaque alpha sample, by sample type
_ALPHA_MAX = {"uint8": 255.0, "uint16": 65535.0, "float32": 1.0}


@dataclass(frozen=True)
class Band:
    name: str
    type: str
    role: str = "color"

    def __post_init__(self) -> None:
        if self.type not in SAMPLE_TYPES:
            msg = f"unknown sample type: {self.type}"
            raise ValueError(msg)
        if self.role not in ROLES:
            msg = f"unknown band role: {self.role}"
            raise ValueError(msg)


# Band metadata for existing modes: colorspace, premultiplied, roles
_MODES: dict[str, tuple[str, bool, tuple[str, ...]]] = {
    "L": ("L", False, ("color",)),
    "LA": ("L", False, ("color", "alpha")),
    "La": ("L", True, ("color", "alpha")),
    "RGB": ("RGB", False, ("color",) * 3),
    "RGBA": ("RGB", False, ("color",) * 3 + ("alpha",)),
    "RGBa": ("RGB", True, ("color",) * 3 + ("alpha",)),
    "RGBX": ("RGB", False, ("color",) * 3 + ("extra",)),
    "CMYK": ("CMYK", False, ("color",) * 4),
    "YCbCr": ("YCbCr", False, ("color",) * 3),
    "LAB": ("LAB", False, ("color",) * 3),
    "HSV": ("HSV", False, ("color",) * 3),
    "I;16": ("L", False, ("color",)),
    "I": ("L", False, ("color",)),
    "F": ("L", False, ("color",)),
}


def bands_for_mode(mode: str) -> tuple[tuple[Band, ...], str, bool]:
    """
    Describes an existing mode as band metadata.

    :returns: A tuple of the bands, the colorspace and whether alpha is
        premultiplied.
    """
    if mode not in _MODES:
        msg = f"mode {mode} cannot be described as planar bands"
        raise ValueError(msg)
    colorspace, premultiplied, roles = _MODES[mode]
    sample_type = "uint8"
    for t, plane_mode in SAMPLE_TYPES.items():
        if plane_mode == mode:
            sample_type = t
    names = Image.getmodebandnames(mode)
    bands = tuple(Band(n, sample_type, r) for n, r in zip(names, roles))
    return bands, colorspace, premultiplied


class PlanarImage:
    """
    An image made of single-band planes of the same size.

    The planes are used as given, not copied. Operations return new images.
    """

    def __init__(
        self,
        planes: Sequence[Image.Image],
        bands: Sequence[Band],
        colorspace: str,
        premultiplied: bool = False,
    ) -> None:
        if not 1 <= len(planes) <= MAX_BANDS:
            msg = f"number of bands must be between 1 and {MAX_BANDS}"
            raise ValueError(msg)
        if len(planes) != len(bands):
            msg = "number of planes and bands must match"
            raise ValueError(msg)
        if len({band.name for band in bands}) != len(bands):
            msg = "band names must be unique"
            raise ValueError(msg)
        for plane, band in zip(planes, bands):
            if plane.mode != SAMPLE_TYPES[band.type]:
                msg = (
                    f"band {band.name} is {band.type}, "
                    f"but its plane has mode {plane.mode}"
                )
                raise ValueError(msg)
            if plane.size != planes[0].size:
                msg = "planes must all be the same size"
                raise ValueError(msg)
        alpha = [i for i, band in enumerate(bands) if band.role == "alpha"]
        if len(alpha) > 1:
            msg = "only one alpha band is supported"
            raise ValueError(msg)
        if premultiplied and not alpha:
            msg = "premultiplied images must have an alpha band"
            raise ValueError(msg)

        self.planes = tuple(planes)
        self.bands = tuple(bands)
        self.colorspace = colorspace
        self.premultiplied = premultiplied
        self._alpha = alpha[0] if alpha else None

    @classmethod
    def new(
        cls,
        size: tuple[int, int],
        bands: Sequence[Band],
        colorspace: str,
        color: Sequence[float] | None = None,
        premultiplied: bool = False,
    ) -> PlanarImage:
        if color is None:
            color = (0,) * len(bands)
        if len(color) != len(bands):
            msg = "color must have one value per band"
            raise ValueError(msg)
        planes = [
            Image.new(SAMPLE_TYPES[band.type], size, value)
            for band, value in zip(bands, color)
        ]
        return cls(planes, bands, colorspace, premultiplied)

    @classmethod
    def from_image(cls, im: Image.Image) -> PlanarImage:
        bands, colorspace, premultiplied = bands_for_mode(im.mode)
        return cls(im.split(), bands, colorspace, premultiplied)

    def to_image(self) -> Image.Image:
        """
        Converts to an existing mode, if one matches the bands exactly.
        """
        for mode in _MODES:
            if bands_for_mode(mode) == (
                self.bands,
                self.colorspace,
                self.premultiplied,
            ):
                if len(self.planes) == 1:
                    return self.planes[0].copy()
                return Image.merge(mode, self.planes)
        msg = "no existing mode matches these bands"
        raise ValueError(msg)

    def __repr__(self) -> str:
        bands = ", ".join(f"{band.name}:{band.type}" for band in self.bands)
        return (
            f"<{self.__class__.__name__} {self.colorspace} ({bands}) "
            f"size={self.width}x{self.height}>"
        )

    @property
    def mode(self) -> str:
        return MODE

    @property
    def size(self) -> tuple[int, int]:
        return self.planes[0].size

    @property
    def width(self) -> int:
        return self.size[0]

    @property
    def height(self) -> int:
        return self.size[1]

    def getbands(self) -> tuple[str, ...]:
        return tuple(band.name for band in self.bands)

    def _index(self, band: int | str) -> int:
        if isinstance(band, str):
            return self.getbands().index(band)
        return band

    def getband(self, band: int | str) -> Image.Image:
        return self.planes[self._index(band)].copy()

    def split(self) -> tuple[Image.Image, ...]:
        return tuple(plane.copy() for plane in self.planes)

    def copy(self) -> PlanarImage:
        return self._map(lambda plane: plane.copy())

    def getpixel(self, xy: tuple[int, int]) -> tuple[float, ...]:
        values = []
        for plane in self.planes:
            value = plane.getpixel(xy)
            assert isinstance(value, (int, float))
            values.append(value)
        return tuple(values)

    def putpixel(self, xy: tuple[int, int], value: Sequence[float]) -> None:
        if len(value) != len(self.planes):
            msg = "value must have one entry per band"
            raise ValueError(msg)
        for plane, v in zip(self.planes, value):
            plane.putpixel(xy, v)

    def _map(self, op: Callable[[Image.Image], Image.Image]) -> PlanarImage:
        return PlanarImage(
            [op(plane) for plane in self.planes],
            self.bands,
            self.colorspace,
            self.premultiplied,
        )

    def _resample(
        self, op: Callable[[Image.Image], Image.Image], resample: int
    ) -> PlanarImage:
        """
        Applies an operation that blends neighboring pixels.

        With straight alpha, color bands are premultiplied first, so that
        the color of transparent pixels does not bleed into the result.
        """
        if (
            self._alpha is None
            or self.premultiplied
            or resample == Image.Resampling.NEAREST
        ):
            return self._map(op)

        alpha_band = self.bands[self._alpha]
        if alpha_band.type not in _ALPHA_MAX:
            msg = f"{alpha_band.type} alpha bands are not supported"
            raise ValueError(msg)
        alpha_max = _ALPHA_MAX[alpha_band.type]
        if self.planes[self._alpha].getextrema() == (alpha_max, alpha_max):
            # Fully opaque, so premultiplying would not change anything
            return self._map(op)
        alpha = self.planes[self._alpha].convert("F")
        new_alpha = op(self.planes[self._alpha])
        # Divide by the unrounded alpha, so opaque colors stay exact
        new_alpha_f = op(alpha)

        planes = []
        for plane, band in zip(self.planes, self.bands):
            if band.role == "alpha":
                planes.append(new_alpha)
            elif band.role == "extra":
                planes.append(op(plane))
            else:
                premultiplied = ImageMath.lambda_eval(
                    lambda args: args["c"] * args["a"] / alpha_max,
                    c=plane.convert("F"),
                    a=alpha,
                )
                assert isinstance(premultiplied, Image.Image)
                # Division by zero gives zero, for fully transparent pixels
                straight = ImageMath.lambda_eval(
                    lambda args: args["c"] * alpha_max / args["a"],
                    c=op(premultiplied),
                    a=new_alpha_f,
                )
                assert isinstance(straight, Image.Image)
                planes.append(_from_float(straight, band.type))
        return PlanarImage(planes, self.bands, self.colorspace)

    def crop(self, box: tuple[int, int, int, int]) -> PlanarImage:
        return self._map(lambda plane: plane.crop(box))

    def transpose(self, method: Image.Transpose) -> PlanarImage:
        return self._map(lambda plane: plane.transpose(method))

    def resize(
        self,
        size: tuple[int, int],
        resample: int = Image.Resampling.BICUBIC,
        box: tuple[float, float, float, float] | None = None,
    ) -> PlanarImage:
        return self._resample(lambda plane: plane.resize(size, resample, box), resample)

    def rotate(
        self,
        angle: float,
        resample: Image.Resampling = Image.Resampling.NEAREST,
        expand: bool = False,
    ) -> PlanarImage:
        return self._resample(
            lambda plane: plane.rotate(angle, resample, expand), resample
        )

    def filter(self, filter: ImageFilter.Filter) -> PlanarImage:
        return self._map(lambda plane: plane.filter(filter))


def _from_float(im: Image.Image, sample_type: str) -> Image.Image:
    """Converts an ``F`` image to a sample type, rounding and clipping."""
    if sample_type == "float32":
        return im
    # Conversions from F truncate, so add 0.5 to round non-negative values
    rounded = ImageMath.lambda_eval(lambda args: args["x"] + 0.5, x=im)
    assert isinstance(rounded, Image.Image)
    if sample_type == "uint8":
        return rounded.convert("L")
    # F to I;16 clips at 255, so convert through I
    converted = rounded.convert("I")
    return converted.convert("I;16") if sample_type == "uint16" else converted
