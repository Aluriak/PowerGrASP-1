# -*- coding: utf-8 -*-
"""
definitions of converter base class InConverter.

Converters are objects that convert a flow of ASP atoms
 in a particular string format.

Supported formats :
- asp: pure asp;
- nnf: nested network format;
- bbl: bubble format, used by Powergraph for printings;

"""
import itertools
import tempfile
import re
import os
from collections import defaultdict

from powergrasp import commons
from powergrasp import atoms
from powergrasp.commons import basename


LOGGER = commons.logger()
PREDICAT_TEMPLATE = 'edge({},{}).'


class InConverter(object):
    """Base class for Converters.

    Converters take an input format, and convert it in internal representation
    of the graph.
    InConverter returns empty graph by default.

    Subclasses should:
        define a class constant FORMAT_NAME giving the format name
        define a class constant FORMAT_EXTENSIONS giving an iterable of file
            extensions readable by the subclass.
        redefine the _gen_edges method.

    Another way to go is to redefine the convert method, which should return
    the filename containing all the input data in ASP-compliant format.

    """
    FORMAT_NAME = 'asp'
    FORMAT_EXTENSIONS = {''}


    def __init__(self, predicat_template=PREDICAT_TEMPLATE):
        self.predicat_name = str(predicat_template)


    def convert(self, filename:str) -> str:
        """Return a filename containing the graph found in given file,
        encoded in valid ASP.

        """
        try:
            with tempfile.NamedTemporaryFile('w', delete=False) as outfile:
                for node, succ in self._gen_edges(filename):
                    outfile.write(atoms.name_args_to_str('edge', (node, succ)))
                return outfile.name
        except (IOError, PermissionError):
            LOGGER.critical('File ' + outputfile + " can't be opened."
                            + ' Graph data retrieving needs this file.'
                            + ' Compression aborted.')
            exit(1)


    def _gen_edges(self, input_file:str) -> dict:
        """Yields pair (node, successor), representing the data contained
        in input file.

        The input file should have an extension defined
        in self.__class__.FORMAT_EXTENSIONS.

        This method is the only one that needs to be overrided
        by subclasses.

        """
        LOGGER.error('The InConverter._convert_to_dict method was called.'
                     ' Subclasses of InConverter should redefine this method.'
                     ' No data generated.')
        yield from ()


    @classmethod
    def error_input_file(cls, filename:str, exception:Exception=None) -> str:
        """return string error for not openable input file"""
        print('BLKQILW:', exception, dir(exception))  # TODO test that case
        exit()
        return ('File ' + filename + ' can\'t be opened as an '
                + self.FORMAT_NAME + ' file.'
                + ' Compression aborted')
