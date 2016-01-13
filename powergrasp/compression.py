"""
Implementation of the compression routine.

"""
import time
import itertools

from powergrasp.commons import ASP_ARG_UPPERBOUND, ASP_ARG_CC
from powergrasp.commons import ASP_ARG_LOWERBOUND, ASP_ARG_STEP

from powergrasp import observers
from powergrasp import solving
from powergrasp import commons
from powergrasp import atoms

from powergrasp.observers import Signals  # shortcut


LOGGER = commons.logger()
# under this minimal score, the found concept is not interesting
MINIMAL_SCORE = 2


def compress_lp_graph(graph_lp, *, all_observers=[],
                      asp_extracting=None, asp_preprocessing=None,
                      asp_ccfinding=None, asp_bcfinding=None,
                      asp_postprocessing=None, interactive=False,
                      lowerbound_cut_off=commons.OPT_LOWERBOUND_CUTOFF):
    """apply the compression algorithm on given graph. Yield lines of
    bubble file.

    graph_lp: filename containing the input graph in ASP readable format.
    all_observers: iterable of observers that needs to be updated when
        something happens.
    asp_extracting: filename of ASP code for graph data extraction.
    asp_preprocessing: filename of ASP code for step preprocessing.
    asp_ccfinding: filename of ASP code for clique finding.
    asp_bcfinding: filename of ASP code for biclique finding..
    asp_postprocessing: filename of ASP code for step postprocessing.
    lowerbound_cut_off: minimal value for the lowerbound optimization.

    """
    # Shortcuts
    def notify_observers(*args, **kwargs):
        "Notify observers with given signals"
        for observer in all_observers:
            observer.update(*args, **kwargs)

    # INIT
    # Extract graph data
    LOGGER.info('#################')
    LOGGER.info('#### EXTRACT ####')
    LOGGER.info('#################')
    notify_observers(
        Signals.CompressionStarted,
        Signals.ExtractionStarted
    )
    # creat a solver that get all information about the graph
    graph_atoms = solving.model_from('', [graph_lp, asp_extracting])
    if graph_atoms is None:
        LOGGER.error('Extraction: no atoms found by graph data extraction.')
        assert(graph_atoms is not None)

    # get all CC, one by one
    atom_ccs = tuple(atoms.split(cc).args[0]
                     for cc in graph_atoms
                     if cc.startswith('cc('))
    notify_observers(connected_components_found=atom_ccs)
    atom_ccs = enumerate(atom_ccs)
    # save atoms as ASP-readable string
    all_edges    = atoms.to_str(graph_atoms, names = 'ccedge')
    first_blocks = atoms.to_str(graph_atoms, names = 'block')
    graph_atoms  = atoms.to_str(graph_atoms, names = ('ccedge', 'membercc'))
    remain_edges_global = all_edges.count('ccedge(')
    # notifications about the extraction
    notify_observers(
        Signals.ExtractionStopped,
        all_edge_generated=remain_edges_global,
        step_data_generated=(0, 0, remain_edges_global)
    )
    # printings
    LOGGER.debug('EXTRACTED: ' + graph_atoms + '\n')
    LOGGER.debug('CCEDGES  : ' + all_edges + '\n')

    # ITERATIVE TREATMENT
    # Find connected components
    LOGGER.info('#################')
    LOGGER.info('####   CC    ####')
    LOGGER.info('#################')
    for cc_nb, cc in atom_ccs:
        notify_observers(connected_component_started=(cc_nb, cc),
                         connected_components_found=cc)
        assert any(isinstance(cc, cls) for cls in (str, int))
        # contains interesting atoms and the non covered edges at last step
        model_found_at_last_iteration = True  # False when no model found
        result_atoms = tuple()
        remain_edges = None
        previous_coverage = ''  # accumulation of covered/2
        previous_blocks   = first_blocks
        # main loop
        k = 0
        last_score = remain_edges_global  # score of the previous step
        # lowerbound value is impossible to now at first 1,
        #  but will be firstly computed if its better than min score.
        # If lowerbound value is smaller or than MINIMAL_SCORE,
        #  the optimization is disabled for avoid a costly treatment while
        #  search for little concepts.
        lowerbound_value = (MINIMAL_SCORE + 1) if lowerbound_cut_off > 0 else 0
        def printable_bounds():
            return '[' + str(lowerbound_value) + ';' + str(last_score) + ']'
        # iteration
        notify_observers(Signals.IterationStarted)
        while model_found_at_last_iteration:
            # STEP INITIALIZATION
            notify_observers(Signals.StepStarted)
            k += 1
            time_iteration = time.time()
            model = None
            best_model = None
            score = None  # contains the score of the generated concept

            # LOWER BOUND: is it necessary to find it ?
            if lowerbound_value > MINIMAL_SCORE:
                #  indicate that the preprocesser must found the max lowerbound
                lowerbound_atom = 'lowerbound.'
            else:
                lowerbound_atom = ''  # no max lowbound search in preprocessing

            #########################
            LOGGER.debug('PREPROCESSING')
            #########################
            notify_observers(
                Signals.PreprocessingStarted
            )
            model = solving.model_from(
                base_atoms=(graph_atoms + previous_coverage
                            + previous_blocks + lowerbound_atom),
                aspfiles=asp_preprocessing,
                aspargs={ASP_ARG_CC: cc}
            )
            if model is None:
                # break # no more models !
                model_found_at_last_iteration = False
                notify_observers(step_data_generated=[None] * 3)
                notify_observers(Signals.StepStopped)
                notify_observers(Signals.StepFinalized)
                continue
            # treatment of the model
            lowbound = tuple(a for a in model if a.startswith('maxlowerbound'))
            preprocessed_graph_atoms = atoms.to_str(
                atom for atom in model
                if not atom.startswith('maxlowerbound(')
            )
            try:
                assert len(lowbound) <= 1  # multiple maxlowerbound is impossible
                lowerbound_value = atoms.split(lowbound[0])[1][0]
            except IndexError:
                lowerbound_value = MINIMAL_SCORE
            # the string 'inf' is the ASP type for 'infinitely small'
            # so, if no lowerbound found, 'inf' will be returned and
            # can't be converted in integer
            try:
                lowerbound_value = int(lowerbound_value)
            except ValueError:
                lowerbound_value = MINIMAL_SCORE
            notify_observers(Signals.PreprocessingStopped)

            #########################
            LOGGER.debug('FIND BEST CLIQUE ' + printable_bounds())
            #########################
            model = solving.model_from(
                base_atoms=(preprocessed_graph_atoms
                            + previous_coverage + previous_blocks),
                aspfiles=(asp_ccfinding, asp_postprocessing),
                aspargs={ASP_ARG_CC:cc, ASP_ARG_STEP:k,
                         ASP_ARG_LOWERBOUND:lowerbound_value,
                         ASP_ARG_UPPERBOUND:last_score}
            )
            # treatment of the model
            if model is None:
                LOGGER.debug('CLIQUE SEARCH: no model found')
            else:
                best_model = model
                assert('score' in str(model))
                score = int(atoms.arg(next(a for a in model if a.startswith('score(')))[0])
                assert(isinstance(score, int))
                lowerbound_value = max(
                    lowerbound_value,
                    score,
                )
                atom_counter = atoms.count(model)
                notify_observers(Signals.CliqueFound)

            #########################
            LOGGER.debug('FIND BEST BICLIQUE' + printable_bounds())
            #########################
            model = solving.model_from(
                base_atoms=(preprocessed_graph_atoms
                            + previous_coverage + previous_blocks),
                aspfiles=(asp_bcfinding, asp_postprocessing),
                aspargs={ASP_ARG_CC: cc, ASP_ARG_STEP: k,
                         ASP_ARG_LOWERBOUND: lowerbound_value,
                         ASP_ARG_UPPERBOUND: last_score}
            )
            # treatment of the model
            if model is None:
                LOGGER.debug('BICLIQUE SEARCH: no model found')
            else:
                best_model = model
                # printings
                LOGGER.debug('BICLIQUE SEARCH: best model found')
                notify_observers(Signals.BicliqueFound)
                LOGGER.debug('\tOUTPUT: ' + atoms.to_str(
                    model, separator='.\n\t'
                ))
                score = int(atoms.arg(next(
                    atom for atom in model if atom.startswith('score(')
                )))
                assert(isinstance(score, int))
                atom_counter = atoms.count(model)

            #########################
            LOGGER.debug('BEST MODEL TREATMENT')
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
                assert(isinstance(score, int))
                assert(score >= MINIMAL_SCORE)
                last_score = score
                remain_edges_global -= score  # score is equals to edge cover
                # atoms to be given to the next step
                previous_coverage += atoms.to_str(
                    best_model, names=('covered',)
                )
                previous_blocks = atoms.to_str(
                    best_model, names=('block', 'include_block')
                )

                # give new powernodes to converter
                notify_observers(model_found=tuple(
                    atom for atom in best_model
                    if atoms.split(atom).name in ('powernode', 'clique', 'poweredge')
                ))

                # save interesting atoms
                result_atoms = itertools.chain(
                    result_atoms,
                    (a for a in best_model
                     if atoms.split(a).name in ('powernode', 'poweredge'))
                )

                # save the number of generated powernodes and poweredges
                new_powernode_count = int(atoms.arg(next(
                    a for a in best_model if a.startswith('powernode_count')
                )))
                if new_powernode_count not in (0,1,2):
                    LOGGER.error('Error of Powernode generation: '
                                 + str(new_powernode_count) + 'generated.'
                                 + ('It can be a problem of stars that are counted as powernodes'
                                    if new_powernode_count < 0 else
                                    'Too many powernodes for one step.')
                                 + ' It\'s probable that this problem will only'
                                 + ' touch the statistics, but the compression'
                                 + ' itself will not be compromised.'
                                )
                new_poweredge_count = atom_counter['poweredge']
                remain_edges = tuple(a for a in best_model if a.startswith('edge('))

                # notify_observers: provide the data
                notify_observers(
                    model_found=result_atoms,
                    step_data_generated=(new_powernode_count,
                                         new_poweredge_count,
                                         remain_edges_global),
                )
                assert(remain_edges_global > 0)
            # notify_observers:
            notify_observers(Signals.StepStopped)
            notify_observers(Signals.StepFinalized)

        notify_observers(Signals.IterationStopped)
        # END while model_found_at_last_iteration
        # Here, all models was processed in the connected component

        # Management of remain data in the connected component
        assert(remain_edges_global >= 0)

        # determine how many edges remains if no compression performed
        if remain_edges is None:  # no compression performed
            # all_edges contains all atoms ccedge/3
            remain_edges = (a for a in all_edges.split('.'))
            remain_edges = tuple(a for a in remain_edges if str(cc) in a)

        # Remain edges in cc
        if len(remain_edges) == 0:
            LOGGER.info('No remaining edge')
        else:
            LOGGER.info(str(len(remain_edges)) + ' remaining edge(s)')
            # send them to observers (including the output converter)
            notify_observers(remain_edge_generated=remain_edges)

        notify_observers(
            Signals.ConnectedComponentStopped,
            final_edge_count_generated=len(remain_edges),
        )

        # print results
        LOGGER.debug('\n\t' + atoms.prettified(
            result_atoms,
            joiner='\n\t',
            sort=True
        ))

    # DEINIT
    LOGGER.info('#################')
    LOGGER.info('#### RESULTS ####')
    LOGGER.info('#################')
    # compute a human readable final results string,
    # and put it in the output and in level info.
    notify_observers(Signals.CompressionStopped)
    notify_observers(Signals.CompressionFinalized)
