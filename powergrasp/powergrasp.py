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
import commons
import gringo
import time
import atoms
import sys


logger = commons.logger()





def compress(graph_data, extracting, lowerbounding, ccfinding, remaining,
             output_file, output_format, heuristic, lowerbound_cut_off=2,
             interactive=False, count_model=False, threading=True,
             aggressive=False):
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
    commons.first_solution_function(
        commons.FIRST_SOLUTION_THREAD if threading
        else commons.FIRST_SOLUTION_NO_THREAD
    )
    # Initialize descriptors
    output    = open(output_file + '.' + output_format, 'w')
    converter = converter_module.converter_for(output_format)
    model     = None
    stats     = statistics.container(graph_data.rstrip('.lp'))
    time_cc   = None
    time_extract = time.time()
    minimal_score = 1 if aggressive else 2

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

    graph_atoms = commons.first_solution(extractor)
    assert(graph_atoms is not None)
    # graph_atoms = sorted(tuple(str(_) for _ in graph_atoms))
    # with open('debug/opt/data_YAL029C_input.lp', 'w') as fd:
        # fd.write('\n'.join(graph_atoms))
    # exit()

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
    statistics.add(stats, initial_edge_count=all_edges.count('.'))
    # printings
    logger.debug('EXTRACTED: ' + graph_atoms + '\n')
    logger.debug('CCEDGES  : ' + all_edges + '\n')
    time_extract = time.time() - time_extract

    # Find connected components
    logger.info('#################')
    logger.info('####   CC    ####')
    logger.info('#################')
    time_cc = time.time()
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
            k += 1

            # FIND THE LOWER BOUND
            if lowerbound_value > minimal_score:
                print('LOWER BOUND SEARCH PERFORMED')
                # solver creation
                lbound_finder = gringo.Control(commons.ASP_OPTIONS + ['--configuration='+heuristic])
                lbound_finder.add('base', [], graph_atoms + previous_blocks + previous_coverage)
                lbound_finder.ground([('base', [])])
                lbound_finder.load(lowerbounding)
                lbound_finder.ground([(basename(lowerbounding), [cc])])
                # solving
                model = commons.first_solution(lbound_finder)
                assert(model is not None)
                model = [a for a in model if a.name() == 'maxlowerbound']
                try:
                    lowerbound_value = model[0].args()[0]
                except IndexError:
                    lowerbound_value = minimal_score
                del lbound_finder
                if lowerbound_value.__class__ is gringo.InfType or lowerbound_value < minimal_score:
                    lowerbound_value = minimal_score
            else:
                lowerbound_value = minimal_score

            # FIND BEST CONCEPT
            # create new solver and ground all data
            logger.debug('\tINPUT: ' + previous_coverage + previous_blocks)
            # Solver creation
            solver = gringo.Control(commons.ASP_OPTIONS + ['--configuration='+heuristic])
            solver.add('base', [], graph_atoms + previous_coverage + previous_blocks)
            solver.ground([('base', [])])
            solver.load(ccfinding)
            solver.ground([(basename(ccfinding), [cc,k,lowerbound_value])])

            # solving
            model = commons.first_solution(solver)
            # treatment of the model
            if model is None:
                if count_model: # replace counter by the final information
                    print('\r', end='')
                    sys.stdout.flush()
                logger.info(str(k) + ' optimal model(s) found by bcfinder.')
                break

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

            # atoms to be given to the next step
            previous_coverage += atoms.to_str(
                model, names=('covered',)
            )
            previous_blocks = atoms.to_str(
                model, names=('block', 'include_block')
            )

            # give new powernodes to converter
            converter.convert((a for a in model if a.name() in (
                'powernode', 'clique', 'poweredge'
            )))

            # save interesting atoms
            result_atoms = itertools.chain(
                result_atoms,
                (a for a in model if a.name() in ('powernode', 'poweredge'))
            )

            # save the number of generated powernodes and poweredges
            new_powernode_count = next(
                a for a in model if a.name() == 'powernode_count'
            ).args()[0]
            new_poweredge_count = atom_counter['poweredge']
            statistics.add(stats,
                           final_poweredge_count=new_poweredge_count,
                           final_powernode_count=new_powernode_count,
                          )
            # statistics.add(stats, final_powernode_count=new_powernode_count)
            remain_edges = tuple(a for a in model if a.name() == 'edge')

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





        logger.info('#################')
        logger.info('## REMAIN DATA ##')
        logger.info('#################')
        # Creat solver and collect remaining edges
        # logger.debug("INPUT REMAIN: " + str(remain_edges) + str(inclusion_tree))

        # Output
        if remain_edges is None or len(remain_edges) == 0:
            logger.info('No remaining edge')
            statistics.add(stats, final_edge_count=0)
        else:
            logger.info(str(len(remain_edges)) + ' remaining edge(s)')
            statistics.add(stats, final_edge_count=len(remain_edges))
            converter.convert(remain_edges)



        logger.info('#################')
        logger.info('#### RESULTS ####')
        logger.info('#################')
        # write output in file
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

    # compute a human readable final results string,
    # and put it in the output and in level info.
    time_cc = time.time() - time_cc
    final_results = (
        "All cc have been performed in " + str(round(time_cc, 3))
        + "s (extraction in " + str(round(time_extract, 3))
        + ") with heuristic " + heuristic + ".\nSolver options: "
        + ' '.join(commons.ASP_OPTIONS)
        + ".\nNow, statistics on "
        + statistics.output(stats)
    )
    logger.info(final_results)
    output.write(converter.comment(final_results.split('\n')))

    output.close()
    # return str(graph)



