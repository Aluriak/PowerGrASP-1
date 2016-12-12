"""
Definition of the atom container model, AtomsModel.

Definitions of many utils functions about gringo atoms manipulation.
Provides converters, access and printings of atoms.

"""


import os
import itertools
from collections import defaultdict, namedtuple

from pyasp import asp


# ASP Parser: if atoms are defined as arguments, consider them strings.
PARSER = asp.Parser(collapseTerms=True, collapseAtoms=False)

# CONSTANTS
RESULTS_PREDICATS = (
    'powernode',
    'poweredge',
    'score',
)


# Atom definition
class ASPAtom(namedtuple('BaseAtom', ['name', 'args'])):

    @property
    def only_arg(self):
        if len(self.args) != 1:
            raise ValueError("Atom {} have multiple parameters. "
                             "only_args() property is not "
                             "accessible.".format(self))
        return self.args[0]

    @property
    def asp(self):
        """Return the self representation compliant with ASP"""
        return "{}({}).".format(self.name, ', '.join(self.args))


class AtomsModel:
    """Main model of atoms data.

    Support parsing from pyasp models and ASP formatted strings.

    Constructor should not be called by client:
     static methods from_* are here to ensure the object construction.

    """

    def __init__(self, data:iter or dict):
        """Expects an iterable of (name, args), or a properly formatted dict"""
        if not isinstance(data, dict):  # data is an iterable of 2-uplets
            assert iter(data)
            inrepr = defaultdict(set)
            for name, args in data:
                assert isinstance(name, str)
                try:
                    iter(args)
                except TypeError:
                    raise ValueError("Given atom {}({}) has only one parameter"
                                     " not encapsulated in an iterable, which"
                                     " is unexpected.".format(name, args))
                inrepr[name].add(tuple(args))
            data = inrepr
        self._payload = defaultdict(set, dict(data))
        self._counts = self.__count_atoms()

    def remove_atoms(self, atoms:iter):
        for name, args in atoms:
            self._payload[name].remove(tuple(args))
        self._counts = self.__count_atoms()

    def add_atoms(self, atoms:iter):
        for name, args in atoms:
            self._payload[name].add(tuple(args))
        self._counts = self.__count_atoms()


    def __count_atoms(self) -> dict:
        """Return number of atom for each predicate"""
        return {name: len(args) for name, args in self._payload.items()}


    @property
    def predicates(self):
        return frozenset(self._payload.keys())

    @property
    def atoms(self) -> iter(('name', 'arg')):
        yield from ((name, arg) for name, args in self._payload.items()
                    for arg in args)

    def __iter__(self):
        return self.atoms

    @property
    def counts(self):
        return self._counts


    def get(self, names:str or iter) -> iter:
        """Yield (predicate, args) for all atoms of given predicate name"""
        for name in ([names] if isinstance(names, str) else names):
            if name not in self._payload:
                # raise ValueError("Given predicate {} is not in {}"
                                 # " container".format(name, self))
                continue
            all_args = tuple(self._payload.get(name, ()))
            yield from (ASPAtom(name, args) for args in all_args)

    def get_only(self, atom_name:str) -> ASPAtom:
        """Return the only one atom having the given predicate name"""
        args = self._payload[atom_name]
        assert len(args) < 2, "given predicate name is shared by multiple predicate"
        assert len(args) > 0, "given predicate name doesn't exists"
        return ASPAtom(atom_name, next(iter(args)))

    def get_str(self, names:str or iter) -> iter:
        """Return a string of atoms for all atoms of given predicate name"""
        return AtomsModel(self.get(names))


    @staticmethod
    def from_asp_string(aspcode:str):
        """Build an AtomsModel instance from an ASP compliant string"""
        inrepr = defaultdict(set)
        atoms = atoms_from_aspstr(aspcode)
        for name, args in atoms:
            inrepr[name].add(tuple(args))
        return AtomsModel(inrepr)

    @staticmethod
    def from_pyasp_termset(termset):
        """Build an AtomsModel instance from an iterable of pyasp Term"""
        inrepr = defaultdict(set)
        for atom in termset:
            inrepr[atom.predicate].add(tuple(atom.args()))
        return AtomsModel(inrepr)

    @staticmethod
    def from_asp_file(filename:str):
        """Build an AtomsModel instance from a filename containing ASP code"""
        return AtomsModel.from_asp_string(open(filename).read())


    @staticmethod
    def from_(source):
        """Detect the input form of atoms, and return the properly
        initialized AtomsModel instance

        """
        if isinstance(source, str):
            if os.path.exists(source):
                 return AtomsModel.from_asp_file(source)
            else:
                 return AtomsModel.from_asp_string(source)
        else:  # should be a pyasp termset
             return AtomsModel.from_pyasp_termset(source)

    def __str__(self):
        """ASP compliant representation"""
        rpr = '.'.join('{}({})'.format(name, ','.join(str(_) for _ in args))
                       for name, args in self.atoms)
        return (rpr + '.') if rpr else ''


def atoms_from_aspstr(aspcode:str) -> iter:
    """Yield (name, args) object found in given ASP code.

    >>> list(atoms_from_aspstr('b("oh?well.",5).'))
    [('b', ('"oh?well."', '5'))]

    """
    for atom in PARSER.parse(aspcode.rstrip('.')):
        yield atom.predicate, tuple(atom.args())


def split(atom:str) -> ASPAtom or None:
    """Return the splitted version of given atom.

    atom -- string formatted as an ASP readable atom.
    return -- None or an ASPAtom object with field name and args.

    If many atoms are defined in the input string,
        only one will be returned.
    If given atom is not valid, None is returned.

    >>> split('edge(lacA,lacZ)')
    ASPAtom(name='edge', args=('lacA', 'lacZ'))
    >>> split('edge(42,12)')
    ASPAtom(name='edge', args=('42', '12'))
    >>> split('edge("ASX38","MER(HUMAN)")')
    ASPAtom(name='edge', args=('"ASX38"', '"MER(HUMAN)"'))
    >>> split('lowerbound.')
    ASPAtom(name='lowerbound', args=())
    >>> split('')

    """
    assert isinstance(atom, str)
    try:
        parsed = next(iter(PARSER.parse(atom.rstrip('.'))))
        return ASPAtom(parsed.predicate, tuple(parsed.args()))
    except StopIteration:
        return None


def arg(atom):
    """Return the argument of given atom, as a tuple

    >>> arg('edge(lacA,lacZ)')
    ('lacA', 'lacZ')
    >>> arg('score(13)')
    ('13',)
    >>> arg('lowerbound')
    ()

    """
    payload = atom.strip('.').strip(')')
    try:
        return tuple(payload.split('(')[1].split(','))
    except IndexError:  # no args !
        return tuple()


def first_arg(atom):
    """Return the first argument of given atom, or None if no arg

    >>> first_arg('edge(lacA,lacZ)')
    'lacA'
    >>> first_arg('score(13)')
    '13'
    >>> first_arg('lowerbound')

    """
    try:
        return arg(atom)[0]
    except IndexError:
        return None


def to_str(atoms, names=None, separator='.'):
    """Return string that is equivalent and ASP-valid from
    given atoms.

    If names is provided, only atoms with given names will be returned.
     names can be a single name or a container of names.
    separator is the string that will be added between each
     and at the end of the atoms.

    """
    if names:
        atoms = atoms.get(names)
    return separator.join(atom.predicate + '(' + ','.join(atom.arguments) + ')'
                          for atom in atoms) + separator


def name_args_to_str(name:str, args:iter, end:str='.') -> str:
    """Return an ASP compliant atom based on given name and args

    >>> name_args_to_str('p', (1, 2))
    'p(1,2).'
    >>> name_args_to_str('p', ())
    'p.'

    """
    if len(args) == 0:
        return name + end
    else:
        args = ((str(arg) if str(arg).isalnum() else ('"' + str(arg) + '"'))
                for arg in args)
        return '{}({}){}'.format(name, ','.join(args), end)
