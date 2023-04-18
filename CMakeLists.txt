cmake_minimum_required(VERSION 3.15)
include(CheckIPOSupported)
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/CPM.cmake)

project(_${SKBUILD_PROJECT_NAME} VERSION ${SKBUILD_PROJECT_VERSION})
string(TOUPPER ${PROJECT_NAME} PROJECT_NAME_UPPER)

# To force building for a specific python version, set Python_ROOT_DIR to the respective path.
# This can be a venv as well.
# See the FIND_PACKAGE python cmake documentation for details.
FIND_PACKAGE(Python COMPONENTS Interpreter Development.Module REQUIRED)

message(STATUS "Found python binary: ${Python_EXECUTABLE} (Version ${Python_VERSION})")

set(PYBIND11_PYTHON_VERSION ${Python_VERSION})
set(PYTHON_EXECUTABLE ${Python_EXECUTABLE})
set(PYTHON_LIBS ${Python_LIBS})

CPMAddPackage(
        NAME pybind11
        GITHUB_REPOSITORY pybind/pybind11
        GIT_TAG smart_holder
)

file(GLOB_RECURSE headers CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/include/*.h")
file(GLOB_RECURSE sources CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp")

pybind11_add_module(${PROJECT_NAME} ${sources})

#
set(ROUTINGBLOCKS_INCLUDE_BASE "${Python_SITELIB}/routingblocks/include")
set(ROUTINGBLOCKS_LIB_NAME "${CMAKE_STATIC_LIBRARY_PREFIX}routingblocks${CMAKE_STATIC_LIBRARY_SUFFIX}")
# lib or lib64
if (EXISTS "${Python_SITELIB}/routingblocks/${ROUTINGBLOCKS_LIB_NAME}")
    set(ROUTINGBLOCKS_LIB "${Python_SITELIB}/routingblocks/${ROUTINGBLOCKS_LIB_NAME}")
else ()
    message(FATAL_ERROR "Could not find the routingblocks native library. Please install the routingblocks python package first.")
endif ()


if (NOT IS_DIRECTORY ${ROUTINGBLOCKS_INCLUDE_BASE}/routingblocks)
    message(FATAL_ERROR "Could not find the routingblocks interface header directory. Please install the routingblocks python package first.")
else ()
    message(STATUS "Found vrpis include directory: ${ROUTINGBLOCKS_INCLUDE_BASE}")
endif ()
# Link to main routing blocks library
target_link_libraries(${PROJECT_NAME} PRIVATE ${ROUTINGBLOCKS_LIB})
# Include main routing blocks library
target_include_directories(${PROJECT_NAME} PRIVATE ${ROUTINGBLOCKS_INCLUDE_BASE})

target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_definitions(${PROJECT_NAME} PRIVATE "ROUTINGBLOCKS_EXT_MODULE_NAME=${PROJECT_NAME}")
target_compile_definitions(${PROJECT_NAME} PRIVATE "ROUTINGBLOCKS_EXT_MODULE_VERSION=${PROJECT_VERSION}")
target_compile_definitions(${PROJECT_NAME} PRIVATE "PYBIND11_USE_SMART_HOLDER_AS_DEFAULT")

# Set up optimization flags
if (CMAKE_COMPILER_IS_GNUCC)
    target_compile_options(${PROJECT_NAME} PRIVATE "$<$<CONFIG:DEBUG>:-O0;-g3>")
    target_compile_options(${PROJECT_NAME} PRIVATE "$<$<CONFIG:RELEASE>:-O3;>")
    target_compile_options(${PROJECT_NAME} PRIVATE "$<$<CONFIG:PROFILE>:-O2;-pg;-fno-omit-frame-pointer;-fno-optimize-sibling-calls;>")
endif ()
if (MSVC)
    target_compile_options(${PROJECT_NAME} PRIVATE "$<$<CONFIG:DEBUG>:/Od>")
    target_compile_options(${PROJECT_NAME} PRIVATE "$<$<CONFIG:RELEASE>:/O2y>")
endif ()

# Enable LTO if supported
check_ipo_supported(RESULT ${PROJECT_NAME}_HAS_LTO)
if (${${PROJECT_NAME}_HAS_LTO})
    message(STATUS "LTO is supported")
    set_target_properties(${PROJECT_NAME} PROPERTIES INTERPROCEDUAL_OPTIMIZATION TRUE)
endif ()

# Set the compiler standard
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)

# Install the extension module
install(TARGETS ${PROJECT_NAME} DESTINATION ${SKBUILD_PROJECT_NAME})
install(FILES ${ROUTINGBLOCKS_LIB} DESTINATION ${SKBUILD_PROJECT_NAME})
