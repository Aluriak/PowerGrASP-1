# -*- coding: utf-8 -*-
"""
usage:
    __main__.py [options]

options:
    --help, -h
    --version, -v
    --iterations=NUMBER  number of iterations performed, or None if no maximum
    --graph-data=FILE    filepath to ASP graph definition       [default: tests/double_biclique.lp]
    --extract=FILE       filepath to ASP extraction program     [default: asprgc/ASPsources/extract.lp]
    --findconcept=FILE   filepath to ASP concept finder program [default: asprgc/ASPsources/findbestconcept.lp]
    --update=FILE        filepath to ASP updating program       [default: asprgc/ASPsources/edgeupdate.lp]
    --remain=FILE        filepath to ASP remain finder program  [default: asprgc/ASPsources/remains.lp]
    --output-file=NAME   output file (without extension)        [default: data/output]
    --output-format=NAME output format                          [default: bbl]
    --interactive=BOOL   if true, program ask user for next step[default: 0]

output formats:
    human                something like (almost) human readable
    ASP                  ASP atoms, ready to be grounded
    NNF                  usable by Cytoscape and others NNF readers
"""

from __future__          import print_function, absolute_import
from docopt              import docopt
from asprgc              import asprgc
from info                import __version__
from converter.converter import OUTPUT_FORMATS




if __name__ == '__main__':
    # read options
    options = docopt(__doc__, version=__version__)

    # parse them
    try:    iterations  = int(options['--iterations'])
    except: iterations  = None
    try:    interactive = options['--interactive'] in ('1', 'True', 'true')
    except: iterations  = False
    assert(options['--output-format'] in OUTPUT_FORMATS)

    # launch compression
    (asprgc(
        iterations    = iterations,
        graph         = options['--graph-data'   ],
        extract       = options['--extract'      ],
        findcc        = options['--findconcept'  ],
        update        = options['--update'       ],
        remain        = options['--remain'       ],
        output_file   = options['--output-file'  ],
        output_format = options['--output-format'],
        interactive   = interactive,

    ))




