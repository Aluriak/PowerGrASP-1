# -*- coding: utf-8 -*-

# IMPORTS
from __future__   import absolute_import, print_function
import logging
from   logging.handlers import RotatingFileHandler
import os


# DIRECTORIES, FILENAMES
LOGGER_NAME     = 'asprgc'
DIR_LOGS        = 'logs/'
DIR_ASP_SRC     = 'data/'
ASP_FILE_EXT    = '.lp'
ASP_SRC_GRAPH   = DIR_ASP_SRC + 'diamond' + ASP_FILE_EXT
ASP_SRC_EXTRACT = DIR_ASP_SRC + 'extract' + ASP_FILE_EXT
ASP_SRC_FINDCC  = DIR_ASP_SRC + 'findconcept' + ASP_FILE_EXT

# ASP SOLVER OPTIONS
ASP_OPTIONS     = []
ASP_OPTIONS.append('-Wno-atom-undefined')
ASP_OPTIONS.append('--configuration=frumpy')
ASP_OPTIONS.append('--heuristic=Vsids')
# ASP_OPTIONS     = []
# ASP_OPTIONS.append('--opt-strategy=bb,1') # default and best with frumpy + Vsids
# ASP_OPTIONS.append('--opt-strategy=bb,2') # better in default mode
# ASP_OPTIONS.append('--opt-strategy=bb,3') # longest of the bb
# ASP_OPTIONS.append('--opt-strategy=usc,1') # usc seems to never finish…
# ASP_OPTIONS.append('--opt-strategy=usc,2')
# ASP_OPTIONS.append('--opt-strategy=usc,3')


# ASP_OPTIONS.append('--heuristic=Berkmin') # default and ok
# ASP_OPTIONS.append('--heuristic=Vsids') # the faster
# ASP_OPTIONS.append('--heuristic=Vmtf')
# ASP_OPTIONS.append('--heuristic=Domain')
# ASP_OPTIONS.append('--heuristic=Unit')
# ASP_OPTIONS.append('--heuristic=None')


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

def logger(name='asprgc', logfilename=None):
    """Return logger of given name, without initialize it.

    Equivalent of logging.getLogger() call.
    """
    return logging.getLogger(name)



_logger = logging.getLogger(LOGGER_NAME)
_logger.setLevel(LOG_LEVEL)

# log file
formatter    = logging.Formatter(
    '%(asctime)s :: %(levelname)s :: %(message)s'
)
file_handler = RotatingFileHandler(
    DIR_LOGS + LOGGER_NAME + '.log',
    'a', 1000000, 1
)
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(formatter)
_logger.addHandler(file_handler)

# terminal log
stream_handler = logging.StreamHandler()
formatter      = logging.Formatter('%(levelname)s: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(LOG_LEVEL)
_logger.addHandler(stream_handler)


def log_level(level):
    """Set terminal log level to given one"""
    handlers = (_ for _ in _logger.handlers
                if _.__class__ is logging.StreamHandler
               )
    for handler in handlers:
        handler.setLevel(level.upper())



