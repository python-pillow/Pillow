from helper import unittest, PillowTestCase

from PIL import ImagePath

import array


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


if __name__ == '__main__':
    unittest.main()

# End of file
