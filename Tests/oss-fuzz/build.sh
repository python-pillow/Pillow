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

python3 setup.py build --build-base=/tmp/build install

# Build fuzzers in $OUT.
for fuzzer in $(find $SRC -name 'fuzz_*.py'); do
  fuzzer_basename=$(basename -s .py $fuzzer)
  fuzzer_package=${fuzzer_basename}.pkg
  pyinstaller \
      --add-binary /usr/local/lib/libjpeg.so.9:. \
      --add-binary /usr/local/lib/libfreetype.so.6:. \
      --add-binary /usr/local/lib/liblcms2.so.2:. \
      --add-binary /usr/local/lib/libopenjp2.so.7:. \
      --add-binary /usr/local/lib/libpng16.so.16:. \
      --add-binary /usr/local/lib/libtiff.so.5:. \
      --add-binary /usr/local/lib/libwebp.so.7:. \
      --add-binary /usr/local/lib/libwebpdemux.so.2:. \
      --add-binary /usr/local/lib/libwebpmux.so.3:. \
      --add-binary /usr/local/lib/libxcb.so.1:. \
      --distpath $OUT --onefile --name $fuzzer_package $fuzzer

  # Create execution wrapper.
  echo "#!/bin/sh
# LLVMFuzzerTestOneInput for fuzzer detection.
this_dir=\$(dirname \"\$0\")
LD_PRELOAD=\$this_dir/sanitizer_with_fuzzer.so \
ASAN_OPTIONS=\$ASAN_OPTIONS:symbolize=1:external_symbolizer_path=\$this_dir/llvm-symbolizer:detect_leaks=0 \
\$this_dir/$fuzzer_package \$@" > $OUT/$fuzzer_basename
  chmod u+x $OUT/$fuzzer_basename
done

find Tests/images Tests/icc -print | zip -q $OUT/fuzz_pillow_seed_corpus.zip -@
find Tests/fonts -print | zip -q $OUT/fuzz_font_seed_corpus.zip -@
