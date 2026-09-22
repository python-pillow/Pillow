from __future__ import annotations

from unittest.mock import Mock

import pytest

from PIL import Image, ImageFile

from .helper import hopper


def test_sanity() -> None:
    data = hopper().tobytes()
    assert isinstance(data, bytes)


@pytest.mark.parametrize("failure", (None, "setimage", "encode", "status"))
def test_encoder_cleanup(failure: str | None, monkeypatch: pytest.MonkeyPatch) -> None:
    encoder = Mock(spec=ImageFile.PyEncoder)
    encoder.encode.return_value = (6, 1, b"pixels")
    monkeypatch.setattr(Image, "_getencoder", lambda *args: encoder)
    im = Image.new("RGB", (1, 1))

    if failure in ("setimage", "encode"):
        getattr(encoder, failure).side_effect = ValueError(failure)
        with pytest.raises(ValueError, match=failure):
            im.tobytes()
    elif failure == "status":
        encoder.encode.return_value = (0, -2, b"")
        with pytest.raises(RuntimeError, match="encoder error -2 in tobytes"):
            im.tobytes()
    else:
        assert im.tobytes() == b"pixels"

    encoder.cleanup.assert_called_once_with()
