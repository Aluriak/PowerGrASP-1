# -*- coding: utf-8 -*-
"""
Main source file of the package, containing tho compress function.

The compress function get numerous arguments,
 for allowing a parametrable compression.

"""
import os
import sys
import time
import itertools
from builtins           import input
from collections        import defaultdict

from powergrasp.commons import basename
from powergrasp.commons import ASP_SRC_EXTRACT, ASP_SRC_PREPRO , ASP_SRC_FINDCC
from powergrasp.commons import ASP_SRC_FINDBC , ASP_SRC_POSTPRO, ASP_SRC_POSTPRO
from powergrasp.commons import ASP_ARG_UPPERBOUND, ASP_ARG_CC
from powergrasp.commons import ASP_ARG_LOWERBOUND, ASP_ARG_STEP
from powergrasp import converter as converter_module
from powergrasp import statistics
from powergrasp import solving
from powergrasp import commons
from powergrasp import atoms


LOGGER = commons.logger()


def compress(graph_data, output_file=None, *, extracting=None,
             preprocessing=None, ccfinding=None,
             bcfinding=None, postprocessing=None,
             statistics_filename='data/statistics.csv',
             output_format=None, lowerbound_cut_off=2,
             interactive=False, count_model=False, count_cc=False,
             show_preprocessed=False):
    """Performs the graph compression with data found in graph file.

    Use ASP source code found in extract, findcc, findbc
     and {pre,post}processiing files for perform the computations,
     or the default ones if None is provided.
     (which is probably what user want in 99.99% of cases)

    Output format must be a valid string,
     or will be inferred from the output file name, or will be set as bbl.

    If output file is None, result will be printed in stdout.

    If interactive is True, an input will be expected
     from the user after each step.

    Notes about the maximal lowerbound optimization:
      In a linear time, it is possible to compute the
       maximal degree in the non covered graph.
      This value correspond to the minimal best concept score.
      In real life, the blocks (used by ASP for avoid overlapping powernodes)
       complicate the job.
      Moreover, as cliques are searched before the biclique, the lowerbound
       value is increased if a clique with a better score is found.
      The cut-off value is here for allow client code to control
       this optimization, by specify the value that disable this optimization
       when the lowerbound reachs it.

    The function itself returns a float that is, in seconds,
     the time necessary for the compression,
     and the object provided by the statistics module,
     that contains statistics about the compression.

    """
    # defensive returns
    if not graph_data: return
    try:
        with open(graph_data) as fd:
            pass
    except (PermissionError, FileNotFoundError):
        LOGGER.error("input file " + str(graph_data) +
                     " can't be opened. Compression aborted.")
        return

    # Deduce output format:
    if not output_format:
        try:
            output_format = output_file.split('.')[-1]
        except (IndexError, AttributeError):  # use the bbl if nothing found
            output_format = converter_module.DEFAULT_OUTPUT_FORMAT
    assert output_format in converter_module.OUTPUT_FORMATS
    if output_file: assert output_file.endswith(output_format)

    # Select proper ASP source if not given
    if not extracting: extracting         = commons.ASP_SRC_EXTRACT
    if not preprocessing: preprocessing   = commons.ASP_SRC_PREPRO
    if not ccfinding: ccfinding           = commons.ASP_SRC_FINDCC
    if not bcfinding: bcfinding           = commons.ASP_SRC_FINDBC
    if not postprocessing: postprocessing = commons.ASP_SRC_POSTPRO

    # Initialize descriptors
    output    = open(output_file, 'w') if output_file else sys.stdout
    converter = converter_module.output_converter_for(output_format)
    model     = None
    stats     = statistics.container(graph_data,
                                     statistics_filename)
    output.write(converter.header())
    time_extract = time.time()
    time_compression = time.time()
    minimal_score = 2
    remain_edges_global = 0  # counter of remain_edges in all graph

    # Extract graph data
    LOGGER.info('#################')
    LOGGER.info('#### EXTRACT ####')
    LOGGER.info('#################')
    # creat a solver that get all information about the graph
    graph_atoms = solving.model_from('', [graph_data, extracting])
    assert(graph_atoms is not None)

    # get all CC, one by one
    atom_ccs = (atoms.split(cc).args[0]
                for cc in graph_atoms
                if cc.startswith('cc(')
               )
    if count_cc:
        atom_ccs = tuple(atom_ccs)
        atom_ccs_count = len(atom_ccs)
    atom_ccs = enumerate(atom_ccs)
    # save atoms as ASP-readable string
    all_edges   = atoms.to_str(graph_atoms, names='ccedge')
    first_blocks= atoms.to_str(graph_atoms, names='block')
    graph_atoms = atoms.to_str(graph_atoms, names=('ccedge', 'membercc'))
    # stats about compression
    remain_edges_global = all_edges.count('ccedge')
    statistics.add(stats, initial_edge_count=remain_edges_global)
    # printings
    LOGGER.debug('EXTRACTED: ' + graph_atoms + '\n')
    LOGGER.debug('CCEDGES  : ' + all_edges + '\n')
    time_extract = time.time() - time_extract

    # Find connected components
    LOGGER.info('#################')
    LOGGER.info('####   CC    ####')
    LOGGER.info('#################')
    for cc_nb, cc in atom_ccs:
        assert(any(isinstance(cc, cls) for cls in (str, int)))
        # contains interesting atoms and the non covered edges at last step
        result_atoms = tuple()
        remain_edges = None
        previous_coverage = ''  # accumulation of covered/2
        previous_blocks   = first_blocks
        # main loop
        LOGGER.info('#### CC ' + str(cc_nb+1)
                    + ('/' + str(atom_ccs_count) if count_cc else '')
                    + ': ' + str(cc) + ' ' + str(cc.__class__))
        k = 0
        last_score = remain_edges_global  # score of the previous step
        # lowerbound value is impossible to now at first 1,
        #  but will be firstly computed if its better than min score.
        # If lowerbound value is smaller or than minimal_score,
        #  the optimization is disabled for avoid a costly treatment while
        #  search for little concepts.
        lowerbound_value = (minimal_score + 1) if lowerbound_cut_off > 0 else 0
        def printable_bounds():
            return '[' + str(lowerbound_value) + ';' + str(last_score) + ']'
        # iteration
        while True:
            # STEP INITIALIZATION
            k += 1
            time_iteration = time.time()
            model = None
            best_model = None
            score = None  # contains the score of the generated concept

            # LOWER BOUND: is it necessary to find it ?
            if lowerbound_value > minimal_score:
                #  indicate that the preprocesser must found the max lowerbound
                lowerbound_atom = 'lowerbound.'
            else:
                lowerbound_atom = ''  # no max lowbound search in preprocessing

            #########################
            LOGGER.debug('PREPROCESSING')
            #########################
            model = solving.model_from(
                base_atoms=(graph_atoms + previous_coverage
                            + previous_blocks + lowerbound_atom),
                aspfiles=preprocessing,
                aspargs={ASP_ARG_CC:cc}
            )
            if model is None:
                # no more models !
                break
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
                lowerbound_value = minimal_score
            # the string 'inf' is the ASP type for 'infinitely small'
            # so, if no lowerbound found, 'inf' will be returned and
            # can't be converted in integer
            try:
                lowerbound_value = int(lowerbound_value)
            except ValueError:
                lowerbound_value = minimal_score
            if show_preprocessed:
                # flag show_preprocessed ask for print output in stdout
                print('PREPROCESSED DATA:',
                      '\n\tlowbound:', lowbound,
                      '\n\tATOMS:', preprocessed_graph_atoms)

            #########################
            LOGGER.debug('FIND BEST CLIQUE ' + printable_bounds())
            #########################
            model = solving.model_from(
                base_atoms=(preprocessed_graph_atoms
                            + previous_coverage + previous_blocks),
                aspfiles=(ccfinding, postprocessing),
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

            #########################
            LOGGER.debug('FIND BEST BICLIQUE' + printable_bounds())
            #########################
            model = solving.model_from(
                base_atoms=(preprocessed_graph_atoms
                            + previous_coverage + previous_blocks),
                aspfiles=(bcfinding, postprocessing),
                aspargs={ASP_ARG_CC:cc, ASP_ARG_STEP:k,
                         ASP_ARG_LOWERBOUND:lowerbound_value,
                         ASP_ARG_UPPERBOUND:last_score}
            )
            # treatment of the model
            if model is None:
                LOGGER.debug('BICLIQUE SEARCH: no model found')
            else:
                best_model = model
                # printings
                LOGGER.debug('\tOUTPUT: ' + atoms.to_str(
                    model, separator='.\n\t'
                ))
                score = int(atoms.arg(next(
                    a for a in model if a.startswith('score(')
                )))
                assert(isinstance(score, int))
                atom_counter = atoms.count(model)

            #########################
            LOGGER.debug('BEST MODEL TREATMENT')
            #########################
            # stop cc compression if no model found
            if best_model is None:
                if count_model: # replace counter by the final information
                    print('\r', end='')
                    sys.stdout.flush()
                    print(str(k-1) + ' optimal model' + ('s' if k-1>1 else '')
                          + ' found by best concept search.')
                break
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
                assert(score >= minimal_score)
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
                converter.convert((
                    a for a in best_model
                    if atoms.split(a).name in ('powernode', 'clique', 'poweredge')
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

                # save statistics: add() method takes all data about the new iteration
                time_iteration = time.time() - time_iteration
                statistics.add(
                    stats,
                    poweredge_count=new_poweredge_count,
                    powernode_count=new_powernode_count,
                    gentime=round(time_iteration, 3),
                    remain_edges_count=remain_edges_global,
                )

            # interactive mode
            if count_model and interactive:
                input(str(k)+'>Next ?')  # my name is spam
            elif interactive:
                input('Next ?')  # my name is spam
            elif count_model:
                print('\r' + str(k) + ' model'
                      + ('s' if k > 1 else '') + ' found'
                      + ' with bounds ' + printable_bounds().ljust(80),
                      end=''
                )
                sys.stdout.flush()





        #####################
        #### REMAIN DATA ####
        #####################
        # statistics
        assert(remain_edges_global >= 0)

        # determine how many edges remains if no compression performed
        if remain_edges is None:  # no compression performed
            # all_edges contains all atoms ccedge/3
            remain_edges = (a for a in all_edges.split('.'))
            remain_edges = tuple(a for a in remain_edges if str(cc) in a)

        # Remain edges in cc
        statistics.add(stats, final_edges_count=len(remain_edges))
        if len(remain_edges) == 0:
            LOGGER.info('No remaining edge')
        else:
            LOGGER.info(str(len(remain_edges)) + ' remaining edge(s)')
            converter.convert(remain_edges)



        ########################
        # WRITE OUTPUT IN FILE #
        ########################
        output.write(converter.finalized())
        converter.release_memory()
        LOGGER.debug('FINAL DATA SAVED IN FILE ' + output.name)

        # print results
        # results_names = ('powernode',)
        LOGGER.debug('\n\t' + atoms.prettified(
            result_atoms,
            joiner='\n\t',
            sort=True
        ))

    LOGGER.info('#################')
    LOGGER.info('#### RESULTS ####')
    LOGGER.info('#################')
    # compute a human readable final results string,
    # and put it in the output and in level info.
    time_compression = time.time() - time_compression
    final_results = (
        "All cc have been performed in " + str(round(time_compression, 3))
        + "s (extraction in " + str(round(time_extract, 3)) + ')'
        + ".\nGrounder options: " + commons.ASP_GRINGO_OPTIONS
        + ".\nSolver options: "   + commons.ASP_CLASP_OPTIONS
        + ".\nNow, statistics on "
        + statistics.output(stats)
    )
    LOGGER.info(final_results)
    output.write(converter.comment(final_results.split('\n')))

    if output is not sys.stdout: output.close()
    statistics.finalize(stats)
    return time_compression, stats
