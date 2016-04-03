from helper import unittest, PillowTestCase

from PIL import ImagePath, Image

import array
import struct

class TestImagePath(PillowTestCase):

    def test_path(self):

        p = ImagePath.Path(list(range(10)))

        # sequence interface
        self.assertEqual(len(p), 5)
        self.assertEqual(p[0], (0.0, 1.0))
        self.assertEqual(p[-1], (8.0, 9.0))
        self.assertEqual(list(p[:1]), [(0.0, 1.0)])
        self.assertEqual(
            list(p),
            [(0.0, 1.0), (2.0, 3.0), (4.0, 5.0), (6.0, 7.0), (8.0, 9.0)])

        # method sanity check
        self.assertEqual(
            p.tolist(),
            [(0.0, 1.0), (2.0, 3.0), (4.0, 5.0), (6.0, 7.0), (8.0, 9.0)])
        self.assertEqual(
            p.tolist(1),
            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])

        self.assertEqual(p.getbbox(), (0.0, 1.0, 8.0, 9.0))

        self.assertEqual(p.compact(5), 2)
        self.assertEqual(list(p), [(0.0, 1.0), (4.0, 5.0), (8.0, 9.0)])

        p.transform((1, 0, 1, 0, 1, 1))
        self.assertEqual(list(p), [(1.0, 2.0), (5.0, 6.0), (9.0, 10.0)])

        # alternative constructors
        p = ImagePath.Path([0, 1])
        self.assertEqual(list(p), [(0.0, 1.0)])
        p = ImagePath.Path([0.0, 1.0])
        self.assertEqual(list(p), [(0.0, 1.0)])
        p = ImagePath.Path([0, 1])
        self.assertEqual(list(p), [(0.0, 1.0)])
        p = ImagePath.Path([(0, 1)])
        self.assertEqual(list(p), [(0.0, 1.0)])
        p = ImagePath.Path(p)
        self.assertEqual(list(p), [(0.0, 1.0)])
        p = ImagePath.Path(p.tolist(0))
        self.assertEqual(list(p), [(0.0, 1.0)])
        p = ImagePath.Path(p.tolist(1))
        self.assertEqual(list(p), [(0.0, 1.0)])
        p = ImagePath.Path(array.array("f", [0, 1]))
        self.assertEqual(list(p), [(0.0, 1.0)])

        arr = array.array("f", [0, 1])
        if hasattr(arr, 'tobytes'):
            p = ImagePath.Path(arr.tobytes())
        else:
            p = ImagePath.Path(arr.tostring())
        self.assertEqual(list(p), [(0.0, 1.0)])


    def test_overflow_segfault(self):
        try:
            # post patch, this fails with a memory error
            x = evil()
            
            # This fails due to the invalid malloc above,
            # and segfaults
            for i in range(200000):
                if str is bytes:
                    x[i] = "0"*16
                else:
                    x[i] = b'0'*16
        except TypeError as msg:
            # Some pythons fail getting the argument as an integer, and
            # it falls through to the sequence. Seeing this on 32bit windows.
            self.assertTrue(True, "Sequence required")
        except MemoryError as msg:
            self.assertTrue(msg)
        except:
            self.assertTrue(False, "Should have received a memory error")


class evil:
	def __init__(self):
		self.corrupt = Image.core.path(0x4000000000000000)

	def __getitem__(self, i):
		x = self.corrupt[i]
		return struct.pack("dd", x[0], x[1])

	def __setitem__(self, i, x):
		self.corrupt[i] = struct.unpack("dd", x)


if __name__ == '__main__':
    unittest.main()

# End of file
