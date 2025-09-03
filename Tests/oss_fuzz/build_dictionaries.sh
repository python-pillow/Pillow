#!/bin/bash -eu
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
#
################################################################################

# Generate image dictionaries here for each of the fuzzers and put them in the
# $OUT directory, named for the fuzzer

git clone --depth 1 https://github.com/google/fuzzing
cat fuzzing/dictionaries/bmp.dict \
    fuzzing/dictionaries/dds.dict \
    fuzzing/dictionaries/gif.dict \
    fuzzing/dictionaries/icns.dict \
    fuzzing/dictionaries/jpeg.dict \
    fuzzing/dictionaries/jpeg2000.dict \
    fuzzing/dictionaries/pbm.dict \
    fuzzing/dictionaries/png.dict \
    fuzzing/dictionaries/psd.dict \
    fuzzing/dictionaries/tiff.dict \
    fuzzing/dictionaries/webp.dict \
    > $OUT/fuzz_pillow.dict
