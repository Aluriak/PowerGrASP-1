"""
Implementation of the compression routine.

"""
import time
import itertools
from functools import partial

from powergrasp.commons import ASP_ARG_UPPERBOUND, ASP_ARG_CC
from powergrasp.commons import ASP_ARG_LOWERBOUND, ASP_ARG_STEP

from powergrasp import observers
from powergrasp import solving
from powergrasp import commons
from powergrasp import atoms
from powergrasp import utils

from powergrasp.observers import Signals  # shortcut


LOGGER = commons.logger()
# under this minimal score, the found concept is not interesting
MINIMAL_SCORE = 2


def search_concept(input_atoms, score_min, score_max, cc, step, aspconfig):
    """Return the concept found and its score.

    if no concept found: return (None, None)
    if concept found: return (atoms, concept score)

    """
    if score_min > score_max: return None, None
    search_clique = commons.ASP_SRC_FINDCC in aspconfig.files
    CONCEPT_NAME = ('' if search_clique else 'BI') + 'CLIQUE'
    LOGGER.debug('FIND BEST ' + CONCEPT_NAME
                 + ' [' + str(score_min) + ';' + str(score_max) + ']')
    model = solving.model_from(
        base_atoms=input_atoms,
        aspargs={ASP_ARG_CC: cc, ASP_ARG_STEP: step,
                 ASP_ARG_LOWERBOUND: score_min,
                 ASP_ARG_UPPERBOUND: score_max},
        aspconfig=aspconfig,
    )
    # treatment of the model
    if model is None:
        LOGGER.debug(CONCEPT_NAME + ' SEARCH: no model found')
        concept_score = None
    else:
        assert('score' in str(model))
        concept_score = int(model.get_first('score').arguments[0])
    return model, concept_score


def compress_lp_graph(graph_lp, *, all_observers=[],
                      extract_config=None, biclique_config=None,
                      clique_config=None):
    """apply the compression algorithm on given graph. Yield lines of
    bubble file.

    graph_lp: filename containing the input graph in ASP readable format.
    all_observers: iterable of observers that needs to be updated when
        something happens.
    extract_config: ASP configuration for the extraction.
    biclique_config: ASP configuration for the biclique search.
    clique_config: ASP configuration for the clique search.

    """
    # None to default value
    if extract_config is None:
        extract_config = solving.CONFIG_EXTRACTION()
    if biclique_config is None:
        biclique_config = solving.CONFIG_BICLIQUE_SEARCH()
    if clique_config is None:
        clique_config = solving.CONFIG_CLIQUE_SEARCH()
    # Shortcuts and curried functions
    def notify_observers(*args, **kwargs):
        "Notify observers with given signals"
        for observer in all_observers:
            observer.update(*args, **kwargs)
    search_clique = partial(search_concept, aspconfig=clique_config)
    search_biclique = partial(search_concept, aspconfig=biclique_config)

    # INIT
    # Extract graph data
    LOGGER.info('#################')
    LOGGER.info('#### EXTRACT ####')
    LOGGER.info('#################')
    notify_observers(
        Signals.CompressionStarted,
        Signals.ExtractionStarted,
        asp_config_updated=(extract_config, clique_config, biclique_config)
    )
    # creat a solver that get all information about the graph
    connected_components = (solving.all_models_from(
        '', aspfiles=[graph_lp], aspconfig=extract_config,
    ))
    notify_observers(Signals.ExtractionStopped)

    # ITERATIVE TREATMENT
    # Find connected components
    LOGGER.info('#################')
    LOGGER.info('####   CC    ####')
    LOGGER.info('#################')
    total_edges_counter = 0  # number of edge in all the graph (for statistics)
    total_remain_edges_counter = 0
    for cc_nb, cc_atoms in enumerate(connected_components):
        # get data from cc_atoms
        cc_name = cc_atoms.get_first('cc').arguments[0]
        notify_observers(cc_count_generated=int(cc_atoms.get_first('nb_cc').arguments[0]))
        assert any(isinstance(cc_name, cls) for cls in (str, int))
        remain_edges_cc = tuple(atom for atom in cc_atoms
                                if atom.predicate == 'oedge')
        def nb_cc_edges(): return len(remain_edges_cc)
        total_edges_counter += nb_cc_edges()
        previous_atoms = atoms.to_str(cc_atoms)
        cc_atoms = atoms.to_str(cc_atoms)
        # treatment of the connected_components stated
        notify_observers(connected_component_started=(cc_nb, cc_name))
        # contains interesting atoms and the non covered edges at last step
        model_found_at_last_iteration = True  # False when no model found
        # main loop
        step = 0
        last_score = nb_cc_edges()  # score of the previous step, or maximal score
        # iteration
        notify_observers(Signals.IterationStarted)
        while model_found_at_last_iteration:
            # STEP INITIALIZATION
            notify_observers(Signals.StepStarted)
            step += 1
            concept_score, best_model = None, None
            score_lowerbound = MINIMAL_SCORE

            clique_model, clique_score = search_clique(
                previous_atoms,
                score_min=score_lowerbound,
                score_max=last_score,
                cc=cc_name,
                step=step,
            )

            if not clique_model or score_lowerbound <= clique_score:
                model, score = search_biclique(
                    previous_atoms,
                    score_min=clique_score if clique_score else score_lowerbound,
                    score_max=last_score,
                    cc=cc_name,
                    step=step,
                )
            best_model = model if model else clique_model
            best_score = score if score else clique_score

            # best_model is computed
            last_score = best_score


            #########################
            LOGGER.debug('BEST MODEL TREATMENT\n\n\n')
            #########################
            # stop cc compression if no model found
            if best_model is None:
                # Send signal with no data ; this is not necessary, but allow
                # the plotting to print all the iterations. Without that signal,
                # the final result cannot show one iteration per connected
                # component, while for each of them the last step will not
                # produce any model. Next line handle the model inexistence.
                notify_observers(step_data_generated=[None] * 3)
                model_found_at_last_iteration = False
            else:  # at least one model was found, and the best is best_model
                # debug printing
                LOGGER.debug('POWERNODES:\n\t' + atoms.prettified(
                    best_model,
                    names=('powernode', 'poweredge', 'score'),
                    joiner='\n\t',
                    sort=True
                ))
                # new concept is the previous concept of next concept
                assert(isinstance(best_score, int))
                assert(best_score >= MINIMAL_SCORE)
                last_score = best_score
                remain_edges_cc = tuple(best_model.get('oedge'))
                previous_atoms = atoms.to_str(best_model.get(
                    ('oedge', 'membercc', 'block', 'include_block')
                ))

                # give new powernodes to converter
                notify_observers(model_found=tuple(
                    atom for atom in best_model
                    if atom.predicate in ('powernode', 'clique', 'poweredge')
                ))

                final_concept = tuple(atom for atom in best_model
                                      if atom.predicate in ('powernode',
                                                            'poweredge'))

                # save the number of generated powernodes and poweredges
                new_powernode_count = next(
                    int(atom.arguments[0]) for atom in best_model
                    if atom.predicate == 'powernode_count')
                new_poweredge_count = next(
                    int(atom.arguments[0]) for atom in best_model
                    if atom.predicate == 'poweredge_count')
                if new_powernode_count not in (0, 1, 2):
                    LOGGER.error('Error of Powernode generation: '
                                 + str(new_powernode_count) + 'generated.'
                                 + ('It can be a problem of stars that are counted as powernodes'
                                    if new_powernode_count < 0 else
                                    'Too many powernodes for one step.')
                                 + ' It\'s probable that this problem will only'
                                 + ' touch the statistics, but the compression'
                                 + ' itself will not be compromised.'
                                )

                # notify_observers: provide the data
                notify_observers(
                    model_found=final_concept,
                    step_data_generated=(new_powernode_count,
                                         new_poweredge_count, best_score)
                )
                if nb_cc_edges() < 0:
                    print('REMAIN_EDGES_GLOBAL:', nb_cc_edges())
                    assert(nb_cc_edges() >= 0)
            # notify_observers:
            notify_observers(Signals.StepStopped)
            notify_observers(Signals.StepFinalized)

        notify_observers(Signals.IterationStopped)
        # END while model_found_at_last_iteration
        # Here, all models was processed in the connected component

        # Management of remain data in the connected component
        assert(nb_cc_edges() >= 0)

        # Remain edges in cc
        notify_observers(cc_remain_edge_generated=remain_edges_cc)
        total_remain_edges_counter += nb_cc_edges()


        notify_observers(Signals.ConnectedComponentStopped)

    # DEINIT
    LOGGER.info('#################')
    LOGGER.info('#### RESULTS ####')
    LOGGER.info('#################')
    # compute a human readable final results string,
    # and put it in the output and in level info.
    notify_observers(final_edge_count_generated=total_edges_counter,
                     final_remain_edge_count_generated=total_remain_edges_counter)
    notify_observers(Signals.CompressionStopped)
    notify_observers(Signals.CompressionFinalized)
