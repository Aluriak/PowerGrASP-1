# -*- coding: utf-8 -*-
"""
definition of the SBML input format converter.

The data is used as follow:
    - species are nodes;
    - reactions are nodes;
    - an edge is created between each reaction node and each species involved in it;

"""
import itertools

from powergrasp import commons
from powergrasp.converter.input_converter import InConverter


LOGGER = commons.logger()
NAME_PREFIX = 'metacyc:'


class InSBML(InConverter):
    """Convert given SBML file in ASP file"""
    FORMAT_NAME = 'sbml'
    FORMAT_EXTENSIONS = ('sbml',)

    def _gen_edges(self, filename_sbml:str) -> dict:
        """Yields pair (node, successor), representing the data contained
        in input sbml file.
        """
        try:
            yield from sbml_to_atom_generator(filename_sbml)
        except IOError as e:
            LOGGER.error(self.error_input_file(filename_sbml, e))
        except ImportError:
            LOGGER.error("libsbml module is necessary for use SBML as input"
                         " format. 'pip install libsbml' should do the job."
                         " Compression aborted.")
            exit(1)
        return  # empty generator pattern
        yield


def sbml_to_atom_generator(filename:str) -> dict:
    from libsbml import readSBML

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

    if (model == None):
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
