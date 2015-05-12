# -*- coding: utf-8 -*-
"""
TOWRITE
"""
from __future__   import print_function, absolute_import
from builtins     import input
from future.utils import itervalues, iteritems
from collections  import defaultdict
from aspsolver    import ASPSolver
import commons
import atoms


logger = commons.logger()





def asprgc(iterations, graph, extract, findcc, update, remain,
           output_file, output_format, interactive=False):
    """Performs the graph compression with data found in graph file.

    Use ASP source code found in extract, findcc and update files
     for perform the computations.

    Output format must be valid. TOCOMPLETE.

    If interactive is True, an input will be expected
     from the user after each step.
    """
    # all atoms are contained as:
    #   atom.name:{atom.args}
    all_atoms = defaultdict(set)
    output = open(output_file, 'w')
    convert_output = atoms.converter_for(output_format)

    # Extract graph data
    logger.info('#################')
    logger.info('#### EXTRACT ####')
    logger.info('#################')
    extractor = ASPSolver().use(graph, program_name='base').use(extract)
    extracted_atoms = extractor.first_solution().atoms()
    # graph data is an ASP code that describes graph and connected components.
    atoms.update(all_atoms, extracted_atoms)
    # logger.debug('graph:\n' + str(all_atoms))
    logger.debug('graph:\n\t' + atoms.prettified(all_atoms, joiner='\n\t'))

    # get all CC, one by one
    atom_ccs = (cc.args()[0]
                for cc in extracted_atoms
                if cc.name() == 'cc'
               )

    # Find connected components
    logger.info('\n\t' + atoms.prettified(all_atoms, joiner='\n\t'))
    logger.info('#################')
    logger.info('####   CC    ####')
    logger.info('#################')
    model_count = 0
    # for cc in :
    for cc in atom_ccs:
        print('#### CC:', str(cc), cc.__class__)

        k = 0
        while True:
            k += 1

            print("\n#### FIND BEST CONCEPT", k, '####')
            input_atoms_names = ('ccedge', 'covered', 'membercc')
            input_atoms = atoms.from_dict(
                all_atoms,
                input_atoms_names,
                '.\n\t'
            )
            print('INPUT:\n\t', input_atoms,
                  atoms.count(all_atoms, input_atoms_names),
                  sep=''
            )

            bcfinder = ASPSolver()
            bcfinder.read(input_atoms)
            bcfinder.use(findcc, [cc, k])

            model = bcfinder.first_solution()
            if model is None:
                print('No model found by bcfinder')
                # print('DEBUG_NOMODEL:\n', atoms.from_dict(
                    # all_atoms, ('cc', 'coverededge', 'ccedge', 'membercc', 'connectedpath'), '.\n'
                # ), '====\n', sep='')
                break
            atoms.update(all_atoms, model.atoms())
            print('OUTPUT:\n\t',
                  '.\n\t'.join(str(model).split(' ')), '.\n',
                  atoms.count(atoms.update(defaultdict(set), model.atoms())),
                  sep=''
            )

            print("\n#### UPDATE", k, '####')
            input_atoms_names = ('concept', 'covered', 'bcovered')
            input_atoms = atoms.from_dict(
                all_atoms,
                input_atoms_names,
                '.\n\t'
            )
            print('INPUT:\n\t', input_atoms,
                  atoms.count(all_atoms, input_atoms_names),
                  sep=''
            )

            # Update edges
            updater = ASPSolver()
            updater.read(input_atoms)
            updater.use(update, [cc, k])

            updater_atoms = updater.first_solution().atoms()
            atoms.update(all_atoms, updater_atoms)
            model_count += 1

            logger.info('COVERING:\n\t' + atoms.prettified(
                all_atoms,
                names=('bcovered',),
                joiner='\n\t'
            ))
            logger.info('POWERNODES:\n\t' + atoms.prettified(
                all_atoms,
                names=('powernode', 'score'),
                joiner='\n\t',
                sort=True
            ))
            nnf = convert_output(updater_atoms)
            logger.debug(output_format.upper() + ':\n' + nnf)
            output.write(nnf)
            if interactive: input('Next ?')  # my name is spam


    logger.info('#################')
    logger.info('## REMAIN DATA ##')
    logger.info('#################')
    input_atoms_names = ('ccedge', 'covered')
    input_atoms = atoms.from_dict(
        all_atoms,
        input_atoms_names,
        '.\n\t'
    )

    print(input_atoms, atoms.count(all_atoms, input_atoms_names))
    remain_collector = ASPSolver().read(input_atoms).use(remain)
    remain_edges = remain_collector.first_solution()
    if remain_edges is None:
        logger.info('No remain edge')
    else:
        # output.write(convert_output(remain_edges))
        logger.info(remain_edges)


    # deinit and print all results
    output.close()
    logger.info('#################')
    logger.info('#### RESULTS ####')
    logger.info('#################')
    results_names = ('powernode')
    logger.info('\n\t' + atoms.prettified(all_atoms,
                                          results_only=True,
                                          joiner='\n\t',
                                          sort=True)
    )
    for to_find in ('powernode', 'edgecover'):
        logger.info(to_find + ' found: \t' + str(to_find in str(all_atoms)))


    # return str(graph)



