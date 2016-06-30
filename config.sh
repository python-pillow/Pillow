# Define custom utilities
# Test for OSX with [ -n "$IS_OSX" ]

function pre_build {
    # Any stuff that you need to do before you start building the wheels
    # Runs in the root directory of this repository.
    set -e
    if [ -n "$IS_OSX" ]; then
        source osx_build_deps.sh
    else
        source multibuild/library_builders.sh
        build_jpeg
        build_tiff
        build_openjpeg
        build_lcms2
        build_libwebp
        build_freetype
    fi
}

function run_tests_in_repo {
    # Run Pillow tests from within source repo
    if [ -f test-installed.py ]; then
        python test-installed.py -s -v Tests/test_*.py
    else
        python Tests/run.py --installed
    fi
}

function run_tests {
    # Runs tests on installed distribution from an empty directory
    export NOSE_PROCESS_TIMEOUT=600
    export NOSE_PROCESSES=0
    (cd ../Pillow && run_tests_in_repo)
}
