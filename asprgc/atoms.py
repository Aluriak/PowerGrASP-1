# -*- coding: utf-8 -*-
"""
Definitions of many utils functions about gringo atoms manipulation.
Provides converters, access and storage of atoms.

"""

from future.utils import iteritems, itervalues
from collections  import defaultdict
from commons      import RESULTS_PREDICATS
import itertools
import gringo
import re



def update(atoms_dict, atoms, avoid='new'):
    """Update given dict with given gringo atoms

    if given atoms dict is None,
     a new and empty dict will be used and returned
    Transform atoms by replace avoid value
     by nothing in the final string."""
    if atoms_dict is None:
        atoms_dict = defaultdict(set)
    # full generator generation
    tuple(
        atoms_dict[
            atom.name()
            if avoid is None or len(avoid) == 0 else
            atom.name().replace(avoid, '')
        ].add(tuple((
                ('"'+arg+'"')
                if isinstance(arg, str)
                else str(arg)
            ) for arg in atom.args()
        ))
        for atom in atoms
        if atom.__class__ is gringo.Fun
    )
    return atoms_dict




def from_dict(atoms_dict, atoms, joiner='.'):
    """Return an ASP code generator that generate
    requested atoms of given atoms_dict,
    as string if joiner is given,
    as generator if joiner is None.
    """
    if atoms.__class__ is str:
        atoms = [atoms]
    ret = (
        name+'('+','.join((str(_)) for _ in args)+')'
        for name in atoms for args in atoms_dict[name]
    )
    if joiner is None:
        return ret
    else:
        return joiner.join(ret) + joiner




def prettified(atoms_dict, names=None, sizes=None,
               joiner='\n', results_only=False, sort=False):
    """Return a human readable string version or
      string generator of given atoms.

    if names is given, only atoms with given name will be used.
    if results_only is True, only some atoms will be printed.
      (defined by commons.RESULTS_PREDICATS)
    if sizes is provided, atoms with args number not in sizes
      will not be printed.

    if sort is True, a non-lazy treatment will be applied to all data,
      and the atoms will be returned in sorted order.

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
    # get final text generator
    source = (
        name+'('+','.join(str(_) for _ in arg)+').'
        for name, set_args in source for arg in set_args
    )
    # sorting
    if sort:
        source = sorted(tuple(source))
    # joining if possible
    return source if joiner is None else joiner.join(source)


def count(atoms_dict, names=None):
    """Return a string that describes how many atoms given atoms_dict have.

    if names is None, all atoms will be returned.
    if names is an iterable of atoms names,
     only founded atoms will be returned.
    """
    if names is None:
        return {name:len(args) for name, args in atoms_dict.iteritems()}
    else:
        return {name:len(atoms_dict[name]) for name in names},



