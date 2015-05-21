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
    extractor = ASPSolver().use(graph, program_name='base').use(extract)
    graph_atoms = extractor.first_solution().atoms()
    # get all CC, one by one
    atom_ccs = (cc.args()[0]  # args is a list of only one element (cc/1)
                for cc in graph_atoms
                if cc.name() == 'cc'
               )
    # save atoms as ASP-readable string
    graph_atoms = atoms.to_str(graph_atoms)
    # printings
    logger.debug('EXTRACTED: ' + graph_atoms + '\n')

    # Find connected components
    logger.info('#################')
    logger.info('####   CC    ####')
    logger.info('#################')
    for cc in atom_ccs:
        # Solver creation
        logger.info('#### CC: ' + str(cc) + ' ' + str(cc.__class__))
        solver = ASPSolver(commons.ASP_OPTIONS)
        solver.read(graph_atoms)       # read all basical data
        solver._prg.load(ccfinding)

        # main loop
        k = 0
        while True:
            # FIND BEST CONCEPT
            # release previous k, ground program and assign new k
            solver.assign_external(name='step', args=[k], truth=False)
            k += 1
            solver.ground(basename(ccfinding), [cc,k])
            solver.assign_external(name='step', args=[k], truth=True)

            # solving
            model = solver.first_solution()
            if model is None:
                print('No model found by bcfinder')
                break
            logger.info('\tOUTPUT: ' + str(atoms.to_str(model.atoms(), separator='.\n\t')))
            logger.info('\tOUTPUT: ' + str(atoms.count(model.atoms())))

            logger.info('POWERNODES:\n\t' + atoms.prettified(
                model.atoms(),
                names=('powernode', 'score'),
                joiner='\n\t',
                sort=True
            ))

            # give new powernodes to converter
            converter.convert(model.atoms(), separator=', ')

            if interactive:
                input('Next ?')  # my name is spam

        # release cc value
        solver.release_external(fun=cc)



    logger.info('#################')
    logger.info('## REMAIN DATA ##')
    logger.info('#################')
    # get atoms necessary for remaining edges solving
    input_atoms_names = ('ccedge', 'covered')
    input_atoms = [a for a in model.atoms() if a.name() in input_atoms_names]

    # Creat solver and collect remaining edges
    remain_collector = ASPSolver().use(remain)
    remain_collector.read(atoms.to_str(input_atoms))
    remain_edges = remain_collector.first_solution()

    # Output
    if remain_edges is None or len(remain_edges.atoms()) == 0:
        logger.info('No remaining edge')
    else:
        converter.convert(remain_edges.atoms())



    logger.info('#################')
    logger.info('#### RESULTS ####')
    logger.info('#################')
    # write output in file
    output.write(converter.finalized())
    output.close()
    logger.debug('FINAL DATA SAVED IN FILE ' + output_file + '.' + output_format)

    # print results
    results_names = ('powernode')
    logger.info('\n\t' + atoms.prettified(all_atoms,
                                          results_only=True,
                                          joiner='\n\t',
                                          sort=True)
    )
    for to_find in ('powernode', 'edgecover'):
        logger.info(to_find + ' found: \t' + str(to_find in str(all_atoms)))


    # return str(graph)



