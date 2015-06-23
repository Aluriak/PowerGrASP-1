# -*- coding: utf-8 -*-
"""
usage:
    __main__.py [options]

options:
    --help, -h
    --version, -v
    --graph-data=FILE    filepath to ASP graph definition       [default: tests/double_biclique.lp]
    --extract=FILE       filepath to ASP extraction program     [default: powergrasp/ASPsources/extract.lp]
    --findconcept=FILE   filepath to ASP concept finder program [default: powergrasp/ASPsources/findbestconcept.lp]
    --remain=FILE        filepath to ASP remain finder program  [default: powergrasp/ASPsources/remains.lp]
    --output-file=NAME   output file (without extension)        [default: data/output]
    --output-format=NAME output format                          [default: bbl]
    --interactive=BOOL   if true, program ask user for next step[default: 0]
    --count-model=BOOL   if true, prints models count in stdout [default: 0]
    --threading=BOOL     if true, use threading optimization    [default: 1]
    --loglevel=NAME      defines terminal log level             [default: debug]
    --heuristic=NAME     defines heuristic used by the solver   [default: frumpy]

output formats:
    BBL                 formated in Bubble format, readable by CyOog plugin of Cytoscape
"""

from __future__ import absolute_import, print_function
from docopt     import docopt
from powergrasp import compress
from info       import __version__
from converter  import OUTPUT_FORMATS
import commons




if __name__ == '__main__':
    # read options
    options = docopt(__doc__, version=__version__)

    # parse them
    def boolean(s): return s not in (0, '0', 'False', 'false')
    interactive = boolean(options['--interactive'])
    count_model = boolean(options['--count-model'])
    threading   = boolean(options['--threading'  ])
    assert(options['--output-format'] in OUTPUT_FORMATS)

    commons.log_level(options['--loglevel'])

    # launch compression
    (compress(
        graph_data    = options['--graph-data'   ],
        extracting    = options['--extract'      ],
        ccfinding     = options['--findconcept'  ],
        remaining     = options['--remain'       ],
        output_file   = options['--output-file'  ],
        output_format = options['--output-format'],
        heuristic     = options['--heuristic'    ],
        interactive   = interactive,
        count_model   = count_model,
        threading     = threading,
    ))




