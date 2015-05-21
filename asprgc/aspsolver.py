# -*- coding: utf-8 -*-
from __future__       import print_function
from __future__       import absolute_import
import commons
import gringo
import os


logger = commons.logger()

class ASPSolver(object):
    """Functionnal gringo abstraction with builder pattern.

    Builder pattern.
     Client can chain calls up to solutions() or first_solution() methods.

    CAREFUL: low level linking.
     For avoid segmentation fault of gringo when solutions are
     manipulated after destruction of Control instance, client code
     needs to keep references to ASPSolver instance while using
     solutions.

     Example of non-valid code:

        print(ASPSolver().use('file1').first_solution())

     Equivalent valid code:

        solver = ASPSolver()
        print(solver.use('file1').first_solution())

     Other valid equivalent:

        solver = ASPSolver().use('file1')
        print(solver.first_solution())
    """

    def __init__(self, args=[]):
        self.args = args
        self.clear()

    def clear(self):
        """Reset instance to default ground"""
        self._prg       = gringo.Control(self.args)
        self._directory = ''
        return self

    def use(self, program, args=[], program_name=None):
        """Wait for a program name, defined in a program.lp
         file in the current directory (default is ./,
         can be changed through in_dir method.
         if not given, program_name will be equal to file basename.
        """
        assert(iter(args))
        self._prg.load(self._directory+program)
        if program_name is None:
            program_name = os.path.splitext(
                os.path.basename(self._directory+program)
            )[0]
        self.ground(program_name, args)
        return self

    def use_all(self, filenames, args):
        """Call use method on all given filenames.

            args -- list of args for each filename
        """
        [self.use(f, a) for f, a in zip(filenames, args)]
        return self

    def read(self, text, args=[], program_name='base'):
        """Read given ASP source code and ground it in given program"""
        self._prg.add(program_name, args, text)
        self.ground(program_name, args)
        return self

    def ground(self, program, args):
        """Proxy to gringo.Control.ground method"""
        # logger.debug('ASPSolver grounds ' + program + ' with ' + str(args))
        self._prg.ground([(program, args)])
        return self

    def in_dir(self, directory):
        """Change used directory"""
        self._directory = directory
        return self

    def solutions(self, solution_count=None):
        """Return generator of gringo.Model"""
        with self._prg.solve_iter() as it:
            solutions = tuple(s for s in it)
        if solution_count is not None:
            solutions = (s for s, _ in zip(solutions, range(solution_count)))
        self._last_solutions = solutions
        return self._last_solutions

    def first_solution(self, asp_readable=False):
        """Compute solutions and returned the first, or None

        if asp_readable is True, returned solution, if exists,
        will be cast in string and modified for being readable
        by the grounder.
        """
        try:
            model = next(self.solutions(1))
            if asp_readable:
                assert(False) # asp_readable flag unused while that never append
                return str(model.atoms()).replace(', ', '.')
            else:
                return model
        except StopIteration:
            return None

    def next_solution(self):
        """Return the next solution or None"""
        try:
            return next(self._last_solutions)
        except StopIteration:
            return None

    def future_solutions(self):
        """Not implemented"""
        raise NotImplementedError  # TODO

    def assign_external(self, name, args=[], truth=None):
        return self._prg.assign_external(gringo.Fun(name, args), truth)

    def release_external(self, name, args=[]):
        return self._prg.release_external(gringo.Fun(name, args))



