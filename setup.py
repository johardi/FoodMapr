from distutils.core import setup

from setuptools import find_packages

from foodmapr import __version__

classifiers = """
Development Status :: 4 - Beta
Environment :: Console
License :: OSI Approved :: GNU General Public License (GPL)
Intended Audience :: Science/Research
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Bio-Informatics
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.6
Operating System :: POSIX :: Linux
""".strip().split('\n')

setup(name='foodmapr',
      version=__version__,
      description='A derived work of LexMapr focusing on food items and products',
      author='Josef Hardi',
      author_email='josef.hardi@gmail.com',
      url='https://github.com/johardi/FoodMapr',
      license='GPL-3.0',
      classifiers=classifiers,
      install_requires=[
          'nltk==3.6.2',
          'inflection==0.5.1',
          'rdflib==5.0.0',
      ],
      python_requires='>=3.5, <3.9',
      test_suite='nose.collector',
      tests_require=['nose'],
      packages=find_packages(),
      include_package_data=True,
      scripts=['bin/foodmapr']
)
