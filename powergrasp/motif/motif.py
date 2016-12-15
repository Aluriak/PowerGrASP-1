"""Definition of Motif and comparer class, including solving functions

See the other files of the package for implemented motifs exposed
to the exterior.

"""


import operator
import itertools
from collections import namedtuple

from powergrasp import atoms
from powergrasp import commons
from powergrasp import solving
from powergrasp.commons import (ASP_ARG_UPPERBOUND, ASP_ARG_CC,
                                ASP_ARG_LOWERBOUND, ASP_ARG_STEP)


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
        super().__init__(name, files + motif_search_files,
                         clasp_options, gringo_options)


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
            LOGGER.debug("\t" + '\n\t'.join(a.asp for a in model.get('powernode', 'poweredge')))
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
        # Detect diff produced by motif compression on the graph model
        for name, args in motif:
            if name in INCREMENTAL_ATOMS:
                graph._payload[name] = {}
                to_replace.append((name, args))
            elif name in ACCUMULABLE_ATOMS:
                graph._payload[name].add(args)
            elif name in METADATA_ATOMS:
                data.append((name, args))
            else:  # predicate not in any class
                raise ValueError("Extraction yield an unexpected atom {}({}).".format(str(name), args))
        # Replacement of incremental atoms
        for name, all_args in itertools.groupby(to_replace, operator.itemgetter(0)):
            all_args = (args for _, args in all_args)
            graph.set_args(name, all_args)

        # All covered edges should be in the graph
        covered_edges = frozenset(self.covered_edges_in_found(motif))
        graph_edges = frozenset(graph.get_args('edge'))
        for covered_edge in covered_edges:
            if covered_edge not in graph_edges:
                LOGGER.warning("Edge ({},{}) declared as covered by motif {} "
                               "doesn't exists in the graph".format(*covered_edge, self))
        # Update the graph model
        graph.set_args('edge', (edge for edge in graph.get_args('edge')
                                if edge not in covered_edges))
        # remove all unnecessary nodes from the graph
        #  a node that is implyied in no edge can't be member of any set.
        #  it is therefore a time waste to give it to the heuristic.
        all_connected_nodes = frozenset(itertools.chain.from_iterable(
            a for _, a in graph.get('edge')
        ))
        graph.set_args('membercc', frozenset((node,) for node in all_connected_nodes))
        return dict(data)


    @staticmethod
    def covered_edges_in_found(self, model:'AtomsModel'):
        """Yield edges covered by given ASP model"""
        raise NotImplementedError("This method should be overwritten by subclasses.")


    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
