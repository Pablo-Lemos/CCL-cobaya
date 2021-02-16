from setuptools import setup
from ccl_cobaya import __author__, __version__
import os

file_dir = os.path.abspath(os.path.dirname(__file__))
os.chdir(file_dir)

setup(name="ccl_cobaya",
      version=__version__,
      author=__author__,
      license='LGPL',
      description='Package to integrate CCL in cobaya',
      zip_safe=False,  # set to false if you want to easily access bundled package data files
      packages=['ccl_cobaya'],
      package_data={'ccl_cobaya': ['*.yaml']},
      install_requires=['cobaya>=2.0.5'],
      #test_suite='plancklensing.tests',
      #tests_require=['camb>=1.0.5']
      # For more see https://github.com/CobayaSampler/planck_lensing_external
      )
