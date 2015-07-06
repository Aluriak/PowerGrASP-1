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

def make_clique(nb_node, filename):
    """write in given file a graph that is a clique of nb_node node"""
    def int2node(i) : return '"n' + str(i+1) + '"'
    with open(filename, 'w') as fd:
            [fd.write('edge(' + int2node(idx) + ',' + int2node(linked) + ').\n')
             for idx in range(nb_node)
             for linked in range(idx+1, nb_node)
            ]


