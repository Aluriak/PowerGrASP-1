"""
definition of the GML input format converter.

"""
from powergrasp.converter.input_converter import InConverter
import powergrasp.commons as commons
import itertools


LOGGER = commons.logger()


class InGML(InConverter):
    """Convert given GML file in uniformized data"""
    FORMAT_NAME = 'gml'
    FORMAT_EXTENSIONS = ('gml',)

    def _gen_edges(self, filename_gml):
        """Yields pair (node, successor), representing the data contained
        in input gml file.
        """
        try:
            from networkx import read_gml
            graph = read_gml(filename_gml)
            for node1, node2 in graph.edges():
                yield node1, node2
        except IOError as e:
            LOGGER.error(self.error_input_file(filename_sbml, e))
            exit(1)
        except ImportError:
            LOGGER.critical('networkx python module is necessary to'
                            ' use GML as input format')
            exit(1)
