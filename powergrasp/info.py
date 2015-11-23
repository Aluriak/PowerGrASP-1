# -*- coding: utf-8 -*-
__name__    = 'PowerGrASP'
__fix       = '22'
__minor     = '3'
__major     = '0'
__version__ = '.'.join((__major, __minor, __fix))


# link between filenames and studies
from collections import defaultdict
STUDYNAMES = defaultdict(lambda: 'No related study')
STUDYNAMES.update({
    'proteome_yeast_1'   : 'Casein Kinase II Complex',
    'proteome_yeast_2'   : 'Histone interaction',
    'structural_binding' : 'Interactions of SH3 Carrying Proteins',
    'phosphatase'        : 'Human Protein Tyrosine Phosphatase Homology Network',
})



