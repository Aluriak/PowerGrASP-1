"""
definition of the ASP input format converter.

"""
import itertools

from powergrasp.converter.input_converter import InConverter
import powergrasp.commons as commons
from powergrasp import solving
from powergrasp import atoms

LOGGER = commons.logger()


class InASP(InConverter):
    """Convert given GML file in uniformized data"""
    FORMAT_NAME = 'asp'
    FORMAT_EXTENSIONS = ('lp',)

    def _gen_edges(self, filename):
        """Yields pair (node, successor), representing the data contained
        in input ASP file.
        """
        models = solving.model_from('', filename)
        try:
            for atom in models:
                if atom.predicate == 'edge' and atom.nb_args() == 2:
                    node, succ = atom.arguments
                    yield node, succ
        except IOError as e:
            LOGGER.error(self.error_input_file(filename_sbml, e))
        except TypeError:  # file is probably empty… so do the graph
            return
            yield
