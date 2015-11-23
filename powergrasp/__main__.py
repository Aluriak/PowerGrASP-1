# -*- coding: utf-8 -*-
"""
usage:
    __main__.py [options]

options:
    --help, -h
    --version, -v
    --graph-data=FILE    filepath to input graph definition
    --extract=FILE       filepath to custom ASP extraction program
    --preprocess=FILE    filepath to custom ASP preprocessing program
    --findbiclique=FILE  filepath to custom ASP biclique finder program
    --findclique=FILE    filepath to custom ASP clique finder program
    --postprocess=FILE   filepath to custom ASP postprocessing program
    --output-file=NAME   output file or dir
    --output-format=NAME output format (see below for formats)      [default: bbl]
    --interactive        program ask user for next step
    --show-pre           print preprocessed data in stdout
    --count-model        prints models count in stdout
    --count-cc           prints connected component count in stdout
    --lbound-cutoff=INT  cut-off for max lowerbound optimization    [default: 2]
    --loglevel=NAME      defines terminal log level                 [default: warning]
    --logfile=FILE       file where all logs will be put in
    --stats-file=FILE    save csv statistics in FILE
    --plot-stats         plot stats found in stats-file if exist
    --plot-file=FILE     instead of show it, save plot in png FILE
    --profiling          print graph info before compress it
    --thread=INT         use n thread for ASP solving               [default: 1]

output formats:
    BBL         formated in Bubble format, readable by CyOog plugin of Cytoscape

input formats:
    ASP         edge/2 atoms, where edge(X,Y) describes a link between X and Y.
    SBML        SBML file. Species and reactions will be translated as nodes.
    GML         Graph Modeling Language file.

"""

from docopt                import docopt
from powergrasp.powergrasp import compress
from powergrasp.converter  import OUTPUT_FORMATS
from powergrasp import info
from powergrasp import statistics
from powergrasp import converter
from powergrasp import commons
from powergrasp import utils
import os




if __name__ == '__main__':
    LOGGER = commons.logger()

    # read options
    options = docopt(__doc__, version=info.__version__)

    # parse them
    # define the log file and the log level, if necessary
    commons.configure_logger(options['--logfile'], options['--loglevel'])
    # threading
    nb_thread = int(options['--thread'])
    if nb_thread > 1:
        commons.thread(nb_thread)
    # cut-off
    lbound_cutoff = int(options['--lbound-cutoff'])
    # output format verification
    assert(options['--output-format'] in OUTPUT_FORMATS)

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
            print(utils.test_integrity(options['--graph-data']))

        if options['--output-file'] is None:
            pass
        elif os.path.isdir(options['--output-file']):
            LOGGER.info('Given output file is not a file, but a directory ('
                        + options['--output-file'] + ').'
                        + ' Output file will be placed in it, with the name '
                        + commons.basename(options['--graph-data']))
            options['--output-file'] = os.path.join(
                options['--output-file'],
                commons.basename(options['--graph-data'])
            )
        elif not options['--output-file'].endswith(options['--output-format']):
            # given output file doesn't ends with the proper extension
            options['--output-file'] += '.' + options['--output-format']

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
            show_preprocessed  = options['--show-pre'     ],
            count_model        = options['--count-model'  ],
            count_cc           = options['--count-cc'     ],
            statistics_filename= options['--stats-file'   ],
        )

    # plotting if statistics csv file given, and showing or saving requested
    if((options['--plot-stats'] or options['--plot-file']) and
            options['--stats-file']):
        statistics.plots(
            options['--stats-file'],
            savefile=options['--plot-file']
        )



