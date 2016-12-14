"""Definitions of input converter functions.

Converters are functions that convert an input non-ASP formated file
 to a new file containing the same data encoded in ASP edge/2 atoms.

All converters should (1) be decorated by edge_generator(), and
(2) expose the following parameters:

    infile -- path to produced bubble file

Then, a converter yields pairs of nodes (a,b) for each edge between a and b
in graph found in input file.

Another way to go is to (1) not be decorated by edge_generator(), and
(2) expose the following supplementary parameter:

    outfile -- path to file to write, or None if a temp file should be used.

and (3) directly return the name of the file written with edge/2 atoms.
Then, the converter should write the atoms in a file by itself.

"""
import re
import shutil
import tempfile
import itertools
import functools
from powergrasp import commons


LOGGER = commons.logger()
PREDICAT_TEMPLATE = 'edge({},{}).'


def formats_converters() -> dict:
    """Return the mapping {extension: converter function}."""
    return {
        'lp': from_lp,
        'gml': from_gml,
        'graphml': from_graphml,
        'sbml': from_sbml,
        dict: from_dict,
    }

def converter_for(extension:str) -> callable:
    """Return a function that convert file formatted with
    a format associated to given extension to an ASP-compliant file.

    If given extension is not associated with any output converter,
    None is returned.

    """
    return formats_converters().get(extension)


def edge_generator(edges_from:callable):
    """Decorator casting a function infile -> iter(edges) to
    a function infile -> outputfile

    edges_from -- a callable infile -> iter(edges)

    """
    functools.wraps(edges_from)
    def wrapper(infile:str, outfile:str=None):
        """Put atoms edge/2 in outfile according to graph found in infile"""
        if outfile:
            fd = open(outfile, 'w')
        else:  # no outfile given
            fd = tempfile.NamedTemporaryFile('w', delete=False)
        outfile = str(fd.name)
        for pred, succ in edges_from(infile):
            fd.write(PREDICAT_TEMPLATE.format(
                commons.to_asp_value(pred),
                commons.to_asp_value(succ)
            ))
        fd.close()
        return outfile
    return wrapper


def from_lp(infile:str, outfile:str=None):
    """Input file contains already ASP formated data."""
    if outfile and infile != outfile:
        shutil.copy(infile, outfile)
    return infile


@edge_generator
def from_gml(infile:str) -> iter:
    """Yield pairs of nodes (a,b) when there is an edge between a and b
    in graph found in given gml file

    Use networkx to read the input file.

    """
    try:
        from networkx import read_gml
        for node1, node2 in read_gml(infile).edges():
            yield node1, node2
    except ImportError:
        LOGGER.critical('networkx python module is necessary to'
        ' use GML as input format.')
        exit(1)


@edge_generator
def from_graphml(infile:str) -> iter:
    """Yield pairs of nodes (a,b) when there is an edge between a and b
    in graph found in given graphml file

    Use networkx to read the input file.

    """
    try:
        from networkx import read_graphml
        graph = read_graphml(infile)
        for node1, node2 in graph.edges():
            yield node1, node2
    except ImportError:
        LOGGER.critical('networkx python module is necessary to'
                        ' use GraphML as input format.')
        exit(1)


@edge_generator
def from_sbml(infile:str) -> iter:
    """Yield pairs of nodes (a,b) when there is an edge between a and b
    in graph found in given sbml file

    Use libsbml to read the input file.

    The data is used as follow:
        - species are nodes;
        - reactions are nodes;
        - an edge is created between each reaction node and
          each species involved in it;

    """
    try:
        from libsbml import readSBML
    except ImportError:
        LOGGER.error("libsbml module is necessary for use SBML as input"
                     " format. `pip install python-libsbml` should do "
                     "the job. Compression aborted.")
        exit(1)

    document = readSBML(filename)
    level    = document.getLevel()
    version  = document.getVersion()
    model    = document.getModel()

    LOGGER.info('libsbml found a SBML data of level ' + str(level)
                + ' and of version ' + str(version) + '.')

    # print lib fatal error of the libsbml
    errors = (document.getError(idx) for idx in itertools.count())
    errors = (err for err in itertools.takewhile(lambda e: e is not None, errors)
              if err.isError() or err.isFatal())
    for error in errors:
        LOGGER.error('libsbml error on input file: ' + error.getMessage().strip())

    if (model is None):
        LOGGER.error('libsbml: No model found in file ' + filename + '.' )
        exit(1)

    # build dictionnary that link species id with its name
    species_name = {}
    for specie in model.getListOfSpecies():
        species_name[specie.getId()] = specie.getName().lstrip(NAME_PREFIX)

    # get reactions, produces all edges in the outputed dict
    for reaction in model.getListOfReactions():
        name = reaction.getName().lstrip(NAME_PREFIX)
        products  = (species_name[p.getSpecies()] for p in reaction.getListOfProducts() )
        reactants = (species_name[p.getSpecies()] for p in reaction.getListOfReactants())
        for node in itertools.chain(products, reactants):
            yield name, node


@edge_generator
def from_dict(graph_dict):
    """convert {node: succs} to pairs (X, Y), where X is a node
    and Y its successor in the graph.

    """
    for node, succs in graph_dict.items():
        for succ in succs:
            yield node, succ
