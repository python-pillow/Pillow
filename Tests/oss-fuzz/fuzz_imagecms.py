#!/usr/bin/python3

# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import atheris

with atheris.instrument_imports():
    import sys

    import fuzzers

MODES = [
    "1",
    "L",
    "P",
    "RGB",
    "RGBA",
    "CMYK",
    "YCbCr",
    "LAB",
    "HSV",
    "I",
    "F",
    "LA",
    "PA",
    "RGBX",
    "RGBa",
    "La",
    "I;16",
    "I;16L",
    "I;16B",
    "I;16N",
    "BGR;15",
    "BGR;16",
    "BGR;24",
]


def TestOneInput(data: bytes) -> None:
    fdp = atheris.FuzzedDataProvider(data)

    mode1 = fdp.PickValueInList(MODES)
    mode2 = fdp.PickValueInList(MODES)
    in_transform = fdp.PickValueInList(MODES)
    out_transform = fdp.PickValueInList(MODES)

    try:
        fuzzers.fuzz_cms(mode1, mode2, in_transform, out_transform)
    except Exception:
        # We're catching all exceptions because Pillow's exceptions are
        # directly inheriting from Exception.
        pass


def main() -> None:
    fuzzers.enable_decompressionbomb_error()
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
    fuzzers.disable_decompressionbomb_error()


if __name__ == "__main__":
    main()
