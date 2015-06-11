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
ASP_OPTIONS     = ['--update-domains']
ASP_OPTIONS     = []

# VALUES
LOG_LEVEL         = logging.DEBUG
RESULTS_PREDICATS = (
    'powernode',
    'poweredge',
    'score',
)



# FUNCTIONS
def first_solution(solver):
    """Return the first model found by given gringo.Control instance.
    If no model is find, None will be return instead."""
    model = None
    with solver.solve_iter() as it:
        # take the first model, or None
        models = tuple(_ for _ in it)
        try:
            model = next(iter(models))
        except StopIteration:
            model = None
    return model


def basename(filepath):
    """Return the basename of given filepath.

    >>> import os
    >>> basename('~/ASP/serious/business/fly.lp')
    fly

    """
    return os.path.splitext(os.path.basename(filepath))[0]

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



