from typing import Tuple, Union
from typing import Any

# Type aliases; names subject to change
LURD = Tuple[int, int, int, int]  # left, up(per), right, down = x0, y0, x1, y1
XY = Tuple[int, int]
Coord = XY
Size = XY  # NOTE: All XY aliases will be interchangeable
Matrix4 = Tuple[float, float, float, float]
Matrix12 = Tuple[float, float, float, float, float, float, float, float, float, float, float, float]
Mode = str
Extrema = Union[Tuple[Any, Any], Tuple[Tuple[Any, Any], ...]]  # Any -> float?

