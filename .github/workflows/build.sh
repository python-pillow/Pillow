
if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
  # webp, zstd, xz, libtiff, libxcb cause a conflict with building webp, libtiff, libxcb
  # curl from brew requires zstd, use system curl
  # if php is installed, brew tries to reinstall these after installing openblas
  # remove lcms2 to fix building openjpeg on arm64
  # remove xmlto to skip building giflib docs
  brew remove --ignore-dependencies webp zstd xz libtiff libxcb curl php lcms2 xmlto ghostscript

  if [[ "$PLAT" == "arm64" ]]; then
    export MACOSX_DEPLOYMENT_TARGET="11.0"
  else
    export MACOSX_DEPLOYMENT_TARGET="10.10"
  fi
fi

if [[ "$MB_PYTHON_VERSION" == pypy3* ]]; then
  MB_PYTHON_OSX_VER="10.9"
  if [[ "$PLAT" == "i686" ]]; then
    DOCKER_TEST_IMAGE="multibuild/xenial_$PLAT"
  fi
elif [[ "$MB_PYTHON_VERSION" == "3.11" ]] && [[ "$PLAT" == "i686" ]]; then
  DOCKER_TEST_IMAGE="radarhere/bionic-$PLAT"
fi

echo "::group::Install a virtualenv"
  source multibuild/common_utils.sh
  source multibuild/travis_steps.sh
  export LATEST_3p11="3.11.0"
  python3 -m pip install virtualenv
  before_install
echo "::endgroup::"

echo "::group::Build wheel"
  clean_code
  build_wheel
  ls -l "${GITHUB_WORKSPACE}/${WHEEL_SDIR}/"
echo "::endgroup::"

if [[ $MACOSX_DEPLOYMENT_TARGET != "11.0" ]]; then
  echo "::group::Test wheel"
    install_run
  echo "::endgroup::"
fi
