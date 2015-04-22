# -*- coding: utf-8 -*-
"""
TOWRITE
"""
# from future.utils import itervalues, iteritems
from future.utils import iteritems
# from collections  import defaultdict
# from aspsolver    import ASPSolver
# from commons      import RESULTS_PREDICATS
# import itertools
# import commons






# def atoms_to_string(atoms, avoid='new'):
    # """convert given atoms in a ASP-valid string"""
    # string = '.\n'.join(str(a) for a in atoms) + '.'
    # if avoid is None:
        # return string
    # else:
        # return string.replace(avoid, '')




def update(atoms_dict, atoms, avoid='new'):
    """Update given dict with given gringo atoms
    
    transform atoms by replace avoid value 
    by nothing in the final string."""
    if avoid is None or len(avoid) == 0:
       tuple(atoms_dict[atom.name()].add(tuple(atom.args())) for atom in atoms)
    else:
       tuple(atoms_dict[atom.name().replace(avoid, '')].add(tuple(atom.args())) for atom in atoms)




def from_dict(atoms_dict, atoms, joiner=None):
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



