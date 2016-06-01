"""
definition of the GraphML input format converter.

"""
from powergrasp.converter.input_converter import InConverter
import powergrasp.commons as commons
import itertools


LOGGER = commons.logger()


class InGraphML(InConverter):
    """Convert given GraphML file in uniformized data"""
    FORMAT_NAME = 'graphml'
    FORMAT_EXTENSIONS = ('graphml',)

    def _gen_edges(self, filename_graphml):
        """Yields pair (node, successor), representing the data contained
        in input graphml file.
        """
        try:
            from networkx import read_graphml
            graph = read_graphml(filename_graphml)
            for node1, node2 in graph.edges():
                yield node1, node2
        except IOError as e:
            LOGGER.error(self.error_input_file(filename_graphml, e))
            exit(1)
        except ImportError:
            LOGGER.critical('networkx python module is necessary to'
                            ' use GraphML as input format')
            exit(1)
