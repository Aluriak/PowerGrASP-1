"""
Definition of the plotting method.

"""
from powergrasp import commons
from powergrasp import statistics

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


# Data for plotting
MEASURES = (statistics.GENR_TIME, statistics.FINL_EDGE,
            statistics.GENR_PWED, statistics.GENR_PWND)
COLORS   = ('black', 'green', 'blue', 'red')
LABELS   = (
    'time per step',
    'remaining edges',
    'generated poweredge',
    'generated powernode',
)


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
        LOGGER.error('Plotting compression statistics require'
                     ' more than one compression iteration')
        LOGGER.error('Plotting aborted')
        return

    # convert in pandas data frame for allow plotting
    gx = pd.DataFrame(data, columns=MEASURES)
    # {black dotted,red,yellow,blue} line with marker o
    styles = ['ko--','ro-','yo-','bo-']

    # get plot, and sets the labels for the axis and the right axis (time)
    plot = gx.plot(style=styles, secondary_y=[statistics.GENR_TIME])
    lines, labels = plot.get_legend_handles_labels()
    rines, rabels = plot.right_ax.get_legend_handles_labels()
    labels = [key2label(l) for l in labels] + ['concept generation time']

    plot.legend(lines + rines, labels)
    plot.set_xlabel(xlabel)
    plot.set_ylabel(ylabel)
    plot.right_ax.set_ylabel('Time (s)')

    # axis limits : show the 0
    plot.right_ax.set_ylim(0, max(gx[statistics.GENR_TIME]) * 2)
    plot.set_ylim(0, max(gx[statistics.FINL_EDGE]) * 1.1)

    # print or save
    if savefile:
        plt.savefig(savefile, dpi=dpi)
        LOGGER.info('Plot of statistics data saved in file '
                    + savefile + ' (' + str(dpi) + ' dpi)')
    else:
        plt.show()