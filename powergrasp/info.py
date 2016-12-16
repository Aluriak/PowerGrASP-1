"""
Some meta informations about the package.

"""


PROGRAM_NAME    = 'PowerGrASP'
PACKAGE_NAME    = PROGRAM_NAME.lower()
__fix           = '4'
__minor         = '5'
__major         = '0'
PACKAGE_VERSION = '.'.join((__major, __minor, __fix))


# link between filenames and studies
from collections import defaultdict
STUDYNAMES = defaultdict(lambda: 'No related study')
STUDYNAMES.update({
    'proteome_yeast_1'   : 'Casein Kinase II Complex',
    'proteome_yeast_2'   : 'Histone interaction',
    'structural_binding' : 'Interactions of SH3 Carrying Proteins',
    'phosphatase'        : 'Human Protein Tyrosine Phosphatase Homology Network',
})
