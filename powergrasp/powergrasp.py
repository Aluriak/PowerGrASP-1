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


logger = commons.logger()





def compress(iterations, graph_data, extracting, ccfinding, updating, remaining,
           output_file, output_format, heuristic, interactive=False):
    """Performs the graph compression with data found in graph file.

    Use ASP source code found in extract, findcc and update files
     for perform the computations.

    Output format must be valid. TOCOMPLETE.

    If interactive is True, an input will be expected
     from the user after each step.
    """
    # Initialize descriptors
    output    = open(output_file + '.' + output_format, 'w')
    converter = converter_module.converter_for(output_format)
    model     = None
    stats     = statistics.container(graph_data.rstrip('.lp'))
    time_cc   = None
    time_extract = time.time()

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

    model = commons.first_solution(extractor)
    assert(model is not None)
    graph_atoms = model.atoms()
    # get all CC, one by one
    atom_ccs = (cc.args()[0]  # args is a list of only one element (cc/1)
                for cc in graph_atoms
                if cc.name() == 'cc'
               )
    # save atoms as ASP-readable string
    all_edges   = atoms.to_str(graph_atoms, names='ccedge')
    graph_atoms = atoms.to_str(graph_atoms)
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
        previous_coverage = ''
        model = None
        while True:
            k += 1
            # FIND BEST CONCEPT
            # create new solver and ground all data
            logger.debug('\tINPUT: ' + previous_coverage)
            # Solver creation
            solver = gringo.Control(commons.ASP_OPTIONS + [' --configuration='+heuristic])
            solver.add('base', [], graph_atoms + previous_coverage)
            solver.ground([('base', [])])
            solver.load(ccfinding)
            solver.ground([(basename(ccfinding), [cc,k])])

            # solving
            model = commons.first_solution(solver)
            # treatment of the model
            if model is None:
                logger.info(str(k) + ' optimal model(s) found by bcfinder.')
                break
            logger.debug('\tOUTPUT: ' + atoms.to_str(
                model.atoms(), separator='.\n\t'
            ))
            logger.debug('\tOUTPUT: ' + str(atoms.count(model.atoms())))

            logger.debug('POWERNODES:\n\t' + atoms.prettified(
                model.atoms(),
                names=('powernode', 'poweredge', 'score'),
                joiner='\n\t',
                sort=True
            ))
            # atoms to be given to the next step
            previous_coverage += atoms.to_str(
                model.atoms(), names=('covered', 'block', 'include_block')
            )

            # give new powernodes to converter
            converter.convert((a for a in model.atoms() if a.name() in (
                'powernode', 'clique', 'poweredge'
            )))
            # save interesting atoms
            result_atoms = itertools.chain(
                result_atoms,
                (a for a in model.atoms() if a.name() in ('powernode', 'poweredge'))
            )
            new_powernode_count = 2
            new_poweredge_count = len(tuple(
                None for a in model.atoms() if a.name() == 'poweredge'
            ))
            statistics.add(stats,
                           final_poweredge_count=new_poweredge_count,
                           final_powernode_count=new_powernode_count,
                          )
            # statistics.add(stats, final_powernode_count=new_powernode_count)
            remain_edges = tuple(a for a in model.atoms() if a.name() == 'edge')
            # interactive mode
            if interactive:
                input('Next ?')  # my name is spam




        logger.info('#################')
        logger.info('## REMAIN DATA ##')
        logger.info('#################')
        # Creat solver and collect remaining edges
        # logger.debug("INPUT REMAIN: " + str(remain_edges) + str(inclusion_tree))

        # Output
        if remain_edges is None or len(remain_edges) == 0:
            logger.info('No remaining edge')
        else:
            logger.info(str(len(remain_edges)) + ' remaining edge(s)')
            statistics.add(stats, final_edge_count=len(remain_edges))
            converter.convert(remain_edges)



        logger.info('#################')
        logger.info('#### RESULTS ####')
        logger.info('#################')
        # write output in file
        output.write(converter.finalized())
        logger.debug('FINAL DATA SAVED IN FILE ' + output_file + '.' + output_format)

        # print results
        # results_names = ('powernode',)
        logger.debug('\n\t' + atoms.prettified(
            result_atoms,
            joiner='\n\t',
            sort=True
        ))

    time_cc = time.time() - time_cc
    logger.info("All cc have been performed in " + str(round(time_cc, 3))
                + "s (extraction in " + str(round(time_extract, 3))
                + "). Now, statistics:\n"
    )
    print(statistics.output(stats))

    output.close()
    # return str(graph)



