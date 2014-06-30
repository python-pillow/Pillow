source terryfy/travis_tools.sh
source library_installers.sh

# Need cmake for openjpeg
brew install cmake
# Need pkg-config for freetype to find libpng
brew install pkg-config
# Set up build
init_vars
clean_builds
install_jpeg
install_tiff
install_libpng
install_lcms2
install_webp
install_openjpeg
# Fix openjpeg library install id
# https://code.google.com/p/openjpeg/issues/detail?id=367
install_name_tool -id $PWD/build/lib/libopenjp2.6.dylib build/lib/libopenjp2.2.0.0.dylib
install_freetype
