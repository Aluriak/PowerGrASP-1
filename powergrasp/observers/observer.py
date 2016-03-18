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
    CCRemainEdgeGenerated     = 'cc_remain_edge_generated'
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
