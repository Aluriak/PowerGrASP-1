# -*- coding: utf-8 -*-
"""
Main source file of the package, containing tho compress function.

The compress function get numerous arguments,
 for allowing a parametrable compression.

"""
import os
import sys
import time
import tempfile
import itertools
from builtins           import input
from collections        import defaultdict

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


def asp_file_from(data):
    """A filename containing the graph data formatted in ASP.

    Data is a filename, or a string containing the graph data,
    encoded in any valid input.
    Detection of the type of data (filename or graph) is performed by detect
     a valid path in data. On failure, data is understood as an input graph.

    """
    # default case: data is a filename
    graph_data_file = data
    # data is a string formatted in an input format.
    if not os.path.isfile(data):
        # write it in a file, and convert this file in ASP.
        file_to_be_converted = tempfile.NamedTemporaryFile('w', delete=False)
        file_to_be_converted.write(data)
        file_to_be_converted.close()
        graph_data_file = converter.converted_to_asp_file(file_to_be_converted)
    # convert graph data into ASP-readable format, if necessary
    graph_data_file = converter.converted_to_asp_file(data)
    return graph_data_file


def deduced_output_format_from(output_file, output_format):
    "Return the most likely expected output format by looking at given args"
    # look at the output_file extension output_format is unusable
    if not output_format or output_format not in converter.OUTPUT_FORMATS:
        try:
            output_format = output_file.split('.')[-1]  # extension of the file
        except (IndexError, AttributeError):
            output_format = converter.DEFAULT_OUTPUT_FORMAT  # use BBL
    # verifications
    assert output_format in converter.OUTPUT_FORMATS
    if output_file:
        assert output_file.endswith(output_format)
    return output_format


def compress(graph_data_or_file=None, output_file=None, *,
             extracting=None, preprocessing=None, ccfinding=None,
             bcfinding=None, postprocessing=None,
             statistics_filename='data/statistics.csv',
             output_format=None, lowerbound_cut_off=2,
             interactive=False, count_model=False, count_cc=False,
             show_preprocessed=False, timers=False):
    """Performs the graph compression with data found in graph file.

    Use ASP source code found in extract, findcc, findbc
     and {pre,post}processing files for perform the computations,
     or the default ones if None is provided.
     (which is probably what client code want in 99.99% of cases)

    Output format must be a valid string,
     or will be inferred from the output file name, or will be set as bbl.

    If output file is None, result will be printed in stdout.

    Notes about the maximal lowerbound optimization:
      In a linear time, it is possible to compute the
       maximal degree in the non covered graph.
      This value correspond to the minimal best concept score.
      In real life, the blocks (used by ASP for avoid overlapping powernodes)
       complicate the job.
      Moreover, as cliques are searched before the biclique, the lowerbound
       value is increased if a clique with a better score is found.
      The cut-off value is here for allow client code to control
       this optimization, by specify the value that disable this optimization
       when the lowerbound reachs it.

    The function itself returns a float that is, in seconds,
     the time necessary for the compression,
     and the object provided by the statistics module,
     that contains statistics about the compression.

    """
    # get data from parameters
    graph_file = asp_file_from(graph_data_or_file)
    output_format = deduced_output_format_from(output_file, output_format)
    # Create the default observers
    output_converter = observers.OutputWriter(output_file, output_format)
    instanciated_observers = [
        output_converter,
    ]
    # Add the optional observers
    if timers:
        time_counter = observers.TimeCounter()
        instanciated_observers.append(time_counter)
    if statistics_filename:
        instanciated_observers.append(statistics.DataExtractor(
            statistics_filename,
            output_converter=output_converter,
            time_counter=time_counter,
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
    if interactive:
        instanciated_observers.append(observers.InteractiveCompression())

    # sort observers, in respect of their priority (smaller is after)
    instanciated_observers.sort(key=lambda o: o.priority, reverse=True)
    assert instanciated_observers[0].priority > instanciated_observers[1].priority

    # Launch the compression
    compression.compress_lp_graph(
        graph_file,
        asp_extracting=extracting,
        asp_preprocessing=preprocessing,
        asp_ccfinding=ccfinding,
        asp_bcfinding=bcfinding,
        asp_postprocessing=postprocessing,
        all_observers=tuple(instanciated_observers)
    )
