"""
Cython build configuration for Aetheris binary distribution.

This setup.py compiles all Python source files to native extensions,
creating a closed-source binary distribution for PyPI.
"""

import glob
import os
import shutil
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py

# Check if Cython is available (only needed during build)
try:
    from Cython.Build import cythonize
    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False


def get_ext_modules():
    """
    Find all .py files in src/ and prepare them for Cython compilation.
    Excludes __init__.py files which are kept as stubs for package imports.
    """
    if not USE_CYTHON:
        return []

    # Find all .py files in src/
    py_files = glob.glob("src/**/*.py", recursive=True)

    # Exclude __init__.py files (needed as stubs for imports)
    ext_modules = [f for f in py_files if "__init__" not in f]

    if not ext_modules:
        return []

    return cythonize(
        ext_modules,
        compiler_directives={
            'language_level': "3",
            'always_allow_keywords': True,
            'embedsignature': False,  # Don't include Python signatures in docstrings
        },
        build_dir="build",
        nthreads=os.cpu_count() or 1,
    )


class build_py(_build_py):
    """Custom build_py that excludes .py files that have been compiled to .so/.pyd."""

    def build_module(self, module, module_file, package):
        """Override to skip .py files that will be replaced by compiled extensions."""
        if USE_CYTHON and ext_modules:
            # Skip non-__init__.py files (they're compiled to .so/.pyd)
            if not module_file.endswith("__init__.py"):
                return None
        return super().build_module(module, module_file, package)


# Only use ext_modules during actual build
ext_modules = get_ext_modules()

setup(
    ext_modules=ext_modules,
    packages=find_packages(),
    package_data={
        "": ["*.md", "*.txt", "*.yaml", "*.yml"],
    },
    cmdclass={
        'build_py': build_py,
    } if USE_CYTHON and ext_modules else {},
)
