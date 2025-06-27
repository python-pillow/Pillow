from __future__ import annotations

import pytest

from PIL import _deprecate


@pytest.mark.parametrize(
    "version, expected",
    [
        (
            12,
            "Old thing is deprecated and will be removed in Pillow 12 "
            r"\(2025-10-15\)\. Use new thing instead\.",
        ),
        (
            None,
            r"Old thing is deprecated and will be removed in a future version\. "
            r"Use new thing instead\.",
        ),
    ],
)
def test_version(version: int | None, expected: str) -> None:
    with pytest.warns(DeprecationWarning, match=expected):
        _deprecate.deprecate("Old thing", version, "new thing")


def test_unknown_version() -> None:
    expected = r"Unknown removal version: 12345. Update PIL\._deprecate\?"
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
def test_old_version(deprecated: str, plural: bool, expected: str) -> None:
    with pytest.raises(RuntimeError, match=expected):
        _deprecate.deprecate(deprecated, 1, plural=plural)


def test_plural() -> None:
    expected = (
        r"Old things are deprecated and will be removed in Pillow 12 \(2025-10-15\)\. "
        r"Use new thing instead\."
    )
    with pytest.warns(DeprecationWarning, match=expected):
        _deprecate.deprecate("Old things", 12, "new thing", plural=True)


def test_replacement_and_action() -> None:
    expected = "Use only one of 'replacement' and 'action'"
    with pytest.raises(ValueError, match=expected):
        _deprecate.deprecate(
            "Old thing", 12, replacement="new thing", action="Upgrade to new thing"
        )


@pytest.mark.parametrize(
    "action",
    [
        "Upgrade to new thing",
        "Upgrade to new thing.",
    ],
)
def test_action(action: str) -> None:
    expected = (
        r"Old thing is deprecated and will be removed in Pillow 12 \(2025-10-15\)\. "
        r"Upgrade to new thing\."
    )
    with pytest.warns(DeprecationWarning, match=expected):
        _deprecate.deprecate("Old thing", 12, action=action)


def test_no_replacement_or_action() -> None:
    expected = (
        r"Old thing is deprecated and will be removed in Pillow 12 \(2025-10-15\)"
    )
    with pytest.warns(DeprecationWarning, match=expected):
        _deprecate.deprecate("Old thing", 12)
