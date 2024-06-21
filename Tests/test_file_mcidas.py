import pytest
from PIL import Image, McIdasImagePlugin

def test_open_invalid_file():
    # Arrange
    invalid_file = "Tests/images/flower.jpg"

    # Act & Assert
    with pytest.raises(SyntaxError):
        McIdasImagePlugin.McIdasImageFile(invalid_file)

def test_open_supported_file():
    # Arrange
    test_file = "Tests/images/cmx3g8_wv_1998.260_0745_mcidas.ara"

    # Act
    with Image.open(test_file) as im:
        im.load()

        # Assert
        assert im.format == "MCIDAS"
        assert im.mode == "I"
        assert im.size == (1800, 400)

def test_open_mode_L():
    # Arrange
    test_file = "Tests/images/mcidas_mode_L.ara"

    # Act
    with Image.open(test_file) as im:
        im.load()

        # Assert
        assert im.format == "MCIDAS"
        assert im.mode == "L"
        assert im.size == (100, 100)

def test_open_mode_I_32B():
    # Arrange
    test_file = "Tests/images/mcidas_mode_I_32B.ara"

    # Act
    with Image.open(test_file) as im:
        im.load()

        # Assert
        assert im.format == "MCIDAS"
        assert im.mode == "I"
        assert im.size == (100, 100)

def test_open_unsupported_format():
    # Arrange
    test_file = "Tests/images/mcidas_unsupported.ara"

    # Act & Assert
    with pytest.raises(SyntaxError, match="unsupported McIdas format"):
        McIdasImagePlugin.McIdasImageFile(test_file)