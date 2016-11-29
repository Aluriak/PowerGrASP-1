"""Definitions of output converter functions.

Converters are functions that convert an input bubble formated file
 to a new file containing the same data encoded in another format.

All converters expose the following parameters:

    bubblefile -- path to produced bubble file
    outfile -- path to file to overwrite with data
    validate -- True to first perform a validation of input bubble file

"""
import shutil
import powergrasp.commons as commons


VALIDATE_BUBBLE = True
LOGGER = commons.logger()


def formats_converters() -> dict:
    """Return the mapping {extension: converter function}."""
    return {
        'bbl': to_bbl,
        'dot': to_dot,
        'gexf': to_gexf,
    }

def converter_for(extension:str) -> callable:
    """Return a function that convert bubble file to file formatted with
    a format associated to given extension

    If given extension is not associated with any output converter,
    None is returned.

    """
    return formats_converters().get(extension)


def to_bbl(bubblefile:str, outfile:str, validate:bool=VALIDATE_BUBBLE):
    """Copy the file to target if necessary, else just return the same file"""
    if validate:
        validate_bubble(bubblefile)
    if bubblefile != outfile:
        shutil.copy(bubblefile, outfile)
    return outfile


def to_dot(bubblefile:str, outfile:str, validate:bool=VALIDATE_BUBBLE):
    """Convert input using bubbletools, return the new filename"""
    if validate:
        validate_bubble(bubblefile)
    get_bubbletools().convert.bubble_to_dot(bubblefile, dotfile=outfile)
    return outfile


def to_gexf(bubblefile:str, outfile:str, validate:bool=VALIDATE_BUBBLE):
    """Convert input using bubbletools, return the new filename"""
    if validate:
        validate_bubble(bubblefile)
    get_bubbletools().convert.bubble_to_gexf(bubblefile, gexffile=outfile)
    return outfile


def validate_bubble(bubblefile:str):
    """Perform a validation of given bubble file"""
    LOGGER.info("Validation of output bubble file…")
    for log in get_bubbletools().validate(bubblefile, profiling=True):
        LOGGER.info('\t' + log)
    LOGGER.info("Finished.")


def get_bubbletools():
    """Return the bubble tool package, or fails gracefully if not available"""
    try:
        import bubbletools
        return bubbletools
    except ImportError:
        LOGGER.error("Package bubbletools is not installed, thus bubble "
                     "validation and conversion to other output formats are "
                     "not available. Bubbletools is available on pypi: "
                     "pip install bubbletools.")
        exit(1)
