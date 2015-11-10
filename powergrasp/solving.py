# -*- coding: utf-8 -*-
"""
Definitions of model_from(5) that encapsulate
 the ASP grounder and solver calls.

"""
from functools   import partial
from collections import deque
import powergrasp.commons as commons
import powergrasp.atoms   as atoms
import pyasp.asp          as asp
import os


LOGGER = commons.logger()


def model_from(base_atoms, aspfiles, aspargs={},
               gringo_options='', clasp_options=''):
    """Compute a model from ASP source code in aspfiles, with aspargs
    given as grounding arguments and base_atoms given as input atoms.

    base_atoms -- string, ASP-readable atoms
    aspfiles -- (list of) filename, contains the ASP source code
    aspargs -- dict of constant:value that will be set as constants in aspfiles
    gringo_options -- string of command-line options given to gringo
    clasp_options -- string of command-line options given to clasp

    """
    # use the right basename and use list of aspfiles in all cases
    if isinstance(aspfiles, str):
        aspfiles = [aspfiles]
    elif isinstance(aspfiles, tuple):  # solver take only list, not tuples
        aspfiles = list(aspfiles)

    # define the command line options for gringo and clasp
    constants = ' -c '.join(str(k)+'='+str(v) for k,v in aspargs.items())
    if len(aspargs) > 0:  # must begin by a -c for announce the first constant
        constants = '-c ' + constants
    gringo_options = ' '.join((constants, commons.ASP_GRINGO_OPTIONS, gringo_options))
    clasp_options += ' ' + ' '.join(commons.ASP_CLASP_OPTIONS)

    #  create solver and ground base and program in a single ground call.
    solver = asp.Gringo4Clasp(gringo_options=gringo_options,
                              clasp_options=clasp_options)
    # print('SOLVING:', aspfiles, constants)
    # print('INPUT:', base_atoms.__class__, base_atoms)
    answers = solver.run(aspfiles, additionalProgramText=base_atoms)
    # print('OK !')
    # print(len(answers), 'ANSWER(S):', '\n'.join(str(_) for _ in answers))

    # return the last solution (which is the best), or None if no solution
    try:
        last_solution = deque(answers, maxlen=1)[0]
        # print('LAST_SOLUTION: ', len(last_solution), ' "', last_solution, '"', sep='')
        # a solution is valid if at least one atom is returned
        return last_solution if len(last_solution) > 0 else None
        LOGGER.debug(title + ' OUTPUT: ' + atoms.to_str(model))
        LOGGER.debug(title + ' OUTPUT: ' + str(atoms.count(model)))
    except IndexError:
        # no valid model
        return None
