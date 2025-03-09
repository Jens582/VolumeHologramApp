cmake_minimum_required(VERSION 3.10)
project(VolumeHologramEvaluation)

set(CMAKE_CXX_STANDARD 20)

file(GLOB_RECURSE SOURCES "src/*.cpp")

find_package(Armadillo REQUIRED)
include_directories(${ARMADILLO_INCLUDE_DIRS})
add_executable(VolumeHologramEvaluation ${SOURCES})
target_link_libraries(VolumeHologramEvaluation ${ARMADILLO_LIBRARIES})

add_custom_command(TARGET VolumeHologramEvaluation POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy 
    ${CMAKE_SOURCE_DIR}/hoeInputvalues.dat 
    ${CMAKE_BINARY_DIR}/$<CONFIG>/hoeInputvalues.dat
    COMMAND ${CMAKE_COMMAND} -E copy 
    ${CMAKE_SOURCE_DIR}/InputFileCreator.ipynb 
    ${CMAKE_BINARY_DIR}/$<CONFIG>/InputFileCreator.ipynb
)
