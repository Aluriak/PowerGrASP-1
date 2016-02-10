"""
Definition of numerous constants, for paths, names, arguments for ASP solvers.
Moreover, some generalist functions are defined,
 notabily for solving management and logging.

"""

# IMPORTS
import logging, logging.handlers
import multiprocessing  # get number of available CPU
import pkg_resources  # packaging facilies
import os

from functools   import partial
from collections import ChainMap

from docopt import docopt

from powergrasp.info import PACKAGE_NAME, PACKAGE_VERSION


# Constants
ASP_FILE_EXTENSION = '.lp'
BUBBLE_FORMAT_ID   = 'bbl'

# Directories (starting from the package level)
DIR_SOURCES     = ''  # sources are inside the package
DIR_DATA        = 'data/'
DIR_TEST_CASES  = 'tests/'
DIR_LOGS        = 'logs/'
DIR_ASP_SOURCES = 'ASPsources/'

# Packaging: access to the file, inside the package,
#   independently of the installation directory
access_packaged_file = partial(pkg_resources.resource_filename, PACKAGE_NAME)

# LOGGING VALUES
LOGGER_NAME       = PACKAGE_NAME
DEFAULT_LOG_FILE  = access_packaged_file(DIR_LOGS + LOGGER_NAME + '.log')
DEFAULT_LOG_LEVEL = logging.DEBUG

# PATH INSIDE PACKAGE
PACKAGE_DIR_DATA = access_packaged_file('data/')

# Optimization values
OPT_LOWERBOUND_CUTOFF = 2  # minimal value for the lowerbound optimization

# ASP SOURCES
def __asp_file(name):
    "path to given asp source file name"
    return access_packaged_file(DIR_ASP_SOURCES + name + ASP_FILE_EXTENSION)
ASP_SRC_EXTRACT   = __asp_file('extract')
ASP_SRC_PREPRO    = __asp_file('preprocessing')
ASP_SRC_FINDCC    = __asp_file('findbestclique')
ASP_SRC_FINDBC    = __asp_file('findbestbiclique')
ASP_SRC_POSTPRO   = __asp_file('postprocessing')
ASP_SRC_INCLUSION = __asp_file('inclusion')

# Constants involved in ASP solving
ASP_ARG_CC   = 'cc'
ASP_ARG_STEP = 'k'
ASP_ARG_UPPERBOUND = 'upperbound'
ASP_ARG_LOWERBOUND = 'lowerbound'

# ASP Solver options
ASP_GRINGO_OPTIONS = ''  # no default options
ASP_CLASP_OPTIONS  = ''  # options of solving heuristics
ASP_CLASP_OPTIONS += ' --configuration=frumpy'
ASP_CLASP_OPTIONS += ' --heuristic=Vsids'
# ASP_CLASP_OPTIONS.append('--opt-mode=opt')
# ASP_CLASP_OPTIONS.append('--models=0')
# ASP_CLASP_OPTIONS     = []
# ASP_CLASP_OPTIONS.append('--opt-strategy=bb,1') # default and best with frumpy + Vsids
# ASP_CLASP_OPTIONS.append('--opt-strategy=bb,2') # better in default mode
# ASP_CLASP_OPTIONS.append('--opt-strategy=bb,3') # longest of the bb
# ASP_CLASP_OPTIONS.append('--opt-strategy=usc,1') # usc seems to never finish…
# ASP_CLASP_OPTIONS.append('--opt-strategy=usc,2')
# ASP_CLASP_OPTIONS.append('--opt-strategy=usc,3')


# ASP_CLASP_OPTIONS.append('--heuristic=Berkmin') # default and ok
# ASP_CLASP_OPTIONS.append('--heuristic=Vsids') # the faster
# ASP_CLASP_OPTIONS.append('--heuristic=Vmtf')
# ASP_CLASP_OPTIONS.append('--heuristic=Domain')
# ASP_CLASP_OPTIONS.append('--heuristic=Unit')
# ASP_CLASP_OPTIONS.append('--heuristic=None')


# Definition of the default program options
PROGRAM_OPTIONS = {
    'graph_data'      : None,
    'extracting'      : ASP_SRC_EXTRACT,
    'preprocessing'   : ASP_SRC_PREPRO,
    'findingbiclique' : ASP_SRC_FINDBC,
    'findingclique'   : ASP_SRC_FINDCC,
    'postprocessing'  : ASP_SRC_POSTPRO,
    'output_file'     : None,
    'output_format'   : BUBBLE_FORMAT_ID,
    'interactive'     : False,
    'show_pre'        : False,
    'count_model'     : True,
    'count_cc'        : True,
    'timers'          : True,
    'lbound_cutoff'   : OPT_LOWERBOUND_CUTOFF,
    'loglevel'        : DEFAULT_LOG_LEVEL,
    'logfile'         : DEFAULT_LOG_FILE,
    'stats_file'      : None,
    'plot_stats'      : False,
    'plot_file'       : False,
    'profiling'       : False,
    'thread'          : 1,
    'draw_lattice'    : None,
}


# Functions
def basename(filepath):
    """Return the basename of given filepath.

    >>> import os
    >>> basename('~/ASP/serious/business/fly.lp')
    fly

    """
    return os.path.splitext(os.path.basename(filepath))[0]

def extension(filepath):
    """Return the extension of given filepath.

    >>> import os
    >>> basename('~/ASP/serious/business/fly.lp')
    lp

    """
    return os.path.splitext(os.path.basename(filepath))[1][1:]

def options_from_cli(documentation):
    """Parse the arguments with docopt, and return the dictionnary of arguments.

    All None values are put away, and the returned object is a ChainMap that
    use the default configuration for non given parameters.

    """
    docopt_args = docopt(documentation, version=PACKAGE_VERSION)
    IRRELEVANT_CLI_OPTIONS = ('--version', '--help')
    # filter out cli options not given by user
    import sys
    cli_args = set(
        arg.split('=')[0] if '=' in arg else arg
        for arg in sys.argv
    )
    docopt_args = {
        name: value
        for name, value in docopt_args.items()
        if name in cli_args
    }
    cli_args = {
        arg.lstrip('-').replace('-', '_'): value
        for arg, value in docopt_args.items()
        if value is not None and arg not in IRRELEVANT_CLI_OPTIONS
    }
    # raise error in case of unexpected argument
    if any(arg not in PROGRAM_OPTIONS for arg in cli_args):
        unexpected_args = (arg for arg in cli_args
                           if arg not in PROGRAM_OPTIONS)
        raise ValueError(
            'ERROR: ' + str(tuple(unexpected_args)) + ' arguments is not in '
            + str(tuple(PROGRAM_OPTIONS.keys()))
        )
    return ChainMap(cli_args, PROGRAM_OPTIONS)

def thread(number):
    """Return Clasp options for use n thread, or if n is invalid, use the
    number of CPU available"""
    if number is not None and 1 <= int(number) <= 64:
        return ' --parallel-mode=' + str(number)
    else:
        nb_cpu = str(multiprocessing.cpu_count())
        # nb_cpu = '1'
        logger().info('Threading: No valid number of CPU given ([1;64]). '
                      + nb_cpu + ' CPU will be used by Clasp.')
        return ' --parallel-mode=' + nb_cpu


# logging functions
def logger(name=LOGGER_NAME):
    """Return logger of given name, without initialize it.

    Equivalent of logging.getLogger() call.

    """
    return logging.getLogger(name)


def configure_logger(log_filename=DEFAULT_LOG_FILE,
                     term_log_level=DEFAULT_LOG_LEVEL):
    """Operate the logger configuration for the package"""
    # defensive cases: use defaults if None given
    if log_filename is None: log_filename = DEFAULT_LOG_FILE
    if term_log_level is None: term_log_level = DEFAULT_LOG_LEVEL
    # put given log level in upper case
    try:
        term_log_level = term_log_level.upper()
    except AttributeError:  # term_log_level is an integer, not a string
        pass  # nothing to do, lets keep the log level as an int

    # remove any previous configuration
    _logger = logging.getLogger(LOGGER_NAME)
    _logger.handlers.clear()
    _logger.setLevel(DEFAULT_LOG_LEVEL)

    # setup terminal log
    stream_handler = logging.StreamHandler()
    formatter      = logging.Formatter('%(levelname)s: %(message)s')
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(term_log_level)
    _logger.addHandler(stream_handler)

    # setup log file (or log the failure)
    try:
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        file_handler = logging.handlers.RotatingFileHandler(
            log_filename, 'a', 2**16, 0)
        file_handler.setLevel(logging.DEBUG)  # get always all data
        file_handler.setFormatter(formatter)
        _logger.addHandler(file_handler)
    except PermissionError:
        _logger.warning(os.path.abspath(DIR_LOGS + LOGGER_NAME + '.log')
                        + "can't be written because of a permission error."
                        + "No logs will be saved in file.")


def log_file(filename):
    """Set the log file"""
    configure_logger(log_filename=filename)


def log_level(level):
    """Set terminal log level to given one"""
    _logger = logger()
    handlers = (_ for _ in _logger.handlers
                if isinstance(_, logging.StreamHandler)
               )
    for handler in handlers:
        handler.setLevel(level.upper())



