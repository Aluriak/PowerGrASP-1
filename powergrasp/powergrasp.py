"""
Main source file of the package, containing tho compress function.

The compress function get numerous arguments,
 for allowing a parametrable compression.

"""
import os
import inspect
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


def compress(graph_data=None, output_file=None, *,
             output_format=None, interactive=None,
             count_model=None, count_cc=None,
             stats_file=None, timers=None, logfile=None, loglevel=None,
             thread=None, draw_lattice=None, instanciated_observers=None,
             extract_config=None, biclique_config=None, clique_config=None):
    """Performs the graph compression with data found in graph file.

    Any not given argument will be overriden by default values.

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

    # None to default
    if extract_config is None:
        extract_config = solving.CONFIG_EXTRACTION()
    if biclique_config is None:
        biclique_config = solving.CONFIG_BICLIQUE_SEARCH()
    if clique_config is None:
        clique_config = solving.CONFIG_CLIQUE_SEARCH()

    # gives default value for each parameter that needs it
    _, _, _, func_args = inspect.getargvalues(inspect.currentframe())
    func_args = dict(func_args)  # copy data structure
    option = commons.options(parameters=func_args)

    # configs enrichment
    thread_option = commons.thread(option['thread'])
    if thread_option:
        extract_config = solving.ASPConfig(extract_config.files,
                                           extract_config.clasp_options + thread_option,
                                           extract_config.gringo_options)
        clique_config = solving.ASPConfig(clique_config.files,
                                          clique_config.clasp_options + thread_option,
                                           clique_config.gringo_options)
        biclique_config = solving.ASPConfig(biclique_config.files,
                                            biclique_config.clasp_options + thread_option,
                                            biclique_config.gringo_options)

    # get data from parameters
    graph_file = asp_file_from(option['graph_data'])
    # Create the default observers
    output_converter = observers.OutputWriter(option['output_file'],
                                              option['output_format'])
    if instanciated_observers is None:  # default value handling
        instanciated_observers = []
    instanciated_observers += [
        output_converter,
    ]
    # Add the optional observers
    if option['timers']:
        time_counter = observers.TimeCounter(ignore=[
            Signals.IterationStarted, Signals.PreprocessingStarted,
        ])
    else:  # no timers asked, but others modules may want to have a ref to
        time_counter = observers.NullTimeCounter()
    instanciated_observers.append(time_counter)

    if option['stats_file']:
        instanciated_observers.append(statistics.DataExtractor(
            stats_file,
            output_converter=output_converter,
            time_counter=time_counter,
            network_name=network_name_from(graph_data)
        ))

    if option['count_model']:
        instanciated_observers.append(observers.ObjectCounter())
    if option['count_cc']:
        instanciated_observers.append(observers.ConnectedComponentsCounter())

    if option['draw_lattice']:
        instanciated_observers.append(observers.LatticeDrawer(draw_lattice))
    if option['interactive']:
        instanciated_observers.append(observers.InteractiveCompression())

    # sort observers, in respect of their priority (smaller is after)
    instanciated_observers.sort(key=lambda o: o.priority.value, reverse=True)
    assert instanciated_observers[0].priority.value >= instanciated_observers[-1].priority.value
    LOGGER.debug('OBSERVERS:' + str('\n\t'.join(
        str((obs.__class__, obs))
        for obs in instanciated_observers
    )))

    # Launch the compression
    LOGGER.info('COMPRESSION STARTED !')
    compression.compress_lp_graph(
        graph_file,
        all_observers=tuple(instanciated_observers),
        extract_config=extract_config,
        clique_config=clique_config,
        biclique_config=biclique_config,
    )
    LOGGER.info('COMPRESSION FINISHED !')
