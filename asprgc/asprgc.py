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
import converter  as converter_module
import commons
import gringo
import atoms


logger = commons.logger()





def asprgc(iterations, graph_data, extracting, ccfinding, updating, remaining,
           output_file, output_format, interactive=False):
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
    # printings
    logger.debug('EXTRACTED: ' + graph_atoms + '\n')
    logger.debug('CCEDGES  : ' + all_edges + '\n')

    # Find connected components
    logger.info('#################')
    logger.info('####   CC    ####')
    logger.info('#################')
    for cc in atom_ccs:
        # Solver creation
        logger.info('#### CC: ' + str(cc) + ' ' + str(cc.__class__))

        # main loop
        k = 0
        previous_coverage = ''
        model = None
        while True:
            k += 1
            # FIND BEST CONCEPT
            # create new solver and ground all data
            logger.info('\tINPUT: ' + '.\n\t'.join(_ for _ in previous_coverage.split('.') if '(2,' in _))
            logger.info('\tINPUT: ' + '.\n\t'.join(_ for _ in previous_coverage.split('.') if 'ed(' in _))
            logger.info('\tINPUT: ' + previous_coverage)
            solver = gringo.Control(commons.ASP_OPTIONS)
            solver.add('base', [], graph_atoms + previous_coverage)
            solver.ground([('base', [])])
            solver.load(ccfinding)
            solver.ground([(basename(ccfinding), [cc,k])])

            # solving
            model = commons.first_solution(solver)
            # treatment of the model
            if model is None:
                print('No model found by bcfinder')
                break
            logger.info('\tOUTPUT: ' + atoms.to_str(
                model.atoms(), separator='.\n\t'
            ))
            logger.info('\tOUTPUT: ' + str(atoms.count(model.atoms())))

            logger.info('POWERNODES:\n\t' + atoms.prettified(
                model.atoms(),
                names=('powernode', 'score'),
                joiner='\n\t',
                sort=True
            ))
            previous_coverage += atoms.to_str(model.atoms(), names=('covered', 'block'))

            # give new powernodes to converter
            converter.convert(model.atoms(), separator=', ')

            if interactive:
                input('Next ?')  # my name is spam




        logger.info('#################')
        logger.info('## REMAIN DATA ##')
        logger.info('#################')
        # Creat solver and collect remaining edges
        # logger.debug("INPUT REMAIN: " + all_edges + previous_coverage)
        remain_collector = gringo.Control()
        remain_collector.load(remaining)
        remain_collector.add('base', [], all_edges + previous_coverage)
        remain_collector.ground([
            (basename(remaining), []),
            ('base', []),
        ])
        remain_edges = commons.first_solution(remain_collector)
        # logger.debug("OUTPUT REMAIN: " + str(remain_edges))

        # Output
        if remain_edges is None or len(remain_edges.atoms()) == 0:
            logger.info('No remaining edge')
        else:
            logger.info(str(len(remain_edges.atoms())) + ' remaining edge(s)')
            converter.convert(remain_edges.atoms())



        logger.info('#################')
        logger.info('#### RESULTS ####')
        logger.info('#################')
        # write output in file
        output.write(converter.finalized())
        output.close()
        logger.debug('FINAL DATA SAVED IN FILE ' + output_file + '.' + output_format)

        # print results
        # results_names = ('powernode',)
        # logger.info('\n\t' + atoms.prettified(all_atoms,
                                              # results_only=True,
                                              # joiner='\n\t',
                                              # sort=True)
        # )
        # for to_find in ('powernode', 'edgecover'):
            # logger.info(to_find + ' found: \t' + str(to_find in str(all_atoms)))

    logger.info("All cc has been performed")

    # return str(graph)



