# -*- coding: utf-8 -*-
import gringo
from commons import basename, first_solution

ASP_FILE_INTEGRITY = 'powergrasp/ASPsources/integrity.lp'


def test_integrity(asp_graph_data_filename,
                   asp_file_integrity=ASP_FILE_INTEGRITY):
    """Perform integrity and consistency study of the graph described
    by ASP edge/2 atoms contained in file.

    Return a dict property:value.
    """
    solver = gringo.Control()
    solver.load(asp_graph_data_filename)
    solver.ground([('base', [])])
    solver.load(asp_file_integrity)
    solver.ground([(basename(asp_file_integrity), [])])
    graph_atoms = first_solution(solver)
    if graph_atoms:
        return {
            a.args()[0]:a.args()[1]
            for a in graph_atoms
            if  a.name() == 'nb'
            and len(a.args()) == 2
        }
    else:  # no solution
        return {}

