cmake_minimum_required(VERSION 2.8.4)
project(kalman)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")

set(EIGEN_INC_DIR /home/milad/Downloads/eigen )
include_directories(${EIGEN_INC_DIR})

set(SOURCE_FILES kalman.cpp kalman-test.cpp)
add_executable(kalman-test ${SOURCE_FILES})
