#!/usr/bin/python3

# Copyright 2020 Google LLC
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

import io
import sys
import warnings

import atheris_no_libfuzzer as atheris

from PIL import Image, ImageDraw, ImageFont


def TestOneInput(data):
    try:
        with ImageFont.load(io.BytesIO(data)) as font:
            font.getsize_multiline("ABC\nAaaa")
            font.getmask("test text")
            with Image.new(mode="RGBA", size=(200, 200)) as im:
                draw = ImageDraw.Draw(im)
                draw.text((10,10), "Test Text", font)
    except Exception:
        # We're catching all exceptions because Pillow's exceptions are
        # directly inheriting from Exception.
        return
    return


def main():
    atheris.Setup(sys.argv, TestOneInput, enable_python_coverage=True)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
