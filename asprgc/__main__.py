# -*- coding: utf-8 -*-
"""
usage:
    __main__.py [options]

options:
    --help, -h
    --version, -v
    --iterations=NUMBER number of iterations performed, or None if no maximum
    --graph-data=FILE   filepath to ASP graph definition       [default: tests/double_biclique.lp]
    --extract=FILE      filepath to ASP extraction program     [default: data/extract.lp]
    --findconcept=FILE  filepath to ASP concept finder program [default: data/findbestconcept.lp]
    --update=FILE       filepath to ASP updating program       [default: data/edgeupdate.lp]

"""

from __future__ import print_function, absolute_import
from docopt     import docopt
from asprgc     import asprgc
from info       import __version__




if __name__ == '__main__':
    # read options
    options = docopt(__doc__, version=__version__)

    # parse them
    try:    iterations = int(options['--iterations' ])
    except: iterations = None

    # launch compression
    (asprgc(
        iterations = iterations,
        graph      = options['--graph-data' ],
        extract    = options['--extract'    ],
        findcc     = options['--findconcept'],
        update     = options['--update'     ],

    ))




