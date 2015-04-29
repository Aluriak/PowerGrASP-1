# -*- coding: utf-8 -*-
"""
TOWRITE
"""
from __future__   import print_function, absolute_import
from future.utils import itervalues, iteritems
from collections  import defaultdict
from aspsolver    import ASPSolver
from commons      import RESULTS_PREDICATS
import itertools
import commons
import atoms
import sys # flush


logger = commons.logger()





def asprgc(iterations, graph, extract, findcc, findcl, firstmodel, update, nextmodel):
    # all atoms are contained here
    #   atom.name:{atom.args}
    all_atoms = defaultdict(set)

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
    atom_ccs = ([cc.args()[0]]
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
        print('CC:', str(cc[0]), cc[0].__class__)
        # Collect edges in the CC
        ccfinder = ASPSolver()
        # print(atoms.from_dict(
            # all_atoms, ('cc', 'ccedge', 'membercc', 'connectedpath')
        # ))
        # exit(0)
        ccfinder.read(atoms.from_dict(
            all_atoms, ('cc', 'ccedge', 'membercc', 'connectedpath')
        ))
        ccfinder.use(findcc, cc)
        model = ccfinder.first_solution()
        if model is None:
            print('No model found by ccfinder')
            print('====\n', 'DEBUG_NOMODEL:\n', atoms.from_dict(
                all_atoms, ('cc', 'nonsingletoncc', 'ccedge', 'membercc', 'connectedpath'), '.\n'
            ), '====\n', sep='')
            continue
        atoms.update(all_atoms, model.atoms())
        print('DDEBUG:\n', model, '\n', atoms.from_dict(
            all_atoms, ('cc', 'nonsingletoncc', 'concept')
        ))

        # Collect cliques
        clfinder = ASPSolver()
        clfinder.read(atoms.from_dict(
            all_atoms, ('node', 'oedge', 'inter', 'membercc')
        ))
        clfinder.use(findcl, cc)
        findcl_atoms = clfinder.first_solution().atoms()
        atoms.update(all_atoms, findcl_atoms)

        # Perform first model
        firstmodeler = ASPSolver().read(atoms.from_dict(
            all_atoms, ('concept', 'clique', 'edgecoverc', 'edgecoverb')
        )).use(firstmodel, cc + [model_count])
        firstmodel_atoms = firstmodeler.first_solution().atoms()
        atoms.update(all_atoms, firstmodel_atoms)
        model_count += 1 

        k = 0
        while iterations is None or k < iterations:
            k += 1
            print('\tUPDATE', k)
            # Perform update
            updater = ASPSolver().read(atoms.from_dict(
                all_atoms, ('concept', 'clique', 'edgecover', 'node', 'membercc')
            )).use(update, cc + [k, k+1])
            model = updater.first_solution()
            print('UPDATE:', model.atoms() if model is not None else None)
            if model is not None:
                atoms.update(all_atoms, model.atoms())
            else: # model is None ; no solution
                print(' ITERATION FINISHED !')
                break
            model_count += 1


            # Compiling concepts and cliques
            nextmodeler = ASPSolver().read(atoms.from_dict(
                all_atoms, ('concept', 'clique', 'edgecover', 'node', 'membercc')
            )).use(nextmodel, cc + [model_count])
            model = nextmodeler.first_solution()
            print('NEXT_MODEL:', model.atoms() if model is not None else None)
            if model is not None:
                atoms.update(all_atoms, model.atoms())
            else: # model is None ; no solution
                print(' ITERATION FINISHED !')
                break

            model_count += 1

        # print all
        logger.info('#################')
        logger.info('#### RESULTS ####')
        logger.info('#################')
        logger.info('\n\t' + atoms.prettified(all_atoms,
                                              names=('id', 'concept', 'step',
                                                     'clique', 'edgecover', 'coverededge',
                                                     'bestedge', 'tobeupdated',
                                                     'cpowernode', 'bpowernode',
                                                     'powernode', 'notbestnodeb',
                                                     'bestnodeb', 'splitcliqueb',
                                                     'admcliqueb', 'bestnodec', 'splitcliquec',
                                                    ), joiner='\n\t'))
        for to_find in ('id', 'powernode', 'edgecover'):
            logger.info(to_find + ' found: \t' + str(to_find in str(all_atoms)))
        # logger.info('\n\t' + atoms.prettified(all_atoms, joiner='\n\t', sizes=(4,5), results_only=True))



    # return str(graph)




