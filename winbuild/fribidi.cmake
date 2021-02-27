cmake_minimum_required(VERSION 3.12)

project(fribidi)

add_definitions(-D_CRT_SECURE_NO_WARNINGS)

include_directories(${CMAKE_CURRENT_BINARY_DIR})
include_directories(lib)

function(extract_regex_1 var text regex)
	string(REGEX MATCH ${regex} _ ${text})
	set(${var} "${CMAKE_MATCH_1}" PARENT_SCOPE)
endfunction()


function(fribidi_conf)
	file(READ configure.ac FRIBIDI_CONF)
	extract_regex_1(FRIBIDI_MAJOR_VERSION     "${FRIBIDI_CONF}" "\\(fribidi_major_version, ([0-9]+)\\)")
	extract_regex_1(FRIBIDI_MINOR_VERSION     "${FRIBIDI_CONF}" "\\(fribidi_minor_version, ([0-9]+)\\)")
	extract_regex_1(FRIBIDI_MICRO_VERSION     "${FRIBIDI_CONF}" "\\(fribidi_micro_version, ([0-9]+)\\)")
	extract_regex_1(FRIBIDI_INTERFACE_VERSION "${FRIBIDI_CONF}" "\\(fribidi_interface_version, ([0-9]+)\\)")
	extract_regex_1(FRIBIDI_INTERFACE_AGE     "${FRIBIDI_CONF}" "\\(fribidi_interface_age, ([0-9]+)\\)")
	extract_regex_1(FRIBIDI_BINARY_AGE        "${FRIBIDI_CONF}" "\\(fribidi_binary_age, ([0-9]+)\\)")
	set(FRIBIDI_VERSION "${FRIBIDI_MAJOR_VERSION}.${FRIBIDI_MINOR_VERSION}.${FRIBIDI_MICRO_VERSION}")
	set(PACKAGE "fribidi")
	set(PACKAGE_NAME "GNU FriBidi")
	set(PACKAGE_BUGREPORT "https://github.com/fribidi/fribidi/issues/new")
	set(SIZEOF_INT 4)
	set(FRIBIDI_MSVC_BUILD_PLACEHOLDER "#define FRIBIDI_BUILT_WITH_MSVC")
	message("detected ${PACKAGE_NAME} version ${FRIBIDI_VERSION}")
	configure_file(lib/fribidi-config.h.in lib/fribidi-config.h @ONLY)
endfunction()
fribidi_conf()


function(prepend var prefix)
	set(out "")
	foreach(f ${ARGN})
		list(APPEND out "${prefix}${f}")
	endforeach()
	set(${var} "${out}" PARENT_SCOPE)
endfunction()

macro(fribidi_definitions _TGT)
	target_compile_definitions(${_TGT} PUBLIC
		HAVE_MEMSET
		HAVE_MEMMOVE
		HAVE_STRDUP
		HAVE_STDLIB_H=1
		HAVE_STRING_H=1
		HAVE_MEMORY_H=1
		#HAVE_STRINGS_H
		#HAVE_SYS_TIMES_H
		STDC_HEADERS=1
		HAVE_STRINGIZE=1)
endmacro()

function(fribidi_gen _NAME _OUTNAME _PARAM)
	set(_OUT lib/${_OUTNAME})
	prepend(_DEP "${CMAKE_CURRENT_SOURCE_DIR}/gen.tab/" ${ARGN})
	add_executable(gen-${_NAME}
		gen.tab/gen-${_NAME}.c
		gen.tab/packtab.c)
	fribidi_definitions(gen-${_NAME})
	target_compile_definitions(gen-${_NAME}
		PUBLIC DONT_HAVE_FRIBIDI_CONFIG_H)
	add_custom_command(
		COMMAND gen-${_NAME} ${_PARAM} ${_DEP} > ${_OUT}
		DEPENDS ${_DEP}
		OUTPUT ${_OUT})
	list(APPEND FRIBIDI_SOURCES_GENERATED "${_OUT}")
	set(FRIBIDI_SOURCES_GENERATED ${FRIBIDI_SOURCES_GENERATED} PARENT_SCOPE)
endfunction()

fribidi_gen(unicode-version fribidi-unicode-version.h ""
	unidata/ReadMe.txt unidata/BidiMirroring.txt)


macro(fribidi_tab _NAME)
	fribidi_gen(${_NAME}-tab ${_NAME}.tab.i 2 ${ARGN})
	target_sources(gen-${_NAME}-tab
		PRIVATE lib/fribidi-unicode-version.h)
endmacro()

fribidi_tab(bidi-type unidata/UnicodeData.txt)
fribidi_tab(joining-type unidata/UnicodeData.txt unidata/ArabicShaping.txt)
fribidi_tab(arabic-shaping unidata/UnicodeData.txt)
fribidi_tab(mirroring unidata/BidiMirroring.txt)
fribidi_tab(brackets unidata/BidiBrackets.txt unidata/UnicodeData.txt)
fribidi_tab(brackets-type unidata/BidiBrackets.txt)


file(GLOB FRIBIDI_SOURCES lib/*.c)
file(GLOB FRIBIDI_HEADERS lib/*.h)

add_library(fribidi SHARED
	${FRIBIDI_SOURCES}
	${FRIBIDI_HEADERS}
	${FRIBIDI_SOURCES_GENERATED})
fribidi_definitions(fribidi)
target_compile_definitions(fribidi
	PUBLIC "-DFRIBIDI_BUILD")
