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
from __future__ import print_function
from future.utils import iteritems, iterkeys, itervalues
from collections  import defaultdict
from collections  import Counter
import itertools
import commons
import re


logger = commons.logger()


REGEX_PWRNS    = re.compile(r"^powernode\(([^,]+),([^,]+),([^,]+),(.+)\)$")
REGEX_TRIVIAL  = re.compile(r"^trivial\(([^,]+),([^,]+),([^,]+)\)$")
REGEX_CLIQUE   = re.compile(r"^clique\(([^,]+),([^,]+)\)$")
REGEX_EDGES    = re.compile(r"^edge\(([^,]+),([^\)]+)\)$")
REGEX_SUBPOWER = re.compile(r"^p\(([^,]+),([^,]+),(.+)\)$")


def powernode(cc, step, num_set):
    """Return string representation of powernode of given

    this string representation is not ASP valid,
     but can be used as name in most file formats :

        PWRN-<cc>-<step>-<num_set>

    """
    return 'PWRN-' + '-'.join((cc, step, num_set))

def subpowernode_to_powernode(subpowernode):
    """Convert ASP representation of powernode reference (p/3)
     in powernode representation.

    Equivalent to a call to powernode(3) on the three values
     returned by REGEX_SUBPOWER.match(subpowernode).
    """
    return powernode(*REGEX_SUBPOWER.match(subpowernode).groups())

def multiple_matched_splits(atoms, separator, regexs):
    """Return one generator of values finds by each regex on
     each substring of given string splitted by given separator.
    """
    atoms = (a for a in str(atoms).split(separator))
    # atoms = tuple(atoms)
    # print('ATOMS:', atoms)
    matchs = itertools.tee(atoms, len(regexs))
    # for regex, match in zip(regexs, matchs):
        # print(regex, match)
        # for a in match:
            # print(a, regex.match(a))

    matchs = ((regex.match(a)
                for a in match
              )
              for regex, match in zip(regexs, matchs)
             )
    matchs = tuple(tuple(a) for a in matchs)
    print('MATCHS:', matchs)
    return ((a.groups() for a in match if a is not None)
            for match in matchs
           )

def matched_splits(atoms, separator, regex):
    """Return generator of values finds by given regex on
     each substring of given string splitted by given separator.
    """
    matchs = (regex.match(a) for a in str(atoms).split(separator))
    return (a.groups() for a in matchs if a is not None)



class NeutralConverter(object):
    """Base class for Converters.

    Converters take string that describes ASP atoms, and,
     when finalizing, generate all graph description

    NeutralConverter is unusable as is :
     it generates a sensless output.

    """
    def __init__(self):
        self.converted = tuple()

    def convert(self, atoms, separator='.'):
        """Operate convertion on given atoms.

        Atoms are expecting to be powernodes like:
            powernode(a,1,1,a).

        """
        expected_atoms = [REGEX_PWRNS, REGEX_CLIQUE, REGEX_TRIVIAL]
        splits = tuple(multiple_matched_splits(atoms, separator, expected_atoms))
        print('DEBUG', splits)
        self.converted = itertools.chain(
            self.converted,
            self._convert(*splits)
        )

    def convert_edge(self, atoms):
        """Operate convertion on given atoms.

        Atoms are expecting to be edges between nodes like:
            edge(a,b).

        """
        self.converted = itertools.chain(
            self.converted,
            self._convert_edge(matched_splits(atoms, '.', REGEX_EDGES))
        )

    def _convert(self, atoms, cliques=[], trivial=[]):
        """Perform the convertion and return its results

        Wait for atoms data (cc,k,num_set,X),
        for cliques data (cc,k),
        and trivial data (cc,k)."""
        return atoms

    def _convert_edge(self, atoms):
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

    def _convert_edge(self, atoms):
        """Perform the convertion and return its results"""
        # get first item for obtain global data
        cc, k, s = next(atoms)
        atoms = itertools.chain( ((cc,k,s),), atoms )

        # generate lines
        nnf = ('{0}\tpp\t{2}'.format(*g) for g in atoms)
        return nnf



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
        self.nodes      = set()
        self.pwnds      = set()
        # contains is a dict of container:contained
        #  it keep only one node, and its used only
        #  for powernodes with only one node inside
        self.contains   = dict()
        # belongs is a dict of contained:container
        self.belongs    = dict()
        # a powernode is trivial iff contains only one node
        self.trivials   = set()
        # a powernode that is a clique is contained in self.cliques
        self.cliques    = set()
        # count number of nodes in powernodes
        self.containers_size = Counter()
        # linking between powernodes
        self.linked1to2 = defaultdict(set)
        self.linked2to1 = defaultdict(set)
        # linking between nodes
        self.edges      = defaultdict(set)

    def _convert(self, powernodes, cliques=[], trivial=[]):
        # cliques cc, step (a powernode is a clique)
        for cc, step in cliques:
            assert(int(step) > 0)
            pwrn      = powernode(cc,step,'1')
            self.edges[pwrn].add(pwrn)
            self.cliques.add(pwrn)
            logger.debug('CLIQUE:' + cc + step)

        # trivial cc, step, num_set (a powernode contains only one node)
        for cc, step, num_set in trivial:
            assert(int(step) > 0)
            assert(num_set in ('1', '2'))
            self.trivials.add(powernode(cc,step,num_set))
            logger.debug('TRIVIAL:' + cc + step + num_set)

        # powernodes cc, step, num_set, node
        for cc, step, num_set, node in powernodes:
            assert(int(step) > 0)
            assert(num_set in ('1', '2'))
            print('POWERNODES:', cc, step, num_set)
            node = node.strip('"')
            pwrn      = powernode(cc,step,num_set)
            pwrn_comp = powernode(cc,step,str(3-int(num_set)))
            reg_res = REGEX_SUBPOWER.match(node)
            if reg_res is None:
                self.nodes.add(node)
            else: # node match the pattern
                node = subpowernode_to_powernode(node)
            self.belongs[node]           = pwrn
            self.containers_size[pwrn]  += 1
            self.contains[pwrn]          = node

            if pwrn not in self.cliques and pwrn_comp not in self.cliques:
                self.pwnds.add(pwrn)
                if num_set == '1':
                    self.linked1to2[pwrn].add(pwrn_comp)
                else:
                    assert(num_set == '2')
                    self.linked2to1[pwrn].add(pwrn_comp)

        # integrity tests
        assert(all(node in self.trivials
                   for node in self.pwnds
                   if self.containers_size[node] == 1
        ))

    def _convert_edge(self, atoms):
        atoms = tuple(atoms)
        for a, b in atoms:
            # replace powernodes by their string equivalent
            reg_res_a = REGEX_SUBPOWER.match(a)
            reg_res_b = REGEX_SUBPOWER.match(b)
            if reg_res_a is not None: # a is a powernode
                a = subpowernode_to_powernode(a)
            if reg_res_b is not None: # b is a powernode
                b = subpowernode_to_powernode(b)
            # create the links between nodes
            self.edges[a].add(b)


    def finalized(self):
        # define NODEs, SETs, INs and EDGEs relations, and return them
        return '\n'.join(itertools.chain(
        # Header
            ('#BBL-1.0\n#' + BBLConverter.META_DATA + '\n#',),
        # NODEs
            ('NODE\t' + node for node in self.nodes),
        # SETs
            # defines the Graph as the biggest powernode that contain all the graph
            ('SET\tGraph\t1.0',),
            # defines all powernodes of set 1
            ('SET\t' + pwnd + '\t1.0'
             for pwnd in iterkeys(self.linked1to2)
            ),
            # defines all powernodes of set 2
            ('SET\t' + pwnd + '\t1.0'
             for pwnd in iterkeys(self.linked2to1)
            ),
            # defines all cliques
            ('SET\t' + pwnd + '\t1.0'
             for pwnd in self.cliques
            ),
        # INs
            # include in Graph all nodes that are not contained in another one
            ('IN\t' + node + '\tGraph'
             for node in self.nodes
             if self.containers_size[self.belongs[node]] == 1
            ),
            # include in Graph all nodes that ????
            ('IN\t' + node + '\tGraph'
             for node in self.pwnds
             if  node not in iterkeys(self.belongs)
             and self.containers_size[node] > 1
            ),
            # include in container all nodes contained
            ('IN\t'
             + (contained if contained not in self.trivials
                else self.contains[contained]
               )
             + '\t'
             + container
             for contained, container in iteritems(self.belongs)
             if container not in self.trivials
            ),
        # EDGEs
            # create link between powernodes of set 1 to set 2
            ('EDGE\t'
             + (pwnd if pwnd not in self.trivials else self.contains[pwnd])
             + '\t' + (target if target not in self.trivials else self.contains[target])
             + '\t1.0'
             for pwnd, targets in iteritems(self.linked1to2)
             for target in targets
            ),
            # create link between remaining nodes
            ('EDGE\t' + node + '\t' + target + '\t1.0'
             for node, targets in iteritems(self.edges)
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


