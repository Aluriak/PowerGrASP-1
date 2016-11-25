"""
Definitions of observers signals and other related data.

"""
from enum import Enum

from powergrasp import commons
from powergrasp import utils


LOGGER = commons.logger()
SIGNAL_STARTED   = '_started'
SIGNAL_STOPPED   = '_stopped'
SIGNAL_GENERATED = '_generated'
SIGNAL_FOUND     = '_found'


class Signals(Enum):
    # Steps signals
    StepStarted               = 'step_started'
    StepStopped               = 'step_stopped'
    CompressionStarted        = 'compression_started'
    CompressionStopped        = 'compression_stopped'
    ConnectedComponentStarted = 'connected_component_started'
    ConnectedComponentStopped = 'connected_component_stopped'
    IterationStarted          = 'iteration_started'  # send before all iterations
    IterationStopped          = 'iteration_stopped'  # send at the end of all iterations
    ExtractionStarted         = 'extraction_started'
    ExtractionStopped         = 'extraction_stopped'
    PreprocessingStarted      = 'preprocessing_started'
    PreprocessingStopped      = 'preprocessing_stopped'
    # Finalizations
    StepFinalized             = 'step_finalized'         # send after the StepStopped signal
    CompressionFinalized      = 'compression_finalized'  # send after the CompressionStopped signal
    # Objects signals
    ModelFound                = 'model_found'
    BicliqueFound             = 'biclique_found'
    CliqueFound               = 'clique_found'
    # Data signals
    CompressionTimeGenerated  = 'compression_time_generated'
    FinalEdgeCountGenerated   = 'final_edge_count_generated'
    FinalRemainEdgeCountGenerated = 'final_remain_edge_count_generated'
    CCCountGenerated          = 'cc_count_generated'
    StepDataGenerated         = 'step_data_generated'
    ASPConfigUpdated          = 'asp_config_updated'


# Priorities: observers are called with respect to their priority (smaller is after)
class Priorities(Enum):
    Maximal = 100
    High    =  80
    Medium  =  50
    Small   =  20
    Minimal =   0


class CompressionObserver:
    """Base class for all compression observers, where the update method used
    by compression is implemented.

    Derived classes must implements the _update method.
    They can also overwrite the priority method, for ensure to be called before
    others observers.

    """
    def update(self, *args, **kwargs):
        # integrate signals of args in kwargs, convert all into Signals object
        # and finally launch the update
        kwargs.update({sig: None for sig in args})
        kwargs = {Signals(sig): value for sig, value in kwargs.items()}
        assert all(sig in Signals for sig in kwargs.keys())
        self._update(kwargs)

    @property
    def priority(self):
        return Priorities.Medium


class ObserverBatch:
    """Container of observers, providing an API for observed objects.

    Proxy to all contained Observers, having a reference to the configuration
    that have been used to create the 

    It also infer some signals, like 'Compression started',
    based on the received signals.

    """
    def __init__(self, observers:iter, configuration):
        self._observers = tuple(observers)
        self._configuration = configuration
        self.sort_observers()

    @property
    def observers(self):
        return self._observers

    @property
    def configuration(self):
        return self._configuration

    def __iter__(self):
        return iter(self.observers)

    def signal(self, *args, **kwargs):
        for observer in self.observers:
            observer.update(*args, **kwargs)

    def __iadd__(self, othr):
        """Alias for extend method"""
        self.extend(othr)
        return self

    def __add__(self, others):
        """Return a new ObserverBatch instance, created using extend method"""
        ret = ObserverBatch(self.observers, self.configuration)
        ret.extend(others)
        return ret

    def extend(self, others):
        """Return a new batch containing observers in self and
        observers found in othr.

        others -- a list of CompressionObservers, or an ObserverBatch

        """
        whole = self._observers
        if isinstance(others, ObserverBatch):
            others = tuple(others.observers)
        for obs in others:
            if not isinstance(obs, CompressionObserver):
                raise ValueError("Object {} is not a CompressionObserver "
                                 "instance, as needed by ObserverBatch.".format(obs))
        self._observers.extend(others)
        self.sort_observers()

    def sort_observers(self):
        """Sort internals observers in order to preserve their priority order"""
        self._observers = sorted(self._observers, key=lambda o: o.priority.value, reverse=True)
