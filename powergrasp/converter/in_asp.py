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

    def convert(self, filename:str) -> str:
        """If input is ASP, there is no need to convert it.
        This method skip the edge generation and directly
        return the given file.

        """
        return filename
