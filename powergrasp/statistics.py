# -*- coding: utf-8 -*-
"""
Definitions of many functions that works on compressions statistics.

Statistics are mainly a dictionnary with statistics information inside.

Information is itself a dict that links different parameters
 (number of initial edge, number of power{node,edge},…)
 to the value used for compute statistics.

Statistics information can be printed or saved in files
 in raw or latex tabular format.

"""

from __future__   import absolute_import, print_function
from __future__   import division
from future.utils import iteritems, itervalues


# INFORMATION KEYS
INIT_EDGE = 'initial_edge_count'
FINL_EDGE = 'final_edge_count'
FINL_PWED = 'final_poweredge_count'
FINL_PWND = 'final_powernode_count'
CONV_RATE = 'conversion_rate'
EDGE_RDCT = 'edge_reduction'
COMP_RTIO = 'compression_ratio'
ALL_FIELD = (CONV_RATE, EDGE_RDCT, COMP_RTIO,
             INIT_EDGE, FINL_EDGE, FINL_PWND, FINL_PWED)

# global data
NETW_NAME = 'network_name'

# FORMATS
FORMAT_TEX = 'tex'
FORMAT_RAW = 'txt'


# FUNCTIONS

def container(network_name='network'):
    """Return a new container of statistics information"""
    return {
        NETW_NAME: network_name,
        INIT_EDGE: None,
        FINL_EDGE: None,
        FINL_PWED: None,
        FINL_PWND: None,
    }


def add(stats, initial_edge_count=None, final_poweredge_count=None,
        final_edge_count=None, final_powernode_count=None):
    """set to given stats the given values.

    if a value is None, it will be not modified.
    stats is modified in place.
    """
    assert(stats.__class__ == dict)
    keytovar = {
        INIT_EDGE: initial_edge_count,
        FINL_EDGE: final_edge_count,
        FINL_PWED: final_poweredge_count,
        FINL_PWND: final_powernode_count,
    }
    for info, value in iteritems(keytovar):
        if value is not None:
            if stats[info] is not None:
                stats[info] += value
            else:  # first time the value is assigned
                stats[info]  = value


def save(filename, stats, format=FORMAT_TEX, erase=False):
    """Saves given stats in given filename in given format.

    format can be one of available format. Default is tabular in tex.
    if erase is True, existing content of filename will be erased.
    """
    # produce and save data
    with open(filename, ('w' if erase else 'a')) as fd:
        f.write(output(stats, format))


def output(stats, format=FORMAT_RAW):
    """Return given stats as string in given format.

    format can be one of available format. Default is raw text.
    """
    return _final_data(stats, format)




def _final_data(stats, format):
    """Compute and produce all given stats in string."""
    data = dict(stats)
    assert(stats[INIT_EDGE] is not None)
    assert(stats[FINL_EDGE] is not None)
    assert(stats[FINL_PWND] is not None)
    assert(stats[FINL_PWED] is not None)

    data[CONV_RATE] = _conversion_rate(
        stats[INIT_EDGE], stats[FINL_EDGE], stats[FINL_PWED], stats[FINL_PWND]
    )
    data[EDGE_RDCT] = _edge_reduction(
        stats[INIT_EDGE], stats[FINL_EDGE], stats[FINL_PWED]
    )
    data[COMP_RTIO] = _compression_ratio(
        stats[INIT_EDGE], stats[FINL_EDGE], stats[FINL_PWED]
    )

    return _formatted(data, format)


def _formatted(data, format):
    """Return a string formatted in given format that represent the given data.

    """
    fdata = ''
    if format == FORMAT_RAW:
        fdata = data[NETW_NAME] + ':'
        for field in ALL_FIELD:
            fdata += '\n\t' + field + ': ' + str(data[field])
    elif format == FORMAT_TEX:
        header  = 'network'
        payload = data[NETW_NAME]
        for field in ALL_FIELD:
            header  += ' & ' + field
            payload += ' & ' + str(data[field])
        header  += '\\\\'
        payload += '\\\\'
        fdata = header + '\n' + payload
    else:
        raise ValueError('unrecognized format')
    return fdata



# DATA COMPUTATION
def _conversion_rate(initial_edge, final_edge, poweredge, powernode):
    """Compute conversion rate"""
    return (initial_edge - final_edge - poweredge) / powernode

def _edge_reduction(initial_edge, final_edge, poweredge):
    """Compute edge reduction (percentage)"""
    edge = initial_edge - final_edge
    return ((edge - poweredge) / edge) * 100

def _compression_ratio(initial_edge, final_edge, poweredge):
    """Compute data compression ratio"""
    return initial_edge / (final_edge + poweredge)

