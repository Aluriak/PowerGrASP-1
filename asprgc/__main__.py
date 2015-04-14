# -*- coding: utf-8 -*-
"""
usage:
    __main__.py [options]

options:
    --help, -h
    --version, -v
    --graph-data=FILE   filepath to ASP graph definition       [default: data/diamond.lp]
    --extract=FILE      filepath to ASP extraction program     [default: data/extract.lp]
    --findconcept=FILE  filepath to ASP concept finder program [default: data/findconcept.lp]

"""

from __future__ import print_function, absolute_import
from docopt     import docopt
from asprgc     import asprgc 
from info       import __version__

     



if __name__ == '__main__':
    # read options 
    options = docopt(__doc__, version=__version__)
    (asprgc(
        graph   = options['--graph-data'],
        extract = options['--extract'],
        findcc  = options['--findconcept'],
    ))




