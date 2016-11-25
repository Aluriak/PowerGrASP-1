"""

For CLI usage, see the help:
    python -m powergrasp --help

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
            no_save_time    = options['no_save_time'   ],
            do_profiling    = options['profiling'      ],
        )

    # plotting if statistics csv file given, and showing or saving requested
    if((options['plot_stats'] or options['plot_file']) and
            options['stats_file']):
        plots(
            options['stats_file'],
            savefile=options['plot_file']
        )


