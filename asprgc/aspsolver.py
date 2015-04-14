# -*- coding: utf-8 -*-
from __future__       import print_function
from __future__       import absolute_import
import gringo
import os



class ASPSolver():
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

    def __init__(self): 
        self.clear()

    def clear(self):
        self._prg       = gringo.Control()
        self._directory = ''
        return self

    def use(self, program, args=[]):
        self._prg.load(self._directory+program)
        program_name = os.path.splitext(
            os.path.basename(self._directory+program)
        )[0]
        self.ground(program_name, args)
        return self

    def use_all(self, filenames, args):
        [self.use(f, a) for f, a in zip(filenames, args)]
        return self

    def read(self, text, args=[], program_name='base'):
        self._prg.add(program_name, args, text)
        return self

    def ground(self, program, args):
        self._prg.ground([(program, args)])
        return self

    def in_dir(self, directory):
        self._directory = directory
        return self

    def solutions(self, solution_count=None, output=None):
        with self._prg.solve_iter() as it:
            solutions = tuple(s for s in it)
        if solution_count is not None:
            solutions = (s for s, _ in zip(solutions, range(solution_count)))
        self._last_solutions = solutions
        return self._last_solutions

    def first_solution(self):
        return next(self.solutions(1))

    def next_solution(self):
        return next(self._last_solutions)

    def future_solutions(self):
        raise NotImplementedError  # TODO




