# -*- coding: utf-8 -*-
"""
definition of the GML input format converter.

"""
from powergrasp.converter.input_converter import InConverter
import powergrasp.commons as commons
import itertools


LOGGER = commons.logger()


class InGML(InConverter):
    """Convert given GML file in ASP file"""
    FORMAT_NAME = 'gml'

    def _convert_to(self, filedesc_asp, filename_gml):
        """Write in filedesc_asp the ASP version of the file named filename_gml"""
        try:
            [filedesc_asp.write(line)
             for line in gml_to_atom_generator(filename_gml)
            ]
        except IOError:
            return self.error_input_file(inputfilename)
        except ImportError:
            return 'networkx python module is necessary for use GML as input format'


def gml_to_atom_generator(filename):
    from networkx import read_gml
    graph = read_gml(filename)
    for node1, node2 in graph.edges():
        yield 'edge("' + node1 + '","' + node2 + '").'
