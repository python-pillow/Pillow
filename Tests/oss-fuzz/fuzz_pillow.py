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

from PIL import Image, ImageFile, ImageFilter


def TestOneInput(data):
    try:
        with Image.open(io.BytesIO(data)) as im:
            im.rotate(45)
            im.filter(ImageFilter.DETAIL)
            im.save(io.BytesIO(), "BMP")
    except Exception:
        # We're catching all exceptions because Pillow's exceptions are
        # directly inheriting from Exception.
        return
    return


def main():
    ImageFile.LOAD_TRUNCATED_IMAGES = True
    warnings.filterwarnings("ignore")
    warnings.simplefilter("error", Image.DecompressionBombWarning)
    atheris.Setup(sys.argv, TestOneInput, enable_python_coverage=True)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
