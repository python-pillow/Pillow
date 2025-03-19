from __future__ import annotations

import pytest

from PIL import ContainerIO, Image

TEST_FILE = "Tests/images/dummy.container"


def test_sanity() -> None:
    dir(Image)
    dir(ContainerIO)


def test_isatty() -> None:
    with open(TEST_FILE, "rb") as fh:
        container = ContainerIO.ContainerIO(fh, 0, 0)

    assert container.isatty() is False


def test_seekable() -> None:
    with open(TEST_FILE, "rb") as fh:
        container = ContainerIO.ContainerIO(fh, 0, 0)

    assert container.seekable() is True


@pytest.mark.parametrize(
    "mode, expected_position",
    (
        (0, 33),
        (1, 66),
        (2, 100),
    ),
)
def test_seek_mode(mode: int, expected_position: int) -> None:
    # Arrange
    with open(TEST_FILE, "rb") as fh:
        container = ContainerIO.ContainerIO(fh, 22, 100)

        # Act
        container.seek(33, mode)
        container.seek(33, mode)

        # Assert
        assert container.tell() == expected_position


@pytest.mark.parametrize("bytesmode", (True, False))
def test_readable(bytesmode: bool) -> None:
    with open(TEST_FILE, "rb" if bytesmode else "r") as fh:
        container = ContainerIO.ContainerIO(fh, 0, 120)

    assert container.readable() is True


@pytest.mark.parametrize("bytesmode", (True, False))
def test_read_n0(bytesmode: bool) -> None:
    # Arrange
    with open(TEST_FILE, "rb" if bytesmode else "r") as fh:
        container = ContainerIO.ContainerIO(fh, 22, 100)

        # Act
        assert container.seek(81) == 81
        data = container.read()

        # Assert
        if bytesmode:
            data = data.decode()
        assert data == "7\nThis is line 8\n"


@pytest.mark.parametrize("bytesmode", (True, False))
def test_read_n(bytesmode: bool) -> None:
    # Arrange
    with open(TEST_FILE, "rb" if bytesmode else "r") as fh:
        container = ContainerIO.ContainerIO(fh, 22, 100)

        # Act
        assert container.seek(81) == 81
        data = container.read(3)

        # Assert
        if bytesmode:
            data = data.decode()
        assert data == "7\nT"


@pytest.mark.parametrize("bytesmode", (True, False))
def test_read_eof(bytesmode: bool) -> None:
    # Arrange
    with open(TEST_FILE, "rb" if bytesmode else "r") as fh:
        container = ContainerIO.ContainerIO(fh, 22, 100)

        # Act
        assert container.seek(100) == 100
        data = container.read()

        # Assert
        if bytesmode:
            data = data.decode()
        assert data == ""


@pytest.mark.parametrize("bytesmode", (True, False))
def test_readline(bytesmode: bool) -> None:
    with open(TEST_FILE, "rb" if bytesmode else "r") as fh:
        container = ContainerIO.ContainerIO(fh, 0, 120)

        data = container.readline()
        if bytesmode:
            data = data.decode()
        assert data == "This is line 1\n"

        data = container.readline(4)
        if bytesmode:
            data = data.decode()
        assert data == "This"


@pytest.mark.parametrize("bytesmode", (True, False))
def test_readlines(bytesmode: bool) -> None:
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

        data = container.readlines()
        if bytesmode:
            data = [line.decode() for line in data]
        assert data == expected

        assert container.seek(0) == 0

        data = container.readlines(2)
        if bytesmode:
            data = [line.decode() for line in data]
        assert data == expected[:2]


@pytest.mark.parametrize("bytesmode", (True, False))
def test_write(bytesmode: bool) -> None:
    with open(TEST_FILE, "rb" if bytesmode else "r") as fh:
        container = ContainerIO.ContainerIO(fh, 0, 120)

        assert container.writable() is False

        with pytest.raises(NotImplementedError):
            container.write(b"" if bytesmode else "")
        with pytest.raises(NotImplementedError):
            container.writelines([])
        with pytest.raises(NotImplementedError):
            container.truncate()


@pytest.mark.parametrize("bytesmode", (True, False))
def test_iter(bytesmode: bool) -> None:
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
    with open(TEST_FILE, "rb" if bytesmode else "r") as fh:
        container = ContainerIO.ContainerIO(fh, 0, 120)

        # Act
        data = []
        for line in container:
            data.append(line)

        # Assert
        if bytesmode:
            data = [line.decode() for line in data]
        assert data == expected


@pytest.mark.parametrize("bytesmode", (True, False))
def test_file(bytesmode: bool) -> None:
    with open(TEST_FILE, "rb" if bytesmode else "r") as fh:
        container = ContainerIO.ContainerIO(fh, 0, 120)

        assert isinstance(container.fileno(), int)
        container.flush()
        container.close()
