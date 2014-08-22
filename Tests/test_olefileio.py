from helper import unittest, PillowTestCase

import datetime

import PIL.OleFileIO as OleFileIO


class TestOleFileIo(PillowTestCase):

    def test_isOleFile_false(self):
        # Arrange
        non_ole_file = "Tests/images/flower.jpg"

        # Act
        is_ole = OleFileIO.isOleFile(non_ole_file)

        # Assert
        self.assertFalse(is_ole)

    def test_isOleFile_true(self):
        # Arrange
        ole_file = "Tests/images/test-ole-file.doc"

        # Act
        is_ole = OleFileIO.isOleFile(ole_file)

        # Assert
        self.assertTrue(is_ole)

    def test_exists_worddocument(self):
        # Arrange
        ole_file = "Tests/images/test-ole-file.doc"
        ole = OleFileIO.OleFileIO(ole_file)

        # Act
        exists = ole.exists('worddocument')

        # Assert
        self.assertTrue(exists)
        ole.close()

    def test_exists_no_vba_macros(self):
        # Arrange
        ole_file = "Tests/images/test-ole-file.doc"
        ole = OleFileIO.OleFileIO(ole_file)

        # Act
        exists = ole.exists('macros/vba')

        # Assert
        self.assertFalse(exists)
        ole.close()

    def test_get_type(self):
        # Arrange
        ole_file = "Tests/images/test-ole-file.doc"
        ole = OleFileIO.OleFileIO(ole_file)

        # Act
        type = ole.get_type('worddocument')

        # Assert
        self.assertEqual(type, OleFileIO.STGTY_STREAM)
        ole.close()

    def test_get_size(self):
        # Arrange
        ole_file = "Tests/images/test-ole-file.doc"
        ole = OleFileIO.OleFileIO(ole_file)

        # Act
        size = ole.get_size('worddocument')

        # Assert
        self.assertGreater(size, 0)
        ole.close()

    def test_get_rootentry_name(self):
        # Arrange
        ole_file = "Tests/images/test-ole-file.doc"
        ole = OleFileIO.OleFileIO(ole_file)

        # Act
        root = ole.get_rootentry_name()

        # Assert
        self.assertEqual(root, "Root Entry")
        ole.close()

    def test_meta(self):
        # Arrange
        ole_file = "Tests/images/test-ole-file.doc"
        ole = OleFileIO.OleFileIO(ole_file)

        # Act
        meta = ole.get_metadata()

        # Assert
        self.assertEqual(meta.author, b"Laurence Ipsum")
        self.assertEqual(meta.num_pages, 1)
        ole.close()

    def test_gettimes(self):
        # Arrange
        ole_file = "Tests/images/test-ole-file.doc"
        ole = OleFileIO.OleFileIO(ole_file)
        root_entry = ole.direntries[0]

        # Act
        ctime = root_entry.getctime()
        mtime = root_entry.getmtime()

        # Assert
        self.assertIsInstance(ctime, type(None))
        self.assertIsInstance(mtime, datetime.datetime)
        self.assertEqual(ctime, None)
        self.assertEqual(mtime.year, 2014)
        ole.close()

    def test_listdir(self):
        # Arrange
        ole_file = "Tests/images/test-ole-file.doc"
        ole = OleFileIO.OleFileIO(ole_file)

        # Act
        dirlist = ole.listdir()

        # Assert
        self.assertIn(['WordDocument'], dirlist)
        ole.close()

    def test_debug(self):
        # Arrange
        ole_file = "Tests/images/test-ole-file.doc"
        ole = OleFileIO.OleFileIO(ole_file)
        meta = ole.get_metadata()

        # Act
        OleFileIO.set_debug_mode(True)
        ole.dumpdirectory()
        meta.dump()

        OleFileIO.set_debug_mode(False)
        ole.dumpdirectory()
        meta.dump()

        # Assert
        # No assert, just check they run ok
        ole.close()


if __name__ == '__main__':
    unittest.main()

# End of file
