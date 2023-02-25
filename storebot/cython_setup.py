import os
from setuptools import setup
from setuptools.extension import Extension

from Cython.Build import cythonize
import Cython.Compiler.Options as CompilerOpts

"""
Usage: python ./cython_setup.py
"""

CompilerOpts.cimport_from_pyx = False
CompilerOpts.warning_errors = True

compiler_directives: dict[str, int] = {
    "language_level": 3,
    "boundscheck": False,
    "nonecheck": False,
    "overflowcheck": False,
    "wraparound": False,
    "c_api_binop_methods": True,
    "cdivision": True,
    "embedsignature": True,
    "cdivision_warnings": False,
    "optimize.use_switch": True,
}

import pathlib
dir_path: pathlib.Path = pathlib.Path(__file__).parent.resolve() / "Tools"

parse_tools_ext: Extension = Extension(
    name="parse_tools", 
    sources=[str(dir_path / "parse_tools.pyx")],
    language="c",
)

extensions: list[Extension] = [parse_tools_ext]

import sys
if "build_ext" not in sys.argv:
    sys.argv.extend(["build_ext", "--build-lib", dir_path.__str__()])

setup(
    ext_modules=cythonize(
        module_list=extensions,
        nthreads=4,
        compiler_directives=compiler_directives,
        annotate=False,
        # annotate="fullc",
    ),
    zip_safe=False,
)
