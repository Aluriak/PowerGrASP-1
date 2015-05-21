from __future__          import absolute_import
from converter.converter import NeutralConverter
from converter.nnf       import NNFConverter
from converter.bbl       import BBLConverter


# Link between format names and atom2format functions
OUTPUT_FORMATS = (
    'asp',
    'nnf',
    'bbl',
)

OUTPUT_FORMAT_CONVERTERS = {
    'asp' : NeutralConverter,
    'nnf' : NNFConverter,
    'bbl' : BBLConverter,
}

def converter_for(output_format):
    """Return function that take atoms and convert them to output format
    """
    assert(output_format in OUTPUT_FORMATS)
    return OUTPUT_FORMAT_CONVERTERS[output_format]()


