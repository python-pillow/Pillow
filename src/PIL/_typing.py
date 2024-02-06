from __future__ import annotations

import sys
from typing import Sequence, Union

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    try:
        from typing_extensions import TypeGuard
    except ImportError:
        from typing import Any

        class TypeGuard:  # type: ignore[no-redef]
            def __class_getitem__(cls, item: Any) -> type[bool]:
                return bool


Coords = Union[Sequence[float], Sequence[Sequence[float]]]


__all__ = ["TypeGuard"]
