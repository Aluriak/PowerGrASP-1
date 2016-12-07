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
SIGNAL_MOTIF     = '_motif'


class Signals(Enum):
    # Steps signals
    StepStarted               = 'step_started'
    StepStopped               = 'step_stopped'
    CompressionStarted        = 'compression_started'
    CompressionStopped        = 'compression_stopped'
    ConnectedComponentStarted = 'connected_component_started'
    ConnectedComponentStopped = 'connected_component_stopped'
    ExtractionStarted         = 'extraction_started'
    ExtractionStopped         = 'extraction_stopped'
    # Finalizations
    StepFinalized             = 'step_finalized'         # send after the StepStopped signal
    CompressionFinalized      = 'compression_finalized'  # send after the CompressionStopped signal
    # Data signals
    ModelFound                = 'model_found'  # associated with the motif class
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
    """Base class for all compression observers, where each compression
    signal is associated with one method to redefine in derived classes.

    Derived classes must implements the on_* methods that are relevant
    to their tasks.
    They can also overwrite the priority method, for ensure to be called before
    others observers.

    Another way to handle signals is to define on_signals method, which receive
    all signals in a mapping {signal: parameters}.

    """

    def handles(self, *args, **kwargs):
        """Dispatch given signals to (1) on_* methods or (2) on_signals method
        if available.

        Example of call: obs.handles(StepStopped, model_found=params)

        """
        if hasattr(self, 'on_signals'):
            # integrate signals of args in kwargs, convert all into Signals object
            # and finally launch the update
            kwargs.update({sig: None for sig in args})
            kwargs = {Signals(sig): value for sig, value in kwargs.items()}
            assert all(sig in Signals for sig in kwargs.keys())
            self.on_signals(kwargs)
        else:
            for signal in args:
                method = getattr(self, 'on_' + signal.value)
                method()
            for signal, payload in kwargs.items():
                method = getattr(self, 'on_' + signal)
                method() if payload is None else method(payload)

    def on_step_started(self): pass
    def on_step_stopped(self): pass
    def on_step_finalized(self): pass
    def on_model_found(self, result): pass
    def on_step_data_generated(self, payload): pass
    def on_connected_component_started(self, payload): pass
    def on_connected_component_stopped(self, atoms): pass
    def on_extraction_started(self): pass
    def on_extraction_stopped(self): pass
    def on_compression_started(self): pass
    def on_compression_stopped(self): pass
    def on_compression_finalized(self): pass
    def on_cc_count_generated(self, nb_cc:int):  pass
    def on_final_edge_count_generated(self, nb_edge:int): pass
    def on_final_remain_edge_count_generated(self, nb_edge:int): pass
    def on_asp_config_updated(self, payload): pass


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
            observer.handles(*args, **kwargs)

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
