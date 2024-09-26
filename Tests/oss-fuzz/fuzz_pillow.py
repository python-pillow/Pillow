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


import atheris
from atheris.import_hook import instrument_imports

with instrument_imports():
    import sys

    import fuzzers


def TestOneInput(data: bytes) -> None:
    try:
        fuzzers.fuzz_image(data)
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
