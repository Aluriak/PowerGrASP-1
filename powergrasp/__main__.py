"""
usage:
    __main__.py [options]

options:
    --help, -h
    --version, -v
    --graph-data=FILE       filepath to input graph definition
    --output-file=NAME      output file or dir
    --output-format=NAME    output format (see below for formats)
    --interactive           program ask user for next step
    --show-pre              print preprocessed data in stdout
    --count-model           prints models count in stdout
    --count-cc              prints connected component count in stdout
    --timers                prints times of execution in stdout
    --loglevel=NAME         defines terminal log level
    --logfile=FILE          file where all logs will be put in
    --stats-file=FILE       save csv statistics in FILE
    --plot-stats            plot stats found in stats-file if exist
    --plot-file=FILE        instead of show it, save plot in png FILE
    --profiling             print graph info before compress it
    --thread=INT            use INT thread for ASP solving (0 for automatic detection)
    --draw_lattice=DIR      draw in DIR the concept lattice foreach con. comp.

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

    # get options, including CLI
    options = commons.options(cli_doc=__doc__)

    # parse them
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
            graph_data      = options['graph_data'     ],
            output_file     = options['output_file'    ],
            output_format   = options['output_format'  ],
            interactive     = options['interactive'    ],
            count_model     = options['count_model'    ],
            count_cc        = options['count_cc'       ],
            timers          = options['timers'         ],
            stats_file      = options['stats_file'     ],
            logfile         = options['logfile'        ],
            loglevel        = options['loglevel'       ],
            thread          = options['thread'         ],
            draw_lattice    = options['draw_lattice'   ],
        )

    # plotting if statistics csv file given, and showing or saving requested
    if((options['plot_stats'] or options['plot_file']) and
            options['stats_file']):
        plots(
            options['stats_file'],
            savefile=options['plot_file']
        )


