cmake_minimum_required(VERSION 3.12)

project(raqm C)

add_definitions(-D_CRT_SECURE_NO_WARNINGS)

set(RAQM_VERSION "" CACHE STRING "Raqm version, as x.y.z")
string(REPLACE "." ";" RAQM_VERSION_PARTS ${RAQM_VERSION})
list(GET RAQM_VERSION_PARTS 0 RAQM_VERSION_MAJOR)
list(GET RAQM_VERSION_PARTS 1 RAQM_VERSION_MINOR)
list(GET RAQM_VERSION_PARTS 2 RAQM_VERSION_MICRO)
message("Building Raqm version ${RAQM_VERSION}")
configure_file(src/raqm-version.h.in ${CMAKE_CURRENT_SOURCE_DIR}/src/raqm-version.h @ONLY)

# FreeType, HarfBuzz and SheenBidi headers come from INCLUDE, set by build_env.cmd.
add_library(raqm STATIC src/raqm.c)
target_compile_definitions(raqm PRIVATE RAQM_SHEENBIDI RAQM_SHEENBIDI_GT_2_9)
