"""Definition of the Addon object,
a simple mean to extend the behavior of motif search.

Addons are used by Motif instances to enrich the solving with additional
constraints, constants and atoms.

An Addon is basically a 3-uplet (ASP files, add_atoms, add_constants), where:

- ASP files are grounded with the motif search files
- add_atoms a function called before the solving with the atoms model
    to enrich as parameter.
- add_constants a function called before the solving with the atoms model
    to return a mapping {constant name: value}.

Basic Addons are provided in this module, ByDegree and ByFuzzyDegree,
and client can easily create and use it's own addons.

"""

import itertools
from functools import partial
from collections import defaultdict, namedtuple, Counter

from powergrasp import commons
from powergrasp.atoms import AtomsModel


Addon = namedtuple('Addon', 'files add_atoms add_constants')
Addon.__new__.__defaults__ = (), lambda m: m, lambda _: {}


def addon_knodes_degree(model:AtomsModel, k:int=2, max_per_set_only:bool=False):
    """Add maximal degrees atoms to input model.

    A maximal node is a node that share the maximal number of common neigbors
    with k other nodes, and have the greater degree among them.
    With k=1, this function is equivalent
    to addon_degree(include_max_node_degrees=True).
    With k=2, this function also mark as maximal priority the node that share
    N common neighbors with another node, with N the maximal size of a biclique
    implying two elements in one set. Of the two nodes, only those with maximal
    degree is kept. (both in case of equality)

    if max_per_set_only is False, then all nodes involved in a maximal n-uplet
    are added to the max priority nodes, not only the ones of maximal degree.

    """
    # get the complete graph as a dict {pred: {succs}}
    graph = defaultdict(set)
    for na, nb in model.get_args('edge'):
        graph[na].add(nb)
        graph[nb].add(na)
    graph_nodes = tuple(graph.keys())
    max_nodes = set()  # all nodes marked as maximal priority
    for node_per_set in range(1, k+1):
        k_uplets = list()  # all k-uplets that have the maximal common neighbor
        maximal_degree = 0
        for nodes in itertools.combinations(graph_nodes, node_per_set):
            succs = set(graph_nodes)
            for node in nodes:
                succs &= graph[node]
            if len(succs) == maximal_degree:  # found other k nodes with maximal number of common neighbor
                k_uplets.append(set(nodes))
            elif len(succs) > maximal_degree:  # found higher number of common neighbor
                k_uplets = [set(nodes)]
                maximal_degree = len(succs)
        # Compute the maximal degree for all nodes in k-uplet
        # Add nodes of maximal degree to max_nodes for each node in 
        for k_uplet in k_uplets:
            if max_per_set_only:
                degrees = {node: len(graph[node]) for node in k_uplet}
                maximal_degree = max(degrees.values(), default=-1)
                max_nodes |= {node for node, degree in degrees.items()
                              if degree == maximal_degree}
            else:
                max_nodes |= k_uplet
    model.set_args('max_priority', ((node,) for node in max_nodes))
    return model


def addon_degree(model:AtomsModel, include_node_degrees:bool=False,
                 include_max_node_degrees:bool=False):
    """Add degrees and maximal degrees atoms to input model"""
    if not include_node_degrees and not include_max_node_degrees: return model
    # computation of degrees
    edges = frozenset(frozenset(args) for _, args in model.get('edge'))
    degrees = Counter(itertools.chain.from_iterable(edges))
    if include_node_degrees:
        model.set_args('priority', degrees.items())
    # computation of nodes of max degree
    if include_max_node_degrees:
        max_prio = degrees.most_common(1)[0][1] if degrees else 0
        model.set_args('max_priority', ((node,) for node, prio in
                                        degrees.items() if prio == max_prio))
    # consistancy verification
    membercc = frozenset(_[0] for _ in model.get_args('membercc'))
    assert all(node in degrees for node in membercc)

    return model


ByDegree = Addon(
    [commons.ASP_SRC_PRIORITY],
    partial(addon_degree, include_max_node_degrees=True),
)

ByFuzzyDegree = Addon(
    [commons.ASP_SRC_FUZZY_PRIORITY],
    partial(addon_degree, include_node_degrees=True),
)

ByKNodesDegree = Addon(
    [commons.ASP_SRC_PRIORITY],
    partial(addon_knodes_degree, k=2),
)
