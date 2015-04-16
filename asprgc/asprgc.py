# -*- coding: utf-8 -*-
"""
TOWRITE
"""
from __future__   import print_function, absolute_import
from future.utils import itervalues
from collections  import defaultdict
from aspsolver    import ASPSolver
import itertools
import commons


logger = commons.logger()


# def atoms_to_string(atoms, avoid='new'):
    # """convert given atoms in a ASP-valid string"""
    # string = '.\n'.join(str(a) for a in atoms) + '.'
    # if avoid is None:
        # return string
    # else:
        # return string.replace(avoid, '')

def update_from_atoms(atoms_dict, atoms, avoid='new'):
    """Update given dict with given gringo atoms"""
    if avoid is None or len(avoid) == 0:
        atoms = (str(_)+'. ' for _ in atoms)
    else:
        atoms = (str(_).replace(avoid, '')+'. ' for _ in atoms)
    for atom in atoms:
        atoms_dict[atom[:atom.find('(')]] += atom


def atoms_from_dict(atoms_dict, atoms, join=None):
    """Return an ASP code generator that generate 
    requested atoms of given atoms_dict as string.
    """
    if join is None:
        return (atoms_dict[pred] for pred in atoms)
    else:
        return join.join((atoms_dict[pred] for pred in atoms))


def prettified(atoms):
    """Return a human readable string version of given atoms.
    """
    return '\n'.join('.\n'.join(v.split('. ')) for v in itervalues(atoms))


def asprgc(graph, extract, findcc, findcl, firstmodel):
    # all atoms are contained here
    atoms = defaultdict(str)

    # Extract graph data
    logger.info('#################')
    logger.info('#### EXTRACT ####')
    logger.info('#################')
    extractor = ASPSolver().use(graph).use(extract)
    model = extractor.first_solution()
    # graph data is an ASP code that describes graph and connected components.
    update_from_atoms(atoms, model.atoms())
    print(model.atoms())
    # logger.debug('graph:\n' + str(atoms))
    logger.debug('graph:\n' + '\n'.join(atoms_from_dict(atoms, ('node', 'inter', 'cc', 'ccedge'))))

    # graph data:
    # atom_ccs  = (('cc', a.args()) 
    atom_ccs  = (a.args() 
                 for a in model.atoms() 
                 if a.name() == 'newcc'
                )

    # Find connected components
    logger.info('#################')
    logger.info('#### FIND CC ####')
    logger.info('#################')
    # for _, cc in atom_ccs:
    for cc in atom_ccs:
        # Collect edges in the CC
        ccfinder = ASPSolver()
        ccfinder.read(atoms_from_dict(atoms, ('cc', 'ccedge', 'membercc', 'connectedpath'), join=''))
        ccfinder.use(findcc, cc)
        update_from_atoms(atoms, ccfinder.first_solution().atoms())

        # Collect cliques
        clfinder = ASPSolver().read(
            atoms_from_dict(atoms, ('node', 'oedge', 'inter', 'membercc'), join='')
        ).use(findcl, cc)
        findcl_atoms = clfinder.first_solution().atoms()
        update_from_atoms(atoms, findcl_atoms)

        # Perform first model
        firstmodeler = ASPSolver().read(
            atoms_from_dict(atoms, ('node', 'oedge', 'inter', 'membercc'), join='')
        ).use(firstmodel, cc)
        update_from_atoms(atoms, firstmodeler.first_solution().atoms())

        # print all
        print('################')
        print('# ATOMS')
        print('################')
        print(prettified(atoms))
        

    
    # return str(graph)




