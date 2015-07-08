# -*- coding: utf-8 -*-
"""
Definitions of many functions that helps for manipulation of ASP solvers
and best model collecting.

FIRST_SOLUTION_THREAD and FIRST_SOLUTION_NO_THREAD are functions
 that return the best model find by given solver, after a solve call.
These two function should not be called directly:
 instead, client code should use the first_solution function,
 that is an alias to one of them.
By default, FIRST_SOLUTION_THREAD is used, but if clingo is not compiled with
 the thread support, client code can call
 >>> first_solution_function(FIRST_SOLUTION_NO_THREAD)
 for use the non threaded but slower function.

Another util function is model_from(3), that allow the user
 to reuse quickly a solving pattern.

"""
from __future__       import print_function
from __future__       import absolute_import
import commons
import gringo
import atoms
import os


LOGGER = commons.logger()



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


first_solution = FIRST_SOLUTION_THREAD
def first_solution_function(mode=FIRST_SOLUTION_NO_THREAD):
    """allow external client to choose between thread or no-thread
    first solution implementation"""
    assert(mode in (FIRST_SOLUTION_NO_THREAD, FIRST_SOLUTION_THREAD))
    global first_solution
    first_solution = mode


def model_from(base_atoms, aspfile, aspargs=[], program_name=None):
    """Compute a model from ASP source code in aspfile, with aspargs
    given as grounding arguments and base_atoms given as input atoms.

    base_atoms -- string, ASP-readable atoms
    aspfile -- filename, contains the grounded ASP source code
    aspargs -- list of values, arguments of program defined in aspfile
    program_name -- string, name of the program defined in aspfile

    Note that aspfile must contains a program that have the given program_name,
    or the basename of the file.
    For instance, if the aspfile is ~/ASP/solvemyproblem.lp,
     the program_name must be specified or 'solvemyproblem'.

    """
    # use the right basename
    if program_name is None: program_name = commons.basename(aspfile)
    # debug
    LOGGER.debug(program_name.upper() + ' INPUT: ' + base_atoms)
    # create the solver, ground base and program
    solver = gringo.Control(commons.ASP_OPTIONS)
    solver.add('base', [], base_atoms)
    solver.ground([('base', [])])
    solver.load(aspfile)
    solver.ground([(program_name, aspargs)])
    # compute and return the first solution
    model = first_solution(solver)
    # debug
    LOGGER.debug(program_name.upper() + ' OUTPUT: ' + atoms.to_str(model))
    LOGGER.debug(program_name.upper() + ' OUTPUT: ' + str(atoms.count(model)))
    return model


