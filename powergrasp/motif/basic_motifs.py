"""Definition of basic powergraph motifs, Biclique and Clique.

"""


import itertools
from collections import defaultdict, Counter

from powergrasp import atoms
from powergrasp import commons
from powergrasp import solving
from powergrasp.commons import ASP_SRC_FINDBC, ASP_SRC_FINDCC, ASP_SRC_SCORING
from .motif import Motif


LOGGER = commons.logger()


class Clique(Motif):
    """Implementation of the clique motif,
    where the edge cover equals N * (N-1) / 2

    """

    def __init__(self, scoring:str=ASP_SRC_SCORING, gringo_options='',
                 clasp_options=solving.ASP_DEFAULT_CLASP_OPTION):
        super().__init__('clique', [ASP_SRC_FINDCC, scoring],
                         clasp_options, gringo_options)

    def covered_edges_in_found(self, model:'AtomsModel'):
        """Yield edges covered by given clique in given model"""
        nodes = []
        for name, args in model.get('powernode'):
            cc, step, setnb, node = args
            assert setnb == '1'
            nodes.append(node)
        yield from (((f, s) if f < s else (s, f))
                    for f, s in itertools.product(nodes, repeat=2)
                    if f != s)

    @staticmethod
    def for_powergraph():
        """Return a clique object designed to reproduce
        the powergraph compression

        """
        return Clique()


class Biclique(Motif):
    """Implementation of the biclique motif,
    where the edge cover equals N * M

    """

    def __init__(self, scoring:str=ASP_SRC_SCORING, gringo_options='',
                 clasp_options=solving.ASP_DEFAULT_CLASP_OPTION,
                 include_node_degrees:bool=False,
                 include_max_node_degrees:bool=False,
                 additional_files:iter=[]):
        super().__init__('biclique',
                         [ASP_SRC_FINDBC, scoring] + list(additional_files),
                         clasp_options, gringo_options)
        self.include_node_degrees = bool(include_node_degrees)
        self.include_max_node_degrees = bool(include_max_node_degrees)

    def covered_edges_in_found(self, model:'AtomsModel'):
        """Yield edges covered by given biclique in given model"""
        first, secnd = [], []
        for name, args in model.get('powernode'):
            cc, step, setnb, node = args
            assert setnb in '12'
            (first if setnb == '1' else secnd).append(node)
        if not first or not secnd:
            assert model.get_only('star'), "there is no star/1 atom despite empty powernode"
            assert len(model.get_only('star')[1]) == 1, "star atom is not star/1"
            star = model.get_only('star')[1][0]
            empty_set = first if not first else secnd
            empty_set.append(star)
        # print('SETS:', first, secnd)
        assert len(secnd), "The second set of the biclique is empty"
        assert len(first),  "The first set of the biclique is empty"
        yield from (((f, s) if f < s else (s, f))
                    for f, s in itertools.product(first, secnd))

    def _enriched_input_atoms(self, graph:'AtomsModel') -> 'AtomsModel':
        """Modify the input model in order to prepare the next round"""
        # add degrees as priority atoms if necessary
        if self.include_node_degrees or self.include_max_node_degrees:
            degrees = defaultdict(int)
            edges = frozenset(frozenset(args) for _, args in graph.get('edge'))
            degrees = Counter(itertools.chain.from_iterable(edges))
            if self.include_node_degrees:
                graph.set_args('priority', degrees.items())
            max_prio = degrees.most_common(1)[0][1] if degrees else 0
            if self.include_max_node_degrees:
                graph.set_args('max_priority', ((node,) for node, prio in
                                                degrees.items() if prio == max_prio))
            # consistancy verification
            membercc = frozenset(_[0] for _ in graph.get_args('membercc'))
            assert all(node in degrees for node in membercc)
        return graph


    def _supplementary_constants(self, atoms:'AtomsModel') -> dict:
        """Return a dict of supplementary constants {name: value} for solving"""
        nb_node = atoms.counts.get('membercc', 0)
        return {
            'max_set_size': nb_node - 1,
        }

    @staticmethod
    def for_powergraph():
        """Return a biclique object designed to reproduce
        the powergraph compression

        """
        return Biclique()
