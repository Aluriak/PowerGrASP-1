# -*- coding: utf-8 -*-
import gringo
from future.utils import iteritems
from commons      import basename, first_solution

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


def dict2atoms(graph, converted_graph_filename):
    """write in given filename the equivalent to given graph in ASP"""
    with open(converted_graph_filename, 'w') as fd:
        for node, targets in iteritems(converted_graph_filename):
            fd.write('\n'.join(
                'edge("'
                + str(node)
                + '","' + str(n)
                + '").'
                for n in targets
            ))

