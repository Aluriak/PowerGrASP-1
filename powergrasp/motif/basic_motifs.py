"""Definition of basic powergraph motifs, Biclique and Clique.

"""


import itertools
from collections import defaultdict, Counter

from powergrasp import utils
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
                 clasp_options=solving.ASP_DEFAULT_CLASP_OPTION,
                 addons:iter=None):
        super().__init__('clique', [ASP_SRC_FINDCC, scoring],
                         clasp_options, gringo_options, addons=addons)

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
                 additional_files:iter=[], addons:iter=None):
        super().__init__('biclique',
                         [ASP_SRC_FINDBC, scoring] + list(additional_files),
                         clasp_options, gringo_options, addons=addons)

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
        yield from (utils.asp_ordered(f, s)
                    for f, s in itertools.product(first, secnd))

    @staticmethod
    def for_powergraph():
        """Return a biclique object designed to reproduce
        the powergraph compression

        """
        return Biclique()
