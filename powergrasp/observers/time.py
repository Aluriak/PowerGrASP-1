"""
Definitions of observers related to the time.

"""
import time
from functools import partial

from .observer import CompressionObserver, Signals, Priorities
from .observer import SIGNAL_STARTED, SIGNAL_STOPPED
from powergrasp import commons


LOGGER = commons.logger()


class TimeCounter(CompressionObserver):
    """Observer that looks for all received signals, and creates a timer for
    any signal with the value finishing by '_started', and destroys the timer
    after logging its value when receiving the sibling '_stopped' signal.

    This allows a generalist and automatic benchmarking
    of the observed phenomenoms.

    """
    TIMER_PREFIX = '_timer_'  # used for generated attributes
    LAST_PREFIX = '_last_time_'  # used for generated attributes

    def __init__(self, round_ndigits=3, log_times=True, ignore=[]):
        """Wait for the ndigits parameter of the builtin round function.
        If log_times is False, no time will be logged.
        Ignore must be an iterable of Signals *Started to ignore.

        """
        self.log_times = log_times
        if round_ndigits:
            self.round = partial(round, ndigits=round_ndigits)
        else:
            self.round = round
        self.ignored = set(ignore)
        self.ignored |= set(  # add stopped signals
            Signals(s.value[:-len(SIGNAL_STARTED)] + SIGNAL_STOPPED)
            for s in self.ignored
        )
        assert all(s in Signals for s in self.ignored)


    def on_signals(self, signals):
        for signal in signals:
            if signal in self.ignored: continue
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
                                   + ' is stopped but not started.')

    def __get_property_or_none(self, prop):
        """Return given property value for self (use getattr), or None
        in case of AttributeError"""
        try:
            return getattr(self, prop)
        except AttributeError:
            return None

    @property
    def compression_time(self):
        prop = TimeCounter.property_named_from(Signals.CompressionStarted.value,
                                               prefix=TimeCounter.LAST_PREFIX)
        return self.__get_property_or_none(prop)

    @property
    def extraction_time(self):
        prop = TimeCounter.property_named_from(Signals.ExtractionStarted.value,
                                               prefix=TimeCounter.LAST_PREFIX)
        return self.__get_property_or_none(prop)

    @property
    def last_step_time(self):
        prop = TimeCounter.property_named_from(Signals.StepStarted.value,
                                               prefix=TimeCounter.LAST_PREFIX)
        return self.__get_property_or_none(prop)

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
        return Priorities.Maximal


class NullTimeCounter(CompressionObserver):
    """Null Pattern applicated to the TimeCounter class"""

    def __init__(self, round_ndigits=3, log_times=True, ignore=[]):
        pass

    def _update(self, signals):
        pass

    @property
    def compression_time(self):
        return 0.

    @property
    def extraction_time(self):
        return 0.

    @property
    def last_step_time(self):
        return 0.

    def log_timer(self, property_name):
        pass

    @staticmethod
    def property_named_from(signal_name, prefix=''):
        pass

    @staticmethod
    def prettified(property_name):
        return ''

    @property
    def priority(self):
        return Priorities.Maximal
