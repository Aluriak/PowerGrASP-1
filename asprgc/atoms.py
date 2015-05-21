# -*- coding: utf-8 -*-
"""
Definitions of many utils functions about gringo atoms manipulation.
Provides converters, access and printings of atoms.

"""

from __future__   import absolute_import, print_function
from future.utils import iteritems, itervalues
from collections  import defaultdict, Counter
from commons      import RESULTS_PREDICATS
import itertools
import gringo

def prettified(atoms, names=None, sizes=None,
               joiner='\n', results_only=False, sort=False, hashs=False):
    """Return a human readable string version or
      string generator of given atoms.

    if names is given, only atoms with given name will be used.
    if results_only is True, only some atoms will be printed.
      (defined by commons.RESULTS_PREDICATS)
    if sizes is provided, atoms with args number not in sizes
      will not be printed.

    if sort is True, a non-lazy treatment will be applied to all data,
      and the atoms will be returned in sorted order.

    if hash is True, each atom will be printed with its hash.

    atoms must be an iterable of gringo.Fun instances.

    """
    atoms, hashs_values = itertools.tee(atoms)
    atoms = ((a.name(), a.args()) for a in atoms)
    if hashs:
        hashs_values = (a.__hash__() for a in hashs_values)
    # filter results
    if results_only:
        source = ((n,a)
                  for n,a in atoms
                  if n in RESULTS_PREDICATS
                 )
    else:
        source = (_ for _ in atoms)
    # filter names
    if names is not None:
        source = ((name,args)
                  for name,args in source
                  if name in names
                 )
    # filter sizes
    if sizes is not None:
        source = (
                  (name,args)
                  for name, argset in source
                  if len(args) in sizes
                 )
    # get final text generator
    source = (
        name+'('+','.join(str(_) for _ in args)+').'
        for name, args in source
    )
    # hashs
    if hashs:
        source = (
            str(hash) + ' ' + name
            for name, hash in zip(source, hashs_values)
        )
    # sorting
    if sort:
        source = sorted(tuple(source))

    # joining if possible
    return source if joiner is None else joiner.join(source)


def count(atoms, names=None):
    """Return a string that describes how many atoms given atoms_dict have.

    if names is None, all atoms will be returned.
    if names is an iterable of atoms names,
     only founded atoms will be returned.
    """
    counts = iteritems(Counter(a.name() for a in atoms))
    if names is None:
        return {n:c for n, c in counts}
    else:
        return {n:c for n, c in counts if a.name() in names}


def to_str(atoms, names=None, separator='.'):
    """Return string that is equivalent and ASP-valid from
    given atoms.

    If names is provided, only atoms with given names will be returned.
     names can be a single name or a container of names.
    separator is the string that will be added between each
     and at the end of the atoms.

    """
    if names is None:
        atoms = (str(a) for a in atoms)
    else: # names is provided
        # cast in tuple for allow usage of 'in' keyword
        if names.__class__ is str:
            names = (names,)
        # get only atoms that are requested
        atoms = (str(a) for a in atoms if a.name() in names)
    # output construction
    output = separator.join(atoms)
    if len(output) > 0:
        output += separator
    return output

