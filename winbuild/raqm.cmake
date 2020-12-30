cmake_minimum_required(VERSION 3.12)

project(libraqm)


find_library(fribidi NAMES fribidi)
find_library(harfbuzz NAMES harfbuzz)
find_library(freetype NAMES freetype)

add_definitions(-DFRIBIDI_LIB_STATIC)


function(raqm_conf)
	file(READ configure.ac RAQM_CONF)
	string(REGEX MATCH "\\[([0-9]+)\\.([0-9]+)\\.([0-9]+)\\]," _ "${RAQM_CONF}")
	set(RAQM_VERSION_MAJOR "${CMAKE_MATCH_1}")
	set(RAQM_VERSION_MINOR "${CMAKE_MATCH_2}")
	set(RAQM_VERSION_MICRO "${CMAKE_MATCH_3}")
	set(RAQM_VERSION "${RAQM_VERSION_MAJOR}.${RAQM_VERSION_MINOR}.${RAQM_VERSION_MICRO}")
	message("detected libraqm version ${RAQM_VERSION}")
	configure_file(src/raqm-version.h.in src/raqm-version.h @ONLY)
endfunction()
raqm_conf()


set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
set(RAQM_SOURCES
	src/raqm.c)
set(RAQM_HEADERS
	src/raqm.h
	src/raqm-version.h)

add_library(libraqm SHARED
	${RAQM_SOURCES}
	${RAQM_HEADERS})
target_link_libraries(libraqm
	${fribidi}
	${harfbuzz}
	${freetype})
