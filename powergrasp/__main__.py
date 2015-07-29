# -*- coding: utf-8 -*-
"""
usage:
    __main__.py [options]

options:
    --help, -h
    --version, -v
    --graph-data=FILE    filepath to ASP graph definition
    --extract=FILE       filepath to ASP extraction program         [default: powergrasp/ASPsources/extract.lp]
    --preprocess=FILE    filepath to ASP preprocessing program      [default: powergrasp/ASPsources/preprocessing.lp]
    --findbiclique=FILE  filepath to ASP biclique finder program    [default: powergrasp/ASPsources/findbestbiclique.lp]
    --findclique=FILE    filepath to ASP clique finder program      [default: powergrasp/ASPsources/findbestclique.lp]
    --postprocess=FILE   filepath to ASP postprocessing program     [default: powergrasp/ASPsources/postprocessing.lp]
    --remain=FILE        filepath to ASP remain finder program      [default: powergrasp/ASPsources/remains.lp]
    --output-file=NAME   output file or dir (without extension)     [default: data/tmp]
    --output-format=NAME output format (see below for formats)      [default: bbl]
    --interactive        program ask user for next step
    --count-model        prints models count in stdout
    --count-cc           prints connected component count in stdout
    --no-threading       don't use threading optimization
    --lbound-cutoff=INT  cut-off for max lowerbound optimization    [default: 2]
    --loglevel=NAME      defines terminal log level                 [default: debug]
    --stats-file=FILE    save csv statistics in FILE
    --plot-stats         plot stats found in stats-file if exist
    --plot-file=FILE     instead of show it, save plot in png FILE
    --profiling          print graph info before compress it
    --thread=INT         use n thread for ASP solving (one by default)

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
import os
import commons
import converter
import statistics


LOGGER = commons.logger()


if __name__ == '__main__':
    # read options
    options = docopt(__doc__, version=__version__)

    # parse them
    lbound_cutoff = int(options['--lbound-cutoff'])
    assert(options['--output-format'] in OUTPUT_FORMATS)

    commons.log_level(options['--loglevel'])
    commons.thread(options['--thread'])

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

        if os.path.isdir(options['--output-file']):
            LOGGER.info('Given output file is not a file, but a directory ('
                        + options['--output-file'] + ').'
                        + ' Output file will be placed in it, with the name '
                        + commons.basename(options['--graph-data']))
            options['--output-file'] = os.path.join(
                options['--output-file'],
                commons.basename(options['--graph-data'])
            )

        # compression itself
        compress(
            graph_data         = options['--graph-data'   ],
            extracting         = options['--extract'      ],
            preprocessing      = options['--preprocess'   ],
            ccfinding          = options['--findclique'   ],
            bcfinding          = options['--findbiclique' ],
            postprocessing     = options['--postprocess'  ],
            output_file        = options['--output-file'  ],
            output_format      = options['--output-format'],
            lowerbound_cut_off = lbound_cutoff,
            interactive        = options['--interactive'  ],
            count_model        = options['--count-model'  ],
            count_cc           = options['--count-cc'     ],
            no_threading       = options['--no-threading' ],
            statistics_filename= options['--stats-file'   ],
        )

    # plotting if statistics csv file given, and showing or saving requested
    if((options['--plot-stats'] or options['--plot-file']) and
            options['--stats-file']):
        statistics.plots(
            options['--stats-file'],
            savefile=options['--plot-file']
        )



