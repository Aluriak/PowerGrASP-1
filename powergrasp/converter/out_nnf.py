# -*- coding: utf-8 -*-
"""
definition of the NNF format converter.

"""
from powergrasp.converter.output_converter import OutConverter
import powergrasp.commons as commons
import itertools


logger = commons.logger()

class OutNNF(OutConverter):
    """Convert given atoms in NNF format"""

    def _convert(self, powernodes, cliques):
        """Operate convertion on given atoms"""
        # get first item for obtain global data
        cc, k, s, node = next(atoms)
        atoms = itertools.chain( ((cc,k,s,node),), atoms )

        # generate lines
        nnf = ('{0}_{1}_{2}\t{3}'.format(*g) for g in atoms)
        return itertools.chain(
            nnf,
            ('{0}_{1}\t{2}_{3}_{4}\tpp\t{5}_{6}_{7}'.format(cc,k,cc,k,1,cc,k,2),),
            ('{0}_cc\t{1}_{2}'.format(cc,cc,k),),
        )

    def _convert_edge(self, atoms):
        """Perform the convertion and return its results"""
        # get first item for obtain global data
        cc, k, s = next(atoms)
        atoms = itertools.chain( ((cc,k,s),), atoms )

        # generate lines
        nnf = ('{0}\tpp\t{2}'.format(*g) for g in atoms)
        return nnf

