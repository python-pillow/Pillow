from typing import Dict, Tuple, Union, Any, Protocol
from abc import abstractmethod, abstractproperty

# Type aliases; names subject to change
LURD = Tuple[int, int, int, int]  # left, up(per), right, down = x0, y0, x1, y1
XY = Tuple[int, int]
Coord = XY
Size = XY  # NOTE: All XY aliases will be interchangeable
Matrix4 = Tuple[float, float, float, float]
Matrix12 = Tuple[float, float, float, float, float, float,
                 float, float, float, float, float, float]
Mode = str

SingleChannelExtrema = Union[Tuple[float, float], Tuple[int, int]]
MultiChannelExtrema = SingleChannelExtrema  # Note: currently only a Tuple[int,int]
Extrema = Union[SingleChannelExtrema, Tuple[MultiChannelExtrema, ...]]

Color = Union[int, float, Tuple[int, int], Tuple[int, int, int],
              Tuple[int, int, int, int]]

ArrayInterfaceStruct = Dict[unicode, Any]


class SupportsArrayInterface(Protocol):
    @abstractproperty
    def __array_interface__(self):
        # type: () -> ArrayInterfaceStruct
        pass

    @abstractmethod
    def tostring(self):
        # type: () -> str
        pass

    @abstractmethod
    def tobytes(self):
        # type: () -> bytes
        pass
