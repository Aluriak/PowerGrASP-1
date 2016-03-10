"""
Test on graph reduction.

"""

import unittest

from .. import graph_manipulation


class TestGraphReduction(unittest.TestCase):

    def test_completed(self):
        self.assertEqual(
            graph_manipulation.completed({1: {2, 3}, 4: {2, 5}}),
            {1: {2, 3}, 2: {1, 4}, 3: {1}, 4: {2, 5}, 5: {4}},
        )

    def test_completed_empty(self):
        self.assertEqual(
            graph_manipulation.completed({}),
            {},
        )

    def test_reversed(self):
        self.assertEqual(
            graph_manipulation.reversed_graph({1: {3, 4}, 2: {1, 3}}),
            {1: {2}, 3: {1, 2}, 4: {1}},
        )

    def test_remove_repeatitions(self):
        self.assertEqual(
            graph_manipulation.repeatitions_filtered({1: {2, 3}, 2: {1, 3, 4}, 3: {1, 2, 4}}),
            {2: {1, 3, 4}, 3: {1, 2, 4}},
        )

    def test_finalize(self):
        self.assertEqual(
            graph_manipulation.finalize({1: {2, 3}, 3: {4}, 5: {1}}),
            {1: {2, 3}, 3: {1, 4}, 5: {1}}
        )

    def test_reverse_complete_is_complete(self):
        complete_graph = graph_manipulation.completed(
            {1: {2, 3}, 2: {1, 3, 4}, 3: {1, 2, 4}}
        )
        self.assertEqual(
            complete_graph,
            graph_manipulation.reversed_graph(complete_graph)
        )


    def assert_reduce(self, graph, expected_reduced_graph):
        # print('\n   GRAPH:', graph)
        # print(  'EXPECTED:', expected_reduced_graph)
        # print(  '  RESULT:', graph_manipulation.reduced(graph))
        self.assertEqual(graph_manipulation.reduced(graph),
                         expected_reduced_graph)

    def test_empty(self):
        self.assert_reduce({}, {})

    def test_biclique(self):
        graph = {1: {2, 3, 4, 5}, 6: {2, 3, 4, 5}}
        self.assert_reduce(graph, graph)

    def test_case_4_nodes(self):
        graph = {1: {2, 3}, 2: {3, 4}, 3: {4}}
        self.assert_reduce(graph, {2: {1, 3, 4}, 3: {1, 4}})

    def test_case_8_nodes(self):
        graph = {1: {2, 3, 4, 7, 8}, 3: {5}, 4: {5}, 5: {6}}
        self.assert_reduce(graph, {1: {2, 3, 4, 7, 8}, 5: {3, 4, 6}})

    def test_case_8_nodes_rebelotte(self):
        graph = {1: {2, 3, 6}, 2: {4, 5, 6}, 3: {4, 5, 6}, 6: {7, 8}}
        reduced = graph_manipulation.reduced(graph)
        self.assertEqual(set(reduced), {2, 3, 6})
        self.assertEqual(graph_manipulation.columns(reduced),
                         {1, 4, 5, 6, 7, 8})
        self.assert_reduce(graph, {2: {1, 4, 5, 6}, 3: {1, 4, 5, 6}, 6: {1, 7, 8}})

    def test_ddiam(self):
        self.assert_reduce(
            # inital graph
            {'b': {'c'}, 'h': {'g', 'f', 'j', 'l', 'p'},
             'd': {'c', 'q', 'b', 'o', 'e'}, 'n': {'o', 'q', 'l', 'p', 'm'},
             'f': {'g'}, 'm': {'o', 'q', 'l', 'p'},
             'a': {'c', 'q', 'e', 'b', 'o'},
             'i': {'g', 'f', 'j', 'l', 'p'}},
            # reduced graph
            {'c': {'b'}, 'g': {'f', 'h', 'i'},
             'h': {'f', 'j', 'l', 'p'}, 'i': {'f', 'j', 'l', 'p'},
             'a': {'c', 'q', 'b', 'o', 'e'}, 'd': {'c', 'q', 'b', 'o', 'e'},
             'm': {'o', 'q', 'l', 'p', 'n'}, 'n': {'o', 'q', 'l', 'p'}}
        )

    # def test_case_5_nodes(self):
        # self.assert_reduce(
            # # inital graph
            # {'a': {'b', 'c', 'd'}, 'b': {'c', 'd'}, 'c': {'e'}, 'd': {'e'}},
            # # reduced graph
            # {'a': {'b'}, 'd': {'a', 'b', 'e'}, 'c': {'a', 'b', 'e'}},
        # )

    def test_star(self):
        self.assert_reduce(
            # inital graph
            {'a': {'b', 'c', 'd'}},
            # reduced graph
            {'a': {'b', 'c', 'd'}},
        )
