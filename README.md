# RoutingBlocks Native Extension Example

This repository contains a simple example of how to create a native extension for the `RoutingBlocks` package.
This is useful if you want to create high-performance evaluation functions for your routing problem.
Feel free to use this repository as a starting point for your own native extension,
see [this section](#adapting-this-example) for more information.

## Installation

```bash
git clone 
pip install <directory>
```

## Usage example

This example provides a simple CVRP "solver" that uses the implemented evaluation function. To test it, run:

```bash
pip install -r example/requirements.txt
python example/usage.py X-n101-k25
```

## Adapting this example

### Background

`RoutingBlocks` is a native library with Python bindings provided through a package hosted on PyPI. This native library
is
distributed alongside the package, making it accessible to developers for creating extension modules by linking against
it. By implementing the interfaces provided by `RoutingBlocks`, custom classes can be seamlessly integrated and used
with
the main package, allowing for a more tailored and versatile experience when working with the library.

### Structure

The example utilizes [scikit-build-core](https://github.com/scikit-build/scikit-build-core)
and [cmake](https://cmake.org)
to build the native library extension. The following files are relevant and will likely require changes:

* `CMakeLists.txt`: This file contains the build instructions for the native library.
* `pyproject.toml`: This file contains the metadata and build instructions for the python package.

### Steps

1. Adjust the implementation of `CVRPEvaluation` and related classes (i.e., `CVRP_*_data`) to your problem setting.
2. Create bindings for any additional members, classes, and functions you've implemented (
   cf. [pybind11](https://github.com/pybind/pybind11)). Make sure to use the pybind11 `smart_holder` branch. The example
   sets this up automatically.
3. Build and install the library using `pip install .` (or `pip install -e .` for development) or ship it as a wheel ``.
4. (Optional) Generate type stubs for your library using [mypy](tools/stubgen.py).

## License

[MIT](https://choosealicense.com/licenses/mit/)
