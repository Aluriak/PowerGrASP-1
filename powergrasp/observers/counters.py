"""
Definition of various counting related compression observers.

"""
from .observer import CompressionObserver, Signals, SIGNAL_FOUND
from powergrasp import commons


LOGGER = commons.logger()


class ConnectedComponentsCounter(CompressionObserver):
    """Counter of connected components"""

    def __init__(self):
        self._nb_ccs = '?'  # number of cc, printed after current cc number

    def _update(self, signals):
        if Signals.CCCountGenerated in signals:
            self._nb_ccs = str(signals[Signals.CCCountGenerated])
        if Signals.CCRemainEdgeGenerated in signals:
            count = len(signals[Signals.CCRemainEdgeGenerated])
            if count > 0:
                LOGGER.info(self.cc_name + ': ' + str(count)
                            + ' remaining edge(s)')
            else:
                LOGGER.info(self.cc_name + ': ' + 'No remaining edge')
        if Signals.ConnectedComponentStarted in signals:
            self.cc_num, self.cc_name = signals[Signals.ConnectedComponentStarted]
            LOGGER.info('#### CC ' + self.cc_name + ' ' + str(self.cc_num+1)
                        + '/' + self._nb_ccs)


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
        if Signals.CompressionFinalized in signals:
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
