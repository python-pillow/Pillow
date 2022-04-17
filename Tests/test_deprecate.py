import pytest

from PIL import _deprecate


@pytest.mark.parametrize(
    "version, expected",
    [
        (
            10,
            "Old thing is deprecated and will be removed in Pillow 10 "
            r"\(2023-07-01\)\. Use new thing instead\.",
        ),
        (
            None,
            r"Old thing is deprecated and will be removed in a future version\. "
            r"Use new thing instead\.",
        ),
    ],
)
def test_version(version, expected):
    with pytest.warns(DeprecationWarning, match=expected):
        _deprecate.deprecate("Old thing", version, "new thing")


def test_unknown_version():
    expected = r"Unknown removal version, update PIL\._deprecate\?"
    with pytest.raises(ValueError, match=expected):
        _deprecate.deprecate("Old thing", 12345, "new thing")


@pytest.mark.parametrize(
    "deprecated, plural, expected",
    [
        (
            "Old thing",
            False,
            r"Old thing is deprecated and should be removed\.",
        ),
        (
            "Old things",
            True,
            r"Old things are deprecated and should be removed\.",
        ),
    ],
)
def test_old_version(deprecated, plural, expected):
    expected = r""
    with pytest.raises(RuntimeError, match=expected):
        _deprecate.deprecate(deprecated, 1, plural=plural)


def test_plural():
    expected = (
        r"Old things are deprecated and will be removed in Pillow 10 \(2023-07-01\)\. "
        r"Use new thing instead\."
    )
    with pytest.warns(DeprecationWarning, match=expected):
        _deprecate.deprecate("Old things", 10, "new thing", plural=True)


def test_replacement_and_action():
    expected = "Use only one of 'replacement' and 'action'"
    with pytest.raises(ValueError, match=expected):
        _deprecate.deprecate(
            "Old thing", 10, replacement="new thing", action="Upgrade to new thing"
        )


@pytest.mark.parametrize(
    "action",
    [
        "Upgrade to new thing",
        "Upgrade to new thing.",
    ],
)
def test_action(action):
    expected = (
        r"Old thing is deprecated and will be removed in Pillow 10 \(2023-07-01\)\. "
        r"Upgrade to new thing\."
    )
    with pytest.warns(DeprecationWarning, match=expected):
        _deprecate.deprecate("Old thing", 10, action=action)


def test_no_replacement_or_action():
    expected = (
        r"Old thing is deprecated and will be removed in Pillow 10 \(2023-07-01\)"
    )
    with pytest.warns(DeprecationWarning, match=expected):
        _deprecate.deprecate("Old thing", 10)
