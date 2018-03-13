"""
Definition of various functions with no direct link to the package
or the compression.

"""

import math
import os.path
import itertools
from collections import defaultdict

from powergrasp import atoms
from powergrasp import solving
from powergrasp import commons


LOGGER = commons.logger()

LATTICE_FILENAME   = 'powergrasp/data/lattice'  # extension is added by graphviz
ASP_FILE_INTEGRITY = 'powergrasp/ASPsources/integrity.lp'


def draw_lattice(graph_dict, filename):
    line_diagram(
        {k.lower(): {_.upper() for _ in v} for k, v in graph_dict.items()},
        filename=filename
    )


def density(nb_node:int, nb_edge:int) -> float:
    """Return the density of a graph having given number of edges
    and number of nodes.

    >>> density(2, 1)
    1.0
    >>> round(density(3, 2), 2)
    0.67
    >>> round(density(4, 2), 2)
    0.33

    """
    assert isinstance(nb_edge, int)
    assert isinstance(nb_node, int)
    assert nb_edge >= 0
    assert nb_node >= 1
    return 2 * nb_edge / (nb_node * (nb_node - 1))


def asp2graph(asp_atoms):
    """Convert string containing (o)edge(X,Y) or inter(X,Y)
    to dict {node: {succs}}"""
    graph = defaultdict(set)
    edges = (atom for atom in asp_atoms.split('.')
             if any(atom.startswith(prefix) for prefix in ('edge', 'inter')))
    for atom, args in (atoms.split(atom) for atom in edges):
        x, y = args
        ux, uy = x.upper(), y.upper()
        ux = ('attr_' + ux) if ux == x else ux
        uy = ('attr_' + uy) if uy == y else uy
        graph[x].add(uy)
        graph[y].add(ux)
    return graph

def line_diagram(graph, filename=LATTICE_FILENAME):
    import concepts
    diag = concepts.Definition()
    for node in sorted(graph.keys()):
        diag.add_object(node, graph[node])
    context = concepts.Context(*diag)
    context.lattice.graphviz().render(filename=os.path.basename(filename),
                                      directory=os.path.dirname(filename),
                                      cleanup=True)  # cleanup the dot file
    assert os.path.exists(filename + '.pdf')  # output is pdf


def test_integrity(asp_graph_data_filename,
                   asp_file_integrity=ASP_FILE_INTEGRITY):
    """Perform integrity and consistency study of the graph described
    by ASP edge/2 atoms contained in file.

    Return a dict property:value.
    """
    with open(asp_graph_data_filename) as fd:
        graph_atoms = ''.join(fd.read())
    model = solving.model_from(graph_atoms, ASP_FILE_INTEGRITY)
    assert model is not None
    payload = {
        atom.predicate + ' ' + atom.arguments[0]: atom.arguments[1]
        for atom in model
    }
    # density is number of edges divide by maximal number of edges,
    #  which is given by the clique formula (N(N-1)/2), so the density is
    #  (2 * K) / (N(N-1))
    nb_edge, nb_node = int(payload['nb edge']), int(payload['nb node'])
    payload['density'] = (2 * nb_edge) / (nb_node * (nb_node - 1))
    return payload


def dict2atoms(graph, converted_graph_filename):
    """write in given filename the equivalent to given graph in ASP"""
    with open(converted_graph_filename, 'w') as fd:
        for node, targets in converted_graph_filename.items():
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
    UNWANTED_IDS = frozenset(commons.ASP_ARGS_NAMES)
    carac   = (chr(_) for _ in range(ord('a'), ord('z')+1))
    nb_cars = int(math.ceil(math.log(nb_node, 26)))
    label   = (''.join(c)
               for c in itertools.islice(itertools.product(
                carac, repeat=nb_cars), nb_node
               ))
    label = (l for l in label if l not in UNWANTED_IDS)
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


def asp_ordered(one, two) -> ('one', 'two') or ('two', 'one'):
    """Return given ASP values, ordered with the smaller at first position

    In ASP, natural order is used for integers,
    and lexicographical one for strings and litterals.
    Moreover, an integer is always smaller than a litteral, which is always
    smaller than a string.

    >>> asp_ordered(1, 2)
    (1, 2)
    >>> asp_ordered(11, 100)
    (11, 100)
    >>> asp_ordered('1','2')
    ('1', '2')
    >>> asp_ordered('2','1')
    ('1', '2')
    >>> asp_ordered('"1"','2')
    ('2', '"1"')
    >>> asp_ordered('"1"','a')
    ('a', '"1"')
    >>> asp_ordered('"1"','"2"')
    ('"1"', '"2"')
    >>> asp_ordered('"b"','"a"')
    ('"a"', '"b"')
    >>> asp_ordered('"bc"','"b"')
    ('"b"', '"bc"')
    >>> asp_ordered('bc','b')
    ('b', 'bc')
    >>> asp_ordered('11','100')
    ('11', '100')
    >>> asp_ordered('[a]','a')
    ('[a]', 'a')
    >>> asp_ordered('a','[a]')
    ('[a]', 'a')
    >>> asp_ordered('a','[b]')
    ('[b]', 'a')
    >>> asp_ordered('[b]','[a]')
    ('[a]', '[b]')
    >>> asp_ordered('[b]','[a]') == asp_ordered('[a]','[b]')
    True
    >>> asp_ordered('"\"echo coucou\""','"[a]"')
    ('"\"echo coucou\""', '"[a]"')
    >>> asp_ordered('"[a]"', '"\"echo coucou\""')
    ('"\"echo coucou\""', '"[a]"')
    >>> asp_ordered('"a"','"[a]"')
    ('"[a]"', '"a"')
    >>> asp_ordered('"b"','"[a]"')
    ('"[a]"', '"b"')

    """
    TYPES = int, 'litteral', str  # sorted by increasing ASP order
    type = {}
    for elem in (one, two):
        if isinstance(elem, str) and elem.isnumeric():
            elem_type = int
        elif isinstance(elem, int):
            elem_type = int
        else:
            if elem.startswith('"'):
                assert elem.endswith('"')
                elem_type = str
            else:
                elem_type = 'litteral'
        type[elem] = elem_type

    # print('TYPES:', type)
    order = {e: TYPES.index(t) for e, t in type.items()}
    if order[one] < order[two]:  # ex: one is int, two is litteral
        return one, two
    elif order[one] > order[two]:  # ex: one is str, two is int
        return two, one
    elif order[one] == order[two] and type[one] is int:  # both are integers
        return (one, two) if int(one) < int(two) else (two, one)
    elif order[one] == order[two]:  # both are the same (non integer)
        return (one, two) if one < two else (two, one)
    else:
        assert False, "it's impossible to reach here"
