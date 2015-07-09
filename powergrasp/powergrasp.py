# -*- coding: utf-8 -*-
"""
TOWRITE
"""
from __future__   import absolute_import, print_function
from builtins     import input
from future.utils import itervalues, iteritems
from collections  import defaultdict
from aspsolver    import ASPSolver
from commons      import basename
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





def compress(graph_data, extracting, preprocessing, ccfinding, bcfinding,
             postprocessing, remaining, output_file,
             statistics_filename='data/statistics.csv',
             output_format='bbl', lowerbound_cut_off=2,
             interactive=False, count_model=False,
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
            commons.FIRST_SOLUTION_NO_THREAD
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
    # save atoms as ASP-readable string
    all_edges   = atoms.to_str(graph_atoms, names='ccedge')
    first_blocks= atoms.to_str(graph_atoms, names='block')
    graph_atoms = atoms.to_str(graph_atoms, names=('ccedge', 'membercc'))
    del extractor
    # stats about compression
    statistics.add(stats, initial_edge_count=all_edges.count('ccedge'))
    # printings
    logger.debug('EXTRACTED: ' + graph_atoms + '\n')
    logger.debug('CCEDGES  : ' + all_edges + '\n')
    time_extract = time.time() - time_extract

    # Find connected components
    logger.info('#################')
    logger.info('####   CC    ####')
    logger.info('#################')
    for cc in atom_ccs:
        # contains interesting atoms and the non covered edges at last step
        result_atoms = tuple()
        remain_edges = None
        # main loop
        logger.info('#### CC: ' + str(cc) + ' ' + str(cc.__class__))
        k = 0
        previous_coverage = ''  # accumulation of covered/2
        previous_blocks   = first_blocks
        model = None
        lowerbound_value = (minimal_score + 1) if lowerbound_cut_off > 0 else 0
        # iteration
        while True:
            # STEP INITIALIZATION
            k += 1
            time_iteration = time.time()
            number_concept = 0  # cc exhausted if equals to 0 at the loop's end

            # FIND THE LOWER BOUND
            #  indicate that the preprocesser must found the max lowerbound
            if lowerbound_value > minimal_score:
                print('LOWER BOUND SEARCH PERFORMED')
                lowerbound_atom = 'lowerbound.'  # must be found
            else:
                lowerbound_atom = ''  # no search

            # PREPROCESSING
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
            logger.debug('PREPROCESSED: ' + preprocessed_graph_atoms)
            try:
                lowerbound_value = lowbound[0].args()[0]
            except IndexError:
                lowerbound_value = minimal_score
            if lowerbound_value.__class__ is gringo.InfType or lowerbound_value < minimal_score:
                lowerbound_value = minimal_score

            # FIND BEST CLIQUE
            model = solving.model_from(
                base_atoms=(preprocessed_graph_atoms
                            + previous_coverage + previous_blocks),
                aspfile=ccfinding,
                aspargs=[cc,k,lowerbound_value]
            )
            # model = None  # debug: no clique for a simpler world
            # treatment of the model
            if model is not None:
                # keep atoms that describes the maximal clique
                number_concept += 1
                logger.debug('CLIQUE OUTPUT: ' + atoms.to_str(model))
                logger.debug('CLIQUE OUTPUT: ' + str(atoms.count(model)))
                assert('score' in str(model))
                lowerbound_value = max(
                    lowerbound_value,
                    int(next(a for a in model if a.name() == 'score').args()[0]),
                )
                best_model = model
            else:
                logger.debug('CLIQUE SEARCH: no model found')
                best_model = None
            del model

            # FIND BEST BICLIQUE
            model = solving.model_from(
                base_atoms=(preprocessed_graph_atoms
                            + previous_coverage + previous_blocks),
                aspfile=bcfinding,
                aspargs=[cc,k,lowerbound_value]
            )
            # treatment of the model
            if model is None:
                logger.debug('BICLIQUE SEARCH: no model found')
            else:
                best_model = model
                number_concept += 1  # we find a concept
                # printings
                logger.debug('\tOUTPUT: ' + atoms.to_str(
                    model, separator='.\n\t'
                ))
                atom_counter = atoms.count(model)
                logger.debug('\tOUTPUT: ' + str(atom_counter))
                logger.debug('POWERNODES:\n\t' + atoms.prettified(
                    model,
                    names=('powernode', 'poweredge', 'score'),
                    joiner='\n\t',
                    sort=True
                ))
            del model

            if best_model is not None:
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
                    (a for a in best_model if a.name() in ('powernode', 'poweredge'))
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
                    remain_edges_count=len(remain_edges),
                )

            # stop cc compression if no model found
            if number_concept == 0:
                if count_model: # replace counter by the final information
                    print('\r', end='')
                    sys.stdout.flush()
                logger.info(str(k-1) + ' optimal model(s) found by bcfinder.')
                break
            # interactive mode
            if count_model and interactive:
                input(str(k)+'>Next ?')  # my name is spam
            elif interactive:
                input('Next ?')  # my name is spam
            elif count_model:
                print('\r' + str(k) + ' model'
                      + ('s' if k > 1 else '') + ' found',
                      end=''
                )
                sys.stdout.flush()





        #####################
        #### REMAIN DATA ####
        #####################
        # Creat solver and collect remaining edges
        # logger.debug("INPUT REMAIN: " + str(remain_edges) + str(inclusion_tree))

        # determine how many edges remains if no compression performed
        if remain_edges is None:  # no compression performed
            remain_edges = tuple(a+'' for a in all_edges.split('.') if cc in a)

        # Remain edges globally
        remain_edges_global += len(remain_edges) if remain_edges else 0
        statistics.add(stats, final_edges_count=remain_edges_global)

        # Remain edges in cc
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
        + "s (extraction in " + str(round(time_extract, 3))
        + ".\nSolver options: " + ' '.join(commons.ASP_OPTIONS)
        + ".\nNow, statistics on "
        + statistics.output(stats)
    )
    logger.info(final_results)
    output.write(converter.comment(final_results.split('\n')))

    output.close()
    statistics.finalize(stats)
    # return str(graph)




