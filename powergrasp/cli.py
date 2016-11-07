"""Definition of the parameters parsing used by the module itself.

The final Configuration is a product of the parameters.
Parameters are specified by user using CLI or directly by providing
a mapping field: value.

Use argparse for CLI parsing.

Main API is parse(2).

"""


import sys
import argparse
from collections import ChainMap

from powergrasp import commons


def parse(parameters={}, args=sys.argv[1:]) -> dict:
    """Return the default compression options, enriched with result of CLI
    parsing if args is given, and with parameters if given.

    All None values are put away, and the returned object is a ChainMap that
    use the default configuration for non given parameters.

    Parameters have precedence over CLI.
    CLI have precedence over default parameters.

    """
    parameters = {k: v for k, v in parameters.items() if v is not None}

    cli_args = {
        normalized(arg): value
        for arg, value in vars(cli_parser().parse_args(args)).items()
    } if args else {}

    return ChainMap(parameters, cli_args, commons.DEFAULT_PROGRAM_OPTIONS)


def normalized(arg:str) -> str:
    """Normalize argument name to valid identifier.

    >>> normalized('--foo-bar')
    'foo_bar'

    """
    return arg.lstrip('-').replace('-', '_')


def cli_parser() -> argparse.ArgumentParser:
    """Return the dict of options set by CLI"""

    # main parser
    parser = argparse.ArgumentParser(description='CLI for PowerGrASP.')
    subs = parser.add_subparsers()

    # powergraph recipe
    parser_pg = subs.add_parser('powergraph', description='Run a regular Powergraph compression.')

    # I/O arguments
    parser_pg.add_argument('infile', type=str,
                           help='file containing the graph data')
    parser_pg.add_argument('--outfile', '-o', type=str,
                           help='output file. Will be overwritted')
    parser_pg.add_argument('--outformat', type=str,
                           help='Format to use for output')
    parser_pg.add_argument('--loglevel', type=str, default=commons.DEFAULT_LOG_LEVEL,
                           help='Logging level, one of DEBUG, INFO, WARNING, ERROR or CRITICAL')
    parser_pg.add_argument('--logfile', type=str, default=commons.DEFAULT_LOG_FILE,
                           help='Logging file, where all logs are written')

    # Compression arguments
    parser_pg.add_argument('--thread', type=int, default=1,
                           help='number of thread to use during solving')

    # Observers arguments
    parser_pg.add_argument('--count-model', action='store_true', help='Log the number of found models')
    parser_pg.add_argument('--count-cc', action='store_true', help='Log the number of found connected component')
    parser_pg.add_argument('--timers', action='store_true', help='Log measure of various timers')
    parser_pg.add_argument('--interactive', action='store_true', help='Wait for user between two motif search')
    parser_pg.add_argument('--plot-stats', action='store_true', help='Render the final statistic plot')
    parser_pg.add_argument('--draw-lattice', action='store_true', help='Render the lattice representing the graph')
    parser_pg.add_argument('--save-time', action='store_true', help='Save the compression time for further comparison')

    parser_pg.add_argument('--plot-file', help='File used to save the rendered plot')
    parser_pg.add_argument('--stats-file', help='Log measure of various timers')


    # statistic recipe
    parser_stats = subs.add_parser('stats', description='Show statistics of compression.')
    parser_stats.add_argument('--stats-file', help='Log measure of various timers')
    parser_stats.add_argument('--plot-file', help='File used to save the rendered plot')


    # profiling recipe
    parser_prof = subs.add_parser('profiling', description='Run profiling of input data.')
    parser_prof.add_argument('infile', type=str,
                           help='file containing the graph data')

    return parser
