# -*- coding: utf-8 -*-
"""
usage:
    benchmarks.py [options]

options:
    --help, -h
    --version, -v
    --inputs=FILE[,FILE] input files
    --output-file=FILE   filename containing the final csv data     [default: data/benchmarks.csv]
    --runs=INT           number of run for each input               [default: 3]
    --no-threading       don't use threading optimization
    --lbound-cutoff=INT  cut-off for max lowerbound optimization    [default: 2]
    --loglevel=NAME      defines terminal log level                 [default: error]
    --thread=INT         use n thread for ASP solving (one by default)

Performs benchmarks of the compression process.
Generate a CSV file as output.

"""


from docopt     import docopt
from powergrasp import compress
from info       import __version__, STUDYNAMES
from converter  import OUTPUT_FORMATS
from functools  import partial
import os
import csv
import utils
import timeit
import commons
import tempfile
import converter
import statistics


LOGGER = commons.logger()


# CSV DATA
FIELD_NAME = 'name'
FIELD_FLNM = 'filename'
FIELD_METH = 'powergrasp implementation'
FIELD_TIME = 'average time'
FIELD_NODE = '#node'
FIELD_EDGE = '#edge'
FIELD_EGRD = 'edge reduction'
FIELD_CVRT = 'conversion rate'
ALL_FIELDS = (FIELD_NAME, FIELD_FLNM, FIELD_METH, FIELD_TIME,
              FIELD_NODE, FIELD_EDGE, FIELD_EGRD, FIELD_CVRT)

# Method used for implement the non-overlapping power node detection
#  blocks or concept reduction
POWERGRASP_METHOD = 'blocks'



def launch_compression(input_file, compress, writer):
    """
    input_file -- filename that contains the graph data
    compress -- function that takes filename and return the compression time
    writer -- csv writer in the benchmarks file

    """
    input_file_asp = input_file
    # launch compressions
    if input_file:
        # convert given graph in ASP readable edge/2 if necessary
        if commons.extension(input_file) != 'lp':
            converter = converter.input_converter_for(
                commons.extension(input_file)
            )
            if converter:
                input_file_asp = converter.convert(input_file)
            else:
                raise ValueError('Given input is not a valid input format')

        # compression itself
        runs = (  # get a tuple of compression runtime
            compress(input_file_asp)
            for i in range(options['--runs'])
        )
        time_acc = 0.
        edge_reduction  = None
        conversion_rate = None
        for runtime, stats in runs:
            time_acc += runtime
            assert(edge_reduction is None or
                edge_reduction == statistics.edge_reduction(stats))
            assert(conversion_rate is None or
                conversion_rate == statistics.conversion_rate(stats))
            edge_reduction  = statistics.edge_reduction(stats)
            conversion_rate = statistics.conversion_rate(stats)

        graph_data = utils.test_integrity(input_file)

        writer.writerow({
            FIELD_NAME: STUDYNAMES[commons.basename(input_file)],
            FIELD_FLNM: input_file,
            FIELD_METH: POWERGRASP_METHOD,
            FIELD_TIME: round(time_acc / options['--runs'], 2),
            FIELD_EGRD: round(statistics.edge_reduction(stats), 2),
            FIELD_CVRT: round(statistics.conversion_rate(stats), 2),
            FIELD_EDGE: graph_data['edge'],
            FIELD_NODE: graph_data['node'],
        })





if __name__ == '__main__':
    # read options
    options = docopt(__doc__, version=__version__)

    # parse them
    lbound_cutoff = int(options['--lbound-cutoff'])
    commons.log_level(options['--loglevel'])
    commons.thread(options['--thread'])
    options['--runs'] = int(options['--runs'])
    assert(options['--runs'] > 0)

    # create the output file (/dev/null, but compatible with non-Unix)
    dev_null = tempfile.NamedTemporaryFile(delete=False).name

    # create the compression function
    compress = partial(
        compress,
        output_file        = dev_null,
        lowerbound_cut_off = lbound_cutoff,
        no_threading       = options['--no-threading' ],
    )

    # open the benchmark file
    outputfile = open(options['--output-file'], 'w')
    writer = csv.DictWriter(outputfile, fieldnames=ALL_FIELDS)
    writer.writeheader()

    for input_file in options['--inputs'].split(','):
        print('Benchmarking file ' + input_file + '…')
        launch_compression(input_file, compress, writer)

    outputfile.close()



