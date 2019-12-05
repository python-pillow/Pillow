from PIL import ContainerIO, Image

from .helper import PillowTestCase, hopper

TEST_FILE = "Tests/images/dummy.container"


class TestFileContainer(PillowTestCase):
    def test_sanity(self):
        dir(Image)
        dir(ContainerIO)

    def test_isatty(self):
        with hopper() as im:
            container = ContainerIO.ContainerIO(im, 0, 0)

        self.assertFalse(container.isatty())

    def test_seek_mode_0(self):
        # Arrange
        mode = 0
        with open(TEST_FILE) as fh:
            container = ContainerIO.ContainerIO(fh, 22, 100)

            # Act
            container.seek(33, mode)
            container.seek(33, mode)

            # Assert
            self.assertEqual(container.tell(), 33)

    def test_seek_mode_1(self):
        # Arrange
        mode = 1
        with open(TEST_FILE) as fh:
            container = ContainerIO.ContainerIO(fh, 22, 100)

            # Act
            container.seek(33, mode)
            container.seek(33, mode)

            # Assert
            self.assertEqual(container.tell(), 66)

    def test_seek_mode_2(self):
        # Arrange
        mode = 2
        with open(TEST_FILE) as fh:
            container = ContainerIO.ContainerIO(fh, 22, 100)

            # Act
            container.seek(33, mode)
            container.seek(33, mode)

            # Assert
            self.assertEqual(container.tell(), 100)

    def test_read_n0(self):
        # Arrange
        with open(TEST_FILE) as fh:
            container = ContainerIO.ContainerIO(fh, 22, 100)

            # Act
            container.seek(81)
            data = container.read()

            # Assert
            self.assertEqual(data, "7\nThis is line 8\n")

    def test_read_n(self):
        # Arrange
        with open(TEST_FILE) as fh:
            container = ContainerIO.ContainerIO(fh, 22, 100)

            # Act
            container.seek(81)
            data = container.read(3)

            # Assert
            self.assertEqual(data, "7\nT")

    def test_read_eof(self):
        # Arrange
        with open(TEST_FILE) as fh:
            container = ContainerIO.ContainerIO(fh, 22, 100)

            # Act
            container.seek(100)
            data = container.read()

            # Assert
            self.assertEqual(data, "")

    def test_readline(self):
        # Arrange
        with open(TEST_FILE) as fh:
            container = ContainerIO.ContainerIO(fh, 0, 120)

            # Act
            data = container.readline()

            # Assert
            self.assertEqual(data, "This is line 1\n")

    def test_readlines(self):
        # Arrange
        expected = [
            "This is line 1\n",
            "This is line 2\n",
            "This is line 3\n",
            "This is line 4\n",
            "This is line 5\n",
            "This is line 6\n",
            "This is line 7\n",
            "This is line 8\n",
        ]
        with open(TEST_FILE) as fh:
            container = ContainerIO.ContainerIO(fh, 0, 120)

            # Act
            data = container.readlines()

            # Assert

            self.assertEqual(data, expected)
