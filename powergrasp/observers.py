"""
Definitions of observers and related.

"""
import sys
import csv
import time
import itertools
from enum import Enum
from functools import partial

from powergrasp import converter
from powergrasp import commons


LOGGER = commons.logger()
SIGNAL_STARTED   = '_started'
SIGNAL_STOPPED   = '_stopped'
SIGNAL_GENERATED = '_generated'
SIGNAL_FOUND     = '_found'


class Signals(Enum):
    # Steps signals
    StepStarted               = 'step_started'
    StepStopped               = 'step_stopped'
    ModelStarted              = 'model_started'
    ModelStopped              = 'model_stopped'
    CompressionStarted        = 'compression_started'
    CompressionStopped        = 'compression_stopped'
    ConnectedComponentStarted = 'connected_component_started'
    ConnectedComponentStopped = 'connected_component_stopped'
    IterationStarted          = 'iteration_started'
    IterationStopped          = 'iteration_stopped'
    ExtractionStarted         = 'extraction_started'
    ExtractionStopped         = 'extraction_stopped'
    PreprocessingStarted      = 'preprocessing_started'
    PreprocessingStopped      = 'preprocessing_stopped'
    PostprocessingStarted     = 'postprocessing_started'
    PostprocessingStopped     = 'postprocessing_stopped'
    # Finalizations
    StepFinalized             = 'step_finalized'         # send after the StepStopped signal
    CompressionFinalized      = 'compression_finalized'  # send after the CompressionStopped signal
    # Objects signals
    ConnectedComponentsFound  = 'connected_components_found'
    ModelFound                = 'model_found'
    BicliqueFound             = 'biclique_found'
    CliqueFound               = 'clique_found'
    # Data signals
    CompressionTimeGenerated  = 'compression_time_generated'
    AllEdgeGenerated          = 'all_edge_generated'
    RemainEdgeGenerated       = 'remain_edge_generated'
    StepDataGenerated         = 'step_data_generated'


# Priorities: observers are called with respect to their priority (smaller is after)
MAXIMAL_PRIORITY = 100
HIGH_PRIORITY    =  80
MEDIUM_PRIORITY  =  50
SMALL_PRIORITY   =  20
MINIMAL_PRIORITY =   0


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
        return MEDIUM_PRIORITY


class ObservedSignalLogger(CompressionObserver):
    def __init__(self, signal, log_header='', log_level=0):
        self.log_header = log_header
        self.log_level = log_level
        self.signal = Signals(signal)

    def _update(self, signals):
        data = self.signal in signals
        if data:
            LOGGER.log(self.log_level, self.log_header + str(data))


class InteractiveCompression(CompressionObserver):
    """Make the compression interactive: ask for an input from user
    at the end of each step"""
    def _update(self, signals):
        if Signals.StepStopped in signals:
            try:
                input('<hit enter for next model computation>')
            except KeyboardInterrupt:
                exit()

    @property
    def priority(self):
        return MINIMAL_PRIORITY


class ConnectedComponentsCounter(CompressionObserver):
    """Counter of connected components"""

    def _update(self, signals):
        if Signals.ConnectedComponentsFound in signals:
            ccs = signals[Signals.ConnectedComponentsFound]
            self._nb_ccs      = len(ccs)
        if Signals.ConnectedComponentStarted in signals:
            cc_num, cc_name = signals[Signals.ConnectedComponentStarted]
            LOGGER.info('#### CC ' + cc_name + ' ' + str(cc_num+1)
                        + '/' + str(self._nb_ccs))


class ObjectCounter(CompressionObserver):
    """Counter of objects, based on received signals ending with '_found'"""

    PREFIX = '_counter_'

    def __init__(self):
        self.props = []
        for signal in (s for s in Signals if s.value.endswith(SIGNAL_FOUND)):
            prop = ObjectCounter.property_named_from(signal.value)
            setattr(self, prop, 0)
            self.props.append(prop)

    def _update(self, signals):
        for signal in signals:
            name = signal.value
            if name.endswith(SIGNAL_FOUND):
                prop = ObjectCounter.property_named_from(name)
                setattr(self, prop, getattr(self, prop) + 1)
        if Signals.StepFinalized in signals:
            for prop in self.props:
                LOGGER.info(self.__class__.__name__ + ': '
                            + ObjectCounter.prettified(prop)
                            + ': ' + str(getattr(self, prop)))

    @staticmethod
    def property_named_from(signal_name):
        "Return the property name deduced from the signal name"
        return ObjectCounter.PREFIX + signal_name[:-len(SIGNAL_FOUND)]

    @staticmethod
    def prettified(property_name):
        "Return the prettified property name deduced from the property name"
        property_name = property_name[len(ObjectCounter.PREFIX):]
        return property_name.replace('_', ' ').title()


class OutputWriter(CompressionObserver):
    """Manage the output file, and conversion into expected output format"""

    def __init__(self, output_filename, output_format):
        format = OutputWriter.format_deduced_from(output_filename, output_format)
        self.output = open(output_filename, 'w') if output_filename else sys.stdout
        self.converter = converter.output_converter_for(format)

    def _update(self, signals):
        # print('Output Writer:', signals)
        if Signals.ModelFound in signals:
            # give new powernodes to converter
            atoms = signals[Signals.ModelFound]
            self.converter.convert(atoms)
        if Signals.ConnectedComponentStopped in signals:
            self.output.write(self.converter.finalized())
            self.converter.reset_containers()
            LOGGER.debug('Final data saved in file ' + self.output.name)
        if Signals.RemainEdgeGenerated in signals:
            remain_edges = signals[Signals.RemainEdgeGenerated]
            self.converter.convert(remain_edges)
        if Signals.CompressionStopped in signals:
            if self.output is not sys.stdout: self.output.close()
        if Signals.CompressionStarted in signals:
            self.output.write(self.converter.header())

    def comment(self, lines):
        """Add given lines to output as comments"""
        self.output.write(self.converter.comment(lines))

    @property
    def priority(self):
        return MINIMAL_PRIORITY

    @staticmethod
    def format_deduced_from(output_file, output_format):
        """Return the most likely expected output format by looking at given args"""
        # look at the output_file extension if output_format is unusable
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


class TimeCounter(CompressionObserver):
    """Observer that looks for all received signals, and creates a timer for
    any signal with the value finishing by '_started', and destroys the timer
    after logging its value when receiving the sibling '_stopped' signal.

    This allows a generalist and automatic benchmarking
    of the observed phenomenoms.

    """
    TIMER_PREFIX = '_timer_'  # used for generated attributes
    LAST_PREFIX = '_last_time_'  # used for generated attributes

    def __init__(self, round_ndigits=3, log_times=True):
        "Wait for the ndigits parameter of the builtin round function"
        self.log_times = log_times
        if round_ndigits:
            self.round = partial(round, ndigits=round_ndigits)
        else:
            self.round = round

    def _update(self, signals):
        for signal in signals:
            name = signal.value
            if name.endswith(SIGNAL_STARTED):
                prop = TimeCounter.property_named_from(name)
                if hasattr(self, prop):
                    self.log_timer(prop)
                setattr(self, prop, time.time())
            if name.endswith(SIGNAL_STOPPED):
                # stop the timer, log its value and save it
                prop = TimeCounter.property_named_from(name)
                setattr(self, prop, time.time() - getattr(self, prop))
                if hasattr(self, prop):
                    self.log_timer(prop)
                    prop_save = TimeCounter.property_named_from(name, prefix=TimeCounter.LAST_PREFIX)
                    setattr(self, prop_save, getattr(self, prop))
                    delattr(self, prop)
                else:
                    LOGGER.warning('TimeCounter: the process '
                                   + TimeCounter.prettified(prop)
                                   + ' stopped but not started.')

    @property
    def compression_time(self):
        return getattr(self, TimeCounter.property_named_from(
            Signals.CompressionStarted.value,
            prefix=TimeCounter.LAST_PREFIX
        ))

    @property
    def extraction_time(self):
        return getattr(self, TimeCounter.property_named_from(
            Signals.ExtractionStarted.value,
            prefix=TimeCounter.LAST_PREFIX
        ))

    @property
    def last_step_time(self):
        return getattr(self, TimeCounter.property_named_from(
                       Signals.StepStarted.value, prefix=TimeCounter.LAST_PREFIX))

    def log_timer(self, property_name):
        "Perform the logging output for the given property"
        timer = self.round(getattr(self, property_name))
        if self.log_times:
            LOGGER.info(self.__class__.__name__ + ': ' + str(timer)
                        + 's for ' + TimeCounter.prettified(property_name) + '.')

    @staticmethod
    def property_named_from(signal_name, prefix=TIMER_PREFIX):
        "Return the property name deduced from the signal name"
        assert len(SIGNAL_STARTED) == len(SIGNAL_STOPPED)
        return prefix + signal_name[:-len(SIGNAL_STARTED)]

    @staticmethod
    def prettified(property_name):
        "Return the prettified property name deduced from the property name"
        property_name = property_name[len(TimeCounter.TIMER_PREFIX):]
        return property_name.replace('_', ' ').title()

    @property
    def priority(self):
        return MAXIMAL_PRIORITY
