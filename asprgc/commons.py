# -*- coding: utf-8 -*-

# IMPORTS
import logging
from   logging.handlers import RotatingFileHandler


# DIRECTORIES, FILENAMES
DIR_LOGS        = 'logs/'
DIR_ASP_SRC     = 'data/'
ASP_FILE_EXT    = '.lp'
ASP_SRC_GRAPH   = DIR_ASP_SRC + 'diamond' + ASP_FILE_EXT
ASP_SRC_EXTRACT = DIR_ASP_SRC + 'extract' + ASP_FILE_EXT
ASP_SRC_FINDCC  = DIR_ASP_SRC + 'findconcept' + ASP_FILE_EXT

# VALUES
LOG_LEVEL = logging.DEBUG


# FUNCTIONS
def logger(name, logfilename=None):
    """Return logger of given name, after initialize it.
    
    Equivalent of logging.getLogger() 
    and commons.configure_logger() calls.
    """
    configure_logger(name, logfilename)
    return logging.getLogger(name)



def configure_logger(name, logfilename=None):
    """Configure logger of given name for logging 
    in stdout and in a file.

    Log file, if not provided, will be placed in logs 
    directory with a name equivalent to logger name.
    """
    if logfilename is None:
        logfilename = DIR_LOGS + name + '.log'
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # log file
    formatter    = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    file_handler = RotatingFileHandler(logfilename, 'a', 1000000, 1)
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # terminal log
    stream_handler = logging.StreamHandler()
    formatter      = logging.Formatter('%(levelname)s: %(message)s')
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(LOG_LEVEL)
    logger.addHandler(stream_handler)



