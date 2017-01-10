

import unittest
from powergrasp.atoms import AtomsModel
from powergrasp.motif.addon import addon_knodes_degree, addon_degree


def new_model():
    """Create an atoms model describing a graph of four connected components
    that show multiple cases relatives to the addons behavior.

    """
    return AtomsModel.from_(
        # a: star of degree 6
        'edge(a,a1).edge(a,a2).edge(a,a3).edge(a,a4).edge(a,a5).edge(a,a6).'
        # b,c: biclique + b and c both linked to 2 specific nodes
        'edge(b,b1).edge(b,b2).'
        'edge(c,c1).edge(c,c2).'
        'edge(b,bc1).edge(b,bc2).edge(b,bc3).'
        'edge(c,bc1).edge(c,bc2).edge(c,bc3).'
        # d,e: star of one element (de1) + d and e both linked to 1 specific node
        'edge(d,d1).'
        'edge(e,e1).edge(e,e2).'
        'edge(d,de1).'
        'edge(e,de1).'
        # f: degree(f) == 6
        'edge(f,f1).'
        # f,g: biclique
        'edge(f,fg1).edge(f,fg2).edge(f,fg3).'
        # f,g,h: biclique
        'edge(f,fgh1).edge(f,fgh2).'
        'edge(g,fgh1).edge(g,fgh2).'
        'edge(h,fgh1).edge(h,fgh2).'
    )


class TestAddonKnodeDegree(unittest.TestCase):

    def test_addon_degree(self):
        enriched_model = addon_degree(new_model(), include_max_node_degrees=True)
        max_nodes = tuple(enriched_model.get_unique_args('max_priority'))
        expected = {'a', 'f'}
        self.assertEqual(len(max_nodes), len(set(max_nodes)))  # no doublon
        self.assertSetEqual(set(max_nodes), expected)

    def test_k1(self):
        enriched_model = addon_knodes_degree(new_model(), k=1)
        max_nodes = tuple(enriched_model.get_unique_args('max_priority'))
        expected = {'a', 'f'}
        self.assertEqual(len(max_nodes), len(set(max_nodes)))  # no doublon
        self.assertSetEqual(set(max_nodes), expected)

    def test_k2(self):
        enriched_model = addon_knodes_degree(new_model(), k=2)
        max_nodes = tuple(enriched_model.get_unique_args('max_priority'))
        expected = {'a', 'b', 'c', 'f', 'fgh1', 'fgh2'}
        self.assertEqual(len(max_nodes), len(set(max_nodes)))  # no doublon
        self.assertSetEqual(set(max_nodes), expected)

    def test_k3(self):
        enriched_model = addon_knodes_degree(new_model(), k=3, max_per_set_only=True)
        max_nodes = tuple(enriched_model.get_unique_args('max_priority'))
        expected = {'a', 'f', 'b', 'c', 'fgh1', 'fgh2', 'bc1', 'bc2', 'bc3'}
        self.assertEqual(len(max_nodes), len(set(max_nodes)))  # no doublon
        self.assertSetEqual(set(max_nodes), expected)
