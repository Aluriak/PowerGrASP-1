"""Definition of the bubble format writer.

A bubble format file, is structured in four parts:
    - list of nodes
    - list of powernodes
    - containers and contained
    - edges

There is a grammar that can be associated:
S     ::= LINE . S + FF
LINE  ::= NODES + SETS + INS + EDGES + COMMENTS
NODES ::= 'NODE\t' . node_name      . '\n'
SETS  ::= 'SET\t'  . powernode_name . '\t' . coefficient . '\n'
INS   ::= 'IN\t'   . contained      . '\t' . container   . '\n'
EDGES ::= 'EDGE\t' . elementA       . '\t' . elementB    . '\t' . coefficient . '\n'
COMS  ::= '#' . "[^\n]*" . '\n'

Coefficient are currently set to 1.0, and no tests have been performed,
so we don't know what is the purpose of it.
For contained and container, only the direct inclusion must be provided.
The order of the parts/lines can be changed.
Comments are marked by '#' character.

The Cytoscape plugin CyOoG is able to read and print that format.

"""
import itertools
from collections import defaultdict

from powergrasp import info
from powergrasp import commons
from powergrasp import solving


logger         = commons.logger()
GRINGO_OPTIONS = '--warn=no-atom-undefined'
GRINGO_OPTIONS = ''


def to_bubble_value(value:str) -> str:
    """Return input value with quotes if they are necessary"""
    INCOMPLIANT_BUBBLE_CHARS = ' ?#\t\n'
    if any(char in value for char in INCOMPLIANT_BUBBLE_CHARS):
        return commons.quoted(value)
    else:
        return ''.join(c for c in value if c not in '"')


def powernode(cc, step, num_set):
    """Return string representation of powernode of given cc, step and set nb.

    This string representation is not ASP valid,
     but can be used as name in most file formats :

        PWRN-<cc>-<step>-<num_set>

    """
    return 'PWRN-{}-{}-{}'.format(cc, step, num_set)


class BubbleWriter:
    """Convert given atoms in BBL format

    Used bubble format is Bubble V1.0,
     and is used by Powergraph module of BIOTEC
     for save the powernodes cytoscape representation.

    Because of the complexity of the format,
     the complexity is higher than NNFConverter.
     The convert operation stores all atoms without treatment,
      and, for big graphs, performed treatments could be heavy.
    An ASP solver is used for perform complex treatments.

    """
    META_DATA = (
        "File written by the " + info.__name__
        + " module (" + info.PACKAGE_VERSION + ")"
    )


    def __init__(self, filedesc:'file'):
        assert filedesc.write, "given filedesc object is not a file descriptor."
        self.fd = filedesc
        self._reset_containers()


    def write_atoms(self, atoms:str):
        """Write information contains in given atoms.

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


    def write_header(self) -> str:
        """Return header of the file, and write it to output file"""
        header = '#BBL-1.0\n#' + BubbleWriter.META_DATA
        self.fd.write(header)
        return header

    def write_comment(self, lines) -> str:
        """Add given iterable of lines as comments, return it"""
        comments = lines if isinstance(lines, str) else '\n# '.join(lines)
        self.fd.write('\n# ' + comments)
        return comments


    def finalize_cc(self):
        """Compute data, write it as bubble and be ready for the next wave"""
        self._populate_containers()
        self._write_bubble()
        self._reset_containers()


    @property
    def filename(self) -> str:
        """Return the path to the file that is written"""
        return self.fd.name


    def _reset_containers(self):
        """When the data is generated, all containers can be freed
        for memory occupation optimization.

        Initialize all containers.
        """
        # nodes
        self.atoms      = ''
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


    def _parse_atoms(self):
        """Collect data from atoms,
        including direct inclusion and triviality.

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
        input_atoms = self.atoms
        new_atoms = solving.model_from(input_atoms, aspconfig=solving.DEFAULT_CONFIG_INCLUSION())
        if new_atoms is None:
            error = "No model generated by inclusion.lp ASP program"
            logger.critical(error)
            logger.critical(input_atoms)
            assert new_atoms is not None, error
        logger.debug('DEBUG INCLUSION: input     == ' + input_atoms)
        logger.debug('DEBUG INCLUSION: new_atoms == ' + str(new_atoms))
        new_atoms = tuple(iter(new_atoms))
        return (
            ((to_bubble_value(_) for _ in arg) for name, arg in new_atoms if name == 'powernode'),
            ((to_bubble_value(_) for _ in arg) for name, arg in new_atoms if name == 'poweredge'),
            ((to_bubble_value(_) for _ in arg) for name, arg in new_atoms if name == 'clique'),
            ((to_bubble_value(_) for _ in arg) for name, arg in new_atoms if name == 'edge'),
            ((to_bubble_value(_) for _ in arg) for name, arg in new_atoms if name == 'top'),
            ((to_bubble_value(_) for _ in arg) for name, arg in new_atoms if name == 'topnode'),
            ((to_bubble_value(_) for _ in arg) for name, arg in new_atoms if name == 'trivial'),
            ((to_bubble_value(_) for _ in arg) for name, arg in new_atoms if name == 'include_pwrn'),
            ((to_bubble_value(_) for _ in arg) for name, arg in new_atoms if name == 'include_node'),
        )



    def _populate_containers(self):
        """Fill the containers with data found in atoms."""
        # get additionnal data
        (powernodes, poweredges, cliques,
         edges, tops, topnodes, trivials,
         inclusions_powernode, inclusions_node) = self._parse_atoms()

        # cliques cc, step (powernode cc,step is a clique)
        for cc, step in cliques:
            assert(int(step) > 0)
            self.cliques.add(powernode(cc, step, '1'))
            logger.debug('CLIQUE:' + powernode(cc, step, '1'))

        # edges a, b (there is an edge between a and b)
        for a, b in edges:
            assert(a.__class__ is str and b.__class__ is str)
            if a > b:
                a, b = b, a
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
            assert node not in self.belongs
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


    def _write_bubble(self):
        """Write the bubble itself in self file descriptor"""
        self.fd.write('\n' + '\n'.join(itertools.chain(
        # NODEs
            ('NODE\t' + node for node in self.nodes),
        # SETs
            # defines all powernodes
            ('SET\t{}\t1.0'.format(pwnd) for pwnd in self.pwnds),
            # defines all trivial powernodes
            # NB: trivial powernodes are not accepted by
            #   powergraph cytoscape plugin. Trivials must be replaced
            #   earlier by data generation
            ('SET\t{}\t1.0'.format(pwnd) for pwnd in self.trivials),
        # INs
            # include in container all nodes contained
            ('IN\t{}\t{}'.format((contained if contained not in self.trivials
                                  else next(iter(self.contains[contained]))),
                                 container)
             for container, containeds in self.contains.items()
             for contained in containeds),
        # EDGEs
            # create reflexives edges for cliques
            ('EDGE\t{}\t{}\t1.0'.format(clique, clique)
             for clique in self.cliques),
            # create edges
            ('EDGE\t{}\t{}\t1.0'.format(node, target)
             for node, targets in self.edges.items()
             for target in targets),
        )))
