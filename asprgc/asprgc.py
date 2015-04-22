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
    extractor = ASPSolver().use(graph).use(extract)
    extracted_atoms = extractor.first_solution().atoms()
    # graph data is an ASP code that describes graph and connected components.
    atoms.update(all_atoms, extracted_atoms)
    # logger.debug('graph:\n' + str(all_atoms))
    logger.debug('graph:\n\t' + atoms.from_dict(all_atoms, ('node', 'inter', 'cc', 'ccedge'), '.\n\t'))

    # graph data:
    atom_ccs  = (a.args() 
                 for a in extracted_atoms 
                 if a.name() == 'cc'
                )

    # Find connected components
    logger.info('\n\t' + atoms.prettified(all_atoms, joiner='\n\t'))
    logger.info('#################')
    logger.info('####   CC    ####')
    logger.info('#################')
    model_count = 1
    # for _, cc in atom_ccs:
    for cc in atom_ccs:
        # Collect edges in the CC
        ccfinder = ASPSolver()
        ccfinder.read(atoms.from_dict(
            all_atoms, ('cc', 'ccedge', 'membercc', 'connectedpath'), '.'
        ))
        ccfinder.use(findcc, cc)
        ccfinder_atoms = ccfinder.first_solution().atoms()
        atoms.update(all_atoms, ccfinder_atoms)

        # Collect cliques
        clfinder = ASPSolver()
        clfinder.read(atoms.from_dict(
            all_atoms, ('node', 'oedge', 'inter', 'membercc'), '.'
        ))
        clfinder.use(findcl, cc)
        findcl_atoms = clfinder.first_solution().atoms()
        atoms.update(all_atoms, findcl_atoms)
        model_count += 1 

        # Perform first model
        firstmodeler = ASPSolver().read(atoms.from_dict(
            all_atoms, ('concept', 'clique', 'edgecoverc', 'edgecoverb'), '.'
        )).use(firstmodel, cc + [model_count])
        firstmodel_atoms = firstmodeler.first_solution().atoms()
        atoms.update(all_atoms, firstmodel_atoms)
        model_count += 1 

        # Creat solvers
        nextmodeler = ASPSolver().read(atoms.from_dict(
            all_atoms, ('concept', 'clique', 'edgecover'), '.'
        )).use(nextmodel, cc)
        updater = ASPSolver().read(atoms.from_dict(
            all_atoms, ('concept', 'clique', 'edgecover', 'node', 'membercc'), '.'
        )).use(update, cc)

        # updater.assign_external    ('step'     , [-1], True)
        updater.assign_external    ('next_step', [ 1], True)
        # nextmodeler.assign_external('step'     , [-1], True)
        k = 0
        while iterations is None or k < iterations:
            k += 1
            # Perform update
            updater.release_external('step', (k-1,)) # doesn't exist in the first loop
            updater.assign_external ('step', (k  ,), True)
            updater.release_external('next_step', (k  ,)) # doesn't exist in the first loop
            updater.assign_external ('next_step', (k+1,), True)
            model = updater.first_solution()
            if model is not None:
                atoms.update(all_atoms, model.atoms())
            else: # model is None ; no solution
                print(' BROKE !')
                break
            model_count += 1 

            # Compiling concepts and cliques
            nextmodeler.release_external('step', (k-1,))
            nextmodeler.assign_external ('step', (k  ,), True)
            model = nextmodeler.first_solution()
            if model is not None:
                atoms.update(all_atoms, model.atoms())
            else: # model is None ; no solution
                print(' BROKE !')
                break
            model_count += 1 
            print('\r\t' + str(k), end='')
            sys.stdout.flush()

        # print all
        print('')
        logger.info('#################')
        logger.info('#### RESULTS ####')
        logger.info('#################')
        logger.info('\n\t' + atoms.prettified(all_atoms, joiner='\n\t'))
        # logger.info('\n\t' + atoms.prettified(all_atoms, joiner='\n\t', sizes=(4,5), results_only=True))
        

    
    # return str(graph)




