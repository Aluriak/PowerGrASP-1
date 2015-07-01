# -*- coding: utf-8 -*-
"""
definition of the GML input format converter.
"""
from __future__   import absolute_import, print_function
from future.utils import iteritems, iterkeys, itervalues
from converter.input_converter import InConverter
import itertools
import commons


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

    # graph node returns a dict like that:
    # {0: {'id': 0, 'label': u'R_NADK'}}
    # {node_id: {'id': node_id, 'label': node_label}
    # definition of a id:label dict:
    names = {idn:val['label'] for idn, val in iteritems(graph.node)}

    # create all edges:
    for ida, idb in graph.edges():
        yield 'edge("' + names[ida] + '","' + names[idb] + '").'





