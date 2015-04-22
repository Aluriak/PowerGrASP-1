# -*- coding: utf-8 -*-
"""
TOWRITE
"""
from __future__   import print_function, absolute_import
from future.utils import itervalues, iteritems
from collections  import defaultdict
from aspsolver    import ASPSolver
from commons      import ITERATION_COUNT, RESULTS_PREDICATS
import itertools
import commons
import sys # flush


logger = commons.logger()


# def atoms_to_string(atoms, avoid='new'):
    # """convert given atoms in a ASP-valid string"""
    # string = '.\n'.join(str(a) for a in atoms) + '.'
    # if avoid is None:
        # return string
    # else:
        # return string.replace(avoid, '')

def update_atoms(atoms_dict, atoms, avoid='new'):
    """Update given dict with given gringo atoms
    
    transform atoms by replace avoid value 
    by nothing in the final string."""
    if avoid is None or len(avoid) == 0:
       tuple(atoms_dict[atom.name()].add(tuple(atom.args())) for atom in atoms)
    else:
       tuple(atoms_dict[atom.name().replace(avoid, '')].add(tuple(atom.args())) for atom in atoms)


def atoms_from_dict(atoms_dict, atoms, joiner=None):
    """Return an ASP code generator that generate 
    requested atoms of given atoms_dict,
    as string if joiner is given
    """
    ret = (
        name+'('+','.join(str(_) for _ in args)+')'
        for name in atoms for args in atoms_dict[name]
    )
    if joiner is None:
        return ret
    else:
        return joiner.join(ret) + joiner


def prettified(atoms_dict, names=None, sizes=None, 
               joiner='\n', results_only=False):
    """Return a human readable string version or 
      string generator of given atoms.

    if names is given, only atoms with given name will be used.
    if results_only is True, only some atoms will be printed.
      (defined by commons.RESULTS_PREDICATS)
    if sizes is provided, atoms with args number not in sizes 
      will not be printed.

    atoms_dict must be a dictionnary like:
        {atom.name() : {atom.args()}}
        key is string, value is a set of list/tuple of args
    """
    # filter results
    if results_only:
        source = ((n,a) 
                  for n,a in iteritems(atoms_dict) 
                  if n in RESULTS_PREDICATS
                 )
    else:
        source = (_ for _ in iteritems(atoms_dict))
    # filter names
    if names is not None:
        source = ((name,argset) 
                  for name,argset in source 
                  if name in names
                 )
    # filter sizes
    if sizes is not None:
        source = (
            ( name, (args 
                     for args in argset 
                     if len(args) in sizes
                    )
            ) 
            for name, argset in source
        )
    
    return joiner.join(
        name+'('+','.join(str(_) for _ in arg)+').'
        for name, set_args in source for arg in set_args
    )






def asprgc(graph, extract, findcc, findcl, firstmodel, update, nextmodel):
    # all atoms are contained here
    #   atom.name:{atom.args}
    atoms = defaultdict(set)

    # Extract graph data
    logger.info('#################')
    logger.info('#### EXTRACT ####')
    logger.info('#################')
    extractor = ASPSolver().use(graph).use(extract)
    extracted_atoms = extractor.first_solution().atoms()
    # graph data is an ASP code that describes graph and connected components.
    update_atoms(atoms, extracted_atoms)
    # logger.debug('graph:\n' + str(atoms))
    logger.debug('graph:\n\t' + atoms_from_dict(atoms, ('node', 'inter', 'cc', 'ccedge'), '.\n\t'))

    # graph data:
    atom_ccs  = (a.args() 
                 for a in extracted_atoms 
                 if a.name() == 'cc'
                )

    # Find connected components
    logger.info('\n\t' + prettified(atoms, joiner='\n\t'))
    logger.info('#################')
    logger.info('####   CC    ####')
    logger.info('#################')
    model_count = 1
    # for _, cc in atom_ccs:
    for cc in atom_ccs:
        # Collect edges in the CC
        ccfinder = ASPSolver()
        ccfinder.read(atoms_from_dict(
            atoms, ('cc', 'ccedge', 'membercc', 'connectedpath'), '.'
        ))
        ccfinder.use(findcc, cc)
        ccfinder_atoms = ccfinder.first_solution().atoms()
        update_atoms(atoms, ccfinder_atoms)
        print(prettified(atoms))

        # Collect cliques
        clfinder = ASPSolver()
        clfinder.read(atoms_from_dict(
            atoms, ('node', 'oedge', 'inter', 'membercc'), '.'
        ))
        clfinder.use(findcl, cc)
        findcl_atoms = clfinder.first_solution().atoms()
        update_atoms(atoms, findcl_atoms)
        model_count += 1 

        # Perform first model
        firstmodeler = ASPSolver().read(atoms_from_dict(
            atoms, ('concept', 'clique', 'edgecoverc', 'edgecoverb'), '.'
        )).use(firstmodel, cc + [model_count])
        firstmodel_atoms = firstmodeler.first_solution().atoms()
        update_atoms(atoms, firstmodel_atoms)
        model_count += 1 

        # Creat solvers
        nextmodeler = ASPSolver().read(atoms_from_dict(
            atoms, ('concept', 'clique', 'edgecover'), '.'
        )).use(nextmodel, cc)
        updater = ASPSolver().read(atoms_from_dict(
            atoms, ('concept', 'clique', 'edgecover', 'node', 'membercc'), '.'
        )).use(update, cc)

        # updater.assign_external    ('step'     , [-1], True)
        updater.assign_external    ('next_step', [ 1], True)
        # nextmodeler.assign_external('step'     , [-1], True)
        for k in range(1,ITERATION_COUNT+1):
            # Perform update
            updater.release_external('step', (k-1,)) # doesn't exist in the first loop
            updater.assign_external ('step', (k  ,), True)
            updater.release_external('next_step', (k  ,)) # doesn't exist in the first loop
            updater.assign_external ('next_step', (k+1,), True)
            model = updater.first_solution()
            if model is not None:
                update_atoms(atoms, model.atoms())
            else: # model is None ; no solution
                print(' BROKE !')
                break
            model_count += 1 

            # Compiling concepts and cliques
            nextmodeler.release_external('step', (k-1,))
            nextmodeler.assign_external ('step', (k  ,), True)
            model = nextmodeler.first_solution()
            if model is not None:
                update_atoms(atoms, model.atoms())
            else: # model is None ; no solution
                print(' BROKE !')
                break
            model_count += 1 
            print('\r\t' + str(k) + '/' + str(ITERATION_COUNT), end='')
            sys.stdout.flush()

        # print all
        print('')
        logger.info('#################')
        logger.info('#### RESULTS ####')
        logger.info('#################')
        logger.info('\n\t' + prettified(atoms, joiner='\n\t', sizes=(4,5), results_only=True))
        

    
    # return str(graph)




