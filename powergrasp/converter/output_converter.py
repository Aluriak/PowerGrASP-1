# -*- coding: utf-8 -*-
"""
definitions of converter base class OutConverter.

Converters are objects that convert a flow of ASP atoms
 in a particular string format.

"""
import powergrasp.commons as commons
import itertools
import re


logger = commons.logger()

REGEX_PWRNS    = re.compile(r"^powernode\(([^,]+),([^,]+),([^,]+),(.+)\)$")
REGEX_TRIVIAL  = re.compile(r"^trivial\(([^,]+),([^,]+),([^,]+)\)$")
REGEX_CLIQUE   = re.compile(r"^clique\(([^,]+),([^,]+)\)$")
REGEX_EDGES    = re.compile(r"^edge\(([^,]+),([^\)]+)\)$")
REGEX_SUBPOWER = re.compile(r"^p\(([^,]+),([^,]+),(.+)\)$")
REGEX_INC_NODE = re.compile(r"^include\(p\(([^,]+),([^,]+),([^,]+)\),([^\)]+)\)$")
REGEX_INC_PWRN = re.compile(r"^include\(p\(([^,]+),([^,]+),([^,]+)\),p\(([^,]+),([^,]+),([^,]+)\)\)$")


def multiple_matched_splits(atoms, separator, regexs):
    """Return one generator of values finds by each regex on
     each substring of given string splitted by given separator.
    """
    atoms = (a for a in str(atoms).split(separator))
    matchs = itertools.tee(atoms, len(regexs))

    matchs = ((regex.match(a)
                for a in match
              )
              for regex, match in zip(regexs, matchs)
             )
    return ((a.groups() for a in match if a is not None)
            for match in matchs
           )

def matched_splits(atoms, separator, regex):
    """Return generator of values finds by given regex on
     each substring of given string splitted by given separator.
    """
    matchs = (regex.match(a) for a in str(atoms).split(separator))
    return (a.groups() for a in matchs if a is not None)



class OutConverter:
    """Base class for Converters.

    Converters take ASP atoms (gringo.Fun), and,
     when finalizing, generate all graph description
     in the expected format.

    OutConverter is unusable as is :
     it generates ASP output.

    """
    FORMAT_NAME = ''  # no default format
    FORMAT_EXTENSIONS = ()  # no default format

    def __init__(self):
        # for the first convertion, self.converted must be iterable
        self.atoms = ''

    def convert(self, atoms:str):
        """Operate convertion on given atoms.

        Atoms are expecting to be powernodes like:
            powernode(a,1,1,a).
        or cliques like:
            clique(a,1).
        or edges like:
            edge(a,b).

        These atoms will be used for perform the conversion
         in the finalize method.

        """
        assert isinstance(atoms, str)
        self.atoms += atoms

    def _convert(self, atoms:str) -> str:
        """Perform the convertion and return its results

        Wait for atoms powernode(cc,k,num_set,X)
         and for clique(cc,k)
         or  for edges(X,Y).

        """
        return str(atoms)

    def header(self):
        """Return header of the file"""
        return ''

    def finalized(self):
        """Return converted data"""
        return '\n' + '\n'.join(self.atoms)

    def __str__(self):
        """str version of a converter is the finalized string of data"""
        return self.finalized()

    def comment(self, lines):
        """Add given iterable of lines as comments"""
        return '\n# ' + '\n# '.join(lines)
