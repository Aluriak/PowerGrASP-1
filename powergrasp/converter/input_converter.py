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
from __future__   import absolute_import, print_function
import itertools
import commons
import re
import os


logger = commons.logger()

FILE_INPUT_ASP_NAME = 'data/tmp_input_converted.lp'



class InConverter(object):
    """Base class for Converters.

    Converters take an input format, and convert it in ASP atoms (gringo.Fun).

    InConverter is useless as is :
     it reads ASP output.

    """
    FORMAT_NAME = 'asp'

    def convert(self, filename):
        """Read the given file, and put in the returned file
        the equivalent asp data.
        """
        try:
            with open(FILE_INPUT_ASP_NAME, 'w') as fd:
                # NB: opening the file is performed by the subclass, while some
                #  format use an external module that opens itself the file
                #  for extract data.
                error = self._convert_to(fd, filename)
                if error is not None:
                    logger.error(error)
        except IOError:
            logger.critical('File ' + FILE_INPUT_ASP_NAME + " can't be opened."
                            + ' Convertion to ASP data need this file.'
                            + ' Compression aborted')
            return None
        return FILE_INPUT_ASP_NAME

    @staticmethod
    def delete_temporary_file():
        os.remove(FILE_INPUT_ASP_NAME)

    @classmethod
    def error_input_file(cls, filename):
        """return string error for not openable input file"""
        return ('File ' + filename + ' can\'t be opened as an '
                + self.FORMAT_NAME + ' file.'
                + ' Compression aborted')

    def _convert_to(self, filedesc_asp, inputfilename):
        """Write in filedesc_asp the ASP version of filedesc_input

        Return None, or a logging string if something bad happens.
        """
        try:
            with open(inputfilename, 'r') as fd:
                [filedesc_asp.write(line) for line in fd]
        except IOError:
            return self.error_input_file(inputfilename)




