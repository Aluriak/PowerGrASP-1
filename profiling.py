from timeit import timeit
from time import time as now
from functools import partial

import powergrasp as p

DIR_TESTS = './powergrasp/tests/'

FILE = DIR_TESTS + 'structural_binding.lp'  # sbind
FILE = DIR_TESTS + 'big_biclique.lp'
FILE = DIR_TESTS + 'big_biclique_merged.lp'
FILE = DIR_TESTS + 'double_biclique.lp'  # ddiam
# FILE = DIR_TESTS + './rrel_chr1_chr38.lp'  # chr

p.compress(
    graph_data=FILE,
    output_file='./powergrasp/data/output.bbl',
    loglevel='warning',
)
print('Compression finished !')
