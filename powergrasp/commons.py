"""
Definition of numerous constants, for paths, names, arguments for ASP solvers.
Moreover, some generalist functions are defined,
 notabily for solving management and logging.

"""

# IMPORTS
import logging, logging.config
import multiprocessing  # get number of available CPU
import pkg_resources  # packaging facilies
import sys
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
PACKAGE_DIR_DATA = access_packaged_file(DIR_DATA)
PACKAGE_DIR_TESTS = access_packaged_file(DIR_TEST_CASES)

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
# ASP_GRINGO_OPTIONS = ''  # no default options
# ASP_CLASP_OPTIONS  = ''  # options of solving heuristics
# ASP_CLASP_OPTIONS += ' --configuration=frumpy'
# ASP_CLASP_OPTIONS += ' --heuristic=Vsids'
# ASP_CLASP_OPTIONS += ' -n 0'
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
    'output_file'     : None,
    'output_format'   : BUBBLE_FORMAT_ID,
    'interactive'     : False,
    'count_model'     : False,
    'count_cc'        : False,
    'timers'          : False,
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

    >>> basename('~/ASP/serious/business/fly.lp')
    'fly'

    """
    return os.path.splitext(os.path.basename(filepath))[0]

def extension(filepath):
    """Return the extension of given filepath.

    >>> extension('~/ASP/serious/business/fly.lp')
    'lp'
    >>> extension('whatisthat')
    ''
    >>> extension('whatis.that')
    'that'

    """
    return os.path.splitext(os.path.basename(filepath))[1][1:]

def is_valid_path(filepath):
    """True iff given filepath is a valid one (a file exists, or could exists)"""
    if filepath and not os.access(filepath, os.W_OK):
        try:
            open(filepath, 'w').close()
            os.unlink(filepath)
            return True
        except OSError:
            return False
    else:  # path is accessible
        return True


def test_case(filename):
    """Return path to given filename in test case, or None if the test case
    doesn't exists"""
    path = PACKAGE_DIR_TESTS + filename
    return path if os.path.exists(path) else None


def options(*, cli_doc=None, parameters={}):
    """Return the default compression options, enriched with result of CLI
    parsing if docopt documentation is given, and with parameters if given.

    All None values are put away, and the returned object is a ChainMap that
    use the default configuration for non given parameters.

    If documentation is None, CLI will not be parsed. Else docopt will be used.

    Parameters have precedence over CLI in returned options.

    """
    IRRELEVANT_CLI_OPTIONS = ('--version', '--help')
    if cli_doc:
        docopt_args = docopt(cli_doc, version=PACKAGE_VERSION)
    else:
        docopt_args = {}
    # get set of CLI parameters
    cli_args = set(
        arg.split('=')[0] if '=' in arg else arg
        for arg in sys.argv
    )
    # filter out None values
    parameters = {k: v for k, v in parameters.items() if v is not None}
    # get docopt result only for args effectively present in CLI
    docopt_args = {
        name: value
        for name, value in docopt_args.items()
        if name in cli_args
    }
    # CLI args are those returned by docopt, but corrected and filtered
    cli_args = {
        arg.lstrip('-').replace('-', '_'): value
        for arg, value in docopt_args.items()
        if value is not None and arg not in IRRELEVANT_CLI_OPTIONS
    }
    # get arguments given by parameters
    parameters = {
        arg: value
        for arg, value in parameters.items()
        if value is not None
    }
    # raise error in case of unexpected argument
    if any(arg not in PROGRAM_OPTIONS for arg in cli_args):
        unexpected_args = (arg for arg in cli_args
                           if arg not in PROGRAM_OPTIONS)
        raise ValueError(
            'ERROR: ' + str(tuple(unexpected_args)) + ' arguments is not in '
            + str(tuple(PROGRAM_OPTIONS.keys()))
        )
    return ChainMap(parameters, cli_args, PROGRAM_OPTIONS)

def thread(number=None):
    """Return Clasp options for use n thread, or if n is invalid, use the
    number of CPU available"""
    if number is not None and 1 <= int(number):
        if int(number) == 1:
            return ''
        else:
            return ' --parallel-mode=' + str(number)
    else:  # number is None, or invalid
        nb_cpu = str(multiprocessing.cpu_count())
        logger().info('Threading: Non valid number of CPU given ('
                      + str(number) + '). ' + nb_cpu
                      + ' CPU will be used by Clasp.')
        return ' --parallel-mode=' + nb_cpu


# logging functions
def logger(name=LOGGER_NAME):
    """Return logger of given name, without initialize it.

    Equivalent of logging.getLogger() call.

    """
    return logging.getLogger(name)


def configure_logger(log_filename=None, term_loglevel=None, loglevel=None):
    """Operate the logger configuration for the package"""
    # use defaults if None given
    log_filename = DEFAULT_LOG_FILE if log_filename is None else log_filename
    term_loglevel = DEFAULT_LOG_LEVEL if term_loglevel is None else term_loglevel
    loglevel = DEFAULT_LOG_LEVEL if loglevel is None else loglevel
    # put given log level in upper case, or keep it as integer
    try:
        loglevel = loglevel.upper()
    except AttributeError:  # loglevel is an integer, not a string
        pass  # nothing to do, lets keep the log level as an int
    try:
        term_loglevel = term_loglevel.upper()
    except AttributeError:  # term_loglevel is an integer, not a string
        pass  # nothing to do, lets keep the log level as an int
    assert isinstance(term_loglevel, int) or isinstance(term_loglevel, str)
    assert isinstance(loglevel, int) or isinstance(loglevel, str)

    # define the configuration
    logging_config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
            },
            'simple': {
                'format': '%(levelname)s %(message)s',
            },
        },
        'handlers': {
            'console': {
                'level': term_loglevel,
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
            'logfile': {
                'level': loglevel,
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_filename,
                'mode': 'w',
                'maxBytes': 2**16,
                'formatter': 'verbose',
            },
        },
        'loggers': {
            PACKAGE_NAME: {
                'handlers':['console', 'logfile'],
                'propagate': True,
                'level': loglevel,
            },
        }
    }

    # apply the configuration
    try:
        # free possible previous configuration
        handlers = logger().handlers[:]
        for handler in handlers:
            handler.close()
            logger().removeHandler(handler)
        logging.config.dictConfig(logging_config)
    except PermissionError:
        logger().warning(os.path.abspath(DIR_LOGS + LOGGER_NAME + '.log')
                        + "can't be written because of a permission error."
                        + "No logs will be saved in file.")


def log_level(level):
    """Set terminal log level to given one"""
    _logger = logger()
    handlers = (_ for _ in _logger.handlers
                if isinstance(_, logging.StreamHandler)
               )
    for handler in handlers:
        handler.setLevel(level.upper())
