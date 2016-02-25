"""
Implementation of an algo of graph reduction.

Input data:
    - dict {node: (linked nodes)}
Output data:
    - dict {node: (linked nodes)}

The outputed version of the graph minimize the number of keys in the dictionnary.
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
set 2 = {a, c, d} (values in dictionnary values)


"""
import sys
from itertools import chain
from collections import defaultdict


def completed(graph):
    """Return the same graph, with all edges specified"""
    complete_graph = defaultdict(set)
    for node, succs in graph.items():
        for succ in succs:
            complete_graph[succ].add(node)
            complete_graph[node].add(succ)
    return complete_graph

def completed_to_oriented(graph):
    """filter out edges in complete graph in order to limits repeatitions"""
    output = defaultdict(set)
    for node in sorted(graph.keys()):
        succs = graph[node]
        for succ in succs:
            if succ not in output and succ in graph[node]:
                output[node].add(succ)
    return output

def oriented_to_reduced(graph):
    """return given oriented graph, reduced in order to eliminate
    unnecessary repeatitions"""
    output = defaultdict(set)
    for node in sorted(graph.keys()):
        succs = graph[node]
        if all(succ in graph for succ in succs):
            [output[succ].add(node) for succ in succs]
        else:  # at least one succ is not in graph
            [output[node].add(succ) for succ in succs]
    return output

def reduced(graph):
    """Return the given graph, completed, oriented and reduced"""
    return oriented_to_reduced(completed_to_oriented(completed(graph)))

def stats(graph, reduced):
    all_nodes = set(chain.from_iterable(graph.values())) | set(graph.keys())
    reduced_a = set(chain.from_iterable(graph.values()))
    reduced_b = set(graph.keys())
    return (len(reduced_a) * len(reduced_b)) / pow(len(all_nodes), 2)
