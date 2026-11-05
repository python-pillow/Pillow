from __future__ import annotations

import pytest

from PIL import Image, ImageFile

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any


@pytest.mark.parametrize("mode", Image.MODES)
def test_raw_encoder_optimal_bufsize(mode: str) -> None:
    # Test the raw encoder does know the exact buffer size.
    im = Image.new(mode, (300, 200))
    encoder = Image._getencoder(mode, "raw", mode)
    encoder.setimage(im.im)
    assert encoder.optimal_bufsize == len(im.tobytes())


def test_raw_encoder_optimal_bufsize_stride() -> None:
    im = Image.new("RGB", (100, 50))
    encoder = Image._getencoder("RGB", "raw", ("RGB", 400))
    encoder.setimage(im.im)
    assert encoder.optimal_bufsize == 400 * im.height


def test_encoder_optimal_bufsize_unknown() -> None:
    im = Image.new("1", (64, 64))

    # the size is not known before the image has been assigned
    encoder = Image._getencoder("1", "raw", "1")
    assert encoder.optimal_bufsize == 0

    # nor for encoders whose output size depends on the pixel data
    encoder = Image._getencoder("1", "xbm", "1")
    encoder.setimage(im.im)
    assert encoder.optimal_bufsize == 0


@pytest.mark.parametrize("mode", ("L", "RGB"))
@pytest.mark.parametrize(
    "size",
    (
        (20000, 1),
        (1, 20000),
        (3, 3),
        (500, 500),
    ),
)
def test_tobytes_exact_buffer_and_single_pass(
    mode: str,
    size: tuple[int, int],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Test that the raw encoder gets asked exactly the correct size,
    and ends up doing its work in a single pass.
    """
    bufsizes: list[int] = []

    class EncoderSpy:
        def __init__(
            self, encoder: Image.core.ImagingEncoder | ImageFile.PyEncoder
        ) -> None:
            self._encoder = encoder

        def __getattr__(self, name: str) -> Any:
            return getattr(self._encoder, name)

        def encode(self, bufsize: int) -> tuple[int, int, bytes]:
            bufsizes.append(bufsize)
            return self._encoder.encode(bufsize)

    _getencoder = Image._getencoder
    monkeypatch.setattr(
        Image,
        "_getencoder",
        lambda *args: EncoderSpy(_getencoder(*args)),
    )

    im = Image.new(mode, size)
    expected_size = size[0] * size[1] * Image.getmodebands(mode)
    assert len(im.tobytes()) == expected_size
    assert bufsizes == [expected_size]
