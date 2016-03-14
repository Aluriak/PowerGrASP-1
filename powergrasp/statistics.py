# -*- coding: utf-8 -*-
"""
Definitions of many functions that works on compressions statistics.

Statistics are mainly a dictionnary with statistics information inside.

Information is itself a dict that links different parameters
 (number of initial edge, number of power{node,edge},…)
 to the value used for compute statistics.

Statistics information can be printed or saved in files
 in raw or latex tabular format.

"""
import csv

from powergrasp import observers
from powergrasp import commons
from powergrasp.observers import Signals  # shortcut


LOGGER = commons.logger()


# Compression data
# class CompressionData(Enum):
# numbers
INIT_EDGE = 'initial_edge_count'  # number of edges in the input graph
FINL_EDGE = 'remain_edge_count'   # number of edges not compressed since the compression beginning
GENR_PWED = 'poweredge_count'     # number of poweredges created since the beginning
GENR_PWND = 'powernode_count'     # number of powernodes created since the beginning
CONV_RATE = 'conversion_rate'     # computed conversion rate
EDGE_RDCT = 'edge_reduction'      # computed edge reduction
COMP_RTIO = 'compression_ratio'   # computed compression ratio
GENR_TIME = 'gentime'             # generation time for last iteration
# general
NETW_NAME = 'network_name'        # name of the input graph (name of the file containing input data)
FILE_DESC = 'file_descriptor'     # file descriptor of the output CSV file, or None if no output expected
FILE_WRTR = 'file_writer'         # CSV writer on the output CSV file, or None if no output expected

# All fields that are useful at the end of the compression are put here
PRINTABLE_FIELD = (
    INIT_EDGE, GENR_PWED, GENR_PWND, CONV_RATE,
    EDGE_RDCT, COMP_RTIO, FINL_EDGE,
)


# Output formats
FORMAT_TEX = 'tex'
FORMAT_RAW = 'txt'

# Data for plotting
MEASURES = (GENR_TIME, FINL_EDGE, GENR_PWED, GENR_PWND)
COLORS   = ('black', 'green', 'blue', 'red')
LABELS   = (
    'time per step',
    'remaining edges',
    'generated poweredge',
    'generated powernode',
)


class DataExtractor(observers.CompressionObserver, dict):
    """
    DataExtractor is a repository of various data, used for statistical analysis
     of the compression and other treatments.

    """
    GENERATED_PREFIX = '_generated_'

    def __init__(self, statistics_filename=None, network_name='network',
                 output_converter=None, time_counter=None):
        """The statistics_filename, if not None, must be a valid name of file
        that will be overrided, and will contains some data in csv format.

        The output converter, if given, is used at the end for add comments
         containing the final statistic report in the output file.
        Moreover, if the time_counter object is given, the final statistics
         will contains information about compression time.

        """
        statistics_file = None
        if statistics_filename:
            try:
                statistics_file = open(statistics_filename, 'w')
                statistics_writer = csv.DictWriter(statistics_file,
                                                   fieldnames=MEASURES)
                statistics_writer.writeheader()
            except IOError as e:
                LOGGER.warning("The file "
                               + statistics_filename + " can't be opened."
                               + " No statistics will be saved.")
        else:
            statistics_writer = None
        self.output_converter = output_converter
        self.time_counter = time_counter

        dict.__init__(self, {
            NETW_NAME: network_name,
            INIT_EDGE: 0,
            FINL_EDGE: 0,
            GENR_PWED: 0,
            GENR_PWND: 0,
            GENR_TIME: 0,
            FILE_DESC: statistics_file,
            FILE_WRTR: statistics_writer,
        })

    @property
    def compression_time(self):
        if self.time_counter:
            return self.time_counter.compression_time
        return 0.

    @property
    def extraction_time(self):
        if self.time_counter:
            return self.time_counter.extraction_time
        return 0.

    def prettified_configs(self):
        """Yield lines of a prettified view of solvers config"""
        for name, config in self.configs:
            yield from (
                name + ' configuration: ',
                '\tfiles   : ' + ', '.join(commons.basename(_) for _ in config.files),
                '\tgrounder: ' + config.gringo_options,
                '\tsolver  : ' + config.clasp_options,
            )

    def _update(self, signals):
        if Signals.CompressionStopped in signals:
            # create the final result render
            final_results = (
                "All cc have been performed"
                + ((' in ' + str(round(self.compression_time, 3)) + 's.')
                   if self.compression_time else '.')
                + ((' (including extraction in ' + str(round(self.extraction_time, 3)) + ')')
                   if self.extraction_time else '')
                + '\n' + '\n'.join(self.prettified_configs())
                + "\nNow, statistics on "
                + self.stats_output()
            )
            LOGGER.info(final_results)
            if self.output_converter:
                self.output_converter.comment(final_results.split('\n'))
            self.finalize()

        if Signals.ASPConfigUpdated in signals:
            extract, clique, biclique = signals[Signals.ASPConfigUpdated]
            self.configs = (
                ('Extraction', extract),
                ('Find best clique', clique),
                ('Find best biclique', biclique),
            )
        if Signals.FinalEdgeCountGenerated in signals:
            self[INIT_EDGE] = int(signals[Signals.FinalEdgeCountGenerated])
        if Signals.FinalRemainEdgeCountGenerated in signals:
            self[FINL_EDGE] = int(signals[Signals.FinalRemainEdgeCountGenerated])
        if Signals.StepDataGenerated in signals:
            powernode_count, poweredge_count = signals[Signals.StepDataGenerated]
            # defense against a no-data case
            if powernode_count is None:
                assert poweredge_count is None
            else:  # all data is given
                self[GENR_PWED] += int(poweredge_count)
                self[GENR_PWND] += int(powernode_count)
        if Signals.StepStopped in signals:
            if self.time_counter:
                gentime = self.time_counter.last_step_time
            else:
                gentime = 0.
            self.write_csv_data(self[GENR_PWED], self[GENR_PWND],
                                gentime, self[FINL_EDGE])


    def stats_output(self, format=FORMAT_RAW):
        """Return self as string in given format.

        format can be one of available format. Default is raw text.
        """
        assert self[INIT_EDGE] is not None
        assert self[FINL_EDGE] is not None
        assert self[GENR_PWND] is not None
        assert self[GENR_PWED] is not None
        self[CONV_RATE] = conversion_rate(
            self[INIT_EDGE], self[FINL_EDGE], self[GENR_PWED], self[GENR_PWND]
        )
        self[EDGE_RDCT] = edge_reduction(
            self[INIT_EDGE], self[FINL_EDGE], self[GENR_PWED]
        )
        self[COMP_RTIO] = compression_ratio(
            self[INIT_EDGE], self[FINL_EDGE], self[GENR_PWED]
        )
        return _formatted(dict(self), format)


    def finalize(self):
        """Close files"""
        if self[FILE_DESC]:
            self[FILE_WRTR] = None
            self[FILE_DESC].close()


    def save(self, filename, format=FORMAT_TEX, erase=False):
        """Saves itself in given filename in given format.

        format can be one of available format. Default is tabular in tex.
        if erase is True, existing content of filename will be erased.
        """
        # produce and save data
        with open(filename, ('w' if erase else 'a')) as fd:
            f.write(self.output(format))


    def write_csv_data(self, poweredge_count, powernode_count,
                       gentime, remain_edges_count):
        """Write data in the csv file, if exists, else do nothing"""
        if self[FILE_DESC]:
            self[FILE_WRTR].writerow({
                GENR_TIME: gentime,
                FINL_EDGE: remain_edges_count,
                GENR_PWED: poweredge_count,
                GENR_PWND: powernode_count,
            })


def _formatted(data, format):
    """Return a string formatted in given format that represent the given data.

    """
    fdata = ''
    if format == FORMAT_RAW:
        fdata = data[NETW_NAME] + ':'
        for field in PRINTABLE_FIELD:
            fdata += '\n\t' + field + ': ' + str(data[field])
    elif format == FORMAT_TEX:
        header  = 'network'
        payload = data[NETW_NAME]
        for field in PRINTABLE_FIELD:
            header  += ' & ' + field
            payload += ' & ' + str(data[field])
        header  += '\\\\'
        payload += '\\\\'
        fdata = header + '\n' + payload
    else:
        raise ValueError('unrecognized format')
    return fdata


# DATA COMPUTATION
def conversion_rate(initial_edge, final_edge, poweredge, powernode):
    """Compute conversion rate"""
    try:
        edge = initial_edge
        poweredge = final_edge + poweredge
        return (edge - poweredge) / powernode
    except ZeroDivisionError:
        return 1.

def edge_reduction(initial_edge, final_edge, poweredge):
    """Compute edge reduction (percentage)"""
    try:
        edge = initial_edge
        poweredge = final_edge + poweredge
        return ((edge - poweredge) / edge) * 100
    except ZeroDivisionError:
        return 100.

def compression_ratio(initial_edge, final_edge, poweredge):
    """Compute data compression ratio"""
    try:
        return initial_edge / (final_edge + poweredge)
    except ZeroDivisionError:
        return 1.
