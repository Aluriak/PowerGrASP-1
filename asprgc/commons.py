# -*- coding: utf-8 -*-

# IMPORTS
import logging
from   logging.handlers import RotatingFileHandler


# DIRECTORIES, FILENAMES
LOGGER_NAME     = 'asprgc'
DIR_LOGS        = 'logs/'
DIR_ASP_SRC     = 'data/'
ASP_FILE_EXT    = '.lp'
ASP_SRC_GRAPH   = DIR_ASP_SRC + 'diamond' + ASP_FILE_EXT
ASP_SRC_EXTRACT = DIR_ASP_SRC + 'extract' + ASP_FILE_EXT
ASP_SRC_FINDCC  = DIR_ASP_SRC + 'findconcept' + ASP_FILE_EXT

# VALUES
LOG_LEVEL         = logging.DEBUG
RESULTS_PREDICATS = (
    'clique',
    'concept',
    'cardinal',
)



# FUNCTIONS
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



