# -*- coding: utf-8 -*-
"""
usage:
    __main__.py [options]

options:
    --help, -h
    --version, -v
    --graph-data=FILE    filepath to ASP graph definition
    --extract=FILE       filepath to ASP extraction program         [default: powergrasp/ASPsources/extract.lp]
    --lowerbound=FILE    filepath to ASP lowerbound program         [default: powergrasp/ASPsources/scorebound.lp]
    --findconcept=FILE   filepath to ASP concept finder program     [default: powergrasp/ASPsources/findbestconcept.lp]
    --remain=FILE        filepath to ASP remain finder program      [default: powergrasp/ASPsources/remains.lp]
    --output-file=NAME   output file (without extension)            [default: data/output]
    --output-format=NAME output format (see below for formats)      [default: bbl]
    --interactive        program ask user for next step
    --count-model        prints models count in stdout
    --no-threading       don't use threading optimization
    --aggressive         compress cliques of 2 elements
    --lbound-cutoff=INT  cut-off for max lowerbound optimization    [default: 2]
    --loglevel=NAME      defines terminal log level                 [default: debug]
    --heuristic=NAME     defines heuristic used by the solver       [default: frumpy]
    --stats-file=FILE    save csv statistics in FILE
    --plot-stats         plot stats found in stats-file if exist
    --plot-file=FILE     instead of show it, save plot in png FILE
    --profiling          print graph info before compress it

output formats:
    BBL         formated in Bubble format, readable by CyOog plugin of Cytoscape

input formats:
    ASP         edge/2 atoms, where edge(X,Y) describes a link between X and Y.
    SBML        SBML file. Species and reactions will be translated as nodes.
    GML         Graph Modeling Language file.
"""

from __future__ import absolute_import, print_function
from docopt     import docopt
from powergrasp import compress
from info       import __version__
from converter  import OUTPUT_FORMATS
import commons
import converter
import statistics




if __name__ == '__main__':
    # read options
    options = docopt(__doc__, version=__version__)

    # parse them
    lbound_cutoff = int(options['--lbound-cutoff'])
    assert(options['--output-format'] in OUTPUT_FORMATS)

    commons.log_level(options['--loglevel'])

    # launch compression
    if options['--graph-data']:
        # convert given graph in ASP readable edge/2 if necessary
        if commons.extension(options['--graph-data']) != 'lp':
            converter = converter.input_converter_for(
                commons.extension(options['--graph-data'])
            )
            if converter:
                options['--graph-data'] = converter.convert(options['--graph-data'])
            else:
                options['--graph-data'] = None

        if options['--profiling']:
            import utils
            print(utils.test_integrity(options['--graph-data']))

        # compression itself
        compress(
            graph_data         = options['--graph-data'   ],
            extracting         = options['--extract'      ],
            lowerbounding      = options['--lowerbound' ],
            ccfinding          = options['--findconcept'  ],
            remaining          = options['--remain'       ],
            output_file        = options['--output-file'  ],
            output_format      = options['--output-format'],
            heuristic          = options['--heuristic'    ],
            lowerbound_cut_off = lbound_cutoff,
            interactive        = options['--interactive'  ],
            count_model        = options['--count-model'  ],
            no_threading       = options['--no-threading' ],
            statistics_filename= options['--stats-file'   ],
            aggressive         = options['--aggressive'   ],
        )

    # plotting if statistics csv file given, and showing or saving requested
    if((options['--plot-stats'] or options['--plot-file']) and
            options['--stats-file']):
        statistics.plots(
            options['--stats-file'],
            savefile=options['--plot-file']
        )



