from PIL import GimpGradientFile, ImagePalette


def test_linear_pos_le_middle():
    # Arrange
    middle = 0.5
    pos = 0.25

    # Act
    ret = GimpGradientFile.linear(middle, pos)

    # Assert
    assert ret == 0.25


def test_linear_pos_le_small_middle():
    # Arrange
    middle = 1e-11
    pos = 1e-12

    # Act
    ret = GimpGradientFile.linear(middle, pos)

    # Assert
    assert ret == 0.0


def test_linear_pos_gt_middle():
    # Arrange
    middle = 0.5
    pos = 0.75

    # Act
    ret = GimpGradientFile.linear(middle, pos)

    # Assert
    assert ret == 0.75


def test_linear_pos_gt_small_middle():
    # Arrange
    middle = 1 - 1e-11
    pos = 1 - 1e-12

    # Act
    ret = GimpGradientFile.linear(middle, pos)

    # Assert
    assert ret == 1.0


def test_curved():
    # Arrange
    middle = 0.5
    pos = 0.75

    # Act
    ret = GimpGradientFile.curved(middle, pos)

    # Assert
    assert ret == 0.75


def test_sine():
    # Arrange
    middle = 0.5
    pos = 0.75

    # Act
    ret = GimpGradientFile.sine(middle, pos)

    # Assert
    assert ret == 0.8535533905932737


def test_sphere_increasing():
    # Arrange
    middle = 0.5
    pos = 0.75

    # Act
    ret = GimpGradientFile.sphere_increasing(middle, pos)

    # Assert
    assert round(abs(ret - 0.9682458365518543), 7) == 0


def test_sphere_decreasing():
    # Arrange
    middle = 0.5
    pos = 0.75

    # Act
    ret = GimpGradientFile.sphere_decreasing(middle, pos)

    # Assert
    assert ret == 0.3385621722338523


def test_load_via_imagepalette():
    # Arrange
    test_file = "Tests/images/gimp_gradient.ggr"

    # Act
    palette = ImagePalette.load(test_file)

    # Assert
    # load returns raw palette information
    assert len(palette[0]) == 1024
    assert palette[1] == "RGBA"


def test_load_1_3_via_imagepalette():
    # Arrange
    # GIMP 1.3 gradient files contain a name field
    test_file = "Tests/images/gimp_gradient_with_name.ggr"

    # Act
    palette = ImagePalette.load(test_file)

    # Assert
    # load returns raw palette information
    assert len(palette[0]) == 1024
    assert palette[1] == "RGBA"
