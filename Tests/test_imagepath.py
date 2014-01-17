from tester import *

from PIL import Image
from PIL import ImagePath

import array

def test_path():

    p = ImagePath.Path(list(range(10)))

    # sequence interface
    assert_equal(len(p), 5)
    assert_equal(p[0], (0.0, 1.0))
    assert_equal(p[-1], (8.0, 9.0))
    assert_equal(list(p[:1]), [(0.0, 1.0)])
    assert_equal(list(p), [(0.0, 1.0), (2.0, 3.0), (4.0, 5.0), (6.0, 7.0), (8.0, 9.0)])

    # method sanity check
    assert_equal(p.tolist(), [(0.0, 1.0), (2.0, 3.0), (4.0, 5.0), (6.0, 7.0), (8.0, 9.0)])
    assert_equal(p.tolist(1), [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])

    assert_equal(p.getbbox(), (0.0, 1.0, 8.0, 9.0))

    assert_equal(p.compact(5), 2)
    assert_equal(list(p), [(0.0, 1.0), (4.0, 5.0), (8.0, 9.0)])

    p.transform((1,0,1,0,1,1))
    assert_equal(list(p), [(1.0, 2.0), (5.0, 6.0), (9.0, 10.0)])

    # alternative constructors
    p = ImagePath.Path([0, 1])
    assert_equal(list(p), [(0.0, 1.0)])
    p = ImagePath.Path([0.0, 1.0])
    assert_equal(list(p), [(0.0, 1.0)])
    p = ImagePath.Path([0, 1])
    assert_equal(list(p), [(0.0, 1.0)])
    p = ImagePath.Path([(0, 1)])
    assert_equal(list(p), [(0.0, 1.0)])
    p = ImagePath.Path(p)
    assert_equal(list(p), [(0.0, 1.0)])
    p = ImagePath.Path(p.tolist(0))
    assert_equal(list(p), [(0.0, 1.0)])
    p = ImagePath.Path(p.tolist(1))
    assert_equal(list(p), [(0.0, 1.0)])
    p = ImagePath.Path(array.array("f", [0, 1]))
    assert_equal(list(p), [(0.0, 1.0)])

    arr = array.array("f", [0, 1])
    if hasattr(arr, 'tobytes'):
        p = ImagePath.Path(arr.tobytes())
    else:
        p = ImagePath.Path(arr.tostring())
    assert_equal(list(p), [(0.0, 1.0)])
