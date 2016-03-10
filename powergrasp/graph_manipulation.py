"""
Implementation of routines about dictionnary representation of graphs.
Main API is:
    reduced(1), perform the reduction shown below
    reduction_ratio(2), return the compression ratio between two graphs
    integerised_id(1), simplify keys to integers
    completed(1), return the completed graph
    reversed_graph(1), return the same graph where keys and values are reversed
    columns(1), return set of successors in the graph


Notes about the dictionnary representation for graphs:

Dictionnary {1: {2, 3}} describes a graph where a node 1 is linked
to nodes 2 and 3.
In this module, graphs are assumed non-oriented.


Notes about the reduction algorithm:

The outputed version of the graph minimize the size of the table
representation of the dictionnary.
This reduction is essentially a reorganization of the graph.
All nodes are put in at least one of the two created sets.
(the set of dictionnary keys, and the set of values in the dictionnary values)

In case of a bipartite graph, the intersection of the two sets is {}.
In other case, some nodes are present in the two sets.

This choice gives an important hint of which nodes are in which part of
bicliques in case of a powergraph compression.

Example:
Initial graph:       ->         reduced graph:

     a b c d                      a c d
   a   X X                      b X X X
   b X   X X                    c X   X
   c X X   X
   d   X X

Initial graph dict: {'a': {'b', 'c'}, 'b': {'c', 'd'}, 'd': {'c'}}
Reduced graph dict: {'b': {'a', 'c', 'd'}, 'c': {'a', 'd'}}

set 1 = {b, c}  (dictionnary keys)
set 2 = {a, c, d} (values in dictionnary values, given by columns(1) function)

"""
import sys
import itertools
from itertools import chain
from collections import defaultdict


def integerised_id(graph):
    """Return the same graph dict, simplified with integer as node id."""
    ids = itertools.count()
    symbol = defaultdict(lambda: next(ids))
    output = defaultdict(set)
    for node, succs in graph.items():
        for succ in succs:
            output[symbol[node]].add(symbol[succ])
    return output


def completed(graph):
    """Return the same graph, with all edges specified"""
    complete_graph = defaultdict(set)
    for node, succs in graph.items():
        for succ in succs:
            complete_graph[succ].add(node)
            complete_graph[node].add(succ)
    return complete_graph


def reversed_graph(graph):
    """Return {v: k} for input graph {k: v}"""
    output = defaultdict(set)
    for node, succs in graph.items():
        for succ in succs:
            output[succ].add(node)
    return dict(output)


def repeatitions_filtered(graph):
    output = dict(graph)  # struct copy
    assert output is not graph
    for node, succs in sorted(tuple(graph.items())):
        # a node is repeated if all successors are also keys,
        # and is itself in values. (so successors keys have node as value)
        isrepeated = (all(succ in output for succ in succs) and
                      node in columns(graph))
        # delete any repeated node
        if isrepeated:
            del output[node]
    return output


def columns(graph):
    return set(itertools.chain.from_iterable(graph.values()))


def finalize(graph):
    """Return a graph equivalent to given one, where if any node b is succ of a
    and both a and b are keys of graph, a will be marked also as succ of b.
    """
    output = defaultdict(set)
    graph_columns = columns(graph)
    for node, succs in graph.items():
        for succ in succs:
            output[node].add(succ)
            # add also the edge for succ if possible without changing columns and rows
            if succ in graph and node in graph_columns:
                output[succ].add(node)
    assert set(graph) == set(output)
    assert graph_columns == columns(output)
    return dict(output)


def reduced(graph):
    """Return the given graph, completed, oriented and reduced"""
    graph = completed(graph)
    output = defaultdict(set)
    # print('BEFORE FIRST STEP:', output, graph)
    # first step: add all edges of each node while at least one of them is
    #  not already put in.
    for node in sorted(graph.keys()):
        succs = graph[node]
        if any(succ not in output for succ in succs):
            output[node] |= succs

    # print('AFTER FIRST STEP :', output)

    # second step: filter out a row if all succs are in rows
    output = repeatitions_filtered(output)
    # print('AFTER SECOND STEP:', output)

    output = reversed_graph(output)
    # print('AFTER REVERSION  :', output)

    # third step: filter out a row if all succs are in rows
    output = repeatitions_filtered(output)
    # print('AFTER THIRD STEP :', output)

    # minimize the amount of keys:
    if len(output) > len(columns(output)):
        output = reversed_graph(output)
    # print('AFTER EVENTUAL REVERSION:', output)

    return finalize(output)


def reduction_ratio(graph, reduced_graph):
    """Return the reduction ratio, size of reduced over size of inital"""
    graph = completed(graph)
    graph_a = set(chain.from_iterable(graph.values()))
    graph_b = set(graph.keys())
    reduced_a = set(chain.from_iterable(reduced_graph.values()))
    reduced_b = set(reduced_graph.keys())
    return (len(reduced_a) * len(reduced_b)) / (len(graph_a) * len(graph_b))
