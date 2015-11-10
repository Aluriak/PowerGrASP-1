# -*- coding: utf-8 -*-
__name__ = 'PowerGrASP'
__version__ = '0.3.5'


# link between filenames and studies
from collections import defaultdict
STUDYNAMES = defaultdict(lambda: 'No related study')
STUDYNAMES.update({
    'proteome_yeast_1'   : 'Casein Kinase II Complex',
    'proteome_yeast_2'   : 'Histone interaction',
    'structural_binding' : 'Interactions of SH3 Carrying Proteins',
    'phosphatase'        : 'Human Protein Tyrosine Phosphatase Homology Network',
})



