"""Definition of the oriented motif: OrientedBiclique.

OrientedClique is not implemented, because it's not
very probable to found one.

"""


import itertools
from collections import defaultdict, Counter

from powergrasp import atoms
from powergrasp import commons
from powergrasp import solving
from powergrasp.commons import ASP_SRC_FINDORBC, ASP_SRC_SCORING
from .motif import Motif


LOGGER = commons.logger()


class OrientedBiclique(Motif):
    """Implementation of the oriented biclique motif,
    where the edge cover equals N * M

    Elements in the first set of the oriented biclique are all sources
    of the edges covered by the motif.

    """

    def __init__(self, scoring:str=ASP_SRC_SCORING, gringo_options='',
                 clasp_options=solving.ASP_DEFAULT_CLASP_OPTION,
                 include_node_degrees:bool=False):
        super().__init__('oriented biclique', [ASP_SRC_FINDORBC, scoring],
                         clasp_options, gringo_options)
        self.include_node_degrees = bool(include_node_degrees)

    def covered_edges_in_found(self, model:atoms.AtomsModel):
        """Yield edges covered by given biclique in given model"""
        source, target = [], []
        for name, args in model.get('powernode'):
            cc, step, setnb, node = args
            assert setnb in '12'
            (source if setnb == '1' else target).append(node)
        # star case: add alone node to associated set
        if not source or not target:
            star = model.get_unique_only_arg('star')
            empty_set = source if not source else target
            empty_set.append(star)
        assert len(target), "The second set of the biclique is empty"
        assert len(source),  "The source set of the biclique is empty"
        yield from tuple( itertools.product(source, target))

    def _enriched_input_atoms(self, graph:atoms.AtomsModel) -> atoms.AtomsModel:
        """Modify the input model in order to prepare the next round"""
        if self.include_node_degrees:
            degrees = defaultdict(int)
            graph = atoms.AtomsModel(graph)
            edges = frozenset(frozenset(args) for _, args in graph.get('edge'))
            degrees = Counter(itertools.chain.from_iterable(edges))
            graph.add_atoms(('degree', args) for args in degrees.items())
        return graph


    def _supplementary_constants(self, atoms:atoms.AtomsModel) -> dict:
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
        return OrientedBiclique()
