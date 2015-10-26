# -*- coding: utf-8 -*-
"""
definition of the SBML input format converter.

The data is used as follow:
    - species are nodes;
    - reactions are nodes;
    - an edge is created between each reaction node and each species involved in it;

"""
from powergrasp.converter.input_converter import InConverter
import itertools
import powergrasp.commons as commons


logger = commons.logger()
NAME_PREFIX = 'metacyc:'




class InSBML(InConverter):
    """Convert given SBML file in ASP file"""
    FORMAT_NAME = 'sbml'

    def _convert_to(self, filedesc_asp, filename_sbml):
        """Write in filedesc_asp the ASP version of the file named filename_sbml"""
        try:
            [filedesc_asp.write(line)
             for line in sbml_to_atom_generator(filename_sbml)
            ]
        except IOError:
            return self.error_input_file(inputfilename)
        except ImportError:
            return 'libsbml python module is necessary for use SBML as input format'




def sbml_to_atom_generator(filename):
    from libsbml import readSBML

    document = readSBML(filename);
    level    = document.getLevel()
    version  = document.getVersion()
    model    = document.getModel();

    if (model == None):
        print("No model present." )
        exit()



    # build dictionnary that link species id with its name
    species_name = {}
    for specie in model.getListOfSpecies():
        species_name[specie.getId()] = specie.getName().lstrip(NAME_PREFIX)
    # get reactions, produces all edges
    for reaction in model.getListOfReactions():
        name = reaction.getName().lstrip(NAME_PREFIX)
        products  = (species_name[p.getSpecies()] for p in reaction.getListOfProducts() )
        reactants = (species_name[p.getSpecies()] for p in reaction.getListOfReactants())
        for node in itertools.chain(products, reactants):
            yield 'edge("' + name + '","' + node + '").'



