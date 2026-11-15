#
# The Python Imaging Library
# $Id$
#
# path interface
#
# History:
# 1996-11-04 fl   Created
# 2002-04-14 fl   Added documentation stub class
#
# Copyright (c) Secret Labs AB 1997.
# Copyright (c) Fredrik Lundh 1996.
#
# See the README file for information on usage and redistribution.
#
from __future__ import annotations

from . import Image

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from ._typing import Buffer

Path: Callable[
    [int | Image.core._Path | Buffer | Sequence[float]], Image.core._Path
] = Image.core.path
