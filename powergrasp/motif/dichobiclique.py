import itertools
from collections import defaultdict, Counter

from powergrasp import utils
from powergrasp import atoms
from powergrasp import commons
from powergrasp import solving
from powergrasp.atoms import AtomsModel
from powergrasp.commons import ASP_SRC_FINDBCDS, ASP_SRC_FINDCC, ASP_SRC_SCORING
from .motif import Motif


LOGGER = commons.logger()



def dichotomic_search(model:AtomsModel, time_limit:int=3):
    """Search for stable, then inject stable/2 atoms in model"""
    # avoid computation of an existing stable
    already_have_stable = 'stable' in model.counts
    if already_have_stable: return model
    # search for stable
    LOGGER.info('ADDON(NDS): Search for stable in {}s.'.format(time_limit))
    solver_config = solving.ASPConfig(
        'naive dichotomic search',
        [commons.ASP_SRC_STABLE_SEARCH],
        clasp_options='--time-limit={}'.format(time_limit)
    )
    stable_model = solving.model_from(
        base_atoms=str(model),
        aspconfig=solver_config,
    )
    if stable_model is None:
        LOGGER.info('STABLE SEARCH: no stable found')
        stable = ()
    else:
        stable = frozenset(stable_model.get('stable'))
        LOGGER.info("STABLE SEARCH: {} nodes".format(len(stable)))
        LOGGER.debug("STABLE SEARCH: " + str(stable))
        print(stable)

    # update and return model
    # print('LRYSNM:', model.counts)
    model.set_args('stable', (a.args for a in stable))
    # print('YCCLYH:', model.counts)
    return model


class DichoSearchBiclique(Motif):
    """Implementation of the biclique motif,
    where the edge cover equals N * M.

    Optimization using stable model.

    """

    def __init__(self, scoring:str=ASP_SRC_SCORING, gringo_options='',
                 clasp_options=solving.ASP_DEFAULT_CLASP_OPTION,
                 additional_files:iter=[], addons:iter=None,
                 search:str=ASP_SRC_FINDBCDS):
        super().__init__('biclique',
                         [search, scoring] + list(additional_files),
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


    def _enriched_input_atoms(self, model:AtomsModel) -> 'AtomsModel':
        """Modify the input model in order to prepare the next round"""
        return dichotomic_search(model, time_limit=10)

    @staticmethod
    def for_powergraph():
        """Return a biclique object designed to reproduce
        the powergraph compression

        """
        return DichoSearchBiclique()
