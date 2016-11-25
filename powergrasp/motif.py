"""Definition of data related to motifs, including solving functions

Predefined motifs are defined in this module: biclique and clique.

"""


import operator
import itertools
from collections import namedtuple

from powergrasp import commons
from powergrasp import solving
from powergrasp.commons import (ASP_ARG_UPPERBOUND, ASP_ARG_CC,
                                ASP_ARG_LOWERBOUND, ASP_ARG_STEP,
                                ASP_SRC_FINDCC, ASP_SRC_FINDBC)


LOGGER = commons.logger()

# returned by motif search, embedding all informations about found motif
FoundMotif = namedtuple('FoundMotif', 'model score motif')

# Follows atoms produced by motif solving, splitted in 4 disjoint classes.
# invalidable atoms are atoms that needs to be deleted from the model
INVALIDABLE_ATOMS = {'oedge'}
# incremental atoms replace the existing atoms of same name in the model
INCREMENTAL_ATOMS = {'block', 'membercc', 'include_block'}
# accumulable atoms need to be added to the model
ACCUMULABLE_ATOMS = {'powernode', 'poweredge'}
# metadata are used by observers
METADATA_ATOMS = {'powernode_count', 'poweredge_count', 'score'}


class Motif(solving.ASPConfig):
    """A Motif is basically an named ASPConfig instance.

    This class allows client to simply define new motifs to find,
    and to give a precise context for solving (options and source files).

    """


    def __init__(self, name:str, files=None, clasp_options='', gringo_options='',
                 motif_search_files=solving.ASP_FILES_MOTIF_SEARCH):
        super().__init__(files + motif_search_files, clasp_options, gringo_options)
        self.name = name


    def search(self, input_atoms:str, score_min:int, score_max:int,
               cc:str, step:int):
        """Return the concept found and its score.

        if no concept found: return (None, None)
        if concept found: return (atoms, concept score)

        input_atoms -- string of atoms
        score_min -- minimal score accepted
        score_max -- maximal score accepted
        cc -- connected component identifier
        step -- step number

        """
        assert isinstance(score_min, int)
        assert isinstance(score_max, int)
        if score_min > score_max: return None, None
        LOGGER.debug('FIND BEST ' + self.name
                     + ' [' + str(score_min) + ';' + str(score_max) + ']')
        model = solving.model_from(
            base_atoms=input_atoms,
            aspargs={ASP_ARG_CC: cc, ASP_ARG_STEP: step,
                     ASP_ARG_LOWERBOUND: score_min,
                     ASP_ARG_UPPERBOUND: score_max},
            aspconfig=self,
        )
        # treatment of the model
        if model is None:
            LOGGER.debug(self.name.upper() + ' SEARCH: no model found')
            concept_score = 0
        else:
            assert 'score' in str(model)
            concept_score = int(model.get_only('score').args[0])
        ret = FoundMotif(model=model, score=concept_score, motif=self)
        return ret


    def compress(self, atoms:str, model:'AtomsModel'):
        """Modify self, compressed according to the given motif.

        atoms -- iterable of (name, args)
        model -- AtomsModel instance that will be updated  *MODIFIED*
        return -- metadata extracted from the compression.

        """
        to_remove, to_replace, data = [], [], []
        for name, args in atoms:
            if name in INVALIDABLE_ATOMS:
                to_remove.append((name, args))
            elif name in INCREMENTAL_ATOMS:
                model._payload[name] = {}
                to_replace.append((name, args))
            elif name in ACCUMULABLE_ATOMS:
                model._payload[name].add(args)
            elif name in METADATA_ATOMS:
                data.append((name, args))
            else:
                raise ValueError("Extraction yield an unexpected atom {}({}).".format(str(name), args))
        for name, all_args in itertools.groupby(to_replace, operator.itemgetter(0)):
            all_args = (args for _, args in all_args)
            model._payload[name] = set(all_args)
        for name, all_args in itertools.groupby(to_remove, operator.itemgetter(0)):
            all_args = (args for _, args in all_args)
            all_args = frozenset(all_args)
            model._payload[name] = set(args for args in model._payload[name]
                                      if args not in all_args)
        return dict(data)


CLIQUE   = Motif('clique',   [ASP_SRC_FINDCC], solving.ASP_DEFAULT_CLASP_OPTION)
BICLIQUE = Motif('biclique', [ASP_SRC_FINDBC], solving.ASP_DEFAULT_CLASP_OPTION)
POWERGRAPH = (CLIQUE, BICLIQUE)
ALL = (CLIQUE, BICLIQUE)


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
