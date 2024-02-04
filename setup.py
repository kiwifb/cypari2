#!/usr/bin/env python

import os

from setuptools import setup
from distutils.command.build_ext import build_ext as _build_ext
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg
from setuptools.extension import Extension

from autogen import rebuild
from autogen.paths import include_dirs, library_dirs

ext_kwds = dict(include_dirs=include_dirs(), library_dirs=library_dirs())


if "READTHEDOCS" in os.environ:
    # When building with readthedocs, disable optimizations to decrease
    # resource usage during build
    ext_kwds["extra_compile_args"] = ["-O0"]

    # Print PARI/GP defaults and environment variables for debugging
    from subprocess import Popen, PIPE
    Popen(["gp", "-f", "-q"], stdin=PIPE).communicate(b"default()")
    for item in os.environ.items():
        print("%s=%r" % item)


# Adapted from Cython's new_build_ext
class build_ext(_build_ext):
    def finalize_options(self):
        # Generate auto-generated sources from pari.desc
        rebuild()

        self.directives = {
            "autotestdict.cdef": True,
            "binding": True,
            "cdivision": True,
            "language_level": 2,
            "legacy_implicit_noexcept": True,
            "c_api_binop_methods": True,
        }

        _build_ext.finalize_options(self)

    def run(self):
        # Run Cython
        from Cython.Build.Dependencies import cythonize
        self.distribution.ext_modules[:] = cythonize(
            self.distribution.ext_modules,
            compiler_directives=self.directives)

        _build_ext.run(self)


class no_egg(_bdist_egg):
    def run(self):
        from distutils.errors import DistutilsOptionError
        raise DistutilsOptionError("The package cypari2 will not function correctly when built as egg. Therefore, it cannot be installed using 'python setup.py install' or 'easy_install'. Instead, use 'pip install' to install cypari2.")


setup(
    ext_modules=[Extension("*", ["cypari2/*.pyx"], **ext_kwds)],
    packages=['cypari2'],
    package_dir={'cypari2': 'cypari2'},
    package_data={'cypari2': ['declinl.pxi', '*.pxd', '*.h']},
    cmdclass=dict(build_ext=build_ext, bdist_egg=no_egg)
)
