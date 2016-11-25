"""High level access to a vast set of observers"""


import inspect

from powergrasp import commons
from powergrasp import solving
from powergrasp import converter
from powergrasp import config
from . import (ObserverBatch, CompressionObserver, OutputWriter, TimeCounter,
               Signals, ObjectCounter, ConnectedComponentsCounter,
               NullTimeCounter, TimeComparator, SignalProfiler)


LOGGER = commons.logger()


def most(infile:str, outfile:str) -> (config, CompressionObserver):
    """Initialize a maximum number of observers
    with a dedicated configuration.

    Return the used configuration and a tuple of observers.

    This is a wrapper around built_from, allowing client to use
    a simpler API.

    """
    cfg = config.Configuration(infile=infile, outfile=outfile)
    return built_from(cfg)


def built_from(cfg:config.Configuration) -> ObserverBatch:
    """Return an ObserverBatch instance, containing all observers needed
    to fullfill given configuration needs.

    """
    from powergrasp import statistics
    # define the log file and the log level, if necessary
    commons.configure_logger(cfg.logfile, cfg.loglevel)

    # Create the default observers
    output_converter = OutputWriter(cfg.outfile, cfg.outformat)
    instanciated_observers = [
        output_converter,
    ]

    # Add the optional observers
    if cfg.timers:
        time_counter = TimeCounter(ignore=[
            Signals.IterationStarted, Signals.PreprocessingStarted,
        ])
    else:  # no timers asked, but others modules may want to have a ref to
        time_counter = NullTimeCounter()
    instanciated_observers.append(time_counter)

    if cfg.stats_file:
        instanciated_observers.append(statistics.DataExtractor(
            cfg.stats_file,
            output_converter=output_converter,
            time_counter=time_counter,
            network_name=cfg.network_name
        ))

    if cfg.count_model:
        instanciated_observers.append(ObjectCounter())
    if cfg.count_cc:
        instanciated_observers.append(ConnectedComponentsCounter())

    if cfg.draw_lattice:
        instanciated_observers.append(LatticeDrawer(draw_lattice))
    if cfg.interactive:
        instanciated_observers.append(InteractiveCompression())
    if cfg.signal_profile:
        instanciated_observers.append(SignalProfiler())

    instanciated_observers.append(
        TimeComparator(commons.basename(cfg.network_name),
                       time_counter,
                       save_result=cfg.save_time)
    )

    # sort observers, in respect of their priority (smaller is after)
    instanciated_observers.sort(key=lambda o: o.priority.value, reverse=True)
    assert instanciated_observers[0].priority.value >= instanciated_observers[-1].priority.value
    LOGGER.debug('OBSERVERS:' + str('\n\t'.join(
        str((obs.__class__, obs))
        for obs in instanciated_observers
    )))

    # TODO MOVE THIS BLOCK
    # Launch the compression
    # LOGGER.info('COMPRESSION STARTED !')
    # if do_profiling:
        # print(utils.test_integrity(graph_file))
    # compression.compress_lp_graph(
        # graph_file,
        # all_observers=tuple(instanciated_observers),
        # extract_config=extract_config,
        # clique_config=clique_config,
        # biclique_config=biclique_config,
    # )
    # LOGGER.info('COMPRESSION FINISHED !')

    return ObserverBatch(tuple(instanciated_observers), cfg)
