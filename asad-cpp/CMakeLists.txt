cmake_minimum_required (VERSION 2.8)
project (asad)

set (BUILD_SHARED_LIBS OFF)
set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall -Wextra -Werror")

set (EXTERNAL_SOURCE_DIR "${PROJECT_SOURCE_DIR}/external")
set (ASAD_SOURCE_DIR "${PROJECT_SOURCE_DIR}/src")
set (ASAD_INCLUDE_DIR "${PROJECT_SOURCE_DIR}/include")

file (GLOB ASAD_INCLUDE_FILES "${ASAD_INCLUDE_DIR}/asad/*.h")
file (GLOB ASAD_SOURCE_FILES "${ASAD_SOURCE_DIR}/*.cpp")
set  (ASAD_ALL_FILES ${ASAD_INCLUDE_FILES} ${ASAD_SOURCE_FILES})

set (ARMADILLO_SOURCE_DIR "${EXTERNAL_SOURCE_DIR}/armadillo" CACHE PATH "Armadillo Path")
set (ARMADILLO_INCLUDE_DIR "${ARMADILLO_SOURCE_DIR}/include" CACHE PATH "Armadillo Include Path")

add_subdirectory ("${ARMADILLO_SOURCE_DIR}")

include_directories (
  "${ARMADILLO_INCLUDE_DIR}"
  "${ASAD_INCLUDE_DIR}"
  "${ASAD_SOURCE_DIR}"
)

add_library (asad ${ASAD_ALL_FILES})
target_link_libraries (asad armadillo)

add_executable (main ${ASAD_ALL_FILES} main.cpp)
target_link_libraries (asad armadillo)
