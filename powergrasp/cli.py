"""Definition of the parameters parsing used by the module itself.

The final Configuration is a product of the parameters.
Parameters are specified by user using CLI or directly by providing
a mapping field: value.

Use argparse for CLI parsing.

Main API is parse(2).

"""


import os
import sys
import argparse
from collections import ChainMap

from powergrasp import motif
from powergrasp import commons
from powergrasp import solving
from powergrasp import converter
from powergrasp import config


# args accepted by CLI, but that should not be put in the configuration
CLI_ONLY_ARGS = ['recipe name']


def parse(parameters={}, args=sys.argv[1:], default_options:dict=None) -> dict:
    """Return the default compression options, enriched with result of CLI
    parsing if args is given, and with parameters if given.

    All None values are put away, and the returned object is a ChainMap that
    use the default configuration for non given parameters.

    Parameters have precedence over CLI.
    CLI have precedence over default options.

    """
    parameters = {k: v for k, v in parameters.items() if v is not None}

    parsed_cli = vars(cli_parser().parse_args(args))
    method = str(parsed_cli['recipe name'])
    if method == 'OEM':
        parsed_cli['motifs'] = (
            motif.Clique(scoring=commons.ASP_SRC_SCORING_OEM),
            motif.Biclique(scoring=commons.ASP_SRC_SCORING_OEM)
        )
    elif method == 'oriented':
        parsed_cli.update(config.Configuration.fields_for_oriented_graph())
    cli_args = {
        normalized(arg): value
        for arg, value in parsed_cli.items()
        if arg not in CLI_ONLY_ARGS
    } if args else {}
    return ChainMap(parameters, cli_args, default_options or {})


def normalized(arg:str) -> str:
    """Normalize argument name to valid identifier.

    >>> normalized('--foo-bar')
    'foo_bar'

    """
    return arg.lstrip('-').replace('-', '_')


def loglevel(level:str) -> str:
    """Argparse type, raising an error if given loglevel does not exists"""
    if level.upper() not in commons.LOGLEVELS:
        raise argparse.ArgumentTypeError(
            "Given loglevel ({}) doesn't exists. "
            "Expected: {}.".format(level, ', '.join(commons.LOGLEVELS))
        )
    return level


def thread_number(nbt:int) -> int:
    """Argparse type, raising an error if given thread number is non valid"""
    if float(nbt) != int(nbt):
        raise argparse.ArgumentTypeError(
            "Given number of thread ({}) is a float, not an integer.".format(nbt)
        )
    if int(nbt) < 1:
        raise argparse.ArgumentTypeError(
            "Given number of thread ({}) is not valid.".format(nbt)
        )
    return int(nbt)


def existant_file(filepath:str) -> str:
    """Argparse type, raising an error if given file does not exists"""
    if not os.path.exists(filepath):
        raise argparse.ArgumentTypeError("file {} doesn't exists".format(filepath))
    return filepath


def writable_file(filepath:str) -> str:
    """Argparse type, raising an error if given file is not writable"""
    try:
        with open(filepath, 'a') as fd:
            pass
        return filepath
    except (PermissionError, IOError):
        raise argparse.ArgumentTypeError("file {} is not writable.".format(filepath))


def output_format(format:str) -> str:
    """Argparse type, raising an error if given format does not exists"""
    if format not in converter.OUTPUT_FORMATS:
        raise argparse.ArgumentTypeError(
            "Output format {} not handled. "
            "Expected: {}".format(', '.join(format, converter.OUTPUT_FORMATS))
        )
    return format


def _populate_compression_parser(parser):
    """Add generic parameters to the given parser.

    These parameters are oriented toward compression control

    """
    # I/O arguments
    parser.add_argument('infile', type=existant_file,
                        help='file containing the graph data')
    parser.add_argument('--outfile', '-o', type=writable_file,
                        help='output file. Will be overwritted')
    parser.add_argument('--outformat', type=output_format,
                        help='Format to use for output')
    parser.add_argument('--loglevel', type=loglevel,
                        help='Logging level, one of DEBUG, INFO, WARNING, ERROR or CRITICAL')
    parser.add_argument('--logfile', type=writable_file,
                        help='Logging file, where all logs are written')

    # Compression arguments
    parser.add_argument('--thread', type=thread_number, default=1,
                        help='number of thread to use during solving')

    # Observers arguments
    parser.add_argument('--count-model', action='store_true',
                        help='Log the number of found models')
    parser.add_argument('--count-cc', action='store_true',
                        help='Log the number of found connected component')
    parser.add_argument('--timers', action='store_true',
                        help='Log measure of various timers')
    parser.add_argument('--interactive', action='store_true',
                        help='Wait for user between two motif search')
    parser.add_argument('--plot-stats', action='store_true',
                        help='Render the final statistic plot')
    parser.add_argument('--draw-lattice', action='store_true',
                        help='Render the lattice representing the graph')
    parser.add_argument('--save-time', action='store_true',
                        help='Save the compression time for further comparison')
    parser.add_argument('--signal-profile', action='store_true',
                        help='Print information on signals that are raised by compression.')

    parser.add_argument('--plot-file', help='File used to save the rendered plot')
    parser.add_argument('--stats-file', help='File to write for save statistics')


def cli_parser() -> argparse.ArgumentParser:
    """Return the dict of options set by CLI"""

    # main parser
    parser = argparse.ArgumentParser(description='CLI for PowerGrASP.')
    subs = parser.add_subparsers(dest='recipe name')

    # powergraph recipe
    parser_pwg = subs.add_parser('powergraph', description='Run a regular Powergraph compression.')
    _populate_compression_parser(parser_pwg)


    # oriented powergraph recipe
    parser_opg = subs.add_parser('oriented', description='Run an oriented Powergraph compression.')
    _populate_compression_parser(parser_opg)

    # OEM recipe
    parser_oem = subs.add_parser('OEM', description='Run a Powergraph compression that minimize the amount of outgoing edges per module.')
    _populate_compression_parser(parser_oem)



    # statistic recipe
    parser_stats = subs.add_parser('stats', description='Show statistics of compression.')
    parser_stats.add_argument('--stats-file', type=existant_file,
                              help='File to write for save statistics')
    parser_stats.add_argument('--plot-file', help='File used to save the rendered plot')


    # profiling recipe
    parser_prof = subs.add_parser('profiling', description='Run profiling of input data.')
    parser_prof.add_argument('infile', type=existant_file,
                             help='file containing the graph data')

    return parser
