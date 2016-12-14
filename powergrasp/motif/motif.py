"""Definition of data related to motifs, including solving functions

Predefined motifs are defined in this module: biclique and clique.

"""


import operator
import itertools
from collections import namedtuple, defaultdict, Counter

from powergrasp import atoms
from powergrasp import commons
from powergrasp import solving
from powergrasp.commons import (ASP_ARG_UPPERBOUND, ASP_ARG_CC,
                                ASP_ARG_LOWERBOUND, ASP_ARG_STEP,
                                ASP_SRC_FINDCC, ASP_SRC_FINDBC, ASP_SRC_SCORING)


LOGGER = commons.logger()

# returned by motif search, embedding all informations about found motif
FoundMotif = namedtuple('FoundMotif', 'model score motif')

# Follows atoms produced by motif solving, splitted in 3 disjoint classes.
# incremental atoms replace the existing atoms of same name in the model
INCREMENTAL_ATOMS = {'block', 'include_block'}
# accumulable atoms need to be added to the model
ACCUMULABLE_ATOMS = set()
# metadata are used by observers (or by motif only one time)
METADATA_ATOMS = {'powernode_count', 'poweredge_count', 'score', 'star',
                  'powernode', 'poweredge'}

# ensure that no atom is in two classes
assert not INCREMENTAL_ATOMS & ACCUMULABLE_ATOMS
assert not INCREMENTAL_ATOMS & METADATA_ATOMS
assert not ACCUMULABLE_ATOMS & METADATA_ATOMS


class Motif(solving.ASPConfig):
    """A Motif is basically an named ASPConfig instance.

    This class allows client to simply define new motifs to find,
    and to give a precise context for solving (options and source files).

    """


    def __init__(self, name:str, files=None, clasp_options='', gringo_options='',
                 motif_search_files=solving.ASP_FILES_MOTIF_SEARCH):
        super().__init__(files + motif_search_files, clasp_options, gringo_options)
        self.name = name


    def search(self, input_atoms:'AtomsModel', score_min:int, score_max:int,
               cc:str, step:int):
        """Return the concept found and its score.

        if no concept found: return (None, None)
        if concept found: return (atoms, concept score)

        input_atoms -- AtomsModel instance
        score_min -- minimal score accepted
        score_max -- maximal score accepted
        cc -- connected component identifier
        step -- step number

        """
        assert isinstance(score_min, int)
        assert isinstance(score_max, int)
        if score_min > score_max: return FoundMotif(None, 0, self)
        LOGGER.debug('FIND BEST ' + self.name
                     + ' [' + str(score_min) + ';' + str(score_max) + ']')
        aspargs = {
            ASP_ARG_CC: cc,
            ASP_ARG_STEP: step,
            ASP_ARG_LOWERBOUND: score_min,
            ASP_ARG_UPPERBOUND: score_max
        }
        input_atoms = self._enriched_input_atoms(input_atoms)
        aspargs.update(self._supplementary_constants(input_atoms))
        model = solving.model_from(
            base_atoms=str(input_atoms),
            aspargs=aspargs,
            aspconfig=self,
        )
        # treatment of the model
        if model is None:
            LOGGER.debug(self.name.upper() + ' SEARCH: no model found')
            concept_cover = 0
        else:
            assert 'score' in str(model)
            concept_cover = int(model.get_only('score').args[0])
            LOGGER.debug(self.name.upper() + " SEARCH: model covering {} edges"
                         "found".format(concept_cover))
            LOGGER.debug("\t" + '\n\t'.join(a.asp for a in model.get('powernode')))
        concept_score = self._score_from_cover(concept_cover)
        ret = FoundMotif(model=model, score=concept_score, motif=self)
        return ret


    def _enriched_input_atoms(self, graph:'AtomsModel') -> 'AtomsModel':
        """Modify the input model in order to prepare the next round"""
        return graph


    def _supplementary_constants(self, atoms:'AtomsModel') -> dict:
        """Return a dict of supplementary constants {name: value} for solving"""
        return {}

    def _score_from_cover(self, edge_cover:int) -> int:
        """Return the score for the motif, based on the number of edges
        covered by the motif.

        This method returns the edge_cover as the score, and is here
        to be redefined by subclasses.

        """
        assert isinstance(edge_cover, int)
        return edge_cover


    def compress(self, motif:'AtomsModel', graph:'AtomsModel'):
        """Modify given graph, compressed according to the given motif.

        atoms -- AtomsModel instance describing the motif model
        model -- AtomsModel instance that will be updated  *MODIFIED*
        return -- metadata extracted from the compression.

        """
        assert motif.__class__.__name__ == 'AtomsModel'
        assert graph.__class__.__name__ == 'AtomsModel'
        to_replace, data = [], []
        for name, args in motif:
            if name in INCREMENTAL_ATOMS:
                graph._payload[name] = {}
                to_replace.append((name, args))
            elif name in ACCUMULABLE_ATOMS:
                graph._payload[name].add(args)
            elif name in METADATA_ATOMS:
                data.append((name, args))
            else:
                raise ValueError("Extraction yield an unexpected atom {}({}).".format(str(name), args))
                # print("\nExtraction yield an unexpected atom {}({}).\n".format(str(name), ','.join(args)))
        for name, all_args in itertools.groupby(to_replace, operator.itemgetter(0)):
            all_args = (args for _, args in all_args)
            graph._payload[name] = set(all_args)

        covered_edges = frozenset(self.covered_edges_in_found(motif))
        graph._payload['oedge'] = set(edge for edge in graph._payload['oedge']
                                      if edge not in covered_edges)
        # remove all unnecessary nodes from the graph
        #  a node that is implyied in no edge can't be member of any set.
        #  it is therefore a time waste to give it to the heuristic.
        all_connected_nodes = frozenset(itertools.chain.from_iterable(a for _, a in graph.get('oedge')))
        graph._payload['membercc'] = frozenset((node,) for node in all_connected_nodes)
        return dict(data)


    @staticmethod
    def covered_edges_in_found(self, model:'AtomsModel'):
        """Yield edges covered by given ASP model"""
        raise NotImplementedError("This method should be overwritten by subclasses.")


    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


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
        # print('SET :', nodes)
        yield from (((f, s) if f < s else (s, f))
                    for f, s in itertools.product(nodes, repeat=2))

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
                 include_node_degrees:bool=False):
        super().__init__('biclique', [ASP_SRC_FINDBC, scoring],
                         clasp_options, gringo_options)
        self.include_node_degrees = bool(include_node_degrees)

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
        if self.include_node_degrees:
            degrees = defaultdict(int)
            graph = atoms.AtomsModel(graph)
            edges = frozenset(frozenset(args) for _, args in graph.get('oedge'))
            degrees = Counter(itertools.chain.from_iterable(edges))
            graph.add_atoms(('degree', args) for args in degrees.items())
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


# Expose the motifs as constants.
POWERGRAPH = (Clique.for_powergraph(), Biclique.for_powergraph())


class comparer:
    """Namespace for comparison of models."""

    @staticmethod
    def by_score(ma:FoundMotif, mb:FoundMotif):
        """Return model that have the greater score, or ma on equality"""
        if not isinstance(ma, FoundMotif) and ma is not None:
            print('ASSERT:', ma, type(ma), FoundMotif)
            assert isinstance(ma, FoundMotif) and ma is not None
        if not isinstance(mb, FoundMotif) and mb is not None:
            print('ASSERT:', mb, type(mb), FoundMotif)
            assert isinstance(mb, FoundMotif) and mb is not None
        ma_score = ma.score if ma else 0
        mb_score = mb.score if mb else 0
        return ma if ma_score >= mb_score else mb
