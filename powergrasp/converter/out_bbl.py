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
from powergrasp.commons  import basename
from powergrasp.converter.output_converter import OutConverter
import powergrasp.commons as commons
import powergrasp.solving as solving
import powergrasp.atoms   as atoms
import powergrasp.info    as info
import itertools


logger         = commons.logger()
ASP_INCLUSION  = ['powergrasp/ASPsources/inclusion.lp']
GRINGO_OPTIONS = '--warn=no-atom-undefined'
GRINGO_OPTIONS = ''


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


class OutBBL(OutConverter):
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
    META_DATA = (
        "File written by the " + info.__name__
        + " module (" + info.__version__ + ")"
    )

    def __init__(self):
        try: # python 3
            super().__init__()
        except TypeError: # python 2
            super(OutBBL, self).__init__()
        self.release_memory()  # initialize the containers

    def release_memory(self):
        """When the data is generated, all containers can be freed
        for memory occupation optimization.

        Initialize all containers.
        """
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
        # linking between nodes
        self.edges      = defaultdict(set)
        self.belongs    = dict()

    def _convert(self, atoms):
        """Accumulate atoms"""
        return atoms

    def _additionnal_data_from(self):
        """Collect additionnal data on atoms,
        notabily on direct inclusion and triviality.

        New atoms are generated and returned.

            powernodes -- ASP source code that contains
                atoms like 'powernode(cc,k,t,x).'

        Returns many generators:
            powernode -- powernodes that are contained by nothing
            poweredge -- poweredges that links powernode and {power,}node
            clique -- powernodes that are cliques
            edge -- edges that links elements between nodes
            top -- powernodes that are contained by nothing
            topnode -- nodes that are contained by nothing
            trivial -- powernodes that contains only one element
            include_pwrn -- powernode that include a powernode
            include_node -- powernode that include a node

        """
        # create solver
        input_atoms = atoms.to_str(self.atoms)
        new_atoms = solving.model_from(input_atoms, ASP_INCLUSION, gringo_options=GRINGO_OPTIONS)
        if new_atoms is None:
            logger.critical("no model generated by inclusion.lp ASP program")
            logger.critical(input_atoms)
            assert(new_atoms is not None)
        logger.debug('DEBUG INCLUSION: input     == ' + input_atoms)
        logger.debug('DEBUG INCLUSION: new_atoms == ' + str(new_atoms))
        new_atoms = tuple(atoms.split(a) for a in new_atoms)
        return (
            ((str(_) for _ in arg) for name, arg in new_atoms if name == 'powernode'),
            ((str(_) for _ in arg) for name, arg in new_atoms if name == 'poweredge'),
            ((str(_) for _ in arg) for name, arg in new_atoms if name == 'clique'),
            ((str(_) for _ in arg) for name, arg in new_atoms if name == 'edge'),
            ((str(_) for _ in arg) for name, arg in new_atoms if name == 'top'),
            ((str(_) for _ in arg) for name, arg in new_atoms if name == 'topnode'),
            ((str(_) for _ in arg) for name, arg in new_atoms if name == 'trivial'),
            ((str(_) for _ in arg) for name, arg in new_atoms if name == 'include_pwrn'),
            ((str(_) for _ in arg) for name, arg in new_atoms if name == 'include_node'),
        )

    def _generate_metadata(self):
        """assign to self metadata about knowed atoms.

        Metadata will be used by finalized method.
        """
        # get additionnal data
        powernodes, poweredges, cliques, edges, tops, topnodes, trivials, inclusions_powernode, inclusions_node = (
            self._additionnal_data_from()
        )

        # cliques cc, step (powernode cc,step is a clique)
        for cc, step in cliques:
            assert(int(step) > 0)
            self.cliques.add(powernode(cc, step, '1'))
            logger.debug('CLIQUE:' + powernode(cc, step, '1'))

        # edges a, b (there is an edge between a and b)
        for a, b in edges:
            assert(a.__class__ is str and b.__class__ is str)
            self.edges[a].add(b)
            logger.debug('EDGE:' + a + ' to ' + b)

        # edges a, b (there is an edge between a and b)
        for payload in poweredges:
            payload = tuple(payload)
            if len(payload) == 5: # powernode linked to powernode
                cc, k1, t1, k2, t2 = payload
                a = powernode(cc, k1, t1)
                b = powernode(cc, k2, t2)
            else:  # powernode linked to a node
                assert(len(payload) == 4)
                cc, k, t, node = payload
                a = powernode(cc, k, t)
                b = node
            assert(a.__class__ is str and b.__class__ is str)
            self.edges[a].add(b)
            logger.debug('POWEREDGE:' + a + ' to ' + b)

        # trivial cc, step, num_set (a powernode contains only one node)
        for cc, step, num_set in trivials:
            assert(int(step) > 0)
            assert(num_set in ('1', '2'))
            assert(powernode(cc,step,num_set) not in self.trivials)
            self.trivials.add(powernode(cc,step,num_set))
            logger.debug('TRIVIAL:' + powernode(cc,step,num_set))

        # include cc1, step1, num_set1, cc2, step2, num_set2
        #  (powernode2 is in powernode1)
        for cc1, step1, num_set1, cc2, step2, num_set2 in inclusions_powernode:
            assert(int(step1) > 0 and int(step2) > 0)
            assert(num_set1 in ('1', '2') and num_set2 in ('1', '2'))
            pwrn1 = powernode(cc1, step1, num_set1)
            pwrn2 = powernode(cc2, step2, num_set2)
            if not (pwrn2 not in self.belongs):
                logger.error("ABNORMAL SITUATION: assert(pwrn2 not in self.belongs) FAILED. WITH:")
                logger.error('PWRN1:' + pwrn1)
                logger.error('PWRN2:' + pwrn2)
                logger.error('BELONGS:' + str(self.belongs))
                # assert(pwrn2 not in self.belongs)
            self.belongs[pwrn2] = pwrn1
            logger.debug('INC_PWRN:' + pwrn1 + " contains " + pwrn2)
            self.contains[pwrn1].add(pwrn2)

        # include cc, step, num_set, node
        #  (node is in powernode cc,step,num_set)
        contained = set()
        for cc, step, num_set, node in inclusions_node:
            assert(int(step) > 0)
            assert(num_set in ('1', '2'))
            assert(node not in contained) # False iff cliques are not properly managed
            contained.add(node)
            self.nodes.add(node)
            pwrn = powernode(cc, step, num_set)
            assert(node not in self.belongs)
            self.belongs[node] = pwrn
            self.contains[pwrn].add(node)
            logger.debug('INC_NODE:' + pwrn + ' contains ' + node)

        # top cc, step, num_set (a powernode is contained by nothing)
        for node in topnodes:
            self.tops.add(node[0])
            logger.debug('TOP:' + node[0])

        # top cc, step, num_set (a powernode is contained by nothing)
        for cc, step, num_set in tops:
            self.tops.add(powernode(cc,step,num_set))
            logger.debug('TOP:' + cc + step + num_set)

    def header(self):
        return '#BBL-1.0\n#' + OutBBL.META_DATA + '\n'

    def finalized(self):
        self._generate_metadata()
        # define NODEs, SETs, INs and EDGEs relations, and return them
        return '\n' + '\n'.join(itertools.chain(
        # NODEs
            ('NODE\t' + node for node in self.nodes),
        # SETs
            # defines all powernodes
            ('SET\t' + pwnd + '\t1.0'
             for pwnd in self.pwnds
            ),
            # defines all trivial powernodes
            # NB: trivial powernodes are not accepted by
            #   powergraph cytoscape plugin. Trivials must be replaced by components
            ('SET\t' + pwnd + '\t1.0'
             for pwnd in self.trivials
            ),
        # INs
            # include in container all nodes contained
            ('IN\t'
             + (contained if contained not in self.trivials
                else next(iter(self.contains[contained]))
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
