# -*- coding: utf-8 -*-
"""
usage:
    __main__.py [options]

options:
    --help, -h
    --version, -v
    --iterations=NUMBER number of iterations performed, or None if no maximum
    --graph-data=FILE   filepath to ASP graph definition       [default: data/diamond.lp]
    --extract=FILE      filepath to ASP extraction program     [default: data/extract.lp]
    --findconcept=FILE  filepath to ASP concept finder program [default: data/findconcept.lp]
    --findcliques=FILE  filepath to ASP cliques finder program [default: data/findcliques.lp]
    --firstmodel=FILE   filepath to ASP first model program    [default: data/firstmodel.lp]
    --nextmodel=FILE    filepath to ASP next  model program    [default: data/model.lp]
    --update=FILE       filepath to ASP updating program       [default: data/update.lp]

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
        findcl     = options['--findcliques'],
        firstmodel = options['--firstmodel' ],
        update     = options['--update'     ],
        nextmodel  = options['--nextmodel'  ],

    ))




