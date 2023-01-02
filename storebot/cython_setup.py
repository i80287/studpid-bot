from os.path import join
from setuptools import setup
from setuptools.extension import Extension
# from distutils.core import setup
# from distutils.extension import Extension

from Cython.Build import cythonize
from Cython.Compiler import Options

"""
Usage: python ./cython_setup.py build_ext --build-lib ./Tools
"""

Options.cimport_from_pyx = False
Options.warning_errors = True

parse_tools_ext: Extension = Extension(
    name="parse_tools", 
    sources=[join(r'./Tools', "parse_tools.pyx")],
    language="c",
)

extensions: list[Extension] = [parse_tools_ext]

setup(
    ext_modules=cythonize(
        extensions,
        # annotate="fullc",
        annotate=False,
        compiler_directives={
            "language_level": "3",
            "boundscheck": False,
            "nonecheck": False,
            "overflowcheck": False,
            "wraparound": False,
            "c_api_binop_methods": True,
            "cdivision": True,
            "embedsignature": True,
            "cdivision_warnings": False,
            "optimize.use_switch": True,
        },
    ),
    zip_safe=False,
)