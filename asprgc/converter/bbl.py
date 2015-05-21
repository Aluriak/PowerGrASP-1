# -*- coding: utf-8 -*-
"""
definition of the bubble format converter.
"""
from __future__   import absolute_import, print_function
from future.utils import iteritems, iterkeys, itervalues
from collections  import defaultdict
from aspsolver    import ASPSolver
from converter.converter import NeutralConverter
import atoms
import itertools
import commons

logger        = commons.logger()
ASP_INCLUSION = 'asprgc/ASPsources/inclusion.lp'
ASP_OPTIONS   = ['--warn=no-atom-undefined']


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
        self.nodes      = set()
        self.pwnds      = set()
        # contains is a dict of container:contained
        #  it keep only one node, and its used only
        #  for powernodes with only one node inside
        self.contains   = dict()
        # belongs is a dict of contained:container
        self.belongs    = dict()
        # a {power,}node is in top iff is not contained by another
        self.tops       = set()
        # a powernode is trivial iff contains only one node
        self.trivials   = set()
        # a powernode that is a clique is contained in self.cliques
        self.cliques    = set()
        # linking between powernodes
        self.linked1to2 = defaultdict(set)
        self.linked2to1 = defaultdict(set)
        # linking between nodes
        self.edges      = defaultdict(set)
        self.solver = ASPSolver(ASP_OPTIONS).use(ASP_INCLUSION)

    def _additionnal_data_from(self, powernodes):
        """Collect additionnal data on powernodes,
        notabily on direct inclusion and triviality.

        New atoms are generated and returned.

        """
        self.solver.read(atoms.to_str(powernodes, names='powernode'))
        new_atoms = self.solver.first_solution().atoms()
        return (
            ((str(_) for _ in a.args()) for a in new_atoms if a.name() == 'top'),
            ((str(_) for _ in a.args()) for a in new_atoms if a.name() == 'trivial'),
            ((str(_) for _ in a.args()) for a in new_atoms if a.name() == 'include_pwrn'),
            ((str(_) for _ in a.args()) for a in new_atoms if a.name() == 'include_node'),
        )

    def _convert(self, powernodes, cliques, edges):
        # get additionnal data
        powernodes, powernodes_copy = itertools.tee(powernodes)
        tops, trivials, inclusions_powernode, inclusions_node = (
            self._additionnal_data_from(powernodes_copy)
        )
        # get only the args in string for powernodes, cliques and edges
        powernodes = ((str(_) for _ in a.args()) for a in powernodes)
        cliques    = ((str(_) for _ in a.args()) for a in cliques)
        edges      = ((str(_) for _ in a.args()) for a in edges)

        # cliques cc, step (powernode cc,step is a clique)
        for cc, step in cliques:
            assert(int(step) > 0)
            self.cliques.add(powernode(str(cc),str(step),'1'))
            logger.debug('CLIQUE:' + str(cc) + str(step))

        # top cc, step, num_set (a powernode is contained by nothing)
        for cc, step, num_set in tops:
            assert(int(step) > 0)
            assert(num_set in ('1', '2'))
            self.tops.add(powernode(cc,step,num_set))
            logger.debug('TOP:' + cc + step + num_set)

        # trivial cc, step, num_set (a powernode contains only one node)
        for cc, step, num_set in trivials:
            assert(int(step) > 0)
            assert(num_set in ('1', '2'))
            self.trivials.add(powernode(cc,step,num_set))
            logger.debug('TRIVIAL:' + cc + step + num_set)

        # include cc1, step1, num_set1, cc2, step2, num_set2
        #  (powernode2 is in powernode1)
        for cc1, step1, num_set1, cc2, step2, num_set2 in inclusions_powernode:
            assert(int(step) > 0)
            assert(num_set in ('1', '2'))
            logger.debug('INC_PWRN:' + cc1 + step1 + num_set1 + cc2 + step2 + num_set2)
            pwrn1 = powernode(cc1,step1,num_set1)
            pwrn2 = powernode(cc2,step2,num_set2)
            self.includes[pwrn1].add(pwrn2)

        # include cc, step, num_set, node
        #  (node is in powernode cc,step,num_set)
        for cc, step, num_set, node in inclusions_node:
            assert(int(step) > 0)
            assert(num_set in ('1', '2'))
            pwrn = powernode(cc,step,num_set)
            self.contains[pwrn].add(node)
            logger.debug('INC_NODE:' + cc + step + num_set + node)

        # powernodes cc, step, num_set, node
        for cc, step, num_set, node in powernodes:
            assert(int(step) > 0)
            assert(num_set in ('1', '2'))
            node = node.strip('"')
            pwrn      = powernode(cc,step,num_set)
            pwrn_comp = powernode(cc,step,str(3-int(num_set)))
            self.nodes.add(node)
            self.belongs[node]  = pwrn
            self.contains[pwrn] = node

            if pwrn not in self.cliques and pwrn_comp not in self.cliques:
                self.pwnds.add(pwrn)
                if num_set == '1':
                    self.linked1to2[pwrn].add(pwrn_comp)
                else:
                    assert(num_set == '2')
                    self.linked2to1[pwrn].add(pwrn_comp)

            logger.debug('POWERNODE:' + cc + step + num_set + node)

        for a, b in edges:
            print('_convert_edge:', a, a.__class__, b, b.__class__)
            # replace powernodes by their string equivalent
            assert(a.__class__ is str and b.__class__ is str)
            # if reg_res_a is not None: # a is a powernode
                # a = subpowernode_to_powernode(a)
            # if reg_res_b is not None: # b is a powernode
                # b = subpowernode_to_powernode(b)
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
             for node in self.tops
            ),
            # include in container all nodes contained
            ('IN\t'
             + (contained if contained not in self.trivials
                else self.contains[contained]
               )
             + '\t'
             + container
             for container, contained in iteritems(self.contains)
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
            # create reflexives link of cliques
            ('EDGE\t' + powernode + '\t' + powernode + '\t1.0'
             for powernode in self.cliques
            ),
            # create link between remaining nodes
            ('EDGE\t' + node + '\t' + target + '\t1.0'
             for node, targets in iteritems(self.edges)
             for target in targets
            ),
        ))
