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

import powergrasp.commons as commons
import csv

# Logger
LOGGER = commons.logger()

try:
    # plotting libraries
    #  this is just a test for print a warning if there are not present
    import matplotlib
    import pandas
    import numpy
except ImportError:
    LOGGER.warning('plotting libraries are not all there. '
                   'Maybe you will need to install them.')

# INFORMATION KEYS
INIT_EDGE = 'initial_edge_count'
FINL_EDGE = 'final_edge_count'
FINL_PWED = 'poweredge_count'
FINL_PWND = 'powernode_count'
CONV_RATE = 'conversion_rate'
EDGE_RDCT = 'edge_reduction'
COMP_RTIO = 'compression_ratio'
GENR_TIME = 'gentime'
REMN_EDGE = 'edges'
ALL_FIELD = (CONV_RATE, EDGE_RDCT, COMP_RTIO,
             INIT_EDGE, FINL_EDGE, FINL_PWND,
             FINL_PWED, GENR_TIME, REMN_EDGE,
            )

# global data
NETW_NAME = 'network_name'
FILE_DESC = 'file_descriptor'
FILE_WRTR = 'file_writer'

# FORMATS
FORMAT_TEX = 'tex'
FORMAT_RAW = 'txt'

# DATA FOR PLOTTING
MEASURES = (GENR_TIME, REMN_EDGE, FINL_PWED, FINL_PWND)
COLORS   = ('black'  , 'green'  , 'blue'   , 'red'    )
LABELS   = (
    'time per step',
    'remaining edges',
    'generated poweredge',
    'generated powernode',
)


# MAIN API FUNCTIONS

def container(network_name='network', statistics_filename=None):
    """Return a new container of statistics information

    The statistics_filename, if not None, must be a valid name of file
    that will be overrided, and will contains some data in csv format."""
    statistics_file, statistics_writer = None, None
    # open file of statistics in csv if asked
    if statistics_filename:
        try:
            statistics_file = open(statistics_filename, 'w')
            statistics_writer = csv.DictWriter(statistics_file,
                                               fieldnames=MEASURES)
            statistics_writer.writeheader()
        except IOError as e:
            LOGGER.warning('The file ' + statistics_filename
                           + ' can\'t be opened. No statistics will be saved.')
    else:
        statistics_writer = None
    return {
        NETW_NAME: network_name,
        INIT_EDGE: 0,
        FINL_EDGE: 0,
        FINL_PWED: 0,
        FINL_PWND: 0,
        REMN_EDGE: 0,
        GENR_TIME: 0,
        FILE_DESC: statistics_file,
        FILE_WRTR: statistics_writer,
    }


def add(stats, initial_edge_count=None, poweredge_count=None,
        powernode_count=None, gentime=None,
        final_edges_count=None, remain_edges_count=None):
    """set to given stats the given values.

    if a value is None, it will be not modified.
    stats is modified in place.

    values:
        initial_edge_count -- number of edges at the beginning
        poweredge_count    -- number of poweredge created at last iteration
        powernode_count    -- number of powernode created at last iteration
        gentime            -- time necessary for last iteration
        final_edges_count  -- number of edges at the end
        remain_edges_count -- number of remaining edges at last iteration
    """
    assert(stats.__class__ == dict)

    # treats all accumulative values
    accumulative_values = {
        INIT_EDGE: initial_edge_count,
        FINL_EDGE: final_edges_count,
        FINL_PWED: poweredge_count,
        FINL_PWND: powernode_count,
    }
    for info, value in accumulative_values.items():
        if value is not None:
            stats[info] += value

    # write the data in csv file
    if stats[FILE_DESC] and gentime and remain_edges_count:
        assert(MEASURES[0] == GENR_TIME) # verification of plotting consistency
        assert(MEASURES[1] == REMN_EDGE)
        assert(MEASURES[2] == FINL_PWED)
        assert(MEASURES[3] == FINL_PWND)
        stats[FILE_WRTR].writerow({
            GENR_TIME: gentime,
            REMN_EDGE: remain_edges_count,
            FINL_PWED: stats[FINL_PWED],
            FINL_PWND: stats[FINL_PWND],
        })


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

def conversion_rate(stats):
    """Accessor on data"""
    return stats[CONV_RATE]

def edge_reduction(stats):
    """Accessor on data"""
    return stats[EDGE_RDCT]

def finalize(stats):
    """Close files"""
    if stats[FILE_DESC]:
        stats[FILE_DESC].close()
        stats[FILE_WRTR] = None



def _final_data(stats, format):
    """Compute and produce all given stats in string."""
    assert(stats[INIT_EDGE] is not None)
    assert(stats[FINL_EDGE] is not None)
    assert(stats[FINL_PWND] is not None)
    assert(stats[FINL_PWED] is not None)

    stats[CONV_RATE] = _conversion_rate(
        stats[INIT_EDGE], stats[FINL_EDGE], stats[FINL_PWED], stats[FINL_PWND]
    )
    stats[EDGE_RDCT] = _edge_reduction(
        stats[INIT_EDGE], stats[FINL_EDGE], stats[FINL_PWED]
    )
    stats[COMP_RTIO] = _compression_ratio(
        stats[INIT_EDGE], stats[FINL_EDGE], stats[FINL_PWED]
    )

    return _formatted(dict(stats), format)




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
    try:
        edge = initial_edge
        poweredge = final_edge + poweredge
        return (edge - poweredge) / powernode
    except ZeroDivisionError:
        return 1.

def _edge_reduction(initial_edge, final_edge, poweredge):
    """Compute edge reduction (percentage)"""
    try:
        edge = initial_edge
        poweredge = final_edge + poweredge
        return ((edge - poweredge) / edge) * 100
    except ZeroDivisionError:
        return 100.

def _compression_ratio(initial_edge, final_edge, poweredge):
    """Compute data compression ratio"""
    try:
        return initial_edge / (final_edge + poweredge)
    except ZeroDivisionError:
        return 1.




# PLOTTING
def plots(filename, title="Compression statistics", xlabel='Iterations',
          ylabel='{Power,} {node,edge}s counters', savefile=None, dpi=400):
    """Generate the plot that show all the data generated by the compression

    if savefile is not None and is a filename, the figure will be saved
    in png in given file, with given dpi."""
    try:
        # plotting libraries
        from matplotlib import rc
        rc('text', usetex=True)
        import matplotlib.pyplot as plt
        import numpy as np
        import pandas as pd
        from matplotlib.pyplot import savefig
    except ImportError:
        LOGGER.error('plotting libraries are not all there. '
                     'Please install matplotlib and pandas modules. '
                     'Plotting aborted.')
        return  # end of plotting


    # GET DATA
    try:
        data = np.genfromtxt(
            filename,
            delimiter=',',
            skip_header=0,
            skip_footer=0,
            names=True,  # read names from header
        )
    except IOError as e:
        LOGGER.warning('The file '
                       + statistics_filename
                       + ' can\'t be opened. No statistics will be saved.')


    # Label conversion
    def key2label(key):
        """Convert given string in label printable by matplotlib"""
        return '$\#$' + key.strip('count').replace('_', ' ')

    # PLOTTING
    try:
        data_size = len(data[MEASURES[0]])
    except TypeError:
        LOGGER.error('Plotting compression statistics require more than one compression iteration')
        LOGGER.error('Plotting aborted')
        return

    # convert in pandas data frame for allow plotting
    gx = pd.DataFrame(data, columns=MEASURES)
    # {black dotted,red,yellow,blue} line with marker o
    styles = ['ko--','ro-','yo-','bo-']

    # get plot, and sets the labels for the axis and the right axis (time)
    plot = gx.plot(style=styles, secondary_y=[GENR_TIME])
    lines, labels = plot.get_legend_handles_labels()
    rines, rabels = plot.right_ax.get_legend_handles_labels()
    labels = [key2label(l) for l in labels] + ['concept generation time']

    plot.legend(lines + rines, labels)
    plot.set_xlabel(xlabel)
    plot.set_ylabel(ylabel)
    plot.right_ax.set_ylabel('Time (s)')

    # axis limits : show the 0
    plot.right_ax.set_ylim(0, max(gx[GENR_TIME])*2)
    plot.set_ylim(0, gx[REMN_EDGE][0]*1.1)

    # print or save
    if savefile:
        plt.savefig(savefile, dpi=dpi)
        LOGGER.info('Plot of statistics data saved in file ' + savefile + ' (' + str(dpi) + ' dpi)')
    else:
        plt.show()



