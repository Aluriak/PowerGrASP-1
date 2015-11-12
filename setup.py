# -*- coding: utf-8 -*-
#########################
#       SETUP.PY        #
#########################


#########################
# IMPORTS               #
#########################
from setuptools  import setup, find_packages
from powergrasp.info import __version__, __name__
from pip.req import parse_requirements
from pip.download import PipSession


# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements('requirements.txt', session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]


#########################
# SETUP                 #
#########################
setup(
    name = __name__,
    version = __version__,
    packages = find_packages(),
    package_data = {
        '' : ['README.mkd', 'LICENSE.txt', 'requirements.txt',
              'optional-requirements.txt', 'Makefile', 'LICENCE'],
        'powergrasp': ['ASPsources/*.lp', 'logs/README.txt',
                       'tests/*.lp', 'tests/*.sbml', 'tests/*.gml'],
    },
    include_package_data = True,
    install_requires=reqs,

    author = "lucas bourneuf",
    author_email = "lucas.bourneuf@openmailbox.org",
    description = "Graph compression with Answer Set Programming",
    long_description = open('README.mkd').read(),
    keywords = "graph",
    url = "https://github.com/Aluriak/powergrasp",

    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: ASP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)



