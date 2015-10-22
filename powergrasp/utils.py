# -*- coding: utf-8 -*-
"""
Definition of various functions with no direct link to the package
or the compression.

"""


import itertools
from future.utils       import iteritems

import powergrasp.atoms   as atoms
import powergrasp.solving as solving
from powergrasp.commons import basename


ASP_FILE_INTEGRITY = 'powergrasp/ASPsources/integrity.lp'


def test_integrity(asp_graph_data_filename,
                   asp_file_integrity=ASP_FILE_INTEGRITY):
    """Perform integrity and consistency study of the graph described
    by ASP edge/2 atoms contained in file.

    Return a dict property:value.
    """
    with open(asp_graph_data_filename) as fd:
        graph_atoms = ''.join(l for l in fd.read() if l not in '\n ')
    model = solving.model_from(graph_atoms, ASP_FILE_INTEGRITY)
    assert model is not None
    return {
        name + ' ' + ': '.join(str(_) for _ in args)
        for name, args in (atoms.split(atom) for atom in model)
    }


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


def make_tree(nb_node, filename, nb_child=lambda:2):
    """write in given file a graph that is a bintree of nb_node node"""
    import math
    carac   = (chr(_) for _ in range(ord('a'), ord('z')+1))
    nb_cars = int(math.ceil(math.log(nb_node, 26)))
    label   = (''.join(c)
               for c in itertools.islice(itertools.product(
                carac, repeat=nb_cars), nb_node
               ))
    def childs():
        for _ in range(nb_child()):
            yield next(label)
    def edge(n, m):
        return 'edge(' + n + ',' + m + ').\n'
    nodes = [next(label)]
    with open(filename, 'w') as fd:
        for node in nodes:
            for child in childs():
                fd.write(edge(node, child))
                nodes.append(child)




