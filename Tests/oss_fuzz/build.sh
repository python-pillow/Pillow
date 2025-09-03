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

python3 -m pip install .

# Build fuzzers in $OUT.
for fuzzer in $(find $SRC -name 'fuzz_*.py'); do
  compile_python_fuzzer $fuzzer \
      --add-binary /usr/local/lib/libjpeg.so.62.4.0:. \
      --add-binary /usr/local/lib/libfreetype.so.6:. \
      --add-binary /usr/local/lib/liblcms2.so.2:. \
      --add-binary /usr/local/lib/libopenjp2.so.7:. \
      --add-binary /usr/local/lib/libpng16.so.16:. \
      --add-binary /usr/local/lib/libtiff.so.6:. \
      --add-binary /usr/local/lib/libwebp.so.7:. \
      --add-binary /usr/local/lib/libwebpdemux.so.2:. \
      --add-binary /usr/local/lib/libwebpmux.so.3:. \
      --add-binary /usr/local/lib/libxcb.so.1:.
done

find Tests/images Tests/icc -print | zip -q $OUT/fuzz_pillow_seed_corpus.zip -@
find Tests/fonts -print | zip -q $OUT/fuzz_font_seed_corpus.zip -@
