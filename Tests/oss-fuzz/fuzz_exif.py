#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import io
import sys

import atheris
from atheris.import_hook import instrument_imports

with instrument_imports():
    from PIL import ExifTags, Image


def TestOneInput(data):
    if len(data) < 10:
        return

    try:
        image_io = io.BytesIO(data)

        with Image.open(image_io) as img:
            try:
                exif = img._getexif()
                if exif:
                    for tag_id, value in exif.items():
                        tag_name = ExifTags.TAGS.get(tag_id, tag_id)
                        if tag_id == 34853:  # GPSInfo
                            for gps_tag, gps_value in value.items():
                                gps_tag_name = ExifTags.GPSTAGS.get(gps_tag, gps_tag)
            except Exception:
                pass

            try:
                if hasattr(img, "getexif"):
                    exif = img.getexif()
                    if exif and hasattr(exif, "get_thumbnail"):
                        thumbnail = exif.get_thumbnail()
                        if thumbnail:
                            thumb_img = Image.open(io.BytesIO(thumbnail))
                            thumb_img.load()
            except Exception:
                pass

    except Exception:
        pass


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
