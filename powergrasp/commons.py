# -*- coding: utf-8 -*-
"""
Definition of numerous constants, for paths, names, arguments for ASP solvers.
Moreover, some generalist functions are defined,
 notabily for solving management and logging.

"""

# IMPORTS
from pkg_resources import resource_filename
from functools     import partial
from logging.handlers import RotatingFileHandler
import powergrasp.info as info
import logging
import os


# DIRECTORIES, FILENAMES
PACKAGE_NAME    = info.__name__.lower()
ACCESS_FILE     = partial(resource_filename, PACKAGE_NAME)
LOGGER_NAME     = PACKAGE_NAME
DIR_LOGS        = 'logs/'
DIR_DATA        = 'data/'
DIR_TEST_CASES  = 'tests/'
DIR_SOURCES     = ''
DIR_ASP_SOURCES = DIR_SOURCES + 'ASPsources/'
ASP_FILE_EXT    = '.lp'
FILENAME_LOG    = DIR_LOGS + LOGGER_NAME + '.log'

# ASP SOURCES
ASP_SRC_EXTRACT = ACCESS_FILE(DIR_ASP_SOURCES +'extract'         + ASP_FILE_EXT)
ASP_SRC_PREPRO  = ACCESS_FILE(DIR_ASP_SOURCES +'preprocessing'   + ASP_FILE_EXT)
ASP_SRC_FINDCC  = ACCESS_FILE(DIR_ASP_SOURCES +'findbestclique'  + ASP_FILE_EXT)
ASP_SRC_FINDBC  = ACCESS_FILE(DIR_ASP_SOURCES +'findbestbiclique'+ ASP_FILE_EXT)
ASP_SRC_POSTPRO = ACCESS_FILE(DIR_ASP_SOURCES +'postprocessing'  + ASP_FILE_EXT)

# Constants involved in ASP solving
ASP_ARG_CC   = 'cc'
ASP_ARG_STEP = 'k'
ASP_ARG_UPPERBOUND = 'upperbound'
ASP_ARG_LOWERBOUND = 'lowerbound'

# ASP SOLVER OPTIONS
ASP_GRINGO_OPTIONS = ''  # no default options
ASP_CLASP_OPTIONS  = ''  # options of solving heuristics
ASP_CLASP_OPTIONS += ' -Wno-atom-undefined'
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


# VALUES
LOG_LEVEL         = logging.DEBUG
RESULTS_PREDICATS = (
    'powernode',
    'poweredge',
    'score',
)



# FUNCTIONS
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

def thread(number):
    """Set ASP options for use n thread, or only one if set to None"""
    _logger.warning('Threading optimization is currently not implemented.'
                    'PowerGrASP will run with only one thread.')
    return
    global ASP_CLASP_OPTIONS
    assert(number is None or number > 0)
    if number is not None:
        ASP_CLASP_OPTIONS += '--parallel-mode=' + str(number) + ',split'

def logger(name=LOGGER_NAME, logfilename=None):
    """Return logger of given name, without initialize it.

    Equivalent of logging.getLogger() call.
    """
    return logging.getLogger(name)



_logger = logging.getLogger(LOGGER_NAME)
_logger.setLevel(LOG_LEVEL)

# terminal log
stream_handler = logging.StreamHandler()
formatter      = logging.Formatter('%(levelname)s: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(LOG_LEVEL)
_logger.addHandler(stream_handler)

# log file
formatter    = logging.Formatter(
    '%(asctime)s :: %(levelname)s :: %(message)s'
)
try:
    file_handler = RotatingFileHandler(
        ACCESS_FILE(FILENAME_LOG),
        'a', 1000000, 1
    )
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)
except PermissionError:
    _logger.warning(os.path.abspath(DIR_LOGS + LOGGER_NAME + '.log')
                    + "can't be written because of a permission error."
                    + "No logs will be saved in file.")


def log_file(filename):
    handlers = (_ for _ in _logger.handlers
                if isinstance(_, RotatingFileHandler)
               )
    for handler in handlers:
        print(dir(handler))
        exit()
        handler.setLevel(level.upper())


def log_level(level):
    """Set terminal log level to given one"""
    handlers = (_ for _ in _logger.handlers
                if isinstance(_, logging.StreamHandler)
               )
    for handler in handlers:
        handler.setLevel(level.upper())



