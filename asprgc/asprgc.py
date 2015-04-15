# -*- coding: utf-8 -*-
"""
TOWRITE
"""
from __future__ import print_function, absolute_import
from aspsolver  import ASPSolver
import itertools
import commons



logger = commons.logger('asprgc')



def asprgc(graph, extract, findcc):
    # Extract graph data
    logger.info('#### EXTRACT ####')
    extractor = ASPSolver().use(graph).use(extract)
    graph_atom = extractor.first_solution()
    # graph data is an ASP code that describes graph and connected components.
    graph_data = '.\n'.join(str(graph_atom).replace('new', '').split(' ')) + '.'
    logger.info('graph: ' + graph_data)
    # graph data:
    # atom_ccs  = (('cc', a.args()) 
    atom_ccs  = (a.args() 
                 for a in graph_atom.atoms() 
                 if a.name() == 'newcc'
                )
    # atom_path = ((a.name(), a.args()) 
                 # for a in graph_atom.atoms() 
                 # if a.name() == 'connectedpath'
                # )
    # atom_edge = (('ccedge', a.args()) 
                 # for a in graph_atom.atoms() 
                 # if a.name() == 'newccedge'
                # )
    # atom_graph = list(itertools.chain(atom_edge, atom_path))

    # Find connected components
    logger.info('#### FIND CC ####')
    # for _, cc in atom_ccs: 
    for cc in atom_ccs: 
        # collect edges in the CC
        print('GRAPH:\n\t', graph_data.replace('\n', '\n\t'), sep='')
        cc_finder = ASPSolver().read(graph_data)
        cc_finder = cc_finder.use(findcc, cc)
        print('SOLUTION:\n', cc_finder.first_solution())
        # logger.info('ccs: ' + str(cc_finder.first_solution()))

    
    # return str(graph)




