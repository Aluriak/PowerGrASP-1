# -*- coding: utf-8 -*-
"""
usage:
    __main__.py [options]

options:
    --help, -h
    --version, -v
    --graph-data=FILE       filepath to input graph definition
    --extracting=FILE       filepath to custom ASP extraction program
    --preprocessing=FILE    filepath to custom ASP preprocessing program
    --findingbiclique=FILE  filepath to custom ASP biclique finder program
    --findingclique=FILE    filepath to custom ASP clique finder program
    --postprocessing=FILE   filepath to custom ASP postprocessing program
    --output-file=NAME      output file or dir
    --output-format=NAME    output format (see below for formats)
    --interactive           program ask user for next step
    --show-pre              print preprocessed data in stdout
    --count-model           prints models count in stdout
    --count-cc              prints connected component count in stdout
    --timers                prints times of execution in stdout
    --lbound-cutoff=INT     cut-off for max lowerbound optimization
    --loglevel=NAME         defines terminal log level
    --logfile=FILE          file where all logs will be put in
    --stats-file=FILE       save csv statistics in FILE
    --plot-stats            plot stats found in stats-file if exist
    --plot-file=FILE        instead of show it, save plot in png FILE
    --profiling             print graph info before compress it
    --thread=INT            use INT thread for ASP solving

output formats:
    BBL         formated in Bubble format, readable by CyOog plugin of Cytoscape

input formats:
    ASP         edge/2 atoms, where edge(X,Y) describes a link between X and Y.
    SBML        SBML file. Species and reactions will be translated as nodes.
    GML         Graph Modeling Language file.

"""

import os

from powergrasp.powergrasp import compress
from powergrasp.converter  import OUTPUT_FORMATS
from powergrasp import statistics
from powergrasp import converter
from powergrasp import commons
from powergrasp import plots
from powergrasp import utils
from powergrasp import info


if __name__ == '__main__':
    LOGGER = commons.logger()

    # read CLI options
    options = commons.options_from_cli(__doc__)

    # parse them
    # cut-off
    options['lbound_cutoff'] = int(options['lbound_cutoff'])
    # output format verification
    assert(options['output_format'] in OUTPUT_FORMATS)

    # launch compression
    if options['graph_data']:

        if options['profiling']:
            print(utils.test_integrity(options['graph_data']))

        if options['output_file'] is None:
            pass
        elif os.path.isdir(options['output_file']):
            LOGGER.info('Given output file is not a file, but a directory ('
                        + options['output_file'] + ').'
                        + ' Output file will be placed in it, with the name '
                        + commons.basename(options['graph_data']))
            options['output_file'] = os.path.join(
                options['output_file'],
                commons.basename(options['graph_data'])
            )

        # compression itself
        compress(
            graph_data_or_file = options['graph_data'     ],
            extracting         = options['extracting'     ],
            preprocessing      = options['preprocessing'  ],
            ccfinding          = options['findingclique'  ],
            bcfinding          = options['findingbiclique'],
            postprocessing     = options['postprocessing' ],
            output_file        = options['output_file'    ],
            output_format      = options['output_format'  ],
            lowerbound_cut_off = options['lbound_cutoff'  ],
            interactive        = options['interactive'    ],
            show_preprocessed  = options['show_pre'       ],
            count_model        = options['count_model'    ],
            count_cc           = options['count_cc'       ],
            timers             = options['timers'         ],
            statistics_filename= options['stats_file'     ],
            logfile            = options['logfile'        ],
            loglevel           = options['loglevel'       ],
            thread             = options['thread'         ],
        )

    # plotting if statistics csv file given, and showing or saving requested
    if((options['plot_stats'] or options['plot_file']) and
            options['stats_file']):
        plots(
            options['stats_file'],
            savefile=options['plot_file']
        )


