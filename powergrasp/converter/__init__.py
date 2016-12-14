"""
definitions of converter classes.

"""

from powergrasp.converter import inconverter
from powergrasp.converter import outconverter
from powergrasp.converter.bblwriter import BubbleWriter
from powergrasp import commons


LOGGER = commons.logger()
INPUT_FORMATS = tuple(inconverter.formats_converters())
OUTPUT_FORMATS = tuple(outconverter.formats_converters())
DEFAULT_OUTPUT_FORMAT = 'bbl'


def convert(is_input:bool, infile:str, outfile:str=None,
            format:str=None, oriented:bool=False) -> str:
    """Return the file containing input data formated in ASP-compliant format"""
    if format is None:
        if isinstance(infile, str):
            format = commons.extension(infile)
        elif isinstance(infile, dict):
            format = dict
        else:
            raise ValueError("Input file {} of type {} is not treatable."
                             "".format(infile, type(infile)))
    converter_module = (inconverter if is_input else outconverter)
    func = converter_module.converter_for(format)
    if not func:
        formats = ', '.join(str(f) for f in converter_module.formats_converters())
        error = ("given extension {} not recognized. Supported {}put formats "
                 "are {}. ".format(format, ('in' if is_input else 'out'), formats))
        LOGGER.error(error)
        raise ValueError(error)
    if is_input:
        return func(infile, outfile)
    else:  # oriented information is relevant only for output converters
        return func(infile, outfile, oriented=oriented)


def to_asp_file(input_filename:str, format:str=None) -> str:
    """Return a filename that contains graph found in given filename
    encoded in ASP.

    If given format is None, it will be inferred from file extension.
    If given input_filename is a dict, it will be read a mapping {pred: {succs}}.

    """
    aspfile = convert(is_input=True, infile=input_filename,
                      outfile=None, format=format)
    assert isinstance(aspfile, str)
    return aspfile


def bbl_to_output(bubblefile:str, outfile:str, format:str=None,
                  oriented:bool=False) -> str:
    """Overwrite and return given outfile with graph found in given bubble,
    encoded in given format.

    If given format is None, it will be inferred from file extension.

    """
    outfile = convert(is_input=False, infile=bubblefile,
                      outfile=outfile, format=format, oriented=oriented)
    assert isinstance(outfile, str)
    return outfile
