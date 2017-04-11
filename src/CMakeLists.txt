#
# Usage:
#
# cd <local dir>
# mkdir build
# cd build
# cmake ..
# make
#


cmake_minimum_required(VERSION 2.8 FATAL_ERROR)
PROJECT(OFFLINE_HFT)

seT(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_SOURCE_DIR})

OPTION(FORCE_32BIT "compile 32-bit application" ON)
OPTION(Boost_NO_BOOST_CMAKE "Due to bug in boost cmake files in Scientific Linux" ON)

IF(FORCE_32BIT)
   SET_PROPERTY(GLOBAL PROPERTY FIND_LIBRARY_USE_LIB64_PATHS OFF)
ENDIF()

#SET(CMAKE_CXX_FLAGS "-std=c++0x")

# Find boost headers and library locations
set(Boost_USE_MULTITHREADED OFF)
set(BOOST_INCLUDEDIR $ENV{OPTSTAR}/include)
set(BOOST_LIBRARYDIR $ENV{OPTSTAR}/lib)

find_package( Boost 1.54.0 COMPONENTS program_options regex filesystem)
if(NOT Boost_FOUND)
   message(FATAL_ERROR "Fatal error: Boost (version >= 1.54.0) not found in standard location")
endif()

find_package(ROOT)

include_directories(
   ${Boost_INCLUDE_DIR}
   ${ROOT_INCLUDE_DIR}
   ${ROOTSYS}
)

link_directories(
   ${Boost_LIBRARY_DIR}
   ${ROOT_LIBRARY_DIR}
)

add_library(
   reclust
   SHARED
   Cluster.cpp
   DataPool.cpp
)


add_executable( clust clust.cc )
target_link_libraries( clust reclust ${Boost_LIBRARIES} ${ROOT_LIBRARIES} Table Geom Eve)

if(FORCE_32BIT)
   set_target_properties(reclust PROPERTIES COMPILE_FLAGS "-m32" LINK_FLAGS "-m32")
   set_target_properties(clust   PROPERTIES COMPILE_FLAGS "-m32" LINK_FLAGS "-m32")
endif()
