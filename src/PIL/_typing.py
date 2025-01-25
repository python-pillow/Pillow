from __future__ import annotations

import os
import sys
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, Union, Literal

if TYPE_CHECKING:
    from numbers import _IntegralLike as IntegralLike

    try:
        import numpy.typing as npt

        NumpyArray = npt.NDArray[Any]  # requires numpy>=1.21
    except (ImportError, AttributeError):
        pass

if sys.version_info >= (3, 13):
    from types import CapsuleType
else:
    CapsuleType = object

if sys.version_info >= (3, 12):
    from collections.abc import Buffer
else:
    Buffer = Any

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    try:
        from typing_extensions import TypeGuard
    except ImportError:

        class TypeGuard:  # type: ignore[no-redef]
            def __class_getitem__(cls, item: Any) -> type[bool]:
                return bool


Coords = Union[Sequence[float], Sequence[Sequence[float]]]


_T_co = TypeVar("_T_co", covariant=True)


class SupportsRead(Protocol[_T_co]):
    def read(self, length: int = ..., /) -> _T_co: ...


StrOrBytesPath = Union[str, bytes, os.PathLike[str], os.PathLike[bytes]]

horizontal_anchors = ("l", "m", "r", "s")
vertical_anchors = ("a", "t", "m", "s", "b", "d")
Anchor = Literal[*(horizontal_anchor + vertical_anchor for horizontal_anchor in horizontal_anchors for vertical_anchor in vertical_anchors)]

Align = Literal["left", "center", "right"]

Direction = Literal["rtl", "ltr", "ttb"]

__all__ = ["Buffer", "IntegralLike", "StrOrBytesPath", "SupportsRead", "TypeGuard"]
