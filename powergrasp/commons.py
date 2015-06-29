# -*- coding: utf-8 -*-

# IMPORTS
from __future__   import absolute_import, print_function
from functools    import partial
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
ASP_OPTIONS     = ['--update-domains']
ASP_OPTIONS.append('-Wno-atom-undefined')
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
def FIRST_SOLUTION_THREAD(solver):
    """Return atoms of the first model found by given gringo.Control instance.
    If no model is find, None will be return instead.
    This function assume that the solver is built with the thread support."""
    model = None
    with solver.solve_iter() as it:
        # take the first model, or None
        models = tuple(_ for _ in it)
        try:
            model = next(iter(models)).atoms()
        except StopIteration:
            model = None
    return model

def FIRST_SOLUTION_NO_THREAD(solver):
    """Return atoms of the first model found by given gringo.Control instance.
    If no model is find, None will be return instead.
    These function can be used on solver even if no thread support allowed."""
    # NB: not as the solve_iter method, the models are given
    #     in reversed order by solve(2) method: the best is the last
    models = [None] # None will be replaced at first step by a list of atoms
    def callback(new_model, models):
        models[0] = new_model.atoms()
    solver.solve([], partial(callback, models=models))
    # return the best model
    assert(len(models) == 1)
    model = next(iter(models))
    return tuple(model) if model else None

# here is some lines for allow external client to choose between
#  thread or no-thread first solution implementation:
first_solution = FIRST_SOLUTION_THREAD
def first_solution_function(mode=FIRST_SOLUTION_NO_THREAD):
    assert(mode in (FIRST_SOLUTION_NO_THREAD, FIRST_SOLUTION_THREAD))
    global first_solution
    first_solution = mode



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



