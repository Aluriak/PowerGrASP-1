# -*- coding: utf-8 -*-
"""
TOWRITE
"""
from future.utils import iteritems
from commons      import RESULTS_PREDICATS
import itertools
import gringo
import re



def update(atoms_dict, atoms, avoid='new'):
    """Update given dict with given gringo atoms

    transform atoms by replace avoid value
    by nothing in the final string."""
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
    ret = (
        # name+'('+','.join(args)+')'
        # name+'('+','.join((('"'+_+'"') if isinstance(_, str) else str(_)) for _ in args)+')'
        # name+'('+','.join(str(_) for _ in args)+')'
        # name+'('+','.join(('"'+str(_)+'"') for _ in args)+')'
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


def converter_for(output_format):
    """Return function that take atoms and convert them to output format
    """
    return OUTPUT_FORMAT_CONVERTERS[output_format]


def to_NNF(atoms, separator=' ', simple_edges=False):
    """convert given atoms in NNF format.

    Return NNF formated string.

    args:
        atoms -- string with atoms separated by separator
        separator -- the char that will be used by split
        simple_edges -- True iff given atoms describes simple edges
    """
    if simple_edges:
        reg_atom = re.compile(r"remain\(([^\)]+),([^\)]+)\)")
    else:
        reg_atom = re.compile(r"powernode\(([^\)]+),([^\)]+),([^\)]+),([^\)]+)\)")

    nnf = (reg_atom.match(a) for a in str(atoms).split(separator))
    nnf = (a.groups() for a in nnf if a is not None)

    # get first item for obtain global data
    if not simple_edges:
        cc, k, s, node = next(nnf)
        nnf = itertools.chain( ((cc,k,s,node),), nnf )

    # generate lines
    if simple_edges:
        nnf = ('{2}\tpp\t{3}\n'.format(*g) for g in nnf)
    else:
        keys = set()
        for cc, k, s, node in nnf:
            if (cc, k) in keys:
            line = '{0}_{1}_{2}\t{3}\n'.format(cc, k, s, node)
            nnf = itertools.chain(
                nnf,
                ('{0}_{1}\t{2}_{3}_{4}\tpp\t{5}_{6}_{7}\n'.format(cc,k,cc,k,1,cc,k,2),),
                ('{0}_cc\t{1}_{2}\n'.format(cc,cc,k),),
            )

    return ''.join(str(_) for _ in nnf)



# Link between format names and atom2format functions
OUTPUT_FORMATS = (
    'nnf',
    'human',
)
OUTPUT_FORMAT_CONVERTERS = {
    'nnf'   : to_NNF,
    'human' : None
}



