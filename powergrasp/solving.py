"""
Definitions of model_from(5) that encapsulate
 the ASP grounder and solver calls.

"""
import os
from functools   import partial
from collections import deque, Counter

from powergrasp import commons
from powergrasp import atoms
from pyasp import asp


LOGGER = commons.logger()


def model_from(base_atoms, aspfiles, aspargs={},
               gringo_options=commons.ASP_GRINGO_OPTIONS,
               clasp_options=commons.ASP_CLASP_OPTIONS):
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
    gringo_options = constants + ' ' + gringo_options
    # print('OPTIONS:', gringo_options)
    # print('OPTIONS:', clasp_options)

    #  create solver and ground base and program in a single ground call.
    solver = asp.Gringo4Clasp(gringo_options=gringo_options,
                              clasp_options=clasp_options)
    # print('SOLVING:', aspfiles, constants)
    # print('INPUT:', base_atoms.__class__, base_atoms)
    answers = solver.run(aspfiles, additionalProgramText=base_atoms)
    # if len(answers) > 0:
        # for idx, answer in enumerate(answers):
            # print('ANSWER ' + str(idx) + ':', answer)
            # print('ATOM(S):', atoms.count(answer))
    # else:
        # print('NO MODEL FOUND !')

    # return the last solution (which is the best), or None if no solution
    try:
        last_solution = deque(answers, maxlen=1)[0]
        # print('LAST_SOLUTION: ', len(last_solution), ' "', last_solution, '"', sep='')
        # a solution is valid if at least one atom is returned
        return last_solution if len(last_solution) > 0 else None
    except IndexError:
        # no valid model
        return None
