"""
definitions of converter classes.

Supported formats :
- asp: pure asp;
- nnf: nested network format;
- bbl: bubble format, used by Powergraph for printings;

"""
from powergrasp.converter.output_converter import OutConverter
from powergrasp.converter.input_converter  import InConverter
from powergrasp.converter.out_nnf          import OutNNF
from powergrasp.converter.out_bbl          import OutBBL
from powergrasp.converter.in_sbml          import InSBML
from powergrasp.converter.in_gml           import InGML
import powergrasp.commons as commons


LOGGER = commons.logger()

# Link between format names and atom2format functions
INPUT_FORMAT_CONVERTERS = {
    'lp'   : InConverter,
    'sbml' : InSBML,
    'gml'  : InGML,
}
OUTPUT_FORMAT_CONVERTERS = {
    'asp' : OutConverter,
    'bbl' : OutBBL,
    'nnf' : OutBBL,
}

INPUT_FORMATS  = tuple(INPUT_FORMAT_CONVERTERS.keys())
OUTPUT_FORMATS = tuple(OUTPUT_FORMAT_CONVERTERS.keys())
DEFAULT_OUTPUT_FORMAT = 'bbl'


# converters access
def output_converter_for(format): return converter_for(format,  True)
def  input_converter_for(format): return converter_for(format, False)
def delete_temporary_file(): return InConverter.delete_temporary_file()


def converter_for(format, is_output):
    """Return function that take atoms and convert them to input format or None
    """
    return __non_valid_format_handling(
        format,
        OUTPUT_FORMAT_CONVERTERS if is_output else INPUT_FORMAT_CONVERTERS,
        is_output
    )

def __non_valid_format_handling(format, formats, is_output):
    """Return instance of converter if format is valid, else None"""
    if format not in formats:
        LOGGER.error("given extension " + format + " not recognized. "
                     + 'Supported ' + ('output' if is_output else 'input')
                     + (' formats are ' + ', '.join(formats) + '.')
                    )
        return None
    else:
        return formats[format]()


