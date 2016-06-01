"""
definitions of converter classes.

"""

import inspect

from powergrasp.converter.output_converter import OutConverter
from powergrasp.converter.input_converter  import InConverter
from powergrasp.converter.out_nnf          import OutNNF
from powergrasp.converter.out_bbl          import OutBBL
from powergrasp.converter.in_sbml          import InSBML
from powergrasp.converter.in_gml           import InGML
from powergrasp.converter.in_asp           import InASP
from powergrasp import commons


LOGGER = commons.logger()

# Link between format names and atom2format functions
INPUT_FORMAT_CONVERTERS = {
    ext: cls
    for cls_id, cls in globals().items()
    if inspect.isclass(cls) and issubclass(cls, InConverter)
    for ext in cls.FORMAT_EXTENSIONS
}
OUTPUT_FORMAT_CONVERTERS = {
    ext: cls
    for cls_id, cls in globals().items()
    if inspect.isclass(cls) and issubclass(cls, OutConverter)
    for ext in cls.FORMAT_EXTENSIONS
}

INPUT_FORMATS  = tuple(INPUT_FORMAT_CONVERTERS.keys())
OUTPUT_FORMATS = tuple(OUTPUT_FORMAT_CONVERTERS.keys())
DEFAULT_OUTPUT_FORMAT = 'bbl'


# converters access
def output_converter_for(format): return converter_for(format, is_output=True)
def  input_converter_for(format): return converter_for(format, is_output=False)
def delete_temporary_file(): return InConverter.delete_temporary_file()


def converter_for(format, is_output):
    """Return function that take atoms and convert them to input format or None
    """
    formats = OUTPUT_FORMAT_CONVERTERS if is_output else INPUT_FORMAT_CONVERTERS
    if format not in formats:
        LOGGER.error(
            "given extension " + str(format) + " not recognized. "
            + 'Supported ' + ('output' if is_output else 'input')
            + (' formats are ' + ', '.join(str(_) for _ in formats) + '.')
        )
        return None
    else:
        return formats[format]()


def to_asp_file(input_filename, format=None):
    """Return a dictionnary {node: succ} that contains data in input file"""
    if format is None:
        format = commons.extension(input_filename)
    return input_converter_for(format).convert(input_filename)
