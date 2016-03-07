"""
Main source file of the package, containing tho compress function.

The compress function get numerous arguments,
 for allowing a parametrable compression.

"""
import os
import tempfile
from builtins           import input
from collections        import defaultdict

from powergrasp.observers import Signals  # shortcut
from powergrasp.commons import basename
from powergrasp.commons import ASP_SRC_EXTRACT, ASP_SRC_PREPRO , ASP_SRC_FINDCC
from powergrasp.commons import ASP_SRC_FINDBC , ASP_SRC_POSTPRO, ASP_SRC_POSTPRO
from powergrasp.commons import ASP_ARG_UPPERBOUND, ASP_ARG_CC
from powergrasp.commons import ASP_ARG_LOWERBOUND, ASP_ARG_STEP
from powergrasp import compression
from powergrasp import statistics
from powergrasp import observers
from powergrasp import converter
from powergrasp import solving
from powergrasp import commons
from powergrasp import atoms



LOGGER = commons.logger()


def network_name_from(data):
    """A string describing the graph data received.

    if data is a valid filepath, the filepath will be returned.
    Else, the string 'network' will be returned.

    """
    if os.path.isfile(data):
        return data
    else:
        return 'stdin network'


def asp_file_from(data):
    """A filename containing the graph data formatted in ASP.

    Data is a filename, or a string containing the graph data,
    encoded in ASP format.
    Detection of the type of data (filename or graph) is performed by detect
     a valid path in data. On failure, data is understood as an input graph.

    """
    # default case: data is a filename
    graph_data_file = data
    data_format = None
    # data is a string formatted in an input format.
    # try to access data
    if not commons.is_valid_path(data):
        LOGGER.info('Input data is not a valid path. This data is assumed as'
                    ' ASP formatted data.')
        file_to_be_converted = tempfile.NamedTemporaryFile('w', delete=False)
        file_to_be_converted.write(data)
        file_to_be_converted.close()
        graph_data_file = file_to_be_converted.name
        data_format = 'asp'
    elif not os.path.exists(data):
        # the file is not existing, raise the error !
        open(data)
    # convert graph data into ASP-readable format
    graph = converter.to_asp_file(graph_data_file, format=data_format)
    return graph_dict_to_asp_file(graph)


def graph_dict_to_asp_file(graph_dict):
    """convert {node: succs} to ASP atoms edge/2, where edge(X,Y) defines X
    as node and Y a successor.

    Returns the temp file name where atoms are pushed.

    """
    # write it in a file, and convert this file in ASP.
    asp_file = tempfile.NamedTemporaryFile('w', delete=False)
    def to_asp_value(value):
        if isinstance(value, int):
            return str(value)
        return (  # surround value if necessary
            ('"' if value[0] != '"' else '')
            + str(value)
            + ('"' if value[-1] != '"' else '')
        )
    for node, succs in graph_dict.items():
        for succ in succs:
            asp_file.write('edge(' + to_asp_value(node) + ','
                           + to_asp_value(succ) + ').\n')
    asp_file.close()
    return asp_file.name


def compress(graph_data_or_file=None, output_file=None, *,
             extracting=None, preprocessing=None, ccfinding=None,
             bcfinding=None, postprocessing=None,
             statistics_filename='data/statistics.csv',
             output_format=None, interactive=False,
             count_model=False, count_cc=False,
             show_preprocessed=False, timers=False, logfile=None, loglevel=None,
             thread=None, draw_lattice=False):
    """Performs the graph compression with data found in graph file.

    Use ASP source code found in extract, findcc, findbc
     and {pre,post}processing files for perform the computations,
     or the default ones if None is provided.
     (which is probably what client code want in 99.99% of cases)

    Output format must be a valid string,
     or will be inferred from the output file name, or will be set as bbl.

    If output file is None, result will be printed in stdout.

    The function itself returns a float that is, in seconds,
     the time necessary for the compression,
     and the object provided by the statistics module,
     that contains statistics about the compression.

    """
    # define the log file and the log level, if necessary
    commons.configure_logger(logfile, loglevel)
    # clasp options construction:
    gringo_options = commons.ASP_GRINGO_OPTIONS
    clasp_options = commons.ASP_CLASP_OPTIONS
    # set thread option if necessary
    clasp_options += ' ' + commons.thread(thread)
    # get data from parameters
    graph_file = asp_file_from(graph_data_or_file)
    # Create the default observers
    output_converter = observers.OutputWriter(output_file, output_format)
    instanciated_observers = [
        output_converter,
    ]
    # Add the optional observers
    if timers:
        time_counter = observers.TimeCounter(ignore=[
            Signals.IterationStarted, Signals.PreprocessingStarted,
        ])
    else:  # no timers asked, but others modules may want to have a ref to
        time_counter = observers.NullTimeCounter()
    instanciated_observers.append(time_counter)

    if statistics_filename:
        instanciated_observers.append(statistics.DataExtractor(
            statistics_filename,
            output_converter=output_converter,
            time_counter=time_counter,
            network_name=network_name_from(graph_data_or_file)
        ))

    if show_preprocessed:
        instanciated_observers.append(observers.ObservedSignalLogger(
            observers.Signals.StepPerformed,
            'PREPROCESSED DATA: '
        ))

    if count_model:
        instanciated_observers.append(observers.ObjectCounter())
    if count_cc:
        instanciated_observers.append(observers.ConnectedComponentsCounter())

    if draw_lattice:
        instanciated_observers.append(observers.LatticeDrawer(draw_lattice))
    if interactive:
        instanciated_observers.append(observers.InteractiveCompression())

    # sort observers, in respect of their priority (smaller is after)
    instanciated_observers.sort(key=lambda o: o.priority.value, reverse=True)
    assert instanciated_observers[0].priority.value >= instanciated_observers[-1].priority.value
    LOGGER.debug('OBSERVERS:' + str('\n\t'.join(
        str((obs.__class__, obs))
        for obs in instanciated_observers
    )))

    # Launch the compression
    compression.compress_lp_graph(
        graph_file,
        asp_extracting=extracting,
        asp_preprocessing=preprocessing,
        asp_ccfinding=ccfinding,
        asp_bcfinding=bcfinding,
        asp_postprocessing=postprocessing,
        gringo_options=gringo_options,
        clasp_options=clasp_options,
        all_observers=tuple(instanciated_observers)
    )
