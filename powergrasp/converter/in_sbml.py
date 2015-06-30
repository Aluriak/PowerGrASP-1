# -*- coding: utf-8 -*-
"""
definition of the SBML input format converter.
"""
from __future__   import absolute_import, print_function
from future.utils import iteritems, iterkeys, itervalues
from converter.input_converter import InConverter
import itertools
import commons
from libsbml import readSBML


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
            self.error_input_file(inputfilename)




def sbml_to_atom_generator(filename):

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
    # d = [e for e in dir(model) if e.lower().startswith('getA')]
    # print(d)
    # print(dir(reactions))
    for reaction in model.getListOfReactions():
        name = reaction.getName().lstrip(NAME_PREFIX)
        products  = (species_name[p.getSpecies()] for p in reaction.getListOfProducts() )
        reactants = (species_name[p.getSpecies()] for p in reaction.getListOfReactants())
        for node in itertools.chain(products, reactants):
            yield 'edge("' + name + '","' + node + '").'


if __name__ == '__main__':
    print('\n'.join(sbml_to_atom_generator(sys.argv[1])))

