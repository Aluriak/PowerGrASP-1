# -*- coding: utf-8 -*-
"""
definitions about Converters.

Converters are objects that convert a flow of ASP atoms
 in a particular string format.

Supported formats :
- asp: pure asp;
- nnf: nested network format;
- bbl: bubble format, used by Powergraph for printings;

"""
from future.utils import iteritems, iterkeys, itervalues
from collections  import defaultdict
import itertools
import re


REGEX_ATOMS = re.compile(r"powernode\(([^\)]+),([^\)]+),([^\)]+),([^\)]+)\)")


def atoms_data(atoms, separator=' '):
    """Return generator of atom data
    Each generated element is something like :
        (cc, step, num_set, node)

    """
    data = (REGEX_ATOMS.match(a) for a in str(atoms).split(separator))
    return (a.groups() for a in data if a is not None)



class NeutralConverter(object):
    """Base class for Converters.

    Converters take string that describes ASP atoms, and,
     when finalizing, generate all graph description

    NeutralConverter do nothing : it generates ASP from ASP.

    """
    def __init__(self):
        self.converted = tuple()

    def convert(self, atoms, separator=' '):
        """Operate convertion on given atoms"""
        self.converted = itertools.chain(
            self.converted, self._convert(atoms_data(atoms, separator))
        )

    def _convert(self, atoms):
        """Perform the convertion and return its results"""
        return atoms

    def finalized(self):
        """Return converted data"""
        return '\n'.join(self.converted)

    def __str__(self):
        return self.finalized()



class NNFConverter(NeutralConverter):
    """Convert given atoms in NNF format"""

    def _convert(self, atoms):
        """Operate convertion on given atoms"""
        # get first item for obtain global data
        cc, k, s, node = next(atoms)
        atoms = itertools.chain( ((cc,k,s,node),), atoms )

        # generate lines
        nnf = ('{0}_{1}_{2}\t{3}'.format(*g) for g in atoms)
        return itertools.chain(
            nnf,
            ('{0}_{1}\t{2}_{3}_{4}\tpp\t{5}_{6}_{7}'.format(cc,k,cc,k,1,cc,k,2),),
            ('{0}_cc\t{1}_{2}'.format(cc,cc,k),),
        )



class BBLConverter(NeutralConverter):
    """Convert given atoms in BBL format

    Used bubble format is V1.0,
     and is used by Powergraph module of BIOTEC
     for save the powernodes cytoscape representation.

    Because of the complexity of the format,
     the complexity is higher than NNFConverter.
     The convert operation stores many data,
      and, for big graphs, performed treatments could be heavy.

    """
    META_DATA   = "File written by the ASPRGC module"

    def __init__(self):
        try: # python 3
            super().__init__()
        except TypeError: # python 2
            super(BBLConverter, self).__init__()
        self.nodes    = set()
        self.pwnds    = set()
        self.belongs  = defaultdict(set)
        self.linked   = defaultdict(set)

    def _convert(self, atoms):

        def create_pwnd(cc, step, num_set):
            return 'PWRN-' + '-'.join((cc, step, num_set))

        for cc, step, num_set, node in atoms:
            powernode      = create_pwnd(cc,step,num_set)
            powernode_comp = create_pwnd(cc,step,str(3-int(num_set)))
            self.nodes.add(node)
            self.pwnds.add(powernode)
            # self.pwnds.add(powernode_comp)
            self.belongs[node].add(powernode)
            if num_set == '1':
                self.linked[powernode].add(powernode_comp)

    def finalized(self):
        # define NODEs, SETs, INs and EDGEs relations, and return them
        return '\n'.join(itertools.chain(
            # Header
            ('#BBL-1.0\n#' + BBLConverter.META_DATA + '\n#',),
            # NODEs
            ('NODE\t' + node for node in self.nodes),
            # SETs
            ('SET\tGraph\t1.0',),
            ('SET\t' + pwnd + '\t1.0'
             for pwnd in iterkeys(self.linked)
            ),
            # INs
            ('IN\t' + node + '\tGraph'
             for node in self.pwnds
             if node not in iterkeys(self.belongs)
            ),
            ('IN\t' + node + '\t' + pwnd
             for node, pwnds in iteritems(self.belongs)
             for pwnd in pwnds
            ),
            # EDGEs
            ('EDGE\t' + pwnd + '\t' + target + '\t1.0'
             for pwnd, targets in iteritems(self.linked)
             for target in targets
            ),
        ))


# Link between format names and atom2format functions
OUTPUT_FORMATS = (
    'asp',
    'nnf',
    'bbl',
)

OUTPUT_FORMAT_CONVERTERS = {
    'asp' : NeutralConverter,
    'nnf' : NNFConverter,
    'bbl' : BBLConverter,
}

def converter_for(output_format):
    """Return function that take atoms and convert them to output format
    """
    return OUTPUT_FORMAT_CONVERTERS[output_format]()


