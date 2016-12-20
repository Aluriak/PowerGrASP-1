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


def addon_degree(model:AtomsModel, include_node_degrees:bool=False,
                 include_max_node_degrees:bool=False):
    """Add degrees and maximal degrees atoms to input model"""
    if not include_node_degrees and not include_max_node_degrees: return model
    # computation of degrees
    degrees = defaultdict(int)
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
