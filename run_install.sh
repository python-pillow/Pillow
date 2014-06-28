source terryfy/travis_tools.sh
source library_installers.sh

init_vars
clean_builds
# Need pkg-config for freetype library detection
install_pkg_config
install_jpeg
install_tiff
install_libpng
install_lcms2
install_webp
# Need cmake for openjpeg
brew install cmake
install_openjpeg
# Fix openjpeg library install id
install_name_tool -id $PWD/build/lib/libopenjp2.6.dylib build/lib/libopenjp2.2.0.0.dylib
install_freetype
