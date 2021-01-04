from PIL import ContainerIO, Image

from .helper import hopper

TEST_FILE = "Tests/images/dummy.container"


def test_sanity():
    dir(Image)
    dir(ContainerIO)


def test_isatty():
    with hopper() as im:
        container = ContainerIO.ContainerIO(im, 0, 0)

    assert container.isatty() is False


def test_seek_mode_0():
    # Arrange
    mode = 0
    with open(TEST_FILE, "rb") as fh:
        container = ContainerIO.ContainerIO(fh, 22, 100)

        # Act
        container.seek(33, mode)
        container.seek(33, mode)

        # Assert
        assert container.tell() == 33


def test_seek_mode_1():
    # Arrange
    mode = 1
    with open(TEST_FILE, "rb") as fh:
        container = ContainerIO.ContainerIO(fh, 22, 100)

        # Act
        container.seek(33, mode)
        container.seek(33, mode)

        # Assert
        assert container.tell() == 66


def test_seek_mode_2():
    # Arrange
    mode = 2
    with open(TEST_FILE, "rb") as fh:
        container = ContainerIO.ContainerIO(fh, 22, 100)

        # Act
        container.seek(33, mode)
        container.seek(33, mode)

        # Assert
        assert container.tell() == 100


def test_read_n0():
    # Arrange
    for bytesmode in (True, False):
        with open(TEST_FILE, "rb" if bytesmode else "r") as fh:
            container = ContainerIO.ContainerIO(fh, 22, 100)

            # Act
            container.seek(81)
            data = container.read()

            # Assert
            if bytesmode:
                data = data.decode()
            assert data == "7\nThis is line 8\n"


def test_read_n():
    # Arrange
    for bytesmode in (True, False):
        with open(TEST_FILE, "rb" if bytesmode else "r") as fh:
            container = ContainerIO.ContainerIO(fh, 22, 100)

            # Act
            container.seek(81)
            data = container.read(3)

            # Assert
            if bytesmode:
                data = data.decode()
            assert data == "7\nT"


def test_read_eof():
    # Arrange
    for bytesmode in (True, False):
        with open(TEST_FILE, "rb" if bytesmode else "r") as fh:
            container = ContainerIO.ContainerIO(fh, 22, 100)

            # Act
            container.seek(100)
            data = container.read()

            # Assert
            if bytesmode:
                data = data.decode()
            assert data == ""


def test_readline():
    # Arrange
    for bytesmode in (True, False):
        with open(TEST_FILE, "rb" if bytesmode else "r") as fh:
            container = ContainerIO.ContainerIO(fh, 0, 120)

            # Act
            data = container.readline()

            # Assert
            if bytesmode:
                data = data.decode()
            assert data == "This is line 1\n"


def test_readlines():
    # Arrange
    for bytesmode in (True, False):
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
        with open(TEST_FILE, "rb" if bytesmode else "r") as fh:
            container = ContainerIO.ContainerIO(fh, 0, 120)

            # Act
            data = container.readlines()

            # Assert
            if bytesmode:
                data = [line.decode() for line in data]
            assert data == expected
