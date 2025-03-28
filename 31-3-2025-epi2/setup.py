from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("/Users/nt/Documents/github/Blog-Post-Code/31-3-2025-epi2/Cvirus.pyx")
)