# -*- coding: utf-8 -*-
"""
definition of the bubble format converter.
A bubble format file (version 1), is structured in four parts:
    - list of nodes
    - list of powernodes
    - containers and contained
    - edges

There is a grammar that can be associated:
S     ::= LINE . S + FF
LINE  ::= NODES + SETS + INS + EDGES
NODES ::= 'NODE\t' . node_name      . '\n'
SETS  ::= 'SET\t'  . powernode_name . '\t' . coefficient . '\n'
INS   ::= 'IN\t'   . contained      . '\t' . container   . '\n'
EDGES ::= 'EDGE\t' . elementA       . '\t' . elementB    . '\t' . coefficient . '\n'

Coefficient are currently set to 1.0, and no tests have been performed,
so we don't know what is the purpose of it.
For contained and container, only the direct inclusion must be provided.
The order of the parts/lines can be changed.
Comments are marked by '#' character.

The Cytoscape plugin CyOoG is able to read and print that format.


"""
from __future__          import absolute_import, print_function
from future.utils        import iteritems, iterkeys, itervalues
from collections         import defaultdict
from commons             import basename
from converter.converter import NeutralConverter
import itertools
import commons
import gringo
import atoms

logger        = commons.logger()
ASP_INCLUSION = 'asprgc/ASPsources/inclusion.lp'
ASP_OPTIONS   = ['--warn=no-atom-undefined']
ASP_OPTIONS   = []


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



class BBLConverter(NeutralConverter):
    """Convert given atoms in BBL format

    Used bubble format is Bubble V1.0,
     and is used by Powergraph module of BIOTEC
     for save the powernodes cytoscape representation.

    Because of the complexity of the format,
     the complexity is higher than NNFConverter.
     The convert operation stores many data,
      and, for big graphs, performed treatments could be heavy.
    An ASP solver is used for perform complex treatments.

    """
    META_DATA   = "File written by the ASPRGC module"

    def __init__(self):
        try: # python 3
            super().__init__()
        except TypeError: # python 2
            super(BBLConverter, self).__init__()
        # accumulators of atoms
        self.atoms_powernodes = tuple()
        self.atoms_cliques    = tuple()
        self.atoms_edges      = tuple()
        # nodes
        self.nodes      = set()
        self.pwnds      = set()
        self.cliques    = set()
        # contains is a dict of container:contained
        #  it keep only one node, and its used only
        #  for powernodes with only one node inside
        self.contains   = defaultdict(set)
        # a {power,}node is in top iff is not contained by another
        self.tops       = set()
        # a {power,}node is trivial if it contains only one element
        self.trivials   = set()
        # linking between powernodes
        self.linked1to2 = defaultdict(set)
        self.linked2to1 = defaultdict(set)
        # linking between nodes
        self.edges      = defaultdict(set)

    def _convert(self, powernodes, cliques, edges):
        """Accumulate atoms"""
        self.atoms_powernodes = itertools.chain(self.atoms_powernodes, powernodes)
        self.atoms_cliques    = itertools.chain(self.atoms_cliques, cliques)
        self.atoms_edges      = itertools.chain(self.atoms_edges, edges)

    def _additionnal_data_from(self, powernodes):
        """Collect additionnal data on powernodes,
        notabily on direct inclusion and triviality.

        New atoms are generated and returned.

            powernodes -- ASP source code that contains 
                atoms like 'powernode(cc,k,t,x).'

        Returns many generators:
            top -- powernodes that are contained by nothing
            topnode -- nodes that are contained by nothing
            trivial -- powernodes that contains only one element
            include_pwrn -- powernode that include a powernode
            include_node -- powernode that include a node

        """
        # create solver
        self.solver = gringo.Control(ASP_OPTIONS)
        self.solver.load(ASP_INCLUSION)
        self.solver.add('base', [], powernodes)
        self.solver.ground([
            (basename(ASP_INCLUSION), []),
            ('base', []),
        ])

        new_atoms = commons.first_solution(self.solver).atoms()
        print('DEBUG INCLUSION: input     == ', powernodes)
        print('DEBUG INCLUSION: new_atoms == ', new_atoms)
        return (
            ((str(_) for _ in a.args()) for a in new_atoms if a.name() == 'top'),
            ((str(_) for _ in a.args()) for a in new_atoms if a.name() == 'topnode'),
            ((str(_) for _ in a.args()) for a in new_atoms if a.name() == 'trivial'),
            ((str(_) for _ in a.args()) for a in new_atoms if a.name() == 'include_pwrn'),
            ((str(_) for _ in a.args()) for a in new_atoms if a.name() == 'include_node'),
        )

    def _generate_metadata(self):
        """assign to self metadata about knowed atoms.

        Metadata will be used by finalized method.
        """
        # get additionnal data
        self.atoms_powernodes, powernodes_copy = itertools.tee(self.atoms_powernodes)
        tops, topnodes, trivials, inclusions_powernode, inclusions_node = (
            self._additionnal_data_from(atoms.to_str(powernodes_copy))
        )
        # get only the args in string for powernodes, cliques and edges
        powernodes = ((str(_) for _ in a.args()) for a in self.atoms_powernodes)
        cliques    = ((str(_) for _ in a.args()) for a in self.atoms_cliques)
        edges      = ((str(_) for _ in a.args()) for a in self.atoms_edges)

        # cliques cc, step (powernode cc,step is a clique)
        for cc, step in cliques:
            assert(int(step) > 0)
            self.cliques.add(powernode(str(cc), str(step), '1'))
            logger.debug('CLIQUE:' + str(cc) + str(step))

        # edges a, b (there is an edge between a and b)
        for a, b in edges:
            assert(a.__class__ is str and b.__class__ is str)
            self.edges[a].add(b)

        # powernodes cc, step, num_set, node
        for cc, step, num_set, node in powernodes:
            assert(int(step) > 0)
            assert(num_set in ('1', '2'))
            node = node.strip('"')
            pwrn      = powernode(cc,step,num_set)
            pwrn_comp = powernode(cc,step,str(3-int(num_set)))
            self.nodes.add(node)
            # self.contains[pwrn].add(node)

            if pwrn not in self.cliques and pwrn_comp not in self.cliques:
                self.pwnds.add(pwrn)
                if num_set == '1':
                    self.edges[pwrn].add(pwrn_comp)

            logger.debug('POWERNODE:' + cc + step + num_set + node)

        # top cc, step, num_set (a powernode is contained by nothing)
        for node in topnodes:
            self.tops.add(node[0])
            logger.debug('TOP:' + node[0])

        # top cc, step, num_set (a powernode is contained by nothing)
        for cc, step, num_set in tops:
            self.tops.add(powernode(cc,step,num_set))
            logger.debug('TOP:' + cc + step + num_set)

        # trivial cc, step, num_set (a powernode contains only one node)
        for cc, step, num_set in trivials:
            assert(int(step) > 0)
            assert(num_set in ('1', '2'))
            # self.trivials.add(powernode(cc,step,num_set))
            logger.debug('[NOT USED] TRIVIAL:' + cc + step + num_set)

        # include cc1, step1, num_set1, cc2, step2, num_set2
        #  (powernode2 is in powernode1)
        for cc1, step1, num_set1, cc2, step2, num_set2 in inclusions_powernode:
            assert(int(step) > 0)
            assert(num_set in ('1', '2'))
            pwrn1 = powernode(cc1, step1, num_set1)
            pwrn2 = powernode(cc2, step2, num_set2)
            logger.debug('INC_PWRN:' + pwrn1 + ", " + pwrn2)
            self.contains[pwrn1].add(pwrn2)

        # include cc, step, num_set, node
        #  (node is in powernode cc,step,num_set)
        for cc, step, num_set, node in inclusions_node:
            assert(int(step) > 0)
            assert(num_set in ('1', '2'))
            pwrn = powernode(cc, step, num_set)
            self.contains[pwrn].add(node)
            logger.debug('INC_NODE:' + cc + step + num_set + node)


    def finalized(self):
        self._generate_metadata()
        # define NODEs, SETs, INs and EDGEs relations, and return them
        return '\n'.join(itertools.chain(
        # Header
            ('#BBL-1.0\n#' + BBLConverter.META_DATA + '\n#',),
        # NODEs
            ('NODE\t' + node for node in self.nodes),
        # SETs
            # defines all powernodes of set 1
            ('SET\t' + pwnd + '\t1.0'
             for pwnd in self.pwnds
            ),
        # INs
            # include in container all nodes contained
            ('IN\t'
             + (contained if contained not in self.trivials
                else self.contains[contained]
               )
             + '\t'
             + container
             for container, containeds in iteritems(self.contains)
             for contained in containeds
            ),
        # EDGEs
            # create reflexives edges for cliques
            ('EDGE\t' + clique + '\t' + clique + '\t1.0'
             for clique in self.cliques
            ),
            # create edges
            ('EDGE\t' + node + '\t' + target + '\t1.0'
             for node, targets in iteritems(self.edges)
             for target in targets
            ),
        ))
