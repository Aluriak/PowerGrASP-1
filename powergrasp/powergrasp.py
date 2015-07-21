# -*- coding: utf-8 -*-
"""
TOWRITE
"""
from __future__   import absolute_import, print_function
from builtins     import input
from future.utils import itervalues, iteritems
from collections  import defaultdict
from aspsolver    import ASPSolver
from commons      import basename, FILE_OUTPUT
from commons      import ASP_SRC_EXTRACT, ASP_SRC_PREPRO , ASP_SRC_FINDCC
from commons      import ASP_SRC_FINDBC , ASP_SRC_POSTPRO, ASP_SRC_POSTPRO
import statistics
import itertools
import converter  as converter_module
import solving
import commons
import gringo
import time
import atoms
import sys


logger = commons.logger()






def compress(graph_data, extracting=ASP_SRC_EXTRACT,
             preprocessing=ASP_SRC_PREPRO, ccfinding=ASP_SRC_FINDCC,
             bcfinding=ASP_SRC_FINDBC, postprocessing=ASP_SRC_POSTPRO,
             output_file=FILE_OUTPUT, statistics_filename='data/statistics.csv',
             output_format='bbl', lowerbound_cut_off=2,
             interactive=False, count_model=False, count_cc=False,
             no_threading=True):
    """Performs the graph compression with data found in graph file.

    Use ASP source code found in extract, findcc and update files
     for perform the computations.

    Output format must be valid.

    If interactive is True, an input will be expected
     from the user after each step.

    Notes about the maximal lowerbound optimization:
      In a linear time, it is possible to compute the
       maximal degree in the non covered graph.
      This value correspond to the minimal best concept score.
      The cut-off value is here for allow client code to control
       this optimization, by specify the value that disable this optimization
       when the lowerbound reachs it.
    """
    if not graph_data: return  # simple protection

    # initialization of first solution getter
    if no_threading:
        solving.first_solution_function(
            solving.FIRST_SOLUTION_NO_THREAD
        )
    # Initialize descriptors
    output    = open(output_file + '.' + output_format, 'w')
    converter = converter_module.output_converter_for(output_format)
    model     = None
    stats     = statistics.container(graph_data.rstrip('.lp'),
                                     statistics_filename)
    output.write(converter.header())
    time_extract = time.time()
    time_compression = time.time()
    minimal_score = 2
    remain_edges_global = 0  # counter of remain_edges in all graph

    # Extract graph data
    logger.info('#################')
    logger.info('#### EXTRACT ####')
    logger.info('#################')
    # creat a solver that get all information about the graph
    extractor = gringo.Control()
    extractor.load(graph_data)
    extractor.ground([('base', [])])
    extractor.load(extracting)
    extractor.ground([(basename(extracting), [])])

    graph_atoms = solving.first_solution(extractor)
    assert(graph_atoms is not None)

    # get all CC, one by one
    atom_ccs = (cc.args()[0]  # args is a list of only one element (cc/1)
                for cc in graph_atoms
                if cc.name() == 'cc'
               )
    if count_cc:
        atom_ccs = tuple(atom_ccs)
        atom_ccs_count = len(atom_ccs)
    atom_ccs = enumerate(atom_ccs)
    # save atoms as ASP-readable string
    all_edges   = atoms.to_str(graph_atoms, names='ccedge')
    first_blocks= atoms.to_str(graph_atoms, names='block')
    graph_atoms = atoms.to_str(graph_atoms, names=('ccedge', 'membercc'))
    del extractor
    # stats about compression
    remain_edges_global = all_edges.count('ccedge')
    statistics.add(stats, initial_edge_count=remain_edges_global)
    # printings
    logger.debug('EXTRACTED: ' + graph_atoms + '\n')
    logger.debug('CCEDGES  : ' + all_edges + '\n')
    time_extract = time.time() - time_extract

    # Find connected components
    logger.info('#################')
    logger.info('####   CC    ####')
    logger.info('#################')
    for cc_nb, cc in atom_ccs:
        assert(isinstance(cc, str) or isinstance(cc, gringo.Fun))
        # contains interesting atoms and the non covered edges at last step
        result_atoms = tuple()
        remain_edges = None
        previous_coverage = ''  # accumulation of covered/2
        previous_blocks   = first_blocks
        # main loop
        logger.info('#### CC ' + str(cc_nb+1)
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
                print('LOWER BOUND SET TO ' + str(lowerbound_value))
                #  indicate that the preprocesser must found the max lowerbound
                lowerbound_atom = 'lowerbound.'
            else:
                lowerbound_atom = ''  # no max lowbound search in preprocessing

            #########################
            logger.debug('PREPROCESSING')
            #########################
            model = solving.model_from(
                base_atoms=(graph_atoms + previous_coverage
                            + previous_blocks + lowerbound_atom),
                aspfile=preprocessing,
                aspargs=[cc]
            )
            assert(model is not None)
            # treatment of the model
            lowbound = tuple(a for a in model if a.name() == 'maxlowerbound')
            preprocessed_graph_atoms = atoms.to_str(
                atom for atom in model
                if atom.name() != 'maxlowerbound'
            )
            try:
                lowerbound_value = lowbound[0].args()[0]
            except IndexError:
                lowerbound_value = minimal_score
            if lowerbound_value.__class__ is gringo.InfType or lowerbound_value < minimal_score:
                lowerbound_value = minimal_score

            #########################
            logger.debug('FIND BEST CLIQUE ' + printable_bounds())
            #########################
            model = solving.model_from(
                base_atoms=(preprocessed_graph_atoms
                            + previous_coverage + previous_blocks),
                aspfile=(ccfinding, postprocessing),
                aspargs=([cc,k],
                         [cc,k,lowerbound_value,last_score]),
            )
            # treatment of the model
            if model is None:
                logger.debug('CLIQUE SEARCH: no model found')
            else:
                best_model = model
                assert('score' in str(model))
                score = next(a for a in model if a.name() == 'score').args()[0]
                assert(isinstance(score, int))
                lowerbound_value = max(
                    lowerbound_value,
                    score,
                )
                atom_counter = atoms.count(model)

            #########################
            logger.debug('FIND BEST BICLIQUE' + printable_bounds())
            #########################
            model = solving.model_from(
                base_atoms=(preprocessed_graph_atoms
                            + previous_coverage + previous_blocks),
                aspfile=(bcfinding, postprocessing),
                aspargs=([cc,k],
                         [cc,k,lowerbound_value,last_score]),
            )
            # treatment of the model
            if model is None:
                logger.debug('BICLIQUE SEARCH: no model found')
            else:
                best_model = model
                # printings
                logger.debug('\tOUTPUT: ' + atoms.to_str(
                    model, separator='.\n\t'
                ))
                score = next(a for a in model if a.name() == 'score').args()[0]
                assert(isinstance(score, int))
                atom_counter = atoms.count(model)

            #########################
            logger.debug('BEST MODEL TREATMENT')
            #########################
            # stop cc compression if no model found
            if best_model is None:
                if count_model: # replace counter by the final information
                    print('\r', end='')
                    sys.stdout.flush()
                logger.info(str(k-1) + ' optimal model' + ('s' if k-1>1 else '')
                            + ' found by best concept search.')
                break
            else:  # at least one model was found, and the best is best_model
                # debug printing
                logger.debug('POWERNODES:\n\t' + atoms.prettified(
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
                converter.convert((a for a in best_model if a.name() in (
                    'powernode', 'clique', 'poweredge'
                )))

                # save interesting atoms
                result_atoms = itertools.chain(
                    result_atoms,
                    (a for a in best_model
                     if a.name() in ('powernode', 'poweredge'))
                )

                # save the number of generated powernodes and poweredges
                new_powernode_count = next(
                    a for a in best_model if a.name() == 'powernode_count'
                ).args()[0]
                new_poweredge_count = atom_counter['poweredge']
                remain_edges = tuple(a for a in best_model if a.name() == 'edge')

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
            logger.info('No remaining edge')
        else:
            logger.info(str(len(remain_edges)) + ' remaining edge(s)')
            converter.convert(remain_edges)



        ########################
        # WRITE OUTPUT IN FILE #
        ########################
        output.write(converter.finalized())
        converter.release_memory()
        logger.debug('FINAL DATA SAVED IN FILE ' + output_file + '.' + output_format)

        # print results
        # results_names = ('powernode',)
        logger.debug('\n\t' + atoms.prettified(
            result_atoms,
            joiner='\n\t',
            sort=True
        ))

    logger.info('#################')
    logger.info('#### RESULTS ####')
    logger.info('#################')
    # compute a human readable final results string,
    # and put it in the output and in level info.
    time_compression = time.time() - time_compression
    final_results = (
        "All cc have been performed in " + str(round(time_compression, 3))
        + "s (extraction in " + str(round(time_extract, 3)) + ')'
        + ".\nSolver options: " + ' '.join(commons.ASP_OPTIONS)
        + ".\nNow, statistics on "
        + statistics.output(stats)
    )
    logger.info(final_results)
    output.write(converter.comment(final_results.split('\n')))

    output.close()
    statistics.finalize(stats)




