import warnings

with warnings.catch_warnings(record=True) as w:
    # Arrange: cause all warnings to always be triggered
    warnings.simplefilter("always")

    # Act: trigger a warning with Qt5
    from PIL import ImageQt


def test_deprecated():
    # Assert
    if ImageQt.qt_version in ("5", "side2"):
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message)
    else:
        assert len(w) == 0
