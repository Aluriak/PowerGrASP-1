# -*- coding: utf-8 -*-
#########################
#       SETUP.PY        #
#########################


#########################
# IMPORTS               #
#########################
from setuptools  import setup, find_packages
from asprgc.info import __version__, __name__



#########################
# SETUP                 #
#########################
setup(
    name = __name__,
    version = __version__,
    py_modules = ['info'],
    packages = find_packages(exclude=['asprgc/']), 
    package_data = {
        __name__ : ['README.mkd', 'LICENSE.txt']
    },
    include_package_data = True,

    author = "lucas bourneuf",
    author_email = "lucas.bourneuf@openmailbox.org",
    description = "Graph compression by recursive approach with Answer Set Programming",
    long_description = open('README.mkd').read(),
    keywords = "graph",
    url = "https://github.com/Aluriak/asprgc",

    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2",
        "Programming Language :: ASP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)



